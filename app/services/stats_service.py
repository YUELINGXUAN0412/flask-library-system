# app/services/stats_service.py
from app import db, cache # <-- 新增导入 cache
from app.models.book import Book
from app.models.borrow_record import BorrowRecord
from sqlalchemy import func, select, text

# 新增：为这个函数加上缓存装饰器
@cache.cached(timeout=3600) # 缓存1小时 (3600秒)
def get_top_borrowed_books(limit=10):
    """获取借阅次数最多的图书排行"""
    print("--- EXECUTING DATABASE QUERY for get_top_borrowed_books ---") # 增加一个打印，方便我们测试
    stmt = select(
        Book,
        func.count(BorrowRecord.id).label('borrow_count')
    ).join(
        BorrowRecord, Book.id == BorrowRecord.book_id
    ).group_by(
        Book
    ).order_by(
        func.count(BorrowRecord.id).desc()
    ).limit(limit)
    top_books = db.session.execute(stmt).all()
    return top_books

# 我们暂时不对这个函数加缓存，以作对比
def get_monthly_borrow_stats():
    """获取每月借阅总量统计"""
    sql_query = text("""
        SELECT DATE_FORMAT(borrow_date, '%Y-%m') AS month, COUNT(id) AS total
        FROM borrow_record GROUP BY DATE_FORMAT(borrow_date, '%Y-%m') ORDER BY month ASC;
    """)
    result = db.session.execute(sql_query)
    stats = result.fetchall()
    return stats