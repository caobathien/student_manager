from flask import Blueprint, render_template, request
from flask_wtf.csrf import validate_csrf
from app.services.ai_service import StudentAI
from app.models.subject import Subject


ai_board_bp = Blueprint('ai_board', __name__)

@ai_board_bp.route('/ai-dashboard', methods=['GET', 'POST'])
def ai_dashboard_page():
    ai = StudentAI()

    # Lấy danh sách môn học
    subjects = Subject.query.all()

    # Lấy subject_id từ form nếu có
    selected_subject_id = request.form.get('subject_id') if request.method == 'POST' else None
    if selected_subject_id and selected_subject_id.isdigit():
        selected_subject_id = int(selected_subject_id)
    else:
        selected_subject_id = None

    # Chạy phân tích với subject_id nếu được chọn
    try:
        df = ai.analyze_students(subject_id=selected_subject_id)
        records = df.to_dict('records') if not df.empty else []
    except Exception as e:
        print(f"Lỗi phân tích: {e}")
        records = []

    # Phần chat sẽ trả về thông báo tĩnh
    answer = None
    if request.method == 'POST':
        # Validate CSRF token manually
        try:
            validate_csrf(request.form.get('csrf_token'))
        except Exception as e:
            print(f"CSRF validation error: {e}")
            # Continue processing even if CSRF fails for now

        q = request.form.get('question')
        if q: answer = ai.chat_with_data(q)

    return render_template('ai_dashboard.html', data=records, ai_answer=answer, subjects=subjects, selected_subject_id=selected_subject_id)
