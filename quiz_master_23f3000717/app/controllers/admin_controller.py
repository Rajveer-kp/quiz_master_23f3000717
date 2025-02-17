from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from app import db
from app.models.user import User
from app.models.subject import Chapter, Subject
from app.models.quiz import Quiz, Question
from datetime import datetime
from app.models.scores import UserScore
from sqlalchemy.sql import func

# Create a Blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin-only access decorator


# Admin Dashboard
@admin_bp.route('/dashboard')

def dashboard():
    users = User.query.filter_by(role='user').all()
    subjects = Subject.query.all()
    quizzes = Quiz.query.all()

    # Optional search functionality for subjects
    search_query = request.args.get('search', '')
    if search_query:
        subjects = Subject.query.filter(Subject.name.ilike(f'%{search_query}%')).all()

    return render_template(
        'admin/dashboard.html',
        users=users,
        subjects=subjects,
        quizzes=quizzes
    )


# Quiz Management
@admin_bp.route('/quiz')

def quiz():
    """
    Display the quiz management page with search functionality.
    """
    search_query = request.args.get('search', '')

    if search_query:
        quizzes = Quiz.query.filter(Quiz.title.ilike(f'%{search_query}%')).all()
    else:
        quizzes = Quiz.query.all()

    chapters = Chapter.query.all()
    return render_template('admin/quiz.html', quizzes=quizzes, chapters=chapters, search_query=search_query)



# Add Subject
@admin_bp.route('/add_subject', methods=['GET', 'POST'])

def add_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            subject = Subject(name=name)
            db.session.add(subject)
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Subject name is required!', 'error')
    return render_template('admin/add_subject.html')


# Add Chapter
@admin_bp.route('/add_chapter/<int:subject_id>', methods=['GET', 'POST'])

def add_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        question_count = request.form.get('question_count', 0)

        if title:
            new_chapter = Chapter(
                title=title,
                description=description,
                subject_id=subject_id,
                question_count=question_count
            )
            db.session.add(new_chapter)
            db.session.commit()
            flash('Chapter added successfully!', 'success')
            return redirect(url_for('admin.manage_chapters', subject_id=subject_id))
        flash('Chapter title is required!', 'error')

    return render_template('admin/add_chapter.html', subject=subject)


# Edit Chapter
@admin_bp.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        question_count = request.form.get('question_count')

        if title:
            chapter.title = title
            chapter.description = description
            if question_count is not None:
                chapter.question_count = int(question_count)
            db.session.commit()
            flash('Chapter updated successfully!', 'success')
            return redirect(url_for('admin.manage_chapters', subject_id=chapter.subject_id))
        flash('Chapter title is required!', 'error')

    return render_template('admin/edit_chapter.html', chapter=chapter)


# Delete Chapter
@admin_bp.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if chapter.quizzes:
        flash("Cannot delete chapter because it is associated with quizzes.", "error")
        return redirect(url_for('admin.manage_chapters', subject_id=chapter.subject_id))

    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')

    return redirect(url_for('admin.manage_chapters', subject_id=subject_id))


# Manage Chapters
@admin_bp.route('/manage_chapters/<int:subject_id>')
def manage_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/manage_chapters.html', subject=subject, chapters=chapters)


# Add Quiz
@admin_bp.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        title = request.form.get('title')
        chapter_id = request.form.get('chapter_id')
        date_str = request.form.get('date')
        duration = request.form.get('duration')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('admin.add_quiz'))

        if title and chapter_id and date and duration:
            new_quiz = Quiz(
                title=title,
                chapter_id=int(chapter_id),
                date=date,
                duration=duration
            )
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('admin.quiz'))
        flash('All fields are required!', 'error')

    chapters = Chapter.query.all()
    return render_template('admin/add_quiz.html', chapters=chapters)


@admin_bp.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question.title = request.form.get('title')
        question.statement = request.form.get('statement')
        question.correct_option = int(request.form.get('correct_option', 0))
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')

        if question.title and question.statement and question.correct_option and question.option1 and question.option2:
            db.session.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('admin.quiz'))
        flash('All fields are required!', 'error')

    return render_template('admin/edit_question.html', question=question)



@admin_bp.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id  # Store the quiz ID for redirection
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.quiz'))




# Delete Quiz
@admin_bp.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.quiz'))


# Summary Page
@admin_bp.route('/summary', methods=['GET'])
def summary():
    """
    Render the summary page with subject-wise top scores, quiz attempts, and user-wise scores.
    """

    # Fetch all users
    users = User.query.filter_by(role='user').all()

    # Fetch subject-wise top scores
    top_scores = (
        db.session.query(
            Subject.name.label('subject_name'),
            func.max(UserScore.score).label('top_score')
        )
        .join(Quiz, Quiz.id == UserScore.quiz_id)
        .join(Subject, Subject.id == Quiz.chapter_id)
        .group_by(Subject.id)
        .all()
    )

    # Fetch subject-wise user attempts for the pie chart
    quiz_attempts = (
        db.session.query(
            User.username,
            Subject.name.label('subject_name'),
            func.count(UserScore.id).label('attempts')
        )
        .join(UserScore, User.id == UserScore.user_id)
        .join(Quiz, Quiz.id == UserScore.quiz_id)
        .join(Subject, Subject.id == Quiz.chapter_id)
        .group_by(User.username, Subject.name)
        .all()
    )

    # Fetch user-wise quiz scores
    user_scores = (
        db.session.query(
            User.username,
            Subject.name.label('subject_name'),
            Quiz.title.label('quiz_title'),
            UserScore.score,
            UserScore.total_questions,
            UserScore.date_attempted
        )
        .join(UserScore, User.id == UserScore.user_id)
        .join(Quiz, Quiz.id == UserScore.quiz_id)
        .join(Subject, Subject.id == Quiz.chapter_id)
        .order_by(UserScore.date_attempted.desc())
        .all()
    )

    # Convert data into lists for Jinja
    users_list = [{"id": user.id, "username": user.username} for user in users]
    top_scores_data = [{"subject_name": row[0], "top_score": row[1]} for row in top_scores]
    quiz_attempts_data = [
        {"username": row[0], "subject_name": row[1], "attempts": row[2]} for row in quiz_attempts
    ]
    user_scores_data = [
        {
            "username": row[0],
            "subject_name": row[1],
            "quiz_title": row[2],
            "score": row[3],
            "total_questions": row[4],
            "date_attempted": row[5]
        }
        for row in user_scores
    ]

    return render_template(
        'admin/summary.html',
        users=users_list,
        top_scores=top_scores_data,
        quiz_attempts=quiz_attempts_data,
        user_scores=user_scores_data
    )

@admin_bp.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    """Allows Admin to add questions to a quiz."""
    
    # Check if admin is logged in
   

    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        title = request.form.get('title')
        statement = request.form.get('statement')
        correct_option = request.form.get('correct_option')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')

        # ✅ Ensure all fields are filled
        if not title or not statement or not correct_option or not option1 or not option2:
            flash('All fields are required!', 'danger')
            return redirect(url_for('admin.add_question', quiz_id=quiz_id))

        # ✅ Determine question number for the quiz
        question_number = Question.query.filter_by(quiz_id=quiz_id).count() + 1

        # ✅ Create new question
        question = Question(
            quiz_id=quiz_id,
            question_number=question_number,
            title=title,
            statement=statement,
            correct_option=int(correct_option),
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4
        )
        db.session.add(question)
        db.session.commit()

        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.quiz'))

    return render_template('admin/add_question.html', quiz=quiz)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Access denied: Admins only!", "danger")
            return redirect(url_for('auth.admin_login'))  # ✅ Redirect to admin login
        return f(*args, **kwargs)
    return decorated_function

# ✅ Manage Users Page
@admin_bp.route('/manage_users')
@admin_required
def manage_users():
    users = User.query.filter(User.role != 'admin').all()  # Exclude admins
    return render_template('admin/manage_users.html', users=users)

# ✅ Block User
@admin_bp.route('/block_user/<int:user_id>', methods=['POST'])
def block_user(user_id):
    """Allows admin to block a user."""
    user = User.query.get_or_404(user_id)
    user.is_blocked = True  # ✅ Sets user as blocked
    db.session.commit()

    flash(f'User {user.username} has been blocked.', 'warning')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/unblock_user/<int:user_id>', methods=['POST'])
def unblock_user(user_id):
    """Allows admin to unblock a user."""
    user = User.query.get_or_404(user_id)
    user.is_blocked = False  # ✅ Sets user as active
    db.session.commit()

    flash(f'User {user.username} has been unblocked.', 'success')
    return redirect(url_for('admin.manage_users'))
