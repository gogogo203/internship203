"""Backend模块 - PopQuiz项目的后端功能模块"""

import os
from flask import Flask
from datetime import datetime, timezone, timedelta
from .models import db
from .database import init_database
from .config import (
    UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH,
    SECRET_KEY,
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS
)

class Config:
    SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = SQLALCHEMY_TRACK_MODIFICATIONS
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, 
                template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'front', 'html')),
                static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'front')))

    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化SQLAlchemy
    db.init_app(app)
    
    # 添加时区转换过滤器
    @app.template_filter('to_china_time')
    def to_china_time(utc_time):
        """将UTC时间转换为中国时间（UTC+8）"""
        if utc_time is None:
            return None
        # 如果时间没有时区信息，假设为UTC
        if utc_time.tzinfo is None:
            utc_time = utc_time.replace(tzinfo=timezone.utc)
        # 转换为中国时区
        china_tz = timezone(timedelta(hours=8))
        return utc_time.astimezone(china_tz)
    
    # 初始化数据库
    init_database(app)

    from .routes.auth import auth_bp
    from .routes.main_routes import main_bp
    from .routes.user_routes import user_bp
    from .routes.presentation_routes import presentation_bp
    from .routes.quiz_routes import quiz_bp
    from .routes.feedback_routes import feedback_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(presentation_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(feedback_bp)

    return app

__all__ = [
    'ZHIPU_API_KEY',
    'UPLOAD_FOLDER', 
    'MAX_CONTENT_LENGTH',
    'SECRET_KEY',
    'ALLOWED_EXTENSIONS',
    'USERS',
    'login_required',
    'validate_user',
    'get_all_users',
    'allowed_file',
    'extract_text_from_file',
    'ZhipuAI',
    'generate_mcq_from_text',
    'register_routes'
]
