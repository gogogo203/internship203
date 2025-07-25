from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .auth import role_required, login_required
from ..models import db, Presentation, User

presentation_bp = Blueprint('presentation', __name__)

@presentation_bp.route('/presentations', methods=['GET', 'POST'])
@role_required('teacher', 'organizer')
def manage_presentations():
    """演示文稿管理"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        
        # 如果是组织者，可以选择teacher作为创建者
        current_user_role = session.get('role')
        if current_user_role == 'organizer':
            creator_id = request.form.get('creator_id')
            if not creator_id:
                flash('请选择演讲者（老师）', 'error')
                # 获取所有teacher用户供选择
                teachers = User.query.filter_by(role='teacher', is_active=True).all()
                presentations = Presentation.query.filter_by(is_active=True).all()
                return render_template('manage_presentations.html', 
                                     presentations=presentations, 
                                     teachers=teachers)
        else:
            # 如果是teacher，创建者就是自己
            creator_id = session.get('user_id')
        
        presentation = Presentation(
            title=title,
            description=description,
            creator_id=creator_id
        )
        
        try:
            db.session.add(presentation)
            db.session.commit()
            flash('演示文稿创建成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
    
    presentations = Presentation.query.filter_by(is_active=True).all()
    
    # 如果是组织者，获取所有teacher用户供选择
    teachers = []
    if session.get('role') == 'organizer':
        teachers = User.query.filter_by(role='teacher', is_active=True).all()
    
    return render_template('manage_presentations.html', 
                         presentations=presentations, 
                         teachers=teachers)

@presentation_bp.route('/presentations/<int:id>')
@login_required
def view_presentation(id):
    """查看演示文稿"""
    presentation = Presentation.query.get_or_404(id)
    return render_template('presentation_detail.html', presentation=presentation)