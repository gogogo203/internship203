from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='student')  # admin, teacher, student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)  # 添加这一行
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, username, email, password, role='student'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


from datetime import datetime

class Presentation(db.Model):
    """演讲模型"""
    __tablename__ = 'presentations'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    creator = db.relationship('User', backref='presentations')
    quizzes = db.relationship('Quiz', backref='presentation', cascade='all, delete-orphan')

class Quiz(db.Model):
    """测试模型"""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentations.id'), nullable=True)  # 改为 nullable=True
    questions_data = db.Column(db.Text)  # JSON格式存储题目
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    time_limit = db.Column(db.Integer, default=300)  # 秒
    
    # 关系
    responses = db.relationship('QuizResponse', backref='quiz', cascade='all, delete-orphan')

class QuizResponse(db.Model):
    """答题记录模型"""
    __tablename__ = 'quiz_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers_data = db.Column(db.Text)  # JSON格式存储答案
    score = db.Column(db.Float, default=0.0)
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent = db.Column(db.Integer, default=0)  # 秒
    
    # 关系
    user = db.relationship('User', backref='quiz_responses')
    
    # 唯一约束：每个用户每个测试只能答一次
    __table_args__ = (db.UniqueConstraint('quiz_id', 'user_id', name='unique_user_quiz'),)

class Feedback(db.Model):
    """反馈模型"""
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5星评分
    content = db.Column(db.Text)  # 文字反馈内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, default=False)  # 是否匿名反馈
    
    # 关系
    presentation = db.relationship('Presentation', backref='feedbacks')
    user = db.relationship('User', backref='feedbacks')
    
    # 唯一约束：每个用户每个演讲只能反馈一次
    __table_args__ = (db.UniqueConstraint('presentation_id', 'user_id', name='unique_user_presentation_feedback'),)