from db import db

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    timetables = db.relationship("TimetableModel", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    assignments = db.relationship("AssignmentModel", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    exams = db.relationship("ExamModel", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    notes = db.relationship("NoteModel", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
