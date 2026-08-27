from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

VALID_ROLES = ("admin", "hse", "manager", "user")
VALID_CATEGORIES = ("Unsafe Act", "Unsafe Condition", "Near Miss", "LTI")
VALID_SEVERITIES = ("High", "Medium", "Low", "Not specified")


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    # Only set when role == "manager": which manager this login represents
    # (must match a key in departments.MANAGER_EMAILS, e.g. "Kaleem").
    manager_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    observations = db.relationship("Observation", backref="reporter", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "role": self.role,
            "manager_name": self.manager_name,
        }


class Observation(db.Model):
    __tablename__ = "observations"

    id = db.Column(db.Integer, primary_key=True)

    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reporter_name = db.Column(db.String(120), nullable=False)

    category = db.Column(db.String(30), nullable=False, default="Not specified")
    severity = db.Column(db.String(20), nullable=False, default="Not specified")
    location = db.Column(db.String(120), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    manager = db.Column(db.String(50), nullable=True)

    urdu_script = db.Column(db.Text, nullable=True)
    english_translation = db.Column(db.Text, nullable=True)

    audio_filename = db.Column(db.String(255), nullable=True)
    drive_file_id = db.Column(db.String(255), nullable=True)
    drive_link = db.Column(db.String(500), nullable=True)

    status = db.Column(db.String(20), nullable=False, default="pending")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def to_dict(self):
        pkt_time = self.created_at + timedelta(hours=5) if self.created_at else None

        return {
            "id": self.id,
            "reporter_id": self.reporter_id,
            "reporter_name": self.reporter_name,
            "category": self.category,
            "severity": self.severity,
            "location": self.location,
            "department": self.department,
            "manager": self.manager,
            "urdu_script": self.urdu_script,
            "english_translation": self.english_translation,
            "audio_filename": self.audio_filename,
            "drive_link": self.drive_link,
            "status": self.status,
            "created_at": pkt_time.strftime("%d %b, %H:%M") if pkt_time else None,
            "created_at_iso": pkt_time.isoformat() if pkt_time else None,
        }
