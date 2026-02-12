from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from db import db
from models.exam import ExamModel

blp = Blueprint("Exams", "exams", description="Exam Operations")


# Schemas
class ExamSchema(Schema):
    id = fields.Int(dump_only=True)
    subject = fields.Str(required=True)
    exam_type = fields.Str(required=True)
    exam_date = fields.DateTime(required=True)
    room = fields.Str()
    notes = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class ExamUpdateSchema(Schema):
    subject = fields.Str()
    exam_type = fields.Str()
    exam_date = fields.DateTime()
    room = fields.Str()
    notes = fields.Str()


@blp.route("/exams")
class ExamList(MethodView):
    @jwt_required()
    @blp.response(200, ExamSchema(many=True))
    def get(self):
        """Get all exams for current user"""
        user_id = int(get_jwt_identity())
        return ExamModel.query.filter_by(user_id=user_id).order_by(ExamModel.exam_date).all()

    @jwt_required()
    @blp.arguments(ExamSchema)
    @blp.response(201, ExamSchema)
    def post(self, exam_data):
        """Create a new exam"""
        user_id = int(get_jwt_identity())
        
        exam = ExamModel(
            **exam_data,
            user_id=user_id
        )
        
        db.session.add(exam)
        db.session.commit()
        
        return exam


@blp.route("/exams/<int:exam_id>")
class Exam(MethodView):
    @jwt_required()
    @blp.response(200, ExamSchema)
    def get(self, exam_id):
        """Get a specific exam"""
        user_id = int(get_jwt_identity())
        exam = ExamModel.query.filter_by(id=exam_id, user_id=user_id).first()
        
        if not exam:
            abort(404, message="Exam not found.")
        
        return exam

    @jwt_required()
    @blp.arguments(ExamUpdateSchema)
    @blp.response(200, ExamSchema)
    def put(self, exam_data, exam_id):
        """Update an exam"""
        user_id = int(get_jwt_identity())
        exam = ExamModel.query.filter_by(id=exam_id, user_id=user_id).first()
        
        if not exam:
            abort(404, message="Exam not found.")
        
        for key, value in exam_data.items():
            if value is not None:
                setattr(exam, key, value)
        
        db.session.commit()
        return exam

    @jwt_required()
    def delete(self, exam_id):
        """Delete an exam"""
        user_id = int(get_jwt_identity())
        exam = ExamModel.query.filter_by(id=exam_id, user_id=user_id).first()
        
        if not exam:
            abort(404, message="Exam not found.")
        
        db.session.delete(exam)
        db.session.commit()
        
        return {"message": "Exam deleted."}, 200


@blp.route("/exams/type/<string:exam_type>")
class ExamsByType(MethodView):
    @jwt_required()
    @blp.response(200, ExamSchema(many=True))
    def get(self, exam_type):
        """Get exams by type (midterm/final/quiz)"""
        user_id = int(get_jwt_identity())
        return ExamModel.query.filter_by(user_id=user_id, exam_type=exam_type).all()


@blp.route("/exams/upcoming")
class UpcomingExams(MethodView):
    @jwt_required()
    @blp.response(200, ExamSchema(many=True))
    def get(self):
        """Get upcoming exams (next 7 days)"""
        from datetime import datetime, timedelta
        user_id = int(get_jwt_identity())
        now = datetime.utcnow()
        next_week = now + timedelta(days=7)
        
        return ExamModel.query.filter(
            ExamModel.user_id == user_id,
            ExamModel.exam_date >= now,
            ExamModel.exam_date <= next_week
        ).order_by(ExamModel.exam_date).all()
