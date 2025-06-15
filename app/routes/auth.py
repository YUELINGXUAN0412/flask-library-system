# app/routes/auth.py

from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import login_user, logout_user, current_user
from sqlalchemy import select
from app import db
from app.models.user import User
from app.forms import RegistrationForm, LoginForm

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.password = form.password.data  # 使用新的setter方式设置密码
        db.session.add(user)
        db.session.commit()
        
        login_user(user)  # 注册后自动登录
        flash('恭喜，您已成功注册！', 'success')
        return redirect(url_for('main.index')) # 成功后直接跳转到首页
        
    return render_template('auth/register.html', title='注册', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        query = select(User).where(User.email == form.email.data)
        user = db.session.scalar(query)
        
        if user is None or not user.verify_password(form.password.data): # 使用新的验证方法
            flash('邮箱或密码无效，请重试。', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
            
        flash('登录成功！', 'success')
        return redirect(next_page)
        
    return render_template('auth/login.html', title='登录', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash('您已成功退出登录。', 'info')
    return redirect(url_for('auth.login'))