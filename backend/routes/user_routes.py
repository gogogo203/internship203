from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .auth import role_required
from ..models import db, User

user_bp = Blueprint('user', __name__)

@user_bp.route('/users')
@role_required('organizer')
def manage_users():
    """用户管理页面"""
    users = User.query.all()
    
    current_user_id = session.get('user_id')
    current_user = User.query.get(current_user_id) if current_user_id else None
    
    return render_template('manage_users.html', 
                         users=users, 
                         current_user=current_user)

@user_bp.route('/users/<int:user_id>')
@role_required('organizer')
def view_user_detail(user_id):
    """查看用户详情"""
    user = User.query.get_or_404(user_id)
    return render_template('user_detail.html', user=user)

@user_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@role_required('organizer')
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']
        
        try:
            db.session.commit()
            flash('用户信息更新成功！', 'success')
            return redirect(url_for('user.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('edit_user.html', user=user)

@user_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@role_required('organizer')
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    # 防止删除当前登录用户
    current_user_id = session.get('user_id')
    if user.id == current_user_id:
        flash('不能删除当前登录的用户！', 'error')
        return redirect(url_for('user.manage_users'))
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f'用户 "{username}" 已成功删除！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除用户失败：{str(e)}', 'error')
    
    return redirect(url_for('user.manage_users'))