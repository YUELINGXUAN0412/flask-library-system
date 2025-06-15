# app/models/borrow_record.py
from app import db
from datetime import datetime

class BorrowRecord(db.Model):
    """借阅记录模型"""
    __tablename__ = 'borrow_record'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='申请日期')
    borrow_date = db.Column(db.DateTime, comment='实际借出日期') 
    due_date = db.Column(db.DateTime, comment='应还日期')
    return_date = db.Column(db.DateTime, comment='实际归还日期')
    
    # 0:借阅待批, 1:借阅中, 2:已归还, 3:逾期归还, 6:还书待批, 9:借阅/预约失败或被拒绝
    status = db.Column(db.SmallInteger, nullable=False, default=0, comment='状态')
    
    fine_amount = db.Column(db.Numeric(10, 2), default=0)

    # 新增：用于存储管理员拒绝申请时的理由
    rejection_reason = db.Column(db.String(255), comment='拒绝理由')

    # 关系定义
    borrower = db.relationship('User', back_populates='borrow_records')
    borrowed_book = db.relationship('Book', back_populates='borrows')