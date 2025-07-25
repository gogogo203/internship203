from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import os

from .auth import login_required
from ..file_processor import allowed_file, extract_text_from_file
from ..ai_service import generate_mcq_from_text
from ..config import UPLOAD_FOLDER

main_bp = Blueprint('main', __name__)

# ==================== 基础页面路由 ====================

@main_bp.route('/')
def index():
    """首页"""
    if 'username' in session:
        return redirect(url_for('main.dashboard'))
    # 未登录用户重定向到登录页面
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """仪表板"""
    role = session.get('role', 'audience')
    username = session.get('username', '用户')
    
    if role == 'organizer':
        return render_template('organizer_dashboard.html', username=username)
    elif role == 'teacher':
        return render_template('teacher_dashboard.html', username=username)
    else:
        return render_template('audience_dashboard.html', username=username)

@main_bp.route('/home')
@login_required
def home():
    """主页"""
    return redirect(url_for('main.dashboard'))

# ==================== 文件上传和处理 ====================

@main_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """文件上传处理"""
    if 'file' not in request.files:
        flash('没有选择文件！', 'error')
        return redirect(request.referrer)
    
    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件！', 'error')
        return redirect(request.referrer)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            text_content = extract_text_from_file(filepath)
            questions = generate_mcq_from_text(text_content)
            
            if questions:
                session['questions'] = questions
                session['filename'] = filename
                flash(f'成功生成 {len(questions)} 道题目！', 'success')
                return redirect(url_for('main.quiz'))
            else:
                flash('生成题目失败，请检查文件内容！', 'error')
                
        except Exception as e:
            flash(f'文件处理失败：{str(e)}', 'error')
    else:
        flash('不支持的文件格式！', 'error')
    
    return redirect(request.referrer)

@main_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    """提交答案"""
    questions = session.get('questions', [])
    if not questions:
        flash('没有找到题目数据！', 'error')
        return redirect(url_for('main.dashboard'))
    
    total_questions = len(questions)
    correct_answers = 0
    results = []
    
    for i, question in enumerate(questions):
        user_answer = request.form.get(f'q{i}')
        correct_answer = question.get('answer')
        is_correct = user_answer == correct_answer
        
        if is_correct:
            correct_answers += 1
            
        results.append({
            'index': i + 1,
            'question': question.get('question', ''),
            'user': user_answer,
            'correct': correct_answer,
            'is_correct': is_correct
        })
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    session['score'] = score
    session['correct_answers'] = correct_answers
    session['total_questions'] = total_questions
    session['results'] = results
    
    flash(f'答题完成！得分：{score:.1f}分', 'success')
    return redirect(url_for('main.result'))

@main_bp.route('/result')
@login_required
def result():
    """结果页面"""
    score = session.get('score')
    correct_answers = session.get('correct_answers')
    total_questions = session.get('total_questions')
    results = session.get('results', [])
    
    if score is None:
        flash('没有找到答题结果！', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('result.html',
                         score=f'{score:.1f}',
                         correct_answers=correct_answers, 
                         total_questions=total_questions,
                         results=results)

@main_bp.route('/quiz')
@login_required
def quiz():
    """答题页面"""
    questions = session.get('questions', [])
    filename = session.get('filename', '未知文件')
    
    if not questions:
        flash('没有找到题目数据！', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('quiz.html', questions=questions, filename=filename)