from app import db

class Grade(db.Model):
    """
    Lớp Grade đại diện cho bảng điểm của sinh viên trong các môn học.
    """
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    midterm_score = db.Column(db.Float, nullable=True)  # Điểm giữa kì
    final_score = db.Column(db.Float, nullable=True)    # Điểm cuối kì
    subject_score = db.Column(db.Float, nullable=True)  # Điểm môn học = 0.4*midterm + 0.6*final

    # Mối quan hệ với Student và Subject
    student = db.relationship('Student', backref='grades', lazy=True)

    def __repr__(self):
        return f"Grade(Student: {self.student.full_name if self.student else 'N/A'}, Subject: {self.subject.name if self.subject else 'N/A'}, Midterm: {self.midterm_score}, Final: {self.final_score})"
