# app/routes/borrow.py
from flask import Blueprint, flash, redirect, url_for, render_template, abort
from flask_login import login_required, current_user
from app.services import borrow_service, reservation_service
from app.models.book import Book
from app.models.borrow_record import BorrowRecord
from app.models.reservation import Reservation
from app import db

bp = Blueprint('borrow', __name__)

@bp.route('/borrow/confirm/<int:book_id>')
@login_required
def confirm_borrow(book_id):
    """显示借阅确认页面"""
    book = db.session.get(Book, book_id)
    if book is None or book.status != 1 or book.available_count == 0:
        flash('该图书当前不可借阅。', 'warning')
        return redirect(url_for('main.index'))
    return render_template('borrow/confirm_borrow.html', book=book, title='借阅确认')

@bp.route('/request_borrow/<int:book_id>', methods=['POST'])
@login_required
def request_borrow_route(book_id):
    """处理用户借阅申请的路由"""
    book = db.session.get(Book, book_id)
    if book is None:
        flash('未找到指定的图书。', 'warning')
        return redirect(url_for('main.index'))
    result = borrow_service.request_borrow(user=current_user, book=book)
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    return redirect(url_for('main.index'))

@bp.route('/reserve/confirm/<int:book_id>')
@login_required
def confirm_reserve(book_id):
    """显示预约确认页面"""
    book = db.session.get(Book, book_id)
    if book is None or (book.status == 1 and book.available_count > 0):
        flash('该图书当前无需预约。', 'warning')
        return redirect(url_for('main.index'))
    return render_template('borrow/confirm_reserve.html', book=book, title='预约确认')

@bp.route('/reserve/<int:book_id>', methods=['POST'])
@login_required
def reserve(book_id):
    """处理用户预约图书申请的路由"""
    book = db.session.get(Book, book_id)
    if book is None:
        flash('未找到指定的图书。', 'warning')
        return redirect(url_for('main.index'))
    result = reservation_service.request_reservation(user=current_user, book=book)
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    return redirect(url_for('main.index'))

@bp.route('/my_borrows')
@login_required
def my_borrows():
    """显示用户的借阅列表"""
    # 显示所有状态的借阅记录，让用户可以看到历史
    records = current_user.borrow_records.order_by(BorrowRecord.request_date.desc()).all()
    return render_template('borrow/my_borrows.html', records=records, title='我的借阅')

@bp.route('/request_return/<int:record_id>', methods=['POST'])
@login_required
def request_return_route(record_id):
    """用户申请还书的路由"""
    record = db.session.get(BorrowRecord, record_id)
    if record is None or record.user_id != current_user.id:
        flash('无效的操作或权限不足。', 'danger')
        return redirect(url_for('borrow.my_borrows'))
    result = borrow_service.request_return(record)
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    return redirect(url_for('borrow.my_borrows'))

@bp.route('/my_reservations')
@login_required
def my_reservations():
    """显示用户的预约列表"""
    # 显示所有对用户有意义的预约状态
    reservations = current_user.reservations.order_by(Reservation.reservation_date.asc()).all()
    return render_template('borrow/my_reservations.html', reservations=reservations, title='我的预约')

@bp.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation_route(reservation_id):
    """用户取消预约的路由"""
    reservation = db.session.get(Reservation, reservation_id)
    if reservation is None or reservation.user_id != current_user.id:
        flash('无效的操作或权限不足。', 'danger')
        return redirect(url_for('borrow.my_reservations'))
    result = reservation_service.cancel_reservation(reservation)
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    return redirect(url_for('borrow.my_reservations'))