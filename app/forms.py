# app/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, IntegerField, DecimalField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from sqlalchemy import select
from app import db
from app.models.user import User
from app.models.book_category import BookCategory
from app.models.book import Book
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名。'), Length(min=2, max=20, message='用户名长度应在2到20个字符之间。')])
    email = StringField('邮箱', validators=[DataRequired(message='请输入邮箱地址。'), Email(message='请输入有效的邮箱地址。')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码。'), Length(min=6, message='密码长度不能少于6个字符。')])
    password2 = PasswordField('确认密码', validators=[DataRequired(message='请再次输入密码。'), EqualTo('password', message='两次输入的密码不一致。')])
    submit = SubmitField('立即注册')
    def validate_username(self, username):
        user = db.session.scalar(select(User).where(User.username == username.data))
        if user: raise ValidationError('该用户名已被使用，请选择其他用户名。')
    def validate_email(self, email):
        user = db.session.scalar(select(User).where(User.email == email.data))
        if user: raise ValidationError('该邮箱已被注册，请选择其他邮箱。')

class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(message='请输入你的邮箱地址。'), Email(message='请输入有效的邮箱地址。')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入你的密码。')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('立即登录')

class EditProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('手机号', validators=[Length(min=0, max=20)])
    submit = SubmitField('保存更改')
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(select(User).where(User.username == username.data))
            if user: raise ValidationError('该用户名已被使用，请选择其他名称。')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired(message='请输入你的旧密码。')])
    new_password = PasswordField('新密码', validators=[DataRequired(message='请输入新密码。'), Length(min=6, message='密码长度不能少于6个字符。')])
    new_password2 = PasswordField('确认新密码', validators=[DataRequired(message='请再次输入新密码。'), EqualTo('new_password', message='两次输入的新密码不一致。')])
    submit = SubmitField('确认修改密码')
    def validate_old_password(self, old_password):
        if not current_user.verify_password(old_password.data):
            raise ValidationError('旧密码不正确，请重试。')
            
class UploadAvatarForm(FlaskForm):
    avatar = FileField('选择新头像 (JPG, PNG)', validators=[
        DataRequired(message='请选择一个文件。'),
        FileAllowed(['jpg', 'jpeg', 'png'], '只允许上传图片文件！')
    ])
    submit = SubmitField('上传并保存')

class CategoryForm(FlaskForm):
    category_name = StringField('分类名称', validators=[DataRequired(message='请输入分类名称。'), Length(min=2, max=50, message='分类名称长度应在2到50个字符之间。')])
    description = TextAreaField('分类描述', validators=[Length(max=255, message='描述内容不能超过255个字符。')])
    submit = SubmitField('确认提交')
    def __init__(self, original_category_name=None, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.original_category_name = original_category_name
    def validate_category_name(self, category_name):
        if category_name.data != self.original_category_name:
            category = db.session.scalar(select(BookCategory).where(BookCategory.category_name == category_name.data))
            if category: raise ValidationError('该分类名称已存在，请使用其他名称。')

def get_all_categories():
    return db.session.scalars(select(BookCategory).order_by(BookCategory.category_name)).all()

class BookForm(FlaskForm):
    title = StringField('书名*', validators=[DataRequired(), Length(max=100)])
    author = StringField('作者*', validators=[DataRequired(), Length(max=50)])
    publisher = StringField('出版社*', validators=[DataRequired(), Length(max=50)])
    isbn = StringField('ISBN*', validators=[DataRequired(), Length(min=10, max=13, message='ISBN应为10或13位')])
    publication_date = DateField('出版日期', validators=[DataRequired(message='请输入正确的出版日期。')])
    price = DecimalField('价格', validators=[DataRequired(message='价格不能为空。'), NumberRange(min=0, max=99999999.99, message='价格超出合理范围。')])
    total_count = IntegerField('总数量*', validators=[DataRequired(message='总数量不能为空。'), NumberRange(min=0, max=10000, message='数量超出合理范围。')])
    category = QuerySelectField('分类*', query_factory=get_all_categories, get_label='category_name', allow_blank=False, validators=[DataRequired(message='请选择一个分类。')])
    status = SelectField('图书状态*', coerce=int, choices=[(1, '在架可借'),(4, '仅供馆内阅览'),(5, '已下架/处理中')], validators=[DataRequired(message='请选择一个状态。')])
    cover = FileField('图书封面', validators=[FileAllowed(['jpg', 'jpeg', 'png'], '只允许上传图片文件！')])
    submit = SubmitField('确认提交')
    def __init__(self, original_isbn=None, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.original_isbn = original_isbn
    def validate_isbn(self, isbn):
        if isbn.data != self.original_isbn:
            book = db.session.scalar(select(Book).where(Book.isbn == isbn.data))
            if book: raise ValidationError('该ISBN已被使用。')

class SettingsForm(FlaskForm):
    library_name = StringField('图书馆名称', validators=[DataRequired(), Length(max=100)], description='将显示在系统标题和页面中')
    borrow_days = IntegerField('默认借阅天数', validators=[DataRequired(), NumberRange(min=1)], description='用户借阅一本书的默认时长（天）')
    max_borrow_count = IntegerField('最大借阅数量', validators=[DataRequired(), NumberRange(min=1)], description='单个用户最多能同时借阅的图书数量')
    fine_rate = DecimalField('逾期每日罚款（元）', validators=[DataRequired(), NumberRange(min=0)], description='每本书每逾期一天所需支付的罚款金额')
    submit = SubmitField('保存设置')

class AdminEditUserForm(FlaskForm):
    """管理员编辑用户表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    role = SelectField('角色', coerce=int)
    status = SelectField('状态', coerce=int, choices=[(1, '启用'), (0, '禁用')])
    submit = SubmitField('更新用户信息')
    
    def __init__(self, original_username, current_admin_role=None, *args, **kwargs):
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        
        # 动态设置角色选项
        if current_admin_role == 3: # 只有超级管理员才能看到并设置所有角色
            self.role.choices = [(1, '普通用户'), (2, '管理员'), (3, '超级管理员')]
        else: # 普通管理员只能设置普通用户和管理员
            self.role.choices = [(1, '普通用户'), (2, '管理员')]

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(select(User).where(User.username == username.data))
            if user: raise ValidationError('该用户名已被其他用户使用。')