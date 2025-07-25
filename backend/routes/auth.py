from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..database import authenticate_user, register_user
from ..models import db
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*required_roles):
    """角色验证装饰器 - 支持多个角色"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('请先登录', 'error')
                return redirect(url_for('auth.login'))
            
            from ..models import User
            user = User.query.get(session['user_id'])
            if not user or user.role not in required_roles:
                flash('权限不足', 'error')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 数据库认证
        user = authenticate_user(username, password)
        if user:
            # 更新最后登录时间
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('登录成功！', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'audience')  # 默认角色为 audience
        
        success, message = register_user(username, email, password, role)
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    flash('已成功登出', 'info')
    return redirect(url_for('main.index'))