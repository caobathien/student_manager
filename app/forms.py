from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FloatField, SelectField, SelectMultipleField, ValidationError, PasswordField, BooleanField, DateField, FileField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email, EqualTo
# from wtforms_sqlalchemy.fields import QuerySelectField
from flask import request
from app.models.subject import Subject
from app.models.student import Student
from app.models.grade import Grade
from app.models.user import User
from app.models.class_model import Class

# --- FORM CHO MÔN HỌC ---
class SubjectForm(FlaskForm):
    name = StringField('Tên môn học', validators=[DataRequired(), Length(max=100)])
    code = StringField('Mã môn học', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Mô tả', validators=[Optional()])
    submit = SubmitField('Lưu Môn học')

    def validate_code(self, code):
        subject_id = request.view_args.get('subject_id')
        query = Subject.query.filter_by(code=code.data)
        if subject_id:
            query = query.filter(Subject.id != subject_id)
        if query.first():
            raise ValidationError('Mã môn học này đã tồn tại.')

# --- FORM CHO SINH VIÊN ---
class StudentForm(FlaskForm):
    student_code = StringField('Mã sinh viên', validators=[DataRequired(), Length(max=20)])
    full_name = StringField('Họ và tên', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Ngày sinh', validators=[DataRequired()])
    gender = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')], validators=[DataRequired()])
    class_obj = SelectField('Lớp', choices=[], validators=[DataRequired(message="Vui lòng chọn lớp.")])
    submit = SubmitField('Lưu Sinh viên')

    def validate_student_code(self, student_code):
        student_id = request.view_args.get('student_id')
        query = Student.query.filter_by(student_code=student_code.data)
        if student_id:
            query = query.filter(Student.id != student_id)
        if query.first():
            raise ValidationError('Mã sinh viên này đã tồn tại.')

# --- FORM CHO TÌM KIẾM SINH VIÊN ---
class SearchStudentForm(FlaskForm):
    search_term = StringField('Tìm kiếm', validators=[Optional()])
    class_filter = SelectField('Lọc theo lớp', choices=[], validators=[Optional()])
    submit_search = SubmitField('Tìm kiếm')

# --- FORM CHO ĐIỂM ---
class GradeForm(FlaskForm):
    student_id = SelectField('Sinh viên', choices=[], validators=[DataRequired(message="Vui lòng chọn sinh viên.")])
    subject_id = SelectField('Chọn môn học', coerce=int, choices=[], validators=[DataRequired(message="Vui lòng chọn môn học.")])
    midterm_score = FloatField('Điểm giữa kì', validators=[Optional(), NumberRange(min=0.0, max=10.0, message="Điểm phải từ 0.0 đến 10.0")])
    final_score = FloatField('Điểm cuối kì', validators=[Optional(), NumberRange(min=0.0, max=10.0, message="Điểm phải từ 0.0 đến 10.0")])
    submit = SubmitField('Lưu Điểm')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        # Kiểm tra trùng lặp: một sinh viên chỉ có một điểm cho một môn
        grade_id = request.view_args.get('grade_id')
        query = Grade.query.filter_by(student_id=self.student_id.data, subject_id=self.subject_id.data)
        if grade_id:
            query = query.filter(Grade.id != grade_id)
        if query.first():
            self.student_id.errors.append('Sinh viên này đã có điểm cho môn học này.')
            return False
        return True

# --- FORM CHO PHẢN HỒI ---
class FeedbackForm(FlaskForm):
    content = TextAreaField('Nội dung phản hồi', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Gửi Phản hồi')

# --- FORM CHO ĐĂNG KÝ ---
class RegistrationForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Tên người dùng này đã tồn tại. Vui lòng chọn tên khác.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email này đã được sử dụng. Vui lòng chọn email khác.')

# --- FORM CHO ĐĂNG NHẬP ---
class LoginForm(FlaskForm):
    email = StringField('Email hoặc Mã sinh viên', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')

# --- FORM CHO THÔNG BÁO ---
class AnnouncementForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Nội dung', validators=[DataRequired()])
    image = FileField('Ảnh (tùy chọn)', validators=[Optional()])
    submit = SubmitField('Đăng Thông báo')

# --- FORM CHO CẬP NHẬT TÀI KHOẢN ---
class UpdateAccountForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Cập nhật')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Tên người dùng này đã tồn tại. Vui lòng chọn tên khác.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email này đã được sử dụng. Vui lòng chọn email khác.')

# --- FORM CHO ĐỔI MẬT KHẨU ---
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mật khẩu hiện tại', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('new_password')])
    submit_password = SubmitField('Đổi Mật khẩu')

# --- FORM CHO ADMIN CẬP NHẬT NGƯỜI DÙNG ---
class AdminUpdateUserForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Vai trò', choices=[('user', 'Người dùng'), ('admin', 'Quản trị viên'), ('student', 'Sinh viên')], validators=[DataRequired()])
    submit = SubmitField('Cập nhật')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def validate_username(self, username):
        if self.user and username.data != self.user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Tên người dùng này đã tồn tại.')

    def validate_email(self, email):
        if self.user and email.data != self.user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email này đã được sử dụng.')

# --- FORM CHO LỚP HỌC ---
class ClassForm(FlaskForm):
    name = StringField('Tên lớp', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Lưu Lớp')

    def validate_name(self, name):
        class_id = request.view_args.get('class_id')
        query = Class.query.filter_by(name=name.data)
        if class_id:
            query = query.filter(Class.id != class_id)
        if query.first():
            raise ValidationError('Tên lớp này đã tồn tại.')

# --- FORM CHO ĐĂNG KÝ MÔN HỌC ---
class SubjectRegistrationForm(FlaskForm):
    subjects = SelectMultipleField('Chọn môn học', choices=[], validators=[DataRequired(message="Vui lòng chọn ít nhất một môn học.")])
    submit = SubmitField('Đăng ký')

# --- FORM CHO NHẬP SINH VIÊN ---
class ImportStudentForm(FlaskForm):
    file = FileField('Chọn file', validators=[DataRequired()])
    submit = SubmitField('Nhập dữ liệu')

# ... existing code ...
