# app/models/book.py
from app import db

class Book(db.Model):
    """图书模型"""
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, comment='书名')
    author = db.Column(db.String(50), nullable=False, comment='作者')
    publisher = db.Column(db.String(50), nullable=False, comment='出版社')
    isbn = db.Column(db.String(20), unique=True, nullable=False, comment='ISBN号')
    publication_date = db.Column(db.Date, comment='出版日期')
    price = db.Column(db.Numeric(10, 2), comment='价格')
    total_count = db.Column(db.Integer, nullable=False, default=0, comment='图书总数')
    available_count = db.Column(db.Integer, nullable=False, default=0, comment='可借数量')
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment='图书状态，1为在架可借，2为已借出，3为保留中, 4为仅供馆阅, 5为已下架')
    cover_image = db.Column(db.String(255), comment='封面图片路径')
    create_time = db.Column(db.DateTime, server_default=db.func.now())
    category_id = db.Column(db.Integer, db.ForeignKey('book_category.id'), nullable=False, comment='分类ID')

    # 为关系增加 cascade 选项
    borrows = db.relationship('BorrowRecord', back_populates='borrowed_book', lazy='dynamic', cascade="all, delete-orphan")
    reservations = db.relationship('Reservation', back_populates='book', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Book {self.title}>'