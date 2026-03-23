import os
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='employee')  # 'admin' or 'employee'
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Attendance
    attendances = db.relationship('Attendance', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='present')  # 'present', 'absent', 'late'
    image_path = db.Column(db.String(255))
    location = db.Column(db.String(255))
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Attendance {self.id} - User {self.user_id}>'


class TreeData(db.Model):
    __tablename__ = 'tree_data'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('tree_data.id', ondelete='CASCADE'))

    parent = db.relationship(
        'TreeData',
        remote_side=[id],
        backref=db.backref('children', cascade='all, delete-orphan')
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'children': [child.to_dict() for child in sorted(self.children, key=lambda x: x.id)]
        }

    def __repr__(self):
        return f'<TreeData {self.id} - {self.name}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
