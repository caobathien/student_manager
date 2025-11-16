from app import db

class StudentSubject(db.Model):
    """
    Lớp StudentSubject đại diện cho bảng đăng ký môn học của sinh viên.
    """
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    # Relationships
    student = db.relationship('Student', backref='registered_subjects')
    subject = db.relationship('Subject', backref='registered_students')

    def __repr__(self):
        return f"StudentSubject(Student: {self.student.full_name}, Subject: {self.subject.name})"
