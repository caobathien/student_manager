from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.gpa_service import GPAService

gpa_bp = Blueprint('gpa', __name__)

@gpa_bp.route('/gpa-analysis')
@login_required
def gpa_analysis():
    """
    Hiển thị trang phân tích GPA với biểu đồ cột và biểu đồ đường.
    """
    # Lấy dữ liệu từ service
    distribution = GPAService.get_gpa_distribution()
    avg_gpa_by_class = GPAService.get_average_gpa_by_class()
    stats = GPAService.get_overall_stats()
    risk_by_class = GPAService.get_risk_distribution_by_class()

    return render_template(
        'gpa_analysis.html',
        title='Phân tích GPA',
        distribution=distribution,
        avg_gpa_by_class=avg_gpa_by_class,
        stats=stats,
        risk_by_class=risk_by_class
    )

@gpa_bp.route('/my-gpa-analysis')
@login_required
def my_gpa_analysis():
    """
    Sinh viên xem thống kê GPA cá nhân.
    """
    if current_user.role != 'student' or not current_user.student:
        flash('Bạn không có quyền truy cập trang này.', 'danger')
        return redirect(url_for('main.home'))

    # Lấy dữ liệu GPA cá nhân
    personal_stats = GPAService.get_personal_gpa_stats(current_user.student.id)

    return render_template(
        'my_gpa_analysis.html',
        title='Thống kê GPA cá nhân',
        stats=personal_stats
    )
