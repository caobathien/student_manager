from app.models.student import Student
from app.models.class_model import Class
from app.models.grade import Grade
from app.models.subject import Subject
from app import db
from sqlalchemy import func

class GPAService:
    @staticmethod
    def get_gpa_distribution():
        """
        Trả về phân phối GPA: số lượng sinh viên trong các khoảng GPA.
        """
        ranges = [
            (0.0, 1.0),
            (1.0, 2.0),
            (2.0, 3.0),
            (3.0, 4.0)
        ]
        distribution = {}
        for min_gpa, max_gpa in ranges:
            count = Student.query.filter(Student.gpa >= min_gpa, Student.gpa < max_gpa).count()
            label = f"{min_gpa}-{max_gpa}"
            distribution[label] = count
        return distribution

    @staticmethod
    def get_average_gpa_by_class():
        """
        Trả về điểm GPA trung bình theo từng lớp.
        """
        results = db.session.query(
            Class.name,
            func.avg(Student.gpa).label('avg_gpa')
        ).join(Student).group_by(Class.id, Class.name).order_by(Class.name).all()

        avg_gpa_by_class = {name: round(avg_gpa, 2) if avg_gpa else 0 for name, avg_gpa in results}
        return avg_gpa_by_class

    @staticmethod
    def get_overall_stats():
        """
        Trả về thống kê tổng quan về GPA.
        """
        students = Student.query.all()
        if not students:
            return {
                'total_students': 0,
                'average_gpa': 0,
                'min_gpa': 0,
                'max_gpa': 0
            }

        gpas = [s.gpa for s in students]
        return {
            'total_students': len(students),
            'average_gpa': round(sum(gpas) / len(gpas), 2),
            'min_gpa': min(gpas),
            'max_gpa': max(gpas)
        }

    @staticmethod
    def get_risk_distribution_by_class():
        """
        Trả về phân phối rủi ro học tập theo từng lớp.
        Rủi ro cao: GPA < 2.0
        Rủi ro thấp: GPA >= 2.0
        """
        results = db.session.query(
            Class.name,
            func.count(Student.id).label('total_students'),
            func.sum(db.case((Student.gpa < 2.0, 1), else_=0)).label('high_risk'),
            func.sum(db.case((Student.gpa >= 2.0, 1), else_=0)).label('low_risk')
        ).join(Student).group_by(Class.id, Class.name).order_by(Class.name).all()

        risk_by_class = {}
        for name, total, high_risk, low_risk in results:
            risk_by_class[name] = {
                'total': total,
                'high_risk': high_risk,
                'low_risk': low_risk
            }

        # Thêm thống kê tổng quan
        total_students = sum(data['total'] for data in risk_by_class.values())
        total_high_risk = sum(data['high_risk'] for data in risk_by_class.values())
        total_low_risk = sum(data['low_risk'] for data in risk_by_class.values())

        risk_by_class['all'] = {
            'total': total_students,
            'high_risk': total_high_risk,
            'low_risk': total_low_risk
        }

        return risk_by_class

    @staticmethod
    def get_personal_gpa_stats(student_id):
        """
        Trả về thống kê GPA cá nhân cho một sinh viên.
        """
        student = Student.query.get(student_id)
        if not student:
            return None

        # Lấy tất cả điểm của sinh viên
        grades = Grade.query.filter_by(student_id=student_id).all()

        if not grades:
            return {
                'student': student,
                'total_subjects': 0,
                'completed_subjects': 0,
                'average_score': 0,
                'gpa': student.gpa,
                'grades': [],
                'chart_data': {
                    'current_gpa': student.gpa,
                    'predicted_gpa': student.gpa,  # Dự đoán GPA tương lai
                    'risk_level': 'Thấp' if student.gpa >= 2.5 else 'Cao'
                }
            }

        completed_grades = []
        total_score = 0
        subject_count = 0

        for grade in grades:
            if grade.midterm_score is not None and grade.final_score is not None:
                avg_score = (grade.midterm_score + grade.final_score * 2) / 3
                completed_grades.append({
                    'subject': grade.subject,
                    'midterm': grade.midterm_score,
                    'final': grade.final_score,
                    'average': round(avg_score, 2)
                })
                total_score += avg_score
                subject_count += 1

        average_score = round(total_score / subject_count, 2) if subject_count > 0 else 0

        # Dự đoán GPA tương lai dựa trên xu hướng
        predicted_gpa = min(4.0, student.gpa + 0.1)  # Giả sử tăng 0.1 mỗi kỳ
        risk_level = 'Thấp' if student.gpa >= 2.5 else 'Cao'

        return {
            'student': student,
            'total_subjects': len(grades),
            'completed_subjects': subject_count,
            'average_score': average_score,
            'gpa': student.gpa,
            'grades': completed_grades,
            'chart_data': {
                'current_gpa': student.gpa,
                'predicted_gpa': predicted_gpa,
                'risk_level': risk_level
            }
        }
