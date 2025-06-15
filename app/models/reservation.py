# app/models/reservation.py
from app import db
from datetime import datetime

class Reservation(db.Model):
    """预约记录模型"""
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    
    reservation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='预约申请日期')
    
    # 0:待批, 1:等待队列中, 2:已满足-待取书, 3:已取消, 4:已取书(转为借阅), 9:预约失败
    status = db.Column(db.SmallInteger, nullable=False, default=0, comment='预约状态')

    # 新增：用于存储管理员拒绝申请时的理由
    rejection_reason = db.Column(db.String(255), comment='拒绝理由')
    
    # 关系定义
    user = db.relationship('User', back_populates='reservations')
    book = db.relationship('Book', back_populates='reservations')