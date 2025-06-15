# app/routes/user.py
import os
import uuid
from werkzeug.utils import secure_filename
from flask import render_template, Blueprint, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user, logout_user
from app import db
from app.forms import EditProfileForm, ChangePasswordForm, UploadAvatarForm

bp = Blueprint('user', __name__)

def _save_avatar(file):
    """辅助函数：保存头像图片并返回唯一文件名"""
    if file:
        upload_folder = current_app.config['AVATAR_UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_filename = str(uuid.uuid4()) + ext
        file.save(os.path.join(upload_folder, unique_filename))
        return unique_filename
    return None

@bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', title='个人中心')

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('你的个人资料已更新！', 'success')
        return redirect(url_for('user.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.phone.data = current_user.phone
    return render_template('user/edit_profile.html', title='编辑个人资料', form=form)

@bp.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.commit()
        flash('密码修改成功！为了安全，请使用新密码重新登录。', 'info')
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('user/change_password.html', title='修改密码', form=form)

@bp.route('/profile/upload_avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    """上传头像的路由"""
    form = UploadAvatarForm()
    if form.validate_on_submit():
        # 删除旧头像文件（如果存在）
        if current_user.avatar_image:
            old_avatar_path = os.path.join(current_app.config['AVATAR_UPLOAD_FOLDER'], current_user.avatar_image)
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)
        
        # 保存新头像并更新数据库
        filename = _save_avatar(form.avatar.data)
        current_user.avatar_image = filename
        db.session.commit()
        flash('头像更新成功！', 'success')
        return redirect(url_for('user.profile'))
        
    return render_template('user/upload_avatar.html', title='上传头像', form=form)