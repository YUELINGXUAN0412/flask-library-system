# app/routes/admin.py
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app, Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import current_user
from app.decorators import admin_required
from app.models.user import User
from app.models.book_category import BookCategory
from app.models.book import Book
from app.models.borrow_record import BorrowRecord
from app.models.system_config import SystemConfig
from app.models.reservation import Reservation
from app.forms import CategoryForm, BookForm, SettingsForm, AdminEditUserForm
from sqlalchemy import select, or_, func
from app import db
from app.services import stats_service, borrow_service, reservation_service


bp = Blueprint('admin', __name__)

@bp.context_processor
def inject_pending_counts():
    if current_user.is_authenticated and current_user.role == 2:
        borrow_reqs = db.session.scalar(select(func.count(BorrowRecord.id)).where(BorrowRecord.status == 0)) or 0
        return_reqs = db.session.scalar(select(func.count(BorrowRecord.id)).where(BorrowRecord.status == 6)) or 0
        reserve_reqs = db.session.scalar(select(func.count(Reservation.id)).where(Reservation.status == 0)) or 0
        pickup_reqs = db.session.scalar(select(func.count(Reservation.id)).where(Reservation.status == 2)) or 0
        return dict(
            pending_borrow_count=borrow_reqs, 
            pending_return_count=return_reqs,
            pending_reservation_count=reserve_reqs,
            pending_pickup_count=pickup_reqs
        )
    return {}

def _save_cover_image(file):
    if file:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_filename = str(uuid.uuid4()) + ext
        file.save(os.path.join(upload_folder, unique_filename))
        return unique_filename
    return None

@bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html', title='仪表盘')

@bp.route('/statistics')
@admin_required
def statistics():
    top_books_data = stats_service.get_top_borrowed_books(limit=10)
    top_books_labels = [item.Book.title for item in top_books_data]
    top_books_counts = [item.borrow_count for item in top_books_data]
    return render_template(
        'admin/statistics.html',
        title='统计分析',
        top_books_labels=top_books_labels,
        top_books_counts=top_books_counts
    )

@bp.route('/approvals')
@admin_required
def approvals():
    borrow_requests = db.session.scalars(select(BorrowRecord).where(BorrowRecord.status == 0).order_by(BorrowRecord.request_date.asc())).all()
    return_requests = db.session.scalars(select(BorrowRecord).where(BorrowRecord.status == 6).order_by(BorrowRecord.request_date.asc())).all()
    reservation_requests = db.session.scalars(select(Reservation).where(Reservation.status == 0).order_by(Reservation.reservation_date.asc())).all()
    return render_template(
        'admin/approvals.html', 
        borrow_requests=borrow_requests, 
        return_requests=return_requests,
        reservation_requests=reservation_requests,
        title='事务审批中心'
    )

@bp.route('/approve_borrow/<int:record_id>', methods=['POST'])
@admin_required
def approve_borrow_route(record_id):
    record = db.session.get(BorrowRecord, record_id)
    if record is None:
        flash('无效的操作。', 'warning')
        return redirect(url_for('admin.approvals'))
    result = borrow_service.approve_borrow(record)
    if result['success']: flash(result['message'], 'success')
    else: flash(result['message'], 'danger')
    return redirect(url_for('admin.approvals'))

@bp.route('/reject_borrow/<int:record_id>', methods=['POST'])
@admin_required
def reject_borrow_route(record_id):
    record = db.session.get(BorrowRecord, record_id)
    if record is None:
        flash('无效的操作。', 'warning')
        return redirect(url_for('admin.approvals'))
    reason = request.form.get('reason', '管理员未提供具体理由。')
    result = borrow_service.reject_borrow(record, reason)
    if result['success']: flash(result['message'], 'success')
    else: flash(result['message'], 'danger')
    return redirect(url_for('admin.approvals'))

@bp.route('/approve_return/<int:record_id>', methods=['POST'])
@admin_required
def approve_return_route(record_id):
    record = db.session.get(BorrowRecord, record_id)
    if record is None:
        flash('无效的操作。', 'warning')
        return redirect(url_for('admin.approvals'))
    result = borrow_service.approve_return(record)
    if result['success']: flash(result['message'], 'success')
    else: flash(result['message'], 'danger')
    return redirect(url_for('admin.approvals'))

@bp.route('/approve_reservation/<int:reservation_id>', methods=['POST'])
@admin_required
def approve_reservation_route(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)
    if reservation is None:
        flash('无效的操作。', 'warning')
        return redirect(url_for('admin.approvals'))
    result = reservation_service.approve_reservation(reservation)
    if result['success']: flash(result['message'], 'success')
    else: flash(result['message'], 'danger')
    return redirect(url_for('admin.approvals'))

@bp.route('/reject_reservation/<int:reservation_id>', methods=['POST'])
@admin_required
def reject_reservation_route(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)
    if reservation is None:
        flash('无效的操作。', 'warning')
        return redirect(url_for('admin.approvals'))
    reason = request.form.get('reason', '管理员未提供具体理由。')
    result = reservation_service.reject_reservation(reservation, reason)
    if result['success']: flash(result['message'], 'success')
    else: flash(result['message'], 'danger')
    return redirect(url_for('admin.approvals'))
    
@bp.route('/reservations')
@admin_required
def reservations():
    on_hold_reservations = db.session.scalars(select(Reservation).where(Reservation.status == 2).order_by(Reservation.reservation_date.asc())).all()
    return render_template('admin/reservations.html', reservations=on_hold_reservations, title='预约取书管理')

@bp.route('/fulfill_reservation/<int:reservation_id>', methods=['POST'])
@admin_required
def fulfill_reservation_route(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)
    if reservation is None:
        flash('未找到指定的预约记录。', 'warning')
        return redirect(url_for('admin.reservations'))
    result = reservation_service.fulfill_reservation(reservation)
    if result['success']: flash(result['message'], 'success')
    else: flash(result['message'], 'danger')
    return redirect(url_for('admin.reservations'))
    
@bp.route('/users')
@admin_required
def users():
    stmt = select(User).order_by(User.id.asc())
    user_list = db.session.scalars(stmt).all()
    return render_template('admin/users.html', users=user_list, title='用户管理')

@bp.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    """管理员编辑用户 (增加权限检查)"""
    user_to_edit = db.session.get(User, id)
    if user_to_edit is None:
        flash('未找到指定的用户。', 'warning')
        return redirect(url_for('admin.users'))
    
    # 核心权限检查
    if user_to_edit.id == current_user.id:
        flash('不能在此编辑自己的账户信息。', 'danger')
        return redirect(url_for('admin.users'))
    if user_to_edit.role >= current_user.role:
        flash('权限不足：无法编辑同级或更高级别的管理员。', 'danger')
        return redirect(url_for('admin.users'))

    form = AdminEditUserForm(
        original_username=user_to_edit.username,
        current_admin_role=current_user.role
    )
    if form.validate_on_submit():
        user_to_edit.username = form.username.data
        user_to_edit.role = form.role.data
        user_to_edit.status = form.status.data
        db.session.commit()
        flash('用户信息更新成功！', 'success')
        return redirect(url_for('admin.users'))
    elif request.method == 'GET':
        form.username.data = user_to_edit.username
        form.role.data = user_to_edit.role
        form.status.data = user_to_edit.status
        
    return render_template('admin/edit_user.html', form=form, title='编辑用户', user=user_to_edit)

@bp.route('/user/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    """管理员删除用户 (增加权限检查)"""
    user_to_delete = db.session.get(User, id)
    if user_to_delete is None:
        flash('未找到指定的用户。', 'warning')
        return redirect(url_for('admin.users'))
        
    # 核心权限检查
    if user_to_delete.id == current_user.id:
        flash('不能删除自己的账户！', 'danger')
        return redirect(url_for('admin.users'))
    if user_to_delete.role >= current_user.role:
        flash('权限不足：无法删除同级或更高级别的管理员。', 'danger')
        return redirect(url_for('admin.users'))

    active_borrows = user_to_delete.borrow_records.filter_by(status=1).count()
    if active_borrows > 0:
        flash(f'用户 {user_to_delete.username} 尚有 {active_borrows} 本未归还的图书，无法删除！', 'danger')
        return redirect(url_for('admin.users'))
    pending_actions = user_to_delete.borrow_records.filter(BorrowRecord.status.in_([0, 6])).count()
    if pending_actions > 0:
        flash(f'用户 {user_to_delete.username} 尚有待处理的借阅/还书申请，无法删除！', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f'用户 {user_to_delete.username} 已被成功删除。', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/categories')
@admin_required
def categories():
    stmt = select(BookCategory).order_by(BookCategory.id.asc())
    category_list = db.session.scalars(stmt).all()
    return render_template('admin/categories.html', categories=category_list, title='图书分类管理')

@bp.route('/category/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = BookCategory(category_name=form.category_name.data, description=form.description.data)
        db.session.add(new_category)
        db.session.commit()
        flash('新分类添加成功！', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/add_edit_category.html', form=form, title='添加新分类')

@bp.route('/category/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_category(id):
    category = db.session.get(BookCategory, id)
    if category is None:
        flash('未找到指定的分类。', 'warning')
        return redirect(url_for('admin.categories'))
    form = CategoryForm(original_category_name=category.category_name)
    if form.validate_on_submit():
        category.category_name = form.category_name.data
        category.description = form.description.data
        db.session.commit()
        flash('分类信息更新成功！', 'success')
        return redirect(url_for('admin.categories'))
    elif request.method == 'GET':
        form.category_name.data = category.category_name
        form.description.data = category.description
    return render_template('admin/add_edit_category.html', form=form, title='编辑分类')

@bp.route('/category/delete/<int:id>', methods=['POST'])
@admin_required
def delete_category(id):
    category_to_delete = db.session.get(BookCategory, id)
    if category_to_delete is None:
        flash('未找到指定的分类。', 'warning')
        return redirect(url_for('admin.categories'))
    if category_to_delete.books.first():
        flash(f'分类【{category_to_delete.category_name}】下已有图书，无法删除！', 'danger')
        return redirect(url_for('admin.categories'))
    db.session.delete(category_to_delete)
    db.session.commit()
    flash('分类删除成功！', 'success')
    return redirect(url_for('admin.categories'))

@bp.route('/books')
@admin_required
def books():
    """图书信息管理列表（增加搜索、筛选、分页）"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', type=int)
    category_filter = request.args.get('category', type=int)

    categories = db.session.scalars(select(BookCategory).order_by(BookCategory.category_name)).all()
    status_choices = [(0, '所有状态'), (1, '在架可借'), (2, '全部借出'), (3, '保留中'), (4, '仅供馆阅'), (5, '已下架')]
    
    stmt = select(Book)
    if status_filter and status_filter in [key for key, value in status_choices]:
        stmt = stmt.where(Book.status == status_filter)
    if category_filter and category_filter in [c.id for c in categories]:
        stmt = stmt.where(Book.category_id == category_filter)
    if search_query:
        stmt = stmt.filter(or_(Book.title.like(f'%{search_query}%'), Book.author.like(f'%{search_query}%')))
    
    per_page = int(SystemConfig.get('BOOKS_PER_PAGE', 10))
    pagination = db.paginate(
        stmt.order_by(Book.id.asc()), 
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template(
        'admin/books.html', 
        pagination=pagination,
        title='图书信息管理',
        search_query=search_query,
        status_choices=status_choices,
        active_status=status_filter if status_filter is not None else 0,
        categories=categories,
        active_category=category_filter
    )

@bp.route('/book/history/<int:book_id>')
@admin_required
def book_history(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        flash('未找到指定的图书。', 'warning')
        return redirect(url_for('admin.books'))
    records = book.borrows.order_by(BorrowRecord.request_date.desc()).all()
    return render_template('admin/book_history.html', records=records, book=book, title=f'《{book.title}》的借阅历史')

@bp.route('/book/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        cover_filename = _save_cover_image(form.cover.data)
        new_book = Book(
            title=form.title.data, author=form.author.data, publisher=form.publisher.data,
            isbn=form.isbn.data, publication_date=form.publication_date.data,
            price=form.price.data, total_count=form.total_count.data,
            available_count=form.total_count.data, category_id=form.category.data.id,
            status=form.status.data,
            cover_image=cover_filename
        )
        if new_book.status != 1:
            new_book.available_count = 0
        db.session.add(new_book)
        db.session.commit()
        flash('新图书添加成功！', 'success')
        return redirect(url_for('admin.books'))
    return render_template('admin/add_edit_book.html', form=form, title='添加新图书')

@bp.route('/book/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_book(id):
    book_to_edit = db.session.get(Book, id)
    if book_to_edit is None:
        flash('未找到指定的图书。', 'warning')
        return redirect(url_for('admin.books'))
    form = BookForm(original_isbn=book_to_edit.isbn)
    if form.validate_on_submit():
        if form.cover.data:
            if book_to_edit.cover_image:
                old_cover_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book_to_edit.cover_image)
                if os.path.exists(old_cover_path):
                    os.remove(old_cover_path)
            book_to_edit.cover_image = _save_cover_image(form.cover.data)
        book_to_edit.title = form.title.data
        book_to_edit.author = form.author.data
        book_to_edit.publisher = form.publisher.data
        book_to_edit.isbn = form.isbn.data
        book_to_edit.publication_date = form.publication_date.data
        book_to_edit.price = form.price.data
        book_to_edit.category_id = form.category.data.id
        new_status = form.status.data
        new_total_count = form.total_count.data
        borrowed_count = db.session.query(BorrowRecord).filter_by(book_id=book_to_edit.id, status=1).count()
        if new_status == 1:
            book_to_edit.available_count = new_total_count - borrowed_count
        else:
            book_to_edit.available_count = 0
        book_to_edit.total_count = new_total_count
        book_to_edit.status = new_status
        if book_to_edit.available_count < 0:
            book_to_edit.available_count = 0
        db.session.commit()
        flash('图书信息更新成功！', 'success')
        return redirect(url_for('admin.books'))
    elif request.method == 'GET':
        form.title.data = book_to_edit.title
        form.author.data = book_to_edit.author
        form.publisher.data = book_to_edit.publisher
        form.isbn.data = book_to_edit.isbn
        form.publication_date.data = book_to_edit.publication_date
        form.price.data = book_to_edit.price
        form.total_count.data = book_to_edit.total_count
        form.category.data = book_to_edit.category
        form.status.data = book_to_edit.status
    return render_template('admin/add_edit_book.html', form=form, title='编辑图书', book=book_to_edit)

@bp.route('/book/delete/<int:id>', methods=['POST'])
@admin_required
def delete_book(id):
    book_to_delete = db.session.get(Book, id)
    if book_to_delete is None:
        flash('未找到指定的图书。', 'warning')
        return redirect(url_for('admin.books'))
    active_borrows = book_to_delete.borrows.filter_by(status=1).count()
    if active_borrows > 0:
        flash(f'图书《{book_to_delete.title}》尚在借阅中，无法删除！', 'danger')
        return redirect(url_for('admin.books'))
    active_reservations = book_to_delete.reservations.filter(Reservation.status.in_([0, 1, 2])).count()
    if active_reservations > 0:
        flash(f'图书《{book_to_delete.title}》尚有用户预约或待处理，无法删除！', 'danger')
        return redirect(url_for('admin.books'))
    db.session.delete(book_to_delete)
    db.session.commit()
    flash('图书删除成功！', 'success')
    return redirect(url_for('admin.books'))

@bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        for key, value in form.data.items():
            if key in ['csrf_token', 'submit']: continue
            config_item = db.session.scalar(select(SystemConfig).where(SystemConfig.config_key == key.upper()))
            if config_item: config_item.config_value = str(value)
        db.session.commit()
        flash('系统设置更新成功！', 'success')
        return redirect(url_for('admin.settings'))
    configs = db.session.scalars(select(SystemConfig)).all()
    config_dict = {config.config_key: config.config_value for config in configs}
    form.library_name.data = config_dict.get('LIBRARY_NAME')
    form.borrow_days.data = int(config_dict.get('BORROW_DAYS', 30))
    form.max_borrow_count.data = int(config_dict.get('MAX_BORROW_COUNT', 5))
    form.fine_rate.data = float(config_dict.get('FINE_RATE', 0.5))
    return render_template('admin/settings.html', form=form, title='系统设置管理')