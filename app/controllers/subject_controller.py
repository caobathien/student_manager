from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models.subject import Subject
from app.forms import SubjectForm
from app.decorators import admin_required

subject_bp = Blueprint('subject', __name__, url_prefix='/admin/subjects')

@subject_bp.route('/')
@login_required
@admin_required
def list_subjects():
    """Hiển thị danh sách các môn học."""
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin/subject_list.html', title='Quản lý Môn học', subjects=subjects)

@subject_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subject():
    """Thêm môn học mới."""
    form = SubjectForm()
    if form.validate_on_submit():
        new_subject = Subject(
            name=form.name.data,
            code=form.code.data,
            description=form.description.data
        )
        db.session.add(new_subject)
        db.session.commit()
        flash('Đã thêm môn học mới thành công!', 'success')
        return redirect(url_for('subject.list_subjects'))
    return render_template('admin/subject_form.html', title='Thêm Môn học', form=form, legend='Thêm Môn học')

@subject_bp.route('/<int:subject_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_subject(subject_id):
    """Cập nhật thông tin môn học."""
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.code = form.code.data
        subject.description = form.description.data
        db.session.commit()
        flash('Thông tin môn học đã được cập nhật!', 'success')
        return redirect(url_for('subject.list_subjects'))
    return render_template('admin/subject_form.html', title='Cập nhật Môn học', form=form, legend=f'Cập nhật Môn học: {subject.name}')

@subject_bp.route('/<int:subject_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_subject(subject_id):
    """Xóa môn học (chỉ khi không còn điểm)."""
    subject = Subject.query.get_or_404(subject_id)
    if subject.grades:  # Kiểm tra xem môn học còn điểm không
        flash('Không thể xóa môn học này vì vẫn còn điểm của sinh viên.', 'danger')
    else:
        db.session.delete(subject)
        db.session.commit()
        flash('Môn học đã được xóa!', 'success')
    return redirect(url_for('subject.list_subjects'))
