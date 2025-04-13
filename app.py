from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from news_service import NewsService
from models import db, Submission, Comment, User
from forms import SubmissionForm, CommentForm, LoginForm, RegistrationForm
import os
from dotenv import load_dotenv
import random
from urllib.parse import urlparse
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goodnews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 7  # 7 days in seconds

db.init_app(app)
news_service = NewsService()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

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
    # Get featured articles from climate category
    featured_articles = news_service.get_positive_news('climate', page_size=2)
    return render_template('home.html', 
                         categories=CATEGORIES,
                         featured_articles=featured_articles)

@app.route('/<category>')
def category_page(category):
    if category not in CATEGORIES:
        return "Category not found", 404
    
    # Clear only the articles cache, not the entire session
    if 'article_cache' in session:
        session.pop('article_cache')
    
    # Get fresh articles from the news service
    articles = news_service.get_positive_news(category, page_size=9)
    
    # If we don't have enough articles, try to get more
    if len(articles) < 9:
        additional_articles = news_service.get_positive_news(category, page_size=9)
        if additional_articles:
            articles.extend(additional_articles)
            articles = articles[:9]  # Ensure we don't exceed 9 articles
    
    return render_template('category.html',
                         category=CATEGORIES[category],
                         articles=articles,
                         current_category=category)

@app.route('/user-news')
def user_news():
    # Get submissions from the database, order by most recent first
    submissions = Submission.query.order_by(Submission.created_at.desc()).all()
    return render_template('user_news.html', submissions=submissions)

@app.route('/user-news/<int:story_id>', methods=['GET', 'POST'])
def story_detail(story_id):
    story = Submission.query.get_or_404(story_id)
    comment_form = CommentForm()
    
    if comment_form.validate_on_submit():
        comment = Comment(
            content=comment_form.content.data,
            name=comment_form.name.data,
            story_id=story_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('story_detail', story_id=story_id))
    
    return render_template('story_detail.html', story=story, comment_form=comment_form)

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_story():
    form = SubmissionForm()
    
    # Pre-populate email field if user is logged in
    if request.method == 'GET':
        form.email.data = current_user.email
        form.name.data = current_user.username
    
    if form.validate_on_submit():
        new_submission = Submission(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            name=form.name.data,
            email=form.email.data,
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
            # Make the session permanent and set a long remember duration
            session.permanent = True
            login_user(user, remember=True, duration=timedelta(days=30))  # 30 days remember me
            
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

if __name__ == '__main__':
    app.run(debug=True) 