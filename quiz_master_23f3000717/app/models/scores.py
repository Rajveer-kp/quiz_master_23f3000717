from app import db
from datetime import datetime

class UserScore(db.Model):
    __tablename__ = 'user_scores'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Add user_id to associate with User
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)

    quiz = db.relationship('Quiz', backref=db.backref('scores', lazy=True))
    user = db.relationship('User', backref=db.backref('scores', lazy=True))  # Add relationship with User
