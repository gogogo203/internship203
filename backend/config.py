import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 智谱AI API配置
ZHIPU_API_KEY = os.environ.get('ZHIPU_API_KEY')

# 数据库配置
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///popquiz.db')

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max file size

# 支持的文件类型
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'ppt', 'pptx'}

# 用户角色
USER_ROLES = {
    'organizer': 'Organizer',
    'teacher': 'Teacher',
    'audience': 'Audience'
}

# 默认用户
# 注意：这里的密码是明文存储的，仅用于开发环境的快速设置。
# 在生产环境中，应使用更安全的密码管理策略。
USERS = {
    'organizer': 'password',
    'teacher': 'password',
    'audience': 'password'
}

# 用户角色映射
USER_ROLE_MAPPING = {
    'organizer': 'organizer',
    'teacher': 'teacher', 
    'audience': 'audience'
}

# Flask 应用密钥
SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 检查API密钥
if not ZHIPU_API_KEY:
    print("警告: 未设置ZHIPU_API_KEY环境变量，请在.env文件中添加您的API密钥")