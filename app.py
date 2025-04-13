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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goodnews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 7  # 7 days in seconds

# Register custom filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    if not text:
        return ""
    return text.replace('\n', '<br>')

db.init_app(app)
news_service = NewsService()
ai_service = AIService()
url_scraper = URLScraper()

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
@login_required
def story_detail(story_id):
    story = Submission.query.get_or_404(story_id)
    comment_form = CommentForm()
    
    if comment_form.validate_on_submit():
        comment = Comment(
            content=comment_form.content.data,
            name=current_user.username,  # Use the logged-in user's name
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
    
    # Always set the name and email fields from the current user
    form.name.data = current_user.username
    form.email.data = current_user.email
    
    if form.validate_on_submit():
        new_submission = Submission(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            name=current_user.username,  # Use the logged-in user's name
            email=current_user.email,    # Use the logged-in user's email
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

@app.route('/ai-assistant', methods=['GET', 'POST'])
def ai_assistant():
    form = ArticleAnalysisForm()
    
    if form.validate_on_submit():
        # Extract article from URL
        article_data, error = url_scraper.extract_article(form.article_url.data)
        if error:
            flash(f"Error extracting article: {error}", "danger")
            return render_template('ai_assistant.html', form=form, user_sessions=[])
        
        article_text = article_data['content']
        original_url = article_data['url']
        
        # Use the title from the article
        title = article_data['title'] or "Article Analysis"
        
        # Generate summary
        summary = ai_service.summarize_article(article_text)
        
        # Create a new chat session
        session = ChatSession(
            title=title,
            article_text=article_text,
            summary=summary,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        
        # Add the AI's initial message (the summary)
        initial_message = f"Here's a summary of the article from {original_url}:\n\n{summary}"
        
        ai_message = ChatMessage(
            content=initial_message,
            is_user=False,
            session=session
        )
        
        db.session.add(session)
        db.session.add(ai_message)
        db.session.commit()
        
        return redirect(url_for('chat_session', session_id=session.id))
    
    # Get the user's chat sessions if they're logged in
    user_sessions = []
    if current_user.is_authenticated:
        user_sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    
    return render_template('ai_assistant.html', form=form, user_sessions=user_sessions)

@app.route('/chat/<int:session_id>', methods=['GET', 'POST'])
def chat_session(session_id):
    chat_session = ChatSession.query.get_or_404(session_id)
    
    # Make sure users can only access their own chat sessions if logged in
    if current_user.is_authenticated and chat_session.user_id and chat_session.user_id != current_user.id:
        flash('You do not have permission to access this chat session', 'danger')
        return redirect(url_for('ai_assistant'))
    
    # Get the messages for this session
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
    
    form = ChatMessageForm()
    
    if form.validate_on_submit():
        # Add the user's message
        user_message = ChatMessage(
            content=form.message.data,
            is_user=True,
            session_id=session_id
        )
        db.session.add(user_message)
        db.session.commit()
        
        # Get AI response
        ai_response = ai_service.chat_about_article(chat_session.article_text, messages + [user_message])
        
        # Add the AI's response
        ai_message = ChatMessage(
            content=ai_response,
            is_user=False,
            session_id=session_id
        )
        db.session.add(ai_message)
        db.session.commit()
        
        # Refresh the messages list
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
        
        # Clear the form
        form.message.data = ''
    
    return render_template('chat_session.html', 
                          session=chat_session,
                          messages=messages,
                          form=form)

@app.route('/chat/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_chat_session(session_id):
    chat_session = ChatSession.query.get_or_404(session_id)
    
    # Make sure users can only delete their own chat sessions
    if chat_session.user_id != current_user.id:
        flash('You do not have permission to delete this chat session', 'danger')
        return redirect(url_for('ai_assistant'))
    
    db.session.delete(chat_session)
    db.session.commit()
    
    flash('Chat session deleted', 'success')
    return redirect(url_for('ai_assistant'))

if __name__ == '__main__':
    app.run(debug=True) 