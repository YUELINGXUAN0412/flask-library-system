# app/models/book_category.py
from app import db

class BookCategory(db.Model):
    __tablename__ = 'book_category'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False, comment='分类名称')
    parent_id = db.Column(db.Integer, default=0, comment='父分类ID，0表示顶级分类')
    description = db.Column(db.String(255), comment='分类描述')
    create_time = db.Column(db.DateTime, server_default=db.func.now())
    books = db.relationship('Book', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<BookCategory {self.category_name}>'