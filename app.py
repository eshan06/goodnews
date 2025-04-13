from flask import Flask, render_template, redirect, url_for, flash, request, session
from news_service import NewsService
from models import db, Submission, Comment
from forms import SubmissionForm, CommentForm
import os
from dotenv import load_dotenv
import random

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goodnews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
news_service = NewsService()

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
    
    # Clear the session cache completely
    session.clear()
    
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
    stories = Submission.query.order_by(Submission.created_at.desc()).all()
    return render_template('user_news.html', stories=stories)

@app.route('/user-news/<int:story_id>', methods=['GET', 'POST'])
def story_detail(story_id):
    story = Submission.query.get_or_404(story_id)
    comment_form = CommentForm()
    
    if comment_form.validate_on_submit():
        comment = Comment(
            content=comment_form.content.data,
            author_name=comment_form.author_name.data,
            story_id=story_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('story_detail', story_id=story_id))
    
    return render_template('story_detail.html', story=story, comment_form=comment_form)

@app.route('/submit', methods=['GET', 'POST'])
def submit_story():
    form = SubmissionForm()
    if form.validate_on_submit():
        submission = Submission(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            author_name=form.author_name.data,
            author_email=form.author_email.data,
            image_url=form.image_url.data
        )
        db.session.add(submission)
        db.session.commit()
        flash('Thank you for your submission! Your story has been published.', 'success')
        return redirect(url_for('user_news'))
    return render_template('submit.html', form=form)

if __name__ == '__main__':
    app.run(debug=True) 