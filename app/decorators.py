# app/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 核心改动：将 != 2 修改为 < 2
        # 这样角色为2(管理员)和3(超级管理员)的用户都能通过验证
        if not current_user.is_authenticated or current_user.role < 2:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function