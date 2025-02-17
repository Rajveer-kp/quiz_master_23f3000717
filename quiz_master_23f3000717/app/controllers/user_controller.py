from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.models.subject import Subject, Chapter
from app.models.quiz import Quiz, Question
from app.models.scores import UserScore
from app.models.user import User
from app import db
from datetime import datetime
from sqlalchemy import func
from functools import wraps

# Define the user blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Custom login required decorator


# User Dashboard
@user_bp.route('/dashboard')
def dashboard():
    """
    Display the user dashboard with available subjects and chapters.
    Includes search functionality and disables 'Take Quiz' button if no quiz is available.
    """
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('auth.login'))  # Redirect if not logged in

    search_query = request.args.get('search', '')

    # Fetch subjects based on search query
    if search_query:
        subjects = Subject.query.filter(Subject.name.ilike(f'%{search_query}%')).all()
    else:
        subjects = Subject.query.all()

    # Fetch all chapters in a single query to avoid multiple DB hits
    chapter_map = {chapter.id: chapter for chapter in Chapter.query.all()}

    # Fetch quizzes in a single query to avoid multiple DB hits
    quiz_map = {quiz.chapter_id for quiz in Quiz.query.all()}

    # Assign chapters to subjects and check if they have a quiz
    for subject in subjects:
        subject.chapters = [chapter_map[chap_id] for chap_id in chapter_map if chapter_map[chap_id].subject_id == subject.id]
        for chapter in subject.chapters:
            chapter.has_quiz = chapter.id in quiz_map  # Efficient check if a quiz exists

    # ✅ Pass username explicitly
    return render_template('user/dashboard.html', subjects=subjects, search_query=search_query, username=session.get('username'))





# Take Quiz Route
@user_bp.route('/take_quiz/<int:chapter_id>', methods=['GET', 'POST'])

def take_quiz(chapter_id):
    """
    Allow users to take a quiz based on the chapter, with timing functionality.
    """
    # Fetch the quiz associated with the chapter
    quiz = Quiz.query.filter_by(chapter_id=chapter_id).first()

    if not quiz:
        flash('No quiz available for this subject.', 'error')
        return redirect(url_for('user.dashboard'))

    # Fetch all questions associated with the quiz
    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    if request.method == 'POST':
        # Evaluate the user's answers
        user_answers = request.form
        correct_answers = 0
        total_questions = len(questions)

        for question in questions:
            user_answer = user_answers.get(f'question_{question.id}')
            if user_answer and int(user_answer) == question.correct_option:
                correct_answers += 1

        # Save the score with the user's reference
        user_score = UserScore(
            user_id=session['user_id'],  # Get user ID from session
            quiz_id=quiz.id,
            score=correct_answers,
            total_questions=total_questions,
            date_attempted=datetime.utcnow()
        )
        db.session.add(user_score)
        db.session.commit()

        flash(f'You scored {correct_answers}/{total_questions}!', 'success')
        return redirect(url_for('user.scores'))

    quiz_duration = int(quiz.duration.split()[0]) if quiz.duration else 10  # Default to 10 minutes if no duration

    return render_template(
        'user/take_quiz.html',
        quiz=quiz,
        questions=questions,
        quiz_duration=quiz_duration,
    )


# Scores Page
@user_bp.route('/scores')

def scores():
    """
    Display the scores for quizzes attempted by the current user.
    """
    user_scores = UserScore.query.filter_by(user_id=session['user_id']).order_by(UserScore.date_attempted.desc()).all()
    return render_template('user/scores.html', user_scores=user_scores)


# Summary Page
@user_bp.route('/summary')

def summary():
    """
    Generate summary charts for user's quiz performance.
    """

    # Fetch all subjects for dropdown
    all_subjects = Subject.query.with_entities(Subject.id, Subject.name).all()
    
    # Get selected subject
    selected_subject = request.args.get('selected_subject', '')

    user_scores = []
    total_correct = 0
    total_incorrect = 0

    user_id = session.get('user_id')

    if selected_subject:
        user_scores_query = (
            db.session.query(
                Quiz.title.label('quiz_title'),
                UserScore.score,
                UserScore.total_questions
            )
            .join(UserScore, Quiz.id == UserScore.quiz_id)
            .join(Subject, Subject.id == Quiz.chapter_id)
            .filter(UserScore.user_id == user_id, Subject.id == selected_subject)
        )

        user_scores = user_scores_query.all()

        # Calculate correct & incorrect answers for Pie Chart
        for row in user_scores:
            total_correct += row.score
            total_incorrect += row.total_questions - row.score

    return render_template(
        'user/summary.html',
        all_subjects=all_subjects,
        selected_subject=selected_subject,
        user_scores=user_scores,
        total_correct=total_correct,
        total_incorrect=total_incorrect
    )
