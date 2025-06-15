# app/services/reservation_service.py
from datetime import datetime, timedelta
from app import db
from app.models.book import Book
from app.models.borrow_record import BorrowRecord
from app.models.system_config import SystemConfig
from app.models.reservation import Reservation
from sqlalchemy import func, select

def request_reservation(user, book):
    MAX_RESERVATION_COUNT = int(SystemConfig.get('MAX_RESERVATION_COUNT', 3))
    if book.available_count > 0:
        return {'success': False, 'message': '该图书当前有库存，无需预约，可直接申请借阅。'}
    is_currently_borrowed = user.borrow_records.filter_by(book_id=book.id, status=1).first()
    if is_currently_borrowed:
        return {'success': False, 'message': '你已借阅此书，无需预约。'}
    is_already_reserved = user.reservations.filter(Reservation.book_id == book.id, Reservation.status.in_([0, 1, 2])).first()
    if is_already_reserved:
        return {'success': False, 'message': '你已预约此书或有待处理的申请，请勿重复操作。'}
    current_reservations = user.reservations.filter(Reservation.status.in_([0, 1, 2])).count()
    if current_reservations >= MAX_RESERVATION_COUNT:
        return {'success': False, 'message': f'你已达到最大预约数量（{MAX_RESERVATION_COUNT}本）。'}
    try:
        new_reservation = Reservation(user_id=user.id, book_id=book.id, status=0)
        db.session.add(new_reservation)
        db.session.commit()
        return {'success': True, 'message': f'成功提交《{book.title}》的预约申请，请等待管理员审批。'}
    except Exception as e:
        db.session.rollback()
        print(f"预约申请失败，错误: {e}")
        return {'success': False, 'message': '预约申请过程中发生错误。'}

def approve_reservation(reservation):
    if reservation.status != 0:
        return {'success': False, 'message': '该预约申请状态不正确。'}
    try:
        reservation.status = 1
        db.session.commit()
        return {'success': True, 'message': '预约申请已批准。'}
    except Exception as e:
        db.session.rollback()
        print(f"批准预约失败，错误: {e}")
        return {'success': False, 'message': '批准预约时发生错误。'}

def reject_reservation(reservation, reason):
    if reservation.status != 0:
        return {'success': False, 'message': '该预约申请状态不正确。'}
    try:
        reservation.status = 9
        reservation.rejection_reason = reason
        db.session.commit()
        return {'success': True, 'message': '已拒绝该预约申请。'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': '操作失败。'}

def cancel_reservation(reservation):
    if reservation.status not in [0, 1]:
        return {'success': False, 'message': '该预约已处理或已取消，无法操作。'}
    try:
        db.session.delete(reservation)
        db.session.commit()
        return {'success': True, 'message': '预约已成功取消。'}
    except Exception as e:
        db.session.rollback()
        print(f"取消预约失败，错误: {e}")
        return {'success': False, 'message': '取消预约时发生错误。'}

def fulfill_reservation(reservation):
    """(管理员)为用户完成预约取书，生成“借阅中”的记录，并更新预约状态"""
    if reservation.status != 2:
        return {'success': False, 'message': '该预约状态不正确，无法办理取书。'}
    
    user = reservation.user
    book = reservation.book
    BORROW_DAYS = int(SystemConfig.get('BORROW_DAYS', 30))

    try:
        with db.session.begin_nested():
            # 1. 将图书状态从“保留中”(3)更新为“全部借出”(2)
            book.status = 2 

            # 2. 将此预约记录的状态改为“已取书”(4)，而不是删除
            reservation.status = 4
            
            # 3. 为该用户创建一条新的、状态为1“借阅中”的借阅记录
            due_date = datetime.utcnow() + timedelta(days=BORROW_DAYS)
            new_record = BorrowRecord(
                user_id=user.id,
                book_id=book.id,
                status=1, # 直接就是借阅中
                request_date=reservation.reservation_date,
                borrow_date=datetime.utcnow(),
                due_date=due_date
            )
            db.session.add(new_record)
        
        db.session.commit()
        return {'success': True, 'message': f'已为用户 {user.username} 成功办理《{book.title}》的借阅。'}
    except Exception as e:
        db.session.rollback()
        print(f"完成预约失败，错误: {e}")
        return {'success': False, 'message': '完成预约时发生错误。'}