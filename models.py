from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, nullable=False)

@login_manager.user_loader
def load_admin(admin_id):
    return Admin.query.get(int(admin_id))

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    registrations = db.relationship('Registration', backref='school', lazy=True)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    whatsapp_number = db.Column(db.String(20), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    team_members_count = db.Column(db.Integer, nullable=False)
    society_name = db.Column(db.String(100), nullable=True)
    president_name = db.Column(db.String(100), nullable=True)
    president_number = db.Column(db.String(20), nullable=True)
    teacher_name = db.Column(db.String(100), nullable=True)
    teacher_number = db.Column(db.String(20), nullable=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    team_members = db.relationship('TeamMember', backref='registration', lazy=True, cascade="all, delete-orphan")
    submissions = db.relationship('Submission', backref='registration', lazy=True)

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whatsapp_number = db.Column(db.String(20), nullable=False)
    registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'), nullable=False)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    code_file_path = db.Column(db.String(255), nullable=False)
    presentation_file_path = db.Column(db.String(255), nullable=True)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
