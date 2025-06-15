# manage.py
from app import create_app, db
from app.models.user import User
from app.models.book import Book
from app.models.book_category import BookCategory
from app.models.borrow_record import BorrowRecord
from app.models.system_config import SystemConfig # <-- 新增导入

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """为 flask shell 命令提供上下文，方便调试。"""
    return {
        'db': db, 
        'User': User,
        'Book': Book,
        'BookCategory': BookCategory,
        'BorrowRecord': BorrowRecord,
        'SystemConfig': SystemConfig
    }

# --- 新增的自定义CLI命令 ---
@app.cli.command('seed')
def seed():
    """向数据库填充初始数据"""
    print('Seeding initial system configurations...')
    
    configs = [
        {'key': 'BORROW_DAYS', 'value': '30', 'desc': '默认借阅天数'},
        {'key': 'MAX_BORROW_COUNT', 'value': '5', 'desc': '单个用户最多可借图书数量'},
        {'key': 'FINE_RATE', 'value': '0.5', 'desc': '逾期每日罚款金额（元）'},
        {'key': 'LIBRARY_NAME', 'value': 'Flask图书管理系统', 'desc': '图书馆名称'}
    ]
    
    for config_data in configs:
        config_key = config_data['key']
        existing_config = db.session.scalar(
            db.select(SystemConfig).where(SystemConfig.config_key == config_key)
        )
        if not existing_config:
            new_config = SystemConfig(
                config_key=config_key,
                config_value=config_data['value'],
                description=config_data['desc']
            )
            db.session.add(new_config)
            print(f"Added config: {config_key}")

    db.session.commit()
    print('Seeding completed.')


if __name__ == '__main__':
    app.run(host='10.21.17.57',port='5000',debug=True)
