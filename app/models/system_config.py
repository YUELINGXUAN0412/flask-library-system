# app/models/system_config.py
from app import db

class SystemConfig(db.Model):
    __tablename__ = 'system_config'

    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(50), unique=True, nullable=False, comment='配置项键名')
    config_value = db.Column(db.Text, nullable=False, comment='配置项值')
    description = db.Column(db.String(255), comment='配置项描述')
    create_time = db.Column(db.DateTime, server_default=db.func.now())

    @staticmethod
    def get(key, default=None):
        """一个便捷的静态方法，用于通过键名获取配置值"""
        config = db.session.scalar(
            db.select(SystemConfig).where(SystemConfig.config_key == key)
        )
        return config.config_value if config else default

    def __repr__(self):
        return f'<SystemConfig {self.config_key}>'