from functools import wraps
from flask import request, redirect, url_for, session, flash
from .config import USERS, USER_ROLE_MAPPING


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))  # 修改：添加蓝图前缀
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))  # 修改：添加蓝图前缀
            
            user_role = get_user_role(session['user_id'])
            if user_role != required_role:
                flash('您没有权限访问此页面', 'error')
                return redirect(url_for('main.dashboard'))  # 修改：添加蓝图前缀
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_user_role(username):
    """获取用户角色"""
    return USER_ROLE_MAPPING.get(username, 'audience')


def validate_user(username, password):
    """验证用户名和密码"""
    return username in USERS and USERS[username] == password


def get_all_users():
    """获取所有用户"""
    return list(USERS.keys())

