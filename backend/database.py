from .models import db, User
from .config import USERS

def init_database(app):
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否需要创建默认用户
        if User.query.count() == 0:
            create_default_users()

def create_default_users():
    """创建默认用户"""
    for username, password in USERS.items():
        # 检查用户是否已存在
        if not User.query.filter_by(username=username).first():
            user = User(
                username=username,
                email=f"{username}@popquiz.com",  # 生成一个默认邮箱
                password=password,
                role=username  # 使用 username 作为角色
            )
            db.session.add(user)
    
    db.session.commit()

def register_user(username, email, password, role='audience'):
    """注册新用户"""
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return False, "用户名已存在"
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=email).first():
        return False, "邮箱已被注册"
    
    try:
        # 创建新用户
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return True, "注册成功"
    except Exception as e:
        db.session.rollback()
        return False, f"注册失败: {str(e)}"

def authenticate_user(username, password):
    """验证用户"""
    user = User.query.filter_by(username=username, is_active=True).first()
    if user and user.check_password(password):
        return user
    return None

def get_user_by_username(username):
    """根据用户名获取用户"""
    return User.query.filter_by(username=username, is_active=True).first()