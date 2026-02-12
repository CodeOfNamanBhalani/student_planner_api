from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

from db import db
from config import Config
from resources.user_routes import blp as UserBlueprint
from resources.timetable_routes import blp as TimetableBlueprint
from resources.assignment_routes import blp as AssignmentBlueprint
from resources.exam_routes import blp as ExamBlueprint
from resources.note_router import blp as NoteBlueprint


def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    api = Api(app)
    CORS(app)  # Enable CORS for Flutter
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"message": "Token has expired", "error": "token_expired"}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"message": "Invalid token.", "error": "invalid_token"}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"message": "Authorization token required.", "error": "authorization_required"}, 401
    
    # Register blueprints
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(TimetableBlueprint)
    api.register_blueprint(AssignmentBlueprint)
    api.register_blueprint(ExamBlueprint)
    api.register_blueprint(NoteBlueprint)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5000)
