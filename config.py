# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-and-hard-to-guess-key'
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://root:ASDasd123@"
        f"10.21.17.57:30319/library_db"
        f"?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads/covers')
    # 新增：头像上传配置
    AVATAR_UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads/avatars')

    # --- 新增：缓存配置 ---
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 300 # 默认缓存时间（秒），这里是5分钟
    CACHE_REDIS_URL = 'redis://10.21.17.57:30079/0' # 连接到我们本地Docker运行的Redis