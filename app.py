from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from news_service import NewsService
from ai_service import AIService
from url_scraper import URLScraper
from models import db, Submission, Comment, User, ChatSession, ChatMessage
from forms import SubmissionForm, CommentForm, LoginForm, RegistrationForm, ArticleAnalysisForm, ChatMessageForm
import os
from dotenv import load_dotenv
import random
from urllib.parse import urlparse
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Read the DATABASE_URL from the environment and enforce sslmode if needed.
DATABASE_URL = os.getenv('DATABASE_URL')
# Ensure the connection string uses "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    # Replace it with the correct prefix "postgresql://"
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# Append sslmode=require if not already provided
if DATABASE_URL and "sslmode=" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 7  # 7 days in seconds

# Optionally, you can also enforce SSL through engine options:
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'sslmode': 'require'}}

# Register custom filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    return text.replace('\n', '<br>') if text else ""

# Initialize extensions and services
db.init_app(app)
news_service = NewsService()
ai_service = AIService()
url_scraper = URLScraper()

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables if they do not exist
with app.app_context():
    db.create_all()

# Categories configuration
CATEGORIES = {
    'climate': {
        'name': 'Climate & Sustainability',
        'icon': '🌍',
        'description': 'Discover positive developments in environmental protection and sustainable living.'
    },
    'social-justice': {
        'name': 'Social Justice & Equity',
        'icon': '⚖️',
        'description': 'Read about progress in creating a more just and equitable society.'
    },
    'health': {
        'name': 'Health & Well-being',
        'icon': '🏥',
        'description': 'Stay updated on breakthroughs in healthcare and wellness initiatives.'
    },
    'education': {
        'name': 'Education & Access',
        'icon': '📚',
        'description': 'Learn about innovations in education and efforts to increase access to learning.'
    }
}

@app.route('/')
def home():
    featured_articles = news_service.get_positive_news('climate', page_size=2)
    return render_template('home.html', categories=CATEGORIES, featured_articles=featured_articles)

@app.route('/<category>')
def category_page(category):
    if category not in CATEGORIES:
        return "Category not found", 404

    session.pop('article_cache', None)
    articles = news_service.get_positive_news(category, page_size=9)
    if len(articles) < 9:
        additional_articles = news_service.get_positive_news(category, page_size=9)
        if additional_articles:
            articles.extend(additional_articles)
            articles = articles[:9]
    
    return render_template('category.html', category=CATEGORIES[category], articles=articles, current_category=category)

@app.route('/user-news')
def user_news():
    submissions = Submission.query.order_by(Submission.created_at.desc()).all()
    return render_template('user_news.html', submissions=submissions)

@app.route('/user-news/<int:story_id>', methods=['GET', 'POST'])
@login_required
def story_detail(story_id):
    story = Submission.query.get_or_404(story_id)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = Comment(content=comment_form.content.data, name=current_user.username, story_id=story_id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('story_detail', story_id=story_id))
    return render_template('story_detail.html', story=story, comment_form=comment_form)

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_story():
    form = SubmissionForm()
    form.name.data = current_user.username
    form.email.data = current_user.email
    if form.validate_on_submit():
        new_submission = Submission(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            name=current_user.username,
            email=current_user.email,
            image_url=form.image_url.data
        )
        db.session.add(new_submission)
        db.session.commit()
        flash('Your story has been submitted!', 'success')
        return redirect(url_for('home'))
    return render_template('submit.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session.permanent = True
            login_user(user, remember=True, duration=timedelta(days=30))
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('home')
            flash('You have been logged in successfully!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/ai-assistant', methods=['GET', 'POST'])
def ai_assistant():
    form = ArticleAnalysisForm()
    if form.validate_on_submit():
        article_data, error = url_scraper.extract_article(form.article_url.data)
        if error:
            flash(f"Error extracting article: {error}", "danger")
            return render_template('ai_assistant.html', form=form, user_sessions=[])
        article_text = article_data['content']
        title = article_data['title'] or "Article Analysis"
        summary = ai_service.summarize_article(article_text)
        if "Summary (AI key not configured):" in summary:
            summary = summary.split("Summary (AI key not configured):")[1].strip()
        chat_session = ChatSession(
            title=title,
            article_text=article_text,
            summary=summary,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        ai_message = ChatMessage(content=summary, is_user=False, session=chat_session)
        db.session.add(chat_session)
        db.session.add(ai_message)
        db.session.commit()
        return redirect(url_for('chat_session', session_id=chat_session.id))
    
    user_sessions = []
    if current_user.is_authenticated:
        user_sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    return render_template('ai_assistant.html', form=form, user_sessions=user_sessions)

@app.route('/chat/<int:session_id>', methods=['GET', 'POST'])
def chat_session(session_id):
    chat_session_obj = ChatSession.query.get_or_404(session_id)
    if current_user.is_authenticated and chat_session_obj.user_id and chat_session_obj.user_id != current_user.id:
        flash('You do not have permission to access this chat session', 'danger')
        return redirect(url_for('ai_assistant'))
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
    form = ChatMessageForm()
    if form.validate_on_submit():
        user_message = ChatMessage(content=form.message.data, is_user=True, session_id=session_id)
        db.session.add(user_message)
        db.session.commit()
        ai_response = ai_service.chat_about_article(chat_session_obj.article_text, messages + [user_message])
        ai_message = ChatMessage(content=ai_response, is_user=False, session_id=session_id)
        db.session.add(ai_message)
        db.session.commit()
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
        form.message.data = ''
    return render_template('chat_session.html', session=chat_session_obj, messages=messages, form=form)

@app.route('/chat/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_chat_session(session_id):
    chat_session_obj = ChatSession.query.get_or_404(session_id)
    if chat_session_obj.user_id != current_user.id:
        flash('You do not have permission to delete this chat session', 'danger')
        return redirect(url_for('ai_assistant'))
    db.session.delete(chat_session_obj)
    db.session.commit()
    flash('Chat session deleted', 'success')
    return redirect(url_for('ai_assistant'))

if __name__ == '__main__':
    app.run(debug=True)