# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_caching import Cache
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cache = Cache()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请登录以访问此页面。'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)

    # 注册所有蓝图
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    from app.routes.borrow import bp as borrow_bp
    app.register_blueprint(borrow_bp)
    from app.routes.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    # 导入所有模型
    from .models import user, book, book_category, borrow_record, system_config, reservation

    @app.context_processor
    def inject_global_variables():
        """向所有模板注入全局变量（最终修正版）"""
        from app.models.system_config import SystemConfig
        from app.models.borrow_record import BorrowRecord
        from app.models.reservation import Reservation
        from sqlalchemy import func, select
        
        # 初始化所有计数的默认值
        context_vars = {
            'library_name': SystemConfig.get('LIBRARY_NAME', '图书管理系统'),
            'SystemConfig': SystemConfig,
            'user_borrow_notification_count': 0,
            'user_reservation_notification_count': 0,
            'admin_notification_count': 0,
            'admin_approval_count': 0,
            'admin_pickup_count': 0,
            # 为模板中可能用到的旧变量名提供默认值，以防万一
            'pending_borrow_count': 0,
            'pending_return_count': 0,
            'pending_reservation_count': 0
        }
        
        if current_user.is_authenticated:
            # 首先，为所有登录用户计算个人通知
            pending_user_borrows = db.session.scalar(select(func.count(BorrowRecord.id)).where(BorrowRecord.user_id == current_user.id, BorrowRecord.status.in_([0, 6]))) or 0
            context_vars['user_borrow_notification_count'] = pending_user_borrows
            
            pending_user_reservations = db.session.scalar(select(func.count(Reservation.id)).where(Reservation.user_id == current_user.id, Reservation.status.in_([0, 2]))) or 0
            context_vars['user_reservation_notification_count'] = pending_user_reservations

            # 如果这个用户是管理员或超级管理员，再额外计算管理员的全局通知
            if current_user.role >= 2:
                admin_borrow_reqs = db.session.scalar(select(func.count(BorrowRecord.id)).where(BorrowRecord.status == 0)) or 0
                admin_return_reqs = db.session.scalar(select(func.count(BorrowRecord.id)).where(BorrowRecord.status == 6)) or 0
                admin_reserve_reqs = db.session.scalar(select(func.count(Reservation.id)).where(Reservation.status == 0)) or 0
                admin_pickup_reqs = db.session.scalar(select(func.count(Reservation.id)).where(Reservation.status == 2)) or 0

                # 为 admin_base.html 模板提供新的、清晰的变量名
                context_vars['admin_approval_count'] = admin_borrow_reqs + admin_return_reqs + admin_reserve_reqs
                context_vars['admin_pickup_count'] = admin_pickup_reqs
                
                # 为旧的模板变量名也赋值，做最大程度的兼容
                context_vars['pending_borrow_count'] = admin_borrow_reqs
                context_vars['pending_return_count'] = admin_return_reqs
                context_vars['pending_reservation_count'] = admin_reserve_reqs

                # 头像上的总通知数
                context_vars['admin_notification_count'] = context_vars['admin_approval_count'] + context_vars['admin_pickup_count']
        
        return context_vars

    return app