from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

VALID_ROLES = ("admin", "hse", "user")
VALID_CATEGORIES = ("Unsafe Act", "Unsafe Condition", "Near Miss", "LTI")
VALID_SEVERITIES = ("High", "Medium", "Low", "Not specified")


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # admin / hse / user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    observations = db.relationship("Observation", backref="reporter", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "username": self.username, "role": self.role}


class Observation(db.Model):
    __tablename__ = "observations"

    id = db.Column(db.Integer, primary_key=True)

    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reporter_name = db.Column(db.String(120), nullable=False)

    category = db.Column(db.String(30), nullable=False, default="Not specified")
    severity = db.Column(db.String(20), nullable=False, default="Not specified")
    location = db.Column(db.String(120), nullable=True)

    urdu_script = db.Column(db.Text, nullable=True)
    english_translation = db.Column(db.Text, nullable=True)

    audio_filename = db.Column(db.String(255), nullable=True)   # local filename backup
    drive_file_id = db.Column(db.String(255), nullable=True)
    drive_link = db.Column(db.String(500), nullable=True)

    status = db.Column(db.String(20), nullable=False, default="pending")  # pending / reviewed / closed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "reporter_id": self.reporter_id,
            "reporter_name": self.reporter_name,
            "category": self.category,
            "severity": self.severity,
            "location": self.location,
            "urdu_script": self.urdu_script,
            "english_translation": self.english_translation,
            "audio_filename": self.audio_filename,
            "drive_link": self.drive_link,
            "status": self.status,
            "created_at": self.created_at.strftime("%d %b, %H:%M") if self.created_at else None,
            "created_at_iso": self.created_at.isoformat() if self.created_at else None,
        }
