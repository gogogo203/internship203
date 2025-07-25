from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from .auth import login_required, role_required
from ..models import db, Presentation, Feedback, User
import json

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/presentations/feedback', methods=['GET'])
@login_required
def select_presentation():
    """选择演讲进行反馈"""
    presentations = Presentation.query.filter_by(is_active=True).all()
    user_id = session.get('user_id')
    
    # 获取用户已经反馈过的演讲ID
    existing_feedbacks = Feedback.query.filter_by(user_id=user_id).all()
    feedback_presentation_ids = [f.presentation_id for f in existing_feedbacks]
    
    return render_template('select_presentation_feedback.html', 
                         presentations=presentations,
                         feedback_presentation_ids=feedback_presentation_ids)

@feedback_bp.route('/presentations/<int:presentation_id>/feedback', methods=['GET', 'POST'])
@login_required
def submit_feedback(presentation_id):
    """提交演讲反馈"""
    presentation = Presentation.query.get_or_404(presentation_id)
    user_id = session.get('user_id')
    
    # 检查是否已经反馈过
    existing_feedback = Feedback.query.filter_by(
        presentation_id=presentation_id, 
        user_id=user_id
    ).first()
    
    if request.method == 'POST':
        if existing_feedback:
            flash('您已经对该演讲提交过反馈！', 'warning')
            return redirect(url_for('feedback.select_presentation'))
        
        rating = request.form.get('rating', type=int)
        content = request.form.get('content', '').strip()
        is_anonymous = 'is_anonymous' in request.form
        
        # 收集详细反馈选项
        speaker_feedback = request.form.getlist('speaker_feedback')
        question_feedback = request.form.getlist('question_feedback')
        environment_feedback = request.form.getlist('environment_feedback')
        
        if not rating or rating < 1 or rating > 5:
            flash('请选择有效的评分（1-5星）！', 'error')
            return render_template('submit_feedback.html', 
                                 presentation=presentation,
                                 existing_feedback=existing_feedback)
        
        # 构建详细反馈内容
        detailed_feedback = {
            'speaker': speaker_feedback,
            'questions': question_feedback,
            'environment': environment_feedback,
            'additional_comments': content
        }
        
        feedback = Feedback(
            presentation_id=presentation_id,
            user_id=user_id,
            rating=rating,
            content=json.dumps(detailed_feedback, ensure_ascii=False),  # 存储为JSON
            is_anonymous=is_anonymous
        )
        
        try:
            db.session.add(feedback)
            db.session.commit()
            flash('反馈提交成功！感谢您的详细反馈。', 'success')
            return redirect(url_for('feedback.select_presentation'))
        except Exception as e:
            db.session.rollback()
            flash(f'提交失败：{str(e)}', 'error')
    
    return render_template('submit_feedback.html', 
                         presentation=presentation,
                         existing_feedback=existing_feedback)

@feedback_bp.route('/presentations/<int:presentation_id>/feedbacks', methods=['GET'])
@role_required('teacher', 'organizer')
def view_presentation_feedbacks(presentation_id):
    """查看演讲反馈（仅老师和组织者可见）"""
    presentation = Presentation.query.get_or_404(presentation_id)
    feedbacks = Feedback.query.filter_by(presentation_id=presentation_id).order_by(
        Feedback.created_at.desc()
    ).all()
    
    # 计算统计信息
    total_feedbacks = len(feedbacks)
    if total_feedbacks > 0:
        avg_rating = sum(f.rating for f in feedbacks) / total_feedbacks
        rating_distribution = {i: len([f for f in feedbacks if f.rating == i]) for i in range(1, 6)}
    else:
        avg_rating = 0
        rating_distribution = {i: 0 for i in range(1, 6)}
    
    return render_template('presentation_feedbacks.html',
                         presentation=presentation,
                         feedbacks=feedbacks,
                         total_feedbacks=total_feedbacks,
                         avg_rating=avg_rating,
                         rating_distribution=rating_distribution)

@feedback_bp.route('/my-feedbacks', methods=['GET'])
@login_required
def my_feedbacks():
    """我的反馈历史"""
    user_id = session.get('user_id')
    feedbacks = Feedback.query.filter_by(user_id=user_id).order_by(
        Feedback.created_at.desc()
    ).all()
    
    return render_template('my_feedbacks.html', feedbacks=feedbacks)


# 反馈选项映射
FEEDBACK_MAPPING = {
    'speaker': {
        'too_fast': '讲得太快',
        'too_slow': '讲得太慢',
        'good_pace': '节奏适中',
        'boring': '演讲内容太乏味',
        'engaging': '演讲内容生动有趣',
        'clear_explanation': '讲解清晰易懂',
        'unclear_explanation': '讲解不够清晰',
        'good_interaction': '互动性强',
        'lack_interaction': '缺乏互动',
        'confident': '演讲自信',
        'nervous': '显得紧张'
    },
    'questions': {
        'poor_quality': '题目出得质量不好',
        'good_quality': '题目质量很好',
        'ambiguous': '题目表述不清',
        'too_deep': '题目太深',
        'too_shallow': '题目太浅显',
        'appropriate_difficulty': '难度适中',
        'irrelevant': '和演讲内容不相关',
        'highly_relevant': '与内容高度相关',
        'partially_relevant': '部分相关',
        'too_many': '题目太多',
        'too_few': '题目太少',
        'appropriate_amount': '数量合适'
    },
    'environment': {
        'poor_classroom': '教室环境不好',
        'good_classroom': '教室环境很好',
        'too_crowded': '空间太拥挤',
        'poor_lighting': '光线不足',
        'poor_audio': '音响效果差',
        'good_audio': '音响效果好',
        'volume_too_low': '音量太小',
        'volume_too_high': '音量太大',
        'poor_projection': '投影效果不清晰',
        'good_projection': '投影效果清晰',
        'screen_too_small': '屏幕太小',
        'noisy': '环境太嘈杂',
        'temperature_uncomfortable': '温度不适宜',
        'poor_ventilation': '通风不良',
        'comfortable_environment': '环境舒适'
    }
}

# 注册模板函数
@feedback_bp.app_template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value) if value else {}
    except:
        return {}

@feedback_bp.app_template_global()
def get_feedback_text(code, category):
    return FEEDBACK_MAPPING.get(category, {}).get(code, code)


@feedback_bp.route('/all-feedbacks', methods=['GET'])
@role_required('teacher', 'organizer')
def all_feedbacks_overview():
    """老师和组织者查看所有演讲反馈概览"""
    presentations = Presentation.query.all()
    
    presentation_stats = []
    total_feedbacks = 0
    total_rating_sum = 0
    
    for presentation in presentations:
        feedbacks = Feedback.query.filter_by(presentation_id=presentation.id).all()
        feedback_count = len(feedbacks)
        total_feedbacks += feedback_count
        
        if feedback_count > 0:
            avg_rating = sum(f.rating for f in feedbacks) / feedback_count
            total_rating_sum += sum(f.rating for f in feedbacks)
            rating_distribution = {i: len([f for f in feedbacks if f.rating == i]) for i in range(1, 6)}
        else:
            avg_rating = 0
            rating_distribution = {i: 0 for i in range(1, 6)}
        
        presentation_stat = {
            'presentation': presentation,
            'feedback_count': feedback_count,
            'avg_rating': round(avg_rating, 1),
            'rating_distribution': rating_distribution,
            'latest_feedback': feedbacks[-1] if feedbacks else None
        }
        presentation_stats.append(presentation_stat)
    
    # 计算整体统计
    overall_avg_rating = round(total_rating_sum / total_feedbacks, 1) if total_feedbacks > 0 else 0
    
    overall_stats = {
        'total_presentations': len(presentations),
        'total_feedbacks': total_feedbacks,
        'overall_avg_rating': overall_avg_rating
    }
    
    return render_template('all_feedbacks_overview.html',
                         presentation_stats=presentation_stats,
                         overall_stats=overall_stats)