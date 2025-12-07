from flask import Blueprint, render_template, request
from flask_login import login_required
from app.controllers import student_controller
from app.services.ai_service import StudentAI

main = Blueprint('main', __name__)

@main.route('/')
@login_required 
def index():
    return render_template('index.html')

@main.route('/students')
def students():
    return student_controller.list_students()

@main.route('/my_info')
def my_info():
    return student_controller.view_my_info()

@main.route('/students/add', methods=['GET', 'POST'])
def add_student():
    return student_controller.add_student()

@main.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    return student_controller.edit_student(student_id)

@main.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    return student_controller.delete_student(student_id)

@main.route('/ai-dashboard', methods=['GET', 'POST'])
def ai_dashboard_page():
    ai = StudentAI()
    
    # Chạy phân tích
    try:
        df = ai.analyze_students()
        records = df.to_dict('records') if not df.empty else []
    except Exception as e:
        print(f"Lỗi phân tích: {e}")
        records = []
    
    # Phần chat sẽ trả về thông báo tĩnh
    answer = None
    if request.method == 'POST':
        q = request.form.get('question')
        if q: answer = ai.chat_with_data(q)

    return render_template('ai_dashboard.html', data=records, ai_answer=answer)