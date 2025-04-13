from flask import Flask, render_template, redirect, url_for, flash, request
from news_service import NewsService
from models import db, Submission, Comment
from forms import SubmissionForm, CommentForm
import os
from dotenv import load_dotenv

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

# Sample articles data
ARTICLES = {
    'climate': [
        {
            'id': 1,
            'title': "Renewable Energy Breakthrough: Solar Panel Efficiency Reaches New High",
            'excerpt': "Scientists have developed a new type of solar panel that achieves record-breaking efficiency.",
            'image': "https://images.unsplash.com/photo-1509391366360-2e959784a276",
            'date': "2023-06-15"
        },
        {
            'id': 2,
            'title': "Global Reforestation Efforts Show Promising Results",
            'excerpt': "Countries around the world are seeing success in their tree-planting initiatives.",
            'image': "https://images.unsplash.com/photo-1441974231531-c6227db76b6e",
            'date': "2023-06-10"
        }
    ],
    'social-justice': [
        {
            'id': 1,
            'title': "Community Program Provides Free Legal Aid to Thousands",
            'excerpt': "A volunteer-based initiative is helping underserved communities access legal representation.",
            'image': "https://images.unsplash.com/photo-1589829545856-d10d557cf95f",
            'date': "2023-06-12"
        }
    ],
    'health': [
        {
            'id': 1,
            'title': "Breakthrough in Cancer Research Shows Promise",
            'excerpt': "Scientists have made significant progress in developing new treatments for previously untreatable cancers.",
            'image': "https://images.unsplash.com/photo-1576091160550-2173dba999ef",
            'date': "2023-06-14"
        }
    ],
    'education': [
        {
            'id': 1,
            'title': "Digital Learning Platform Reaches 1 Million Students",
            'excerpt': "An innovative online education platform is making quality education accessible worldwide.",
            'image': "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
            'date': "2023-06-13"
        }
    ]
}

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
    
    articles = news_service.get_positive_news(category)
    return render_template('category.html',
                         category=CATEGORIES[category],
                         articles=articles)

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