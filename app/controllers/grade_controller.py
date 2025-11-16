from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models.grade import Grade
from app.models.student import Student
from app.models.subject import Subject
from app.models.student_subject import StudentSubject
from app.forms import GradeForm
from app.decorators import admin_required
from sqlalchemy import func

grade_bp = Blueprint('grade', __name__)

@grade_bp.route('/grades')
@login_required
@admin_required
def list_grades():
    """Hiển thị danh sách điểm."""
    subject_id = request.args.get('subject_id', type=int)
    class_id = request.args.get('class_id', type=int)

    from app.models.class_model import Class

    if subject_id:
        # Lấy tất cả sinh viên đã đăng ký môn học này
        query = db.session.query(Student).join(StudentSubject).filter(StudentSubject.subject_id == subject_id)
        if class_id:
            query = query.filter(Student.class_id == class_id)
        registered_students = query.order_by(Student.full_name).all()
        # Lấy điểm hiện có
        existing_grades = {grade.student_id: grade for grade in Grade.query.filter_by(subject_id=subject_id).all()}
        # Tạo danh sách điểm với điểm mặc định 0 nếu chưa có
        grades = []
        for student in registered_students:
            if student.id in existing_grades:
                grades.append(existing_grades[student.id])
            else:
                # Tạo grade tạm thời với điểm 0
                fake_grade = type('FakeGrade', (), {
                    'student': student,
                    'subject': Subject.query.get(subject_id),
                    'midterm_score': None,
                    'final_score': None,
                    'subject_score': 0.0,
                    'id': None
                })()
                grades.append(fake_grade)
    else:
        # Khi không chọn môn cụ thể, hiển thị tất cả sinh viên đã đăng ký ít nhất một môn với điểm mặc định 0
        query = db.session.query(Student).join(StudentSubject).distinct()
        if class_id:
            query = query.filter(Student.class_id == class_id)
        all_registered_students = query.order_by(Student.full_name).all()
        all_subjects = Subject.query.all()
        grades = []
        for student in all_registered_students:
            for subject in all_subjects:
                # Kiểm tra sinh viên đã đăng ký môn này chưa
                if StudentSubject.query.filter_by(student_id=student.id, subject_id=subject.id).first():
                    # Lấy điểm hiện có hoặc tạo điểm mặc định 0
                    existing_grade = Grade.query.filter_by(student_id=student.id, subject_id=subject.id).first()
                    if existing_grade:
                        grades.append(existing_grade)
                    else:
                        fake_grade = type('FakeGrade', (), {
                            'student': student,
                            'subject': subject,
                            'midterm_score': None,
                            'final_score': None,
                            'subject_score': 0.0,
                            'id': None
                        })()
                        grades.append(fake_grade)
    subjects = Subject.query.order_by(Subject.name).all()
    classes = Class.query.order_by(Class.name).all()
    return render_template('admin/grade_list.html', title='Quản lý Điểm', grades=grades, subjects=subjects, classes=classes, selected_subject_id=subject_id, selected_class_id=class_id)

@grade_bp.route('/grade/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_grade():
    """Thêm điểm mới."""
    form = GradeForm()
    student_id = request.args.get('student_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    # Nếu có student_id và subject_id từ URL (từ nút "Thêm điểm" của sinh viên cụ thể)
    if student_id and subject_id:
        # Chỉ hiển thị sinh viên và môn học này
        student = Student.query.get_or_404(student_id)
        subject = Subject.query.get_or_404(subject_id)
        form.student_id.choices = [(student.id, f"{student.student_code} - {student.full_name}")]
        form.subject_id.choices = [(subject.id, f"{subject.code} - {subject.name}")]
        form.student_id.data = student_id
        form.subject_id.data = subject_id
    else:
        # Populate choices for students and subjects
        # Chỉ lấy sinh viên đã đăng ký môn học
        registered_students = db.session.query(Student).join(StudentSubject).distinct().order_by(Student.full_name).all()
        subjects = Subject.query.order_by(Subject.name).all()
        form.student_id.choices = [(s.id, f"{s.student_code} - {s.full_name}") for s in registered_students]
        form.subject_id.choices = [(subj.id, f"{subj.code} - {subj.name}") for subj in subjects]

    if form.validate_on_submit():
        # Kiểm tra sinh viên đã đăng ký môn học chưa
        student_subject = StudentSubject.query.filter_by(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data
        ).first()
        if not student_subject:
            flash('Sinh viên chưa đăng ký môn học này!', 'danger')
            return redirect(url_for('grade.add_grade'))

        # Tính điểm môn học
        midterm = form.midterm_score.data or 0
        final = form.final_score.data or 0
        subject_score = (midterm * 0.4) + (final * 0.6)

        grade = Grade(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data,
            midterm_score=form.midterm_score.data,
            final_score=form.final_score.data,
            subject_score=subject_score
        )
        db.session.add(grade)
        db.session.commit()

        # Cập nhật GPA cho sinh viên
        update_student_gpa(form.student_id.data)

        flash('Đã thêm điểm thành công!', 'success')
        return redirect(url_for('grade.list_grades'))

    return render_template('admin/grade_form.html', title='Thêm Điểm', form=form, legend='Thêm Điểm')

@grade_bp.route('/grade/<int:grade_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_grade(grade_id):
    """Cập nhật điểm."""
    grade = Grade.query.get_or_404(grade_id)
    form = GradeForm()

    # Populate choices for students and subjects
    # Chỉ lấy sinh viên đã đăng ký môn học
    registered_students = db.session.query(Student).join(StudentSubject).distinct().order_by(Student.full_name).all()
    subjects = Subject.query.order_by(Subject.name).all()
    form.student_id.choices = [(s.id, f"{s.student_code} - {s.full_name}") for s in registered_students]
    form.subject_id.choices = [(subj.id, f"{subj.code} - {subj.name}") for subj in subjects]

    # Pre-fill form with existing data
    if request.method == 'GET':
        form.student_id.data = grade.student_id
        form.subject_id.data = grade.subject_id
        form.midterm_score.data = grade.midterm_score
        form.final_score.data = grade.final_score

    if form.validate_on_submit():
        # Tính điểm môn học
        midterm = form.midterm_score.data or 0
        final = form.final_score.data or 0
        subject_score = (midterm * 0.4) + (final * 0.6)

        grade.midterm_score = form.midterm_score.data
        grade.final_score = form.final_score.data
        grade.subject_score = subject_score
        db.session.commit()

        # Cập nhật GPA cho sinh viên
        update_student_gpa(grade.student_id)

        flash('Điểm đã được cập nhật!', 'success')
        return redirect(url_for('grade.list_grades'))

    return render_template('admin/grade_form.html', title='Cập nhật Điểm', form=form, legend='Cập nhật Điểm')

@grade_bp.route('/grade/<int:grade_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_grade(grade_id):
    """Xóa điểm."""
    grade = Grade.query.get_or_404(grade_id)
    student_id = grade.student_id
    db.session.delete(grade)
    db.session.commit()

    # Cập nhật GPA cho sinh viên
    update_student_gpa(student_id)

    flash('Điểm đã được xóa!', 'success')
    return redirect(url_for('grade.list_grades'))

def update_student_gpa(student_id):
    """Cập nhật GPA cho sinh viên dựa trên điểm các môn, quy đổi sang thang điểm 4."""
    # Tính trung bình điểm các môn
    result = db.session.query(func.avg(Grade.subject_score)).filter_by(student_id=student_id).scalar()
    if result is not None:
        # Quy đổi sang thang điểm 4 (giả sử điểm 10 tương ứng với 4.0)
        gpa = (result / 10) * 4.0
    else:
        gpa = 0.0

    # Cập nhật GPA cho sinh viên
    student = Student.query.get(student_id)
    if student:
        student.gpa = round(gpa, 2)
        db.session.commit()
