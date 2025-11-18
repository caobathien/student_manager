from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_subject import StudentSubject
from app.models.grade import Grade
from app.decorators import admin_required

subject_student_bp = Blueprint('subject_student', __name__, url_prefix='/admin/subjects')

@subject_student_bp.route('/<int:subject_id>/students')
@login_required
@admin_required
def list_students_in_subject(subject_id):
    """Hiển thị danh sách sinh viên đã đăng ký môn học."""
    subject = Subject.query.get_or_404(subject_id)
    # Lấy danh sách sinh viên đã đăng ký môn học này
    enrolled_students = db.session.query(Student).join(StudentSubject).filter(StudentSubject.subject_id == subject_id).order_by(Student.full_name).all()
    return render_template('admin/subject_students.html', title=f'Sinh viên trong môn {subject.name}', subject=subject, students=enrolled_students)

@subject_student_bp.route('/<int:subject_id>/students/<int:student_id>/remove', methods=['POST'])
@login_required
@admin_required
def remove_student_from_subject(subject_id, student_id):
    """Xóa sinh viên khỏi môn học (xóa đăng ký và điểm liên quan)."""
    subject = Subject.query.get_or_404(subject_id)
    student = Student.query.get_or_404(student_id)

    # Tìm bản ghi đăng ký
    student_subject = StudentSubject.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if not student_subject:
        flash('Sinh viên này chưa đăng ký môn học này.', 'warning')
        return redirect(url_for('subject_student.list_students_in_subject', subject_id=subject_id))

    # Xóa điểm liên quan (nếu có)
    grade = Grade.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if grade:
        db.session.delete(grade)

    # Xóa đăng ký
    db.session.delete(student_subject)
    db.session.commit()

    # Cập nhật GPA cho sinh viên
    from app.controllers.grade_controller import update_student_gpa
    update_student_gpa(student_id)

    flash(f'Đã xóa sinh viên {student.full_name} khỏi môn {subject.name}.', 'success')
    return redirect(url_for('subject_student.list_students_in_subject', subject_id=subject_id))
