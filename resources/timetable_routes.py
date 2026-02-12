from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from db import db
from models.timetable import TimetableModel

blp = Blueprint("Timetable", "timetable", description="Timetable Operations")


# Schemas
class TimetableSchema(Schema):
    id = fields.Int(dump_only=True)
    subject = fields.Str(required=True)
    day = fields.Str(required=True)
    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)
    room = fields.Str()
    teacher = fields.Str()


class TimetableUpdateSchema(Schema):
    subject = fields.Str()
    day = fields.Str()
    start_time = fields.Str()
    end_time = fields.Str()
    room = fields.Str()
    teacher = fields.Str()


@blp.route("/timetable")
class TimetableList(MethodView):
    @jwt_required()
    @blp.response(200, TimetableSchema(many=True))
    def get(self):
        """Get all timetable entries for current user"""
        user_id = int(get_jwt_identity())
        return TimetableModel.query.filter_by(user_id=user_id).all()

    @jwt_required()
    @blp.arguments(TimetableSchema)
    @blp.response(201, TimetableSchema)
    def post(self, timetable_data):
        """Add a new timetable entry"""
        user_id = int(get_jwt_identity())
        
        timetable = TimetableModel(
            **timetable_data,
            user_id=user_id
        )
        
        db.session.add(timetable)
        db.session.commit()
        
        return timetable


@blp.route("/timetable/<int:timetable_id>")
class Timetable(MethodView):
    @jwt_required()
    @blp.response(200, TimetableSchema)
    def get(self, timetable_id):
        """Get a specific timetable entry"""
        user_id = int(get_jwt_identity())
        timetable = TimetableModel.query.filter_by(id=timetable_id, user_id=user_id).first()
        
        if not timetable:
            abort(404, message="Timetable entry not found.")
        
        return timetable

    @jwt_required()
    @blp.arguments(TimetableUpdateSchema)
    @blp.response(200, TimetableSchema)
    def put(self, timetable_data, timetable_id):
        """Update a timetable entry"""
        user_id = int(get_jwt_identity())
        timetable = TimetableModel.query.filter_by(id=timetable_id, user_id=user_id).first()
        
        if not timetable:
            abort(404, message="Timetable entry not found.")
        
        for key, value in timetable_data.items():
            if value is not None:
                setattr(timetable, key, value)
        
        db.session.commit()
        return timetable

    @jwt_required()
    def delete(self, timetable_id):
        """Delete a timetable entry"""
        user_id = int(get_jwt_identity())
        timetable = TimetableModel.query.filter_by(id=timetable_id, user_id=user_id).first()
        
        if not timetable:
            abort(404, message="Timetable entry not found.")
        
        db.session.delete(timetable)
        db.session.commit()
        
        return {"message": "Timetable entry deleted."}, 200


@blp.route("/timetable/day/<string:day>")
class TimetableByDay(MethodView):
    @jwt_required()
    @blp.response(200, TimetableSchema(many=True))
    def get(self, day):
        """Get timetable entries for a specific day"""
        user_id = int(get_jwt_identity())
        return TimetableModel.query.filter_by(user_id=user_id, day=day).all()
