# app/services/borrow_service.py
from datetime import datetime, timedelta
from app import db
from app.models.book import Book
from app.models.borrow_record import BorrowRecord
from app.models.system_config import SystemConfig
from app.models.reservation import Reservation

def request_borrow(user, book):
    """用户申请借书，创建待审批记录"""
    MAX_BORROW_COUNT = int(SystemConfig.get('MAX_BORROW_COUNT', 5))
    if book.status != 1 or book.available_count < 1:
        return {'success': False, 'message': '该图书当前不可借阅。'}
    pending_requests_count = db.session.query(BorrowRecord).filter_by(book_id=book.id, status=0).count()
    if book.available_count <= pending_requests_count:
        return {'success': False, 'message': '该图书的所有可借副本都已有用户正在申请，请稍后再试。'}
    current_borrows_and_requests = user.borrow_records.filter(BorrowRecord.status.in_([0, 1])).count()
    if current_borrows_and_requests >= MAX_BORROW_COUNT:
        return {'success': False, 'message': f'你的借阅和申请总数已达上限({MAX_BORROW_COUNT}本)。'}
    is_already_requested = user.borrow_records.filter_by(book_id=book.id, status=0).first()
    if is_already_requested:
        return {'success': False, 'message': '你已申请借阅此书，请等待审批。'}
    is_currently_borrowed = user.borrow_records.filter_by(book_id=book.id, status=1).first()
    if is_currently_borrowed:
        return {'success': False, 'message': '你已借阅此书，无需再次申请。'}
    try:
        new_record = BorrowRecord(user_id=user.id, book_id=book.id, status=0)
        db.session.add(new_record)
        db.session.commit()
        return {'success': True, 'message': '借阅申请已提交，请等待管理员审批。'}
    except Exception as e:
        db.session.rollback()
        print(f"申请借阅失败: {e}")
        return {'success': False, 'message': '申请借阅时发生错误。'}

def approve_borrow(record):
    """(管理员)批准借阅申请"""
    BORROW_DAYS = int(SystemConfig.get('BORROW_DAYS', 30))
    book = record.borrowed_book
    if record.status != 0:
        return {'success': False, 'message': '该申请状态不正确，无法批准。'}
    if book.available_count < 1:
        record.status = 9
        record.rejection_reason = '批准时库存不足'
        db.session.commit()
        return {'success': False, 'message': f'批准失败：图书《{book.title}》在你批准时已无库存。该申请已作废。'}
    try:
        with db.session.begin_nested():
            book.available_count -= 1
            if book.available_count == 0 and book.status == 1:
                book.status = 2
            record.status = 1
            record.borrow_date = datetime.utcnow()
            record.due_date = record.borrow_date + timedelta(days=BORROW_DAYS)
        db.session.commit()
        return {'success': True, 'message': '借阅申请已批准。'}
    except Exception as e:
        db.session.rollback()
        print(f"批准借阅失败: {e}")
        return {'success': False, 'message': '批准借阅时发生错误。'}

def reject_borrow(record, reason):
    """(管理员)拒绝借阅申请，并记录理由"""
    if record.status != 0:
        return {'success': False, 'message': '该申请状态不正确，无法操作。'}
    try:
        record.status = 9
        record.rejection_reason = reason # 保存拒绝理由
        db.session.commit()
        return {'success': True, 'message': '已拒绝该借阅申请。'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': '操作失败。'}

def request_return(record):
    """用户申请还书，只改变状态"""
    if record.status != 1:
        return {'success': False, 'message': '该书状态不正确，无法申请归还。'}
    try:
        record.status = 6
        db.session.commit()
        return {'success': True, 'message': '还书申请已提交，请等待管理员审批。'}
    except Exception as e:
        db.session.rollback()
        print(f"申请还书失败: {e}")
        return {'success': False, 'message': '申请还书时发生错误。'}

def approve_return(record):
    """(管理员)批准还书，并处理预约队列"""
    FINE_RATE = float(SystemConfig.get('FINE_RATE', 0.5))
    if record.status != 6:
        return {'success': False, 'message': '该记录状态不正确，无法批准。'}
    try:
        book = record.borrowed_book
        if not book:
            return {'success': False, 'message': '关联的图书不存在。'}
        with db.session.begin_nested():
            record.return_date = datetime.utcnow()
            if record.due_date and record.return_date > record.due_date:
                record.status = 3
                fine_days = (record.return_date.date() - record.due_date.date()).days
                record.fine_amount = fine_days * FINE_RATE
            else:
                record.status = 2
            next_reservation = db.session.scalars(db.select(Reservation).where(Reservation.book_id == book.id, Reservation.status == 1).order_by(Reservation.reservation_date.asc())).first()
            if next_reservation:
                book.status = 3
                next_reservation.status = 2
                message = f"归还已批准。图书《{book.title}》已为用户 {next_reservation.user.username} 保留。"
            else:
                book.available_count += 1
                if book.available_count > 0:
                    book.status = 1
                message = "归还已批准，图书已重新上架。"
        db.session.commit()
        return {'success': True, 'message': message}
    except Exception as e:
        db.session.rollback()
        print(f"批准还书失败: {e}")
        return {'success': False, 'message': '批准还书时发生错误。'}