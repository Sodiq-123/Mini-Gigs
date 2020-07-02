from datetime import datetime
import hashlib
from flask import request
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, app, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

users_jobs = db.Table('users_jobs',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('job_id', db.Integer, db.ForeignKey('job.id')),
        # db.PrimaryKeyConstraint('user_id', 'job_id') 
)

users_interests = db.Table('users_interests',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('interest_id', db.Integer, db.ForeignKey('interest.id')),
        # db.PrimaryKeyConstraint('user_id', 'interest_id')
)

users_skills = db.Table('users_skills',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('skill_id', db.Integer, db.ForeignKey('skill.id')),
        # db.PrimaryKeyConstraint('user_id', 'skill_id') 
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20), unique=True, nullable=False)
    fname=db.Column(db.String(20), nullable=False)
    lname=db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True ,nullable=False)
    profile_picture=db.Column(db.String, default='default.jpg')
    resume=db.Column(db.String)
    is_super_admin=db.Column(db.Boolean, default=False)
    is_recruiter=db.Column(db.Boolean, default=False)
    is_actively_interviewing=db.Column(db.Boolean, default=False)
    education_details=db.relationship('Education', backref='author', lazy=True)
    work_experience=db.relationship('WorkExperience', backref='author', lazy=True)
    facebook_link=db.Column(db.String)
    twitter_link=db.Column(db.String)
    linkedin_link=db.Column(db.String)
    salary_expt=db.Column(db.String)
    password=db.Column(db.String(60), nullable=False)
    jobs=db.relationship('Job',
                        secondary=users_jobs,
                        backref=db.backref('users', lazy='dynamic'),
                        lazy='dynamic')
    interests=db.relationship('Interest',
                        secondary=users_interests,
                        backref=db.backref('users', lazy='dynamic'),
                        lazy='dynamic')
    skills=db.relationship('Skill',
                        secondary=users_skills,
                        backref=db.backref('users', lazy='dynamic'),
                        lazy='dynamic')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash_ = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash_}?s={size}&d={default}&r={rating}'.format(
                                                            url=url, 
                                                            hash_=hash_, 
                                                            size=size, 
                                                            default=default, 
                                                            rating=rating)
    
    @staticmethod 
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company=db.Column(db.String)
    description=db.Column(db.Text)
    expiry_date=db.Column(db.DateTime, default=datetime.utcnow)
    is_visible=db.Column(db.Boolean, default=True)
    creator_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

class WorkExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(30), nullable=False)
    description=db.Column(db.Text, nullable=False)
    start_date=db.Column(db.DateTime, default=datetime.utcnow)
    end_date=db.Column(db.DateTime, default=datetime.utcnow)
    impact=db.Column(db.String)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(30), nullable=False)
    description=db.Column(db.Text, nullable=False)
    start_date=db.Column(db.DateTime, default=datetime.utcnow)
    end_date=db.Column(db.DateTime, default=datetime.utcnow)
    impact=db.Column(db.String)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(30), nullable=False)
    description=db.Column(db.Text, nullable=False)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(30), nullable=False)
    description=db.Column(db.Text, nullable=False)
