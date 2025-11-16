from app import db

class Subject(db.Model):
    """
    Lớp Subject đại diện cho bảng môn học trong database.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Mối quan hệ: Một Subject có nhiều Grade
    grades = db.relationship('Grade', backref='subject', lazy=True)

    def __repr__(self):
        return f"Subject('{self.name}', '{self.code}')"
