from app import db
from datetime import datetime

# Quiz Model
class Quiz(db.Model):
    __tablename__ = 'quizzes'  # Table name for the Quiz model
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(100), nullable=False)  # Title of the quiz
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)  # Foreign key to Chapter
    date = db.Column(db.Date, nullable=False)  # Date of the quiz
    duration = db.Column(db.String(50), nullable=False)  # Duration of the quiz (e.g., "2 hours")

    # Relationship with the Chapter model
    chapter = db.relationship('Chapter', backref=db.backref('quizzes', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for quiz creation

    def __repr__(self):
        return f'<Quiz {self.title}, Chapter {self.chapter_id}, Date {self.date}>'


# Question Model
class Question(db.Model):
    __tablename__ = 'questions'  # Table name for the Question model
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)  # Foreign key to Quiz
    question_number = db.Column(db.Integer, nullable=False)  # Question number within the quiz
    title = db.Column(db.String(200), nullable=False)  # Title of the question
    statement = db.Column(db.Text, nullable=False)  # Detailed question statement
    correct_option = db.Column(db.Integer, nullable=False)  # Index of the correct option (1-4)
    option1 = db.Column(db.String(200), nullable=False)  # First option
    option2 = db.Column(db.String(200), nullable=False)  # Second option
    option3 = db.Column(db.String(200), nullable=True)  # Third option (optional)
    option4 = db.Column(db.String(200), nullable=True)  # Fourth option (optional)

    # Relationship with the Quiz model
    quiz = db.relationship('Quiz', backref=db.backref('questions', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for question creation

    def __repr__(self):
        return f'<Question {self.title}, Quiz {self.quiz_id}, Question Number {self.question_number}>'
