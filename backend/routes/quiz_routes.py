from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import json
from werkzeug.utils import secure_filename
import os

from .auth import login_required, role_required
from ..models import db, Quiz, QuizResponse, User, Presentation
from ..ai_service import generate_mcq_from_text
from ..file_processor import extract_text_from_file, allowed_file  # 添加 allowed_file 导入
import uuid
import time
from ..config import UPLOAD_FOLDER

quiz_bp = Blueprint('quiz', __name__)

# ==================== 测验管理 ====================

@quiz_bp.route('/presentation/<int:presentation_id>/create-quiz', methods=['GET', 'POST'])
@role_required('teacher', 'organizer')
def create_quiz(presentation_id):
    """创建测验"""
    presentation = Presentation.query.get_or_404(presentation_id)
    
    if request.method == 'POST':
        title = request.form['title']
        questions_data = request.form['questions_data']
        time_limit = int(request.form.get('time_limit', 300))
        
        quiz = Quiz(
            title=title,
            presentation_id=presentation_id,
            questions_data=questions_data,
            time_limit=time_limit
        )
        
        try:
            db.session.add(quiz)
            db.session.commit()
            flash('测验创建成功！', 'success')
            return redirect(url_for('presentation.manage_presentations'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
    
    # 直接重定向到生成题目界面，而不是渲染不存在的模板
    return redirect(url_for('quiz.create_quiz_from_file'))
    return render_template('create_quiz.html', presentation=presentation)

@quiz_bp.route('/create-quiz-from-file', methods=['GET'])
@login_required
def create_quiz_from_file():
    """从文件创建测验页面"""
    # 获取当前用户创建的演讲或所有活跃演讲（根据权限）
    user_role = session.get('role')
    if user_role == 'organizer':
        # 组织者可以看到所有演讲
        presentations = Presentation.query.filter_by(is_active=True).all()
    else:
        # 老师只能看到自己创建的演讲
        user_id = session.get('user_id')
        presentations = Presentation.query.filter_by(creator_id=user_id, is_active=True).all()
    
    return render_template('create_quiz_from_file.html', presentations=presentations)

@quiz_bp.route('/process-file-for-quiz', methods=['POST'])
@login_required
def process_file_for_quiz():
    """处理文件生成测验"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    # 获取表单参数
    quiz_title = request.form.get('quiz_title', '').strip()
    time_limit = request.form.get('time_limit', 10)
    question_count = request.form.get('question_count', 5)
    presentation_id = request.form.get('presentation_id')  # 添加这行
    
    # 验证参数
    if not quiz_title:
        return jsonify({'success': False, 'message': '请输入测试标题'})
    
    # 验证演讲ID（添加这个验证）
    if presentation_id:
        try:
            presentation_id = int(presentation_id)
            presentation = Presentation.query.get(presentation_id)
            if not presentation:
                return jsonify({'success': False, 'message': '选择的演讲不存在'})
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '演讲选择无效'})
    else:
        presentation_id = None
    
    try:
        time_limit = int(time_limit) * 60  # 转换为秒
        question_count = int(question_count)
        question_count = max(5, min(50, question_count))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '参数格式错误'})
    
    # 使用原始文件名检查扩展名
    if file and allowed_file(file.filename):
        # 保留原始文件名用于扩展名提取
        original_filename = file.filename
        
        # 生成安全的文件名用于保存
        import time
        import uuid
        # 提取扩展名
        file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        # 生成唯一的安全文件名
        safe_filename = f"{uuid.uuid4().hex}_{int(time.time())}.{file_ext}"
        
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        file.save(filepath)
        
        try:
            text_content = extract_text_from_file(filepath)
            if not text_content or len(text_content.strip()) < 50:
                return jsonify({'success': False, 'message': '文件内容太少，无法生成题目'})
            
            # 使用用户指定的题目数量
            questions = generate_mcq_from_text(text_content, question_count)
            
            if questions:
                # 创建测试记录并保存到数据库
                quiz = Quiz(
                    title=quiz_title,
                    presentation_id=presentation_id,  # 修改这行，使用用户选择的演讲ID
                    questions_data=json.dumps(questions),
                    time_limit=time_limit,
                    is_active=True
                )
                
                try:
                    db.session.add(quiz)
                    db.session.commit()
                    
                    return jsonify({
                        'success': True, 
                        'message': f'成功创建测试：{quiz_title}',
                        'quiz_id': quiz.id,
                        'questions': questions,
                        'filename': original_filename
                    })
                except Exception as db_error:
                    db.session.rollback()
                    return jsonify({'success': False, 'message': f'保存测试失败：{str(db_error)}'})
            else:
                return jsonify({'success': False, 'message': 'AI服务暂时不可用，请稍后重试'})
                
        except Exception as e:
            error_msg = str(e)
            if 'timeout' in error_msg.lower():
                return jsonify({'success': False, 'message': '网络连接超时，请检查网络后重试'})
            else:
                return jsonify({'success': False, 'message': f'文件处理失败：{error_msg}'})
    
    return jsonify({'success': False, 'message': '不支持的文件格式'})

# ==================== 听众功能 ====================

@quiz_bp.route('/<int:quiz_id>/join', methods=['GET'])
@login_required
def join_quiz_session(quiz_id):
    """参与测试答题"""
    quiz = Quiz.query.get_or_404(quiz_id)
    if not quiz.is_active:
        flash('该测试已关闭！', 'error')
        return redirect(url_for('quiz.available_quizzes'))
    
    questions = json.loads(quiz.questions_data)
    return render_template('take_quiz.html', quiz=quiz, questions=questions)

@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz_response(quiz_id):
    """提交测试答案"""
    quiz = Quiz.query.get_or_404(quiz_id)
    user_id = session.get('user_id')
    
    existing_response = QuizResponse.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()
    if existing_response:
        flash('您已经提交过该测试！', 'warning')
        return redirect(url_for('quiz.view_quiz_result', response_id=existing_response.id))
    
    questions = json.loads(quiz.questions_data)
    total_questions = len(questions)
    correct_answers = 0
    
    for i, question in enumerate(questions):
        user_answer = request.form.get(f'q{i}')
        correct_answer = question.get('correct_answer')
        
        # 确保大小写一致性比较
        if user_answer and correct_answer:
            if user_answer.upper() == correct_answer.upper():
                correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # 获取答题时间
    time_spent = int(request.form.get('time_spent', 0))
    
    response = QuizResponse(
        quiz_id=quiz_id,
        user_id=user_id,
        answers_data=json.dumps(request.form.to_dict()),
        score=score,
        correct_answers=correct_answers,
        total_questions=total_questions,
        time_spent=time_spent  # 添加这一行
    )
    
    db.session.add(response)
    db.session.commit()
    
    flash(f'提交成功！您的得分：{score:.1f}分', 'success')
    return redirect(url_for('quiz.view_quiz_result', response_id=response.id))

@quiz_bp.route('/result/<int:response_id>', methods=['GET'])
@login_required
def view_quiz_result(response_id):
    """查看答题结果"""
    response = QuizResponse.query.get_or_404(response_id)
    
    if response.user_id != session.get('user_id'):
        flash('无权查看该结果！', 'error')
        return redirect(url_for('quiz.my_quiz_history'))
    
    quiz = Quiz.query.get(response.quiz_id)
    questions = json.loads(quiz.questions_data)
    user_answers = json.loads(response.answers_data)
    
    results = []
    for i, question in enumerate(questions):
        user_answer = user_answers.get(f'q{i}')  # 改为 q{i} 格式
        correct_answer = question.get('correct_answer')
        is_correct = user_answer == correct_answer
        
        results.append({
            'index': i + 1,
            'user': user_answer,
            'correct': correct_answer,
            'is_correct': is_correct
        })
    
    return render_template('quiz_result.html', 
                         score=f'{response.score:.1f}分',
                         results=results,
                         username=session.get('username', '用户'))

@quiz_bp.route('/available', methods=['GET'])
@login_required
def available_quizzes():
    """显示可用的测试列表"""
    quizzes = Quiz.query.filter_by(is_active=True).all()
    user_id = session.get('user_id')
    
    user_responses = {}
    completed_quiz_ids = set()
    
    for response in QuizResponse.query.filter_by(user_id=user_id).all():
        user_responses[response.quiz_id] = response
        completed_quiz_ids.add(response.quiz_id)
    
    return render_template('available_quizzes.html', 
                         quizzes=quizzes,
                         completed_quiz_ids=completed_quiz_ids,
                         user_responses=user_responses,
                         username=session.get('username', '用户'))

@quiz_bp.route('/history', methods=['GET'])
@login_required
def my_quiz_history():
    """我的答题历史"""
    user_id = session.get('user_id')
    responses = QuizResponse.query.filter_by(user_id=user_id).order_by(
        QuizResponse.submitted_at.desc()
    ).all()
    
    # 为每个response计算排名和正确率
    for response in responses:
        # 获取该测试的所有参与者成绩，按分数降序排列
        all_responses = QuizResponse.query.filter_by(quiz_id=response.quiz_id).order_by(
            QuizResponse.score.desc()
        ).all()
        
        # 计算并列排名
        rank = 1
        current_score = None
        for i, r in enumerate(all_responses):
            if current_score is None or r.score < current_score:
                rank = i + 1
                current_score = r.score
            
            if r.id == response.id:
                response.rank = rank
                break
        
        # 计算总参与人数
        response.total_participants = len(all_responses)
        
        # 计算正确率
        if hasattr(response, 'correct_answers') and hasattr(response, 'total_questions'):
            response.accuracy_rate = round((response.correct_answers / response.total_questions) * 100, 1) if response.total_questions > 0 else 0
        else:
            response.accuracy_rate = round(response.score, 1)
    
    if responses:
        total_quizzes = len(responses)
        avg_score = sum(r.score for r in responses) / total_quizzes
        best_score = max(r.score for r in responses)
        # 计算平均排名
        avg_rank = sum(getattr(r, 'rank', 0) for r in responses) / total_quizzes if total_quizzes > 0 else 0
    else:
        total_quizzes = 0
        avg_score = 0
        best_score = 0
        avg_rank = 0
    
    stats = {
        'total_quizzes': total_quizzes,
        'avg_score': round(avg_score, 2),
        'best_score': best_score,
        'avg_rank': round(avg_rank, 1)
    }
    
    return render_template('my_quiz_history.html', responses=responses, stats=stats)

@quiz_bp.route('/quick-join', methods=['POST'])
@login_required
def quick_join_quiz():
    """快速参与测试"""
    quiz_code = request.form.get('quiz_code')
    flash('请从下方选择要参与的测试', 'info')
    return redirect(url_for('quiz.available_quizzes'))

# ==================== 统计和报告 ====================

@quiz_bp.route('/<int:quiz_id>/statistics', methods=['GET'])
@role_required('teacher', 'organizer')
def view_quiz_statistics(quiz_id):
    """查看测试统计"""
    quiz = Quiz.query.get_or_404(quiz_id)
    responses = QuizResponse.query.filter_by(quiz_id=quiz_id).all()
    
    if not responses:
        return render_template('quiz_statistics.html', 
                             quiz=quiz, 
                             responses=[], 
                             overall_stats={},
                             question_stats=[])
    
    # 基本统计
    total_participants = len(responses)
    avg_score = sum(r.score for r in responses) / total_participants
    max_score = max(r.score for r in responses)
    min_score = min(r.score for r in responses)
    completion_rate = 100  # 所有提交的都算完成
    
    # 整体统计
    overall_stats = {
        'total_participants': total_participants,
        'avg_score': round(avg_score, 1),
        'max_score': round(max_score, 1),
        'min_score': round(min_score, 1),
        'completion_rate': completion_rate
    }
    
    # 题目分析
    questions = json.loads(quiz.questions_data)
    question_stats = []
    
    for q_index, question in enumerate(questions):
        # 统计每个选项的选择次数
        option_distribution = {'0': 0, '1': 0, '2': 0, '3': 0}  # A, B, C, D
        correct_count = 0
        total_answers = 0
        
        for response in responses:
            answers_data = json.loads(response.answers_data)
            user_answer = answers_data.get(f'q{q_index}')
            
            if user_answer:
                total_answers += 1
                # 将A,B,C,D转换为0,1,2,3
                option_map = {'A': '0', 'B': '1', 'C': '2', 'D': '3'}
                option_index = option_map.get(user_answer.upper())
                if option_index:
                    option_distribution[option_index] += 1
                
                # 检查是否正确
                correct_answer = question.get('correct_answer', '')
                if user_answer.upper() == correct_answer.upper():
                    correct_count += 1
        
        # 计算正确率
        accuracy_rate = (correct_count / total_answers * 100) if total_answers > 0 else 0
        
        question_stat = {
            'question_num': q_index + 1,
            'question_text': question.get('question', ''),
            'accuracy_rate': round(accuracy_rate, 1),
            'option_distribution': option_distribution,
            'total_answers': total_answers,
            'correct_count': correct_count
        }
        question_stats.append(question_stat)
    
    # 为响应添加排名和额外信息
    responses.sort(key=lambda x: x.score, reverse=True)
    for i, response in enumerate(responses):
        response.rank = i + 1
        # 计算答题时间（如果有的话）
        response.time_spent = getattr(response, 'time_spent', 0)
    
    return render_template('quiz_statistics.html', 
                         quiz=quiz, 
                         responses=responses, 
                         overall_stats=overall_stats,
                         question_stats=question_stats)

@quiz_bp.route('/overview', methods=['GET'])
@role_required('teacher', 'organizer')
def organizer_quiz_overview():
    """组织者测验概览"""
    quizzes = Quiz.query.all()
    
    # 计算整体统计
    total_quizzes = len(quizzes)
    active_quizzes = len([q for q in quizzes if q.is_active])
    
    # 计算每个测试的统计信息
    quiz_stats = []
    total_completion_rate = 0
    
    # 收集所有参与过测试的用户ID（去重）
    unique_participants = set()
    
    for quiz in quizzes:
        responses = QuizResponse.query.filter_by(quiz_id=quiz.id).all()
        response_count = len(responses)
        
        # 收集该测试的参与者ID
        for response in responses:
            unique_participants.add(response.user_id)
        
        if response_count > 0:
            avg_score = sum(r.score for r in responses) / response_count
            excellent_count = len([r for r in responses if r.score >= 80])
            completion_rate = 100  # 假设所有提交的都算完成
        else:
            avg_score = 0
            excellent_count = 0
            completion_rate = 0
        
        total_completion_rate += completion_rate
        
        quiz_stat = {
            'quiz': quiz,
            'total_responses': response_count,
            'avg_score': round(avg_score, 1),
            'completion_rate': completion_rate,
            'excellent_count': excellent_count
        }
        quiz_stats.append(quiz_stat)
    
    # 计算独立参与者总数（去重后的用户数量）
    total_participants = len(unique_participants)
    
    # 计算平均完成率
    avg_completion_rate = round(total_completion_rate / total_quizzes, 1) if total_quizzes > 0 else 0
    
    return render_template('organizer_quiz_overview.html', 
                         quizzes=quizzes,
                         quiz_stats=quiz_stats,
                         total_quizzes=total_quizzes,
                         total_participants=total_participants,
                         active_quizzes=active_quizzes,
                         avg_completion_rate=avg_completion_rate)

# 删除以下路由函数:
# @quiz_bp.route('/reports/audience', methods=['GET'])
# @role_required('organizer')
# def audience_reports():
#     """听众报告"""
#     responses = QuizResponse.query.all()
#     return render_template('audience_reports.html', responses=responses)

@quiz_bp.route('/<int:quiz_id>/participants', methods=['GET'])
@role_required('teacher', 'organizer')
def quiz_participant_list(quiz_id):
    """测验参与者列表"""
    quiz = Quiz.query.get_or_404(quiz_id)
    responses = QuizResponse.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz_participants.html', quiz=quiz, responses=responses)

@quiz_bp.route('/<int:quiz_id>/delete', methods=['POST'])
@role_required('teacher', 'organizer')
def delete_quiz(quiz_id):
    """删除测试"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    try:
        # 删除相关的答题记录（由于设置了cascade，会自动删除）
        db.session.delete(quiz)
        db.session.commit()
        flash(f'测试 "{quiz.title}" 已成功删除！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除测试失败：{str(e)}', 'error')
    
    return redirect(url_for('quiz.organizer_quiz_overview'))