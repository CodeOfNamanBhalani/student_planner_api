from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from db import db
from models.notes import NoteModel

blp = Blueprint("Notes", "notes", description="Notes Operations")
# Schemas
class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class NoteUpdateSchema(Schema):
    title = fields.Str()
    content = fields.Str()

@blp.route("/notes")
class NoteList(MethodView):
    @jwt_required()
    @blp.response(200, NoteSchema(many=True))
    def get(self):
        """Get all notes for current user"""
        user_id = int(get_jwt_identity())
        return NoteModel.query.filter_by(user_id=user_id).order_by(NoteModel.created_at.desc()).all()

    @jwt_required()
    @blp.arguments(NoteSchema)
    @blp.response(201, NoteSchema)
    def post(self, note_data):
        """Create a new note"""
        user_id = int(get_jwt_identity())
        
        note = NoteModel(
            **note_data,
            user_id=user_id
        )
        
        db.session.add(note)
        db.session.commit()
        
        return note

@blp.route("/notes/<int:note_id>")
class Note(MethodView):
    @jwt_required()
    @blp.response(200, NoteSchema)
    def get(self, note_id):
        """Get a specific note by ID"""
        user_id = int(get_jwt_identity())
        note = NoteModel.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            abort(404, message="Note not found")
        return note
    @jwt_required()
    @blp.arguments(NoteUpdateSchema)
    @blp.response(200, NoteSchema)
    def put(self, note_data, note_id):
        """Update a specific note by ID"""
        user_id = int(get_jwt_identity())
        note = NoteModel.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            abort(404, message="Note not found")
        
        if "title" in note_data:
            note.title = note_data["title"]
        if "content" in note_data:
            note.content = note_data["content"]
        
        db.session.commit()
        return note
    @jwt_required()
    @blp.response(204)
    def delete(self, note_id):
        """Delete a specific note by ID"""
        user_id = int(get_jwt_identity())
        note = NoteModel.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            abort(404, message="Note not found")
        
        db.session.delete(note)
        db.session.commit()
        return {"message": "Note deleted."}, 200
        
    
    