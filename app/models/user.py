# app/models/user.py
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(256), nullable=False, comment='加密密码')
    email = db.Column(db.String(100), unique=True, nullable=False, comment='邮箱')
    phone = db.Column(db.String(20), comment='手机号')
    avatar_image = db.Column(db.String(255), comment='用户头像图片路径')
    
    # 核心改动：更新角色注释
    role = db.Column(db.SmallInteger, nullable=False, default=1, comment='角色: 1-普通用户, 2-管理员, 3-超级管理员')
    
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment='账号状态，1为启用，0为禁用')
    create_time = db.Column(db.DateTime, server_default=db.func.now(), comment='创建时间')

    # 关系定义
    borrow_records = db.relationship('BorrowRecord', back_populates='borrower', lazy='dynamic', cascade="all, delete-orphan")
    reservations = db.relationship('Reservation', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))