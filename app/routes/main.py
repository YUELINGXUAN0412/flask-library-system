# app/routes/main.py
from flask import render_template, Blueprint, request, abort
from app.models.book import Book
from app.models.book_category import BookCategory # 导入 BookCategory 模型
from app.models.system_config import SystemConfig
from sqlalchemy import select, or_
from app import db
from app.services import stats_service

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """公开的首页和图书目录，增加分类筛选"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', type=int)
    # 新增：从URL参数中获取分类ID
    category_filter = request.args.get('category', type=int)

    # 查询所有分类，用于生成下拉菜单
    categories = db.session.scalars(select(BookCategory).order_by(BookCategory.id.asc())).all()
    
    status_choices = [(0, '全部'), (1, '在架可借'), (2, '全部借出'), (4, '仅供馆阅'), (5, '已下架')]
    
    stmt = select(Book)

    # 筛选逻辑
    # 状态筛选
    if status_filter and status_filter in [key for key, value in status_choices]:
        stmt = stmt.where(Book.status == status_filter)
    else:
        default_visible_statuses = [1, 2, 3, 4, 5]
        stmt = stmt.where(Book.status.in_(default_visible_statuses))

    # 新增：分类筛选
    if category_filter and category_filter in [c.id for c in categories]:
        stmt = stmt.where(Book.category_id == category_filter)

    # 搜索逻辑
    if search_query:
        stmt = stmt.filter(or_(Book.title.like(f'%{search_query}%'), Book.author.like(f'%{search_query}%')))
    
    per_page = int(SystemConfig.get('BOOKS_PER_PAGE', 10))

    pagination = db.paginate(
        stmt.order_by(Book.create_time.desc()), 
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template(
        'main/index.html', 
        title='图书目录', 
        pagination=pagination,
        search_query=search_query,
        status_choices=status_choices,
        active_status=status_filter if status_filter is not None else 0,
        categories=categories, # 将分类列表传给模板
        active_category=category_filter # 将当前选择的分类ID传给模板
    )

@bp.route('/book/<int:book_id>')
def book_detail(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        abort(404)
    return render_template('main/book_detail.html', title=book.title, book=book)

@bp.route('/popular')
def popular_books():
    """热门图书排行榜页面"""
    top_books = stats_service.get_top_borrowed_books(limit=20)
    return render_template('main/popular_books.html', title='热门排行', top_books=top_books)