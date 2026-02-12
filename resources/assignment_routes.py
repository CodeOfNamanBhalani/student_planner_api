from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields
from datetime import datetime

from db import db
from models.assignment import AssignmentModel

blp = Blueprint("Assignments", "assignments", description="Assignment Operations")


# Schemas
class AssignmentSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    subject = fields.Str(required=True)
    description = fields.Str()
    due_date = fields.DateTime(required=True)
    status = fields.Str()
    priority = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class AssignmentUpdateSchema(Schema):
    title = fields.Str()
    subject = fields.Str()
    description = fields.Str()
    due_date = fields.DateTime()
    status = fields.Str()
    priority = fields.Str()


@blp.route("/assignments")
class AssignmentList(MethodView):
    @jwt_required()
    @blp.response(200, AssignmentSchema(many=True))
    def get(self):
        """Get all assignments for current user"""
        user_id = int(get_jwt_identity())
        return AssignmentModel.query.filter_by(user_id=user_id).order_by(AssignmentModel.due_date).all()

    @jwt_required()
    @blp.arguments(AssignmentSchema)
    @blp.response(201, AssignmentSchema)
    def post(self, assignment_data):
        """Create a new assignment"""
        user_id = int(get_jwt_identity())
        
        assignment = AssignmentModel(
            **assignment_data,
            user_id=user_id
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return assignment


@blp.route("/assignments/<int:assignment_id>")
class Assignment(MethodView):
    @jwt_required()
    @blp.response(200, AssignmentSchema)
    def get(self, assignment_id):
        """Get a specific assignment"""
        user_id = int(get_jwt_identity())
        assignment = AssignmentModel.query.filter_by(id=assignment_id, user_id=user_id).first()
        
        if not assignment:
            abort(404, message="Assignment not found.")
        
        return assignment

    @jwt_required()
    @blp.arguments(AssignmentUpdateSchema)
    @blp.response(200, AssignmentSchema)
    def put(self, assignment_data, assignment_id):
        """Update an assignment"""
        user_id = int(get_jwt_identity())
        assignment = AssignmentModel.query.filter_by(id=assignment_id, user_id=user_id).first()
        
        if not assignment:
            abort(404, message="Assignment not found.")
        
        for key, value in assignment_data.items():
            if value is not None:
                setattr(assignment, key, value)
        
        db.session.commit()
        return assignment

    @jwt_required()
    def delete(self, assignment_id):
        """Delete an assignment"""
        user_id = int(get_jwt_identity())
        assignment = AssignmentModel.query.filter_by(id=assignment_id, user_id=user_id).first()
        
        if not assignment:
            abort(404, message="Assignment not found.")
        
        db.session.delete(assignment)
        db.session.commit()
        
        return {"message": "Assignment deleted."}, 200


@blp.route("/assignments/status/<string:status>")
class AssignmentsByStatus(MethodView):
    @jwt_required()
    @blp.response(200, AssignmentSchema(many=True))
    def get(self, status):
        """Get assignments by status (pending/completed)"""
        user_id = int(get_jwt_identity())
        return AssignmentModel.query.filter_by(user_id=user_id, status=status).all()


@blp.route("/assignments/<int:assignment_id>/complete")
class MarkAssignmentComplete(MethodView):
    @jwt_required()
    @blp.response(200, AssignmentSchema)
    def patch(self, assignment_id):
        """Mark an assignment as completed"""
        user_id = int(get_jwt_identity())
        assignment = AssignmentModel.query.filter_by(id=assignment_id, user_id=user_id).first()
        
        if not assignment:
            abort(404, message="Assignment not found.")
        
        assignment.status = "completed"
        db.session.commit()
        
        return assignment


@blp.route("/assignments/upcoming")
class UpcomingAssignments(MethodView):
    @jwt_required()
    @blp.response(200, AssignmentSchema(many=True))
    def get(self):
        """Get upcoming assignment deadlines (next 7 days, pending only)"""
        from datetime import timedelta
        user_id = int(get_jwt_identity())
        now = datetime.utcnow()
        next_week = now + timedelta(days=7)
        
        return AssignmentModel.query.filter(
            AssignmentModel.user_id == user_id,
            AssignmentModel.due_date >= now,
            AssignmentModel.due_date <= next_week,
            AssignmentModel.status != "completed"
        ).order_by(AssignmentModel.due_date).all()


@blp.route("/assignments/overdue")
class OverdueAssignments(MethodView):
    @jwt_required()
    @blp.response(200, AssignmentSchema(many=True))
    def get(self):
        """Get overdue assignments (past due date, not completed)"""
        user_id = int(get_jwt_identity())
        now = datetime.utcnow()
        
        return AssignmentModel.query.filter(
            AssignmentModel.user_id == user_id,
            AssignmentModel.due_date < now,
            AssignmentModel.status != "completed"
        ).order_by(AssignmentModel.due_date).all()
