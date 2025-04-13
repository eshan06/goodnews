from flask import Flask, render_template, redirect, url_for, flash, request
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
        },
        {
            'id': 3,
            'title': "Ocean Cleanup Project Removes 100,000 Tons of Plastic",
            'excerpt': "Innovative technology helps clean our oceans and protect marine life.",
            'image': "https://images.unsplash.com/photo-1534447677768-be436bb09401",
            'date': "2023-06-08"
        },
        {
            'id': 4,
            'title': "Cities Worldwide Adopt Green Roof Initiatives",
            'excerpt': "Urban areas are transforming rooftops into green spaces to combat climate change.",
            'image': "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df",
            'date': "2023-06-05"
        },
        {
            'id': 5,
            'title': "Breakthrough in Carbon Capture Technology",
            'excerpt': "New method makes carbon capture more efficient and cost-effective.",
            'image': "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d",
            'date': "2023-06-03"
        },
        {
            'id': 6,
            'title': "Electric Vehicle Sales Reach Record High",
            'excerpt': "Global shift to electric transportation accelerates with new sales records.",
            'image': "https://images.unsplash.com/photo-1551830820-330a71b99659",
            'date': "2023-06-01"
        },
        {
            'id': 7,
            'title': "Community Gardens Flourish in Urban Areas",
            'excerpt': "Local initiatives bring fresh produce and green spaces to city dwellers.",
            'image': "https://images.unsplash.com/photo-1466692476868-aef1dfb1b735",
            'date': "2023-05-29"
        },
        {
            'id': 8,
            'title': "Wind Energy Production Sets New Records",
            'excerpt': "Advancements in wind turbine technology lead to increased energy production.",
            'image': "https://images.unsplash.com/photo-1508517284886-4a2550d0acd7",
            'date': "2023-05-27"
        },
        {
            'id': 9,
            'title': "Sustainable Agriculture Practices Gain Traction",
            'excerpt': "Farmers worldwide adopt eco-friendly farming methods to protect the environment.",
            'image': "https://images.unsplash.com/photo-1500382017468-9049fed747ef",
            'date': "2023-05-25"
        }
    ],
    'social-justice': [
        {
            'id': 1,
            'title': "Community Program Provides Free Legal Aid to Thousands",
            'excerpt': "A volunteer-based initiative is helping underserved communities access legal representation.",
            'image': "https://images.unsplash.com/photo-1589829545856-d10d557cf95f",
            'date': "2023-06-12"
        },
        {
            'id': 2,
            'title': "New Initiative Supports Minority-Owned Businesses",
            'excerpt': "Program provides funding and mentorship to help minority entrepreneurs succeed.",
            'image': "https://images.unsplash.com/photo-1556741533-6e6a62bd8b49",
            'date': "2023-06-10"
        },
        {
            'id': 3,
            'title': "Education Program Bridges Digital Divide",
            'excerpt': "Nonprofit organization provides technology and training to underserved communities.",
            'image': "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
            'date': "2023-06-08"
        },
        {
            'id': 4,
            'title': "Community Center Offers Free Job Training",
            'excerpt': "Local initiative helps unemployed individuals gain new skills and find work.",
            'image': "https://images.unsplash.com/photo-1521791136064-7986c2920216",
            'date': "2023-06-05"
        },
        {
            'id': 5,
            'title': "Youth Mentorship Program Expands Nationwide",
            'excerpt': "Program connects young people with mentors to help them achieve their goals.",
            'image': "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
            'date': "2023-06-03"
        },
        {
            'id': 6,
            'title': "Affordable Housing Initiative Breaks Ground",
            'excerpt': "New development will provide quality housing for low-income families.",
            'image': "https://images.unsplash.com/photo-1560518883-ce09059eeffa",
            'date': "2023-06-01"
        },
        {
            'id': 7,
            'title': "Community Food Bank Serves Record Numbers",
            'excerpt': "Local organization expands to meet growing demand for food assistance.",
            'image': "https://images.unsplash.com/photo-1541643600914-78b084683601",
            'date': "2023-05-29"
        },
        {
            'id': 8,
            'title': "New Program Supports Refugee Integration",
            'excerpt': "Initiative helps refugees build new lives in their adopted communities.",
            'image': "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
            'date': "2023-05-27"
        },
        {
            'id': 9,
            'title': "Community Policing Initiative Shows Success",
            'excerpt': "Program builds trust between law enforcement and local communities.",
            'image': "https://images.unsplash.com/photo-1589829545856-d10d557cf95f",
            'date': "2023-05-25"
        }
    ],
    'health': [
        {
            'id': 1,
            'title': "Breakthrough in Cancer Research Shows Promise",
            'excerpt': "Scientists have made significant progress in developing new treatments for previously untreatable cancers.",
            'image': "https://images.unsplash.com/photo-1576091160550-2173dba999ef",
            'date': "2023-06-14"
        },
        {
            'id': 2,
            'title': "New Mental Health Initiative Launches",
            'excerpt': "Program provides free counseling and support services to those in need.",
            'image': "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d",
            'date': "2023-06-12"
        },
        {
            'id': 3,
            'title': "Community Health Center Expands Services",
            'excerpt': "Local clinic adds new programs to serve more patients in need.",
            'image': "https://images.unsplash.com/photo-1579684385127-1ef15d508118",
            'date': "2023-06-10"
        },
        {
            'id': 4,
            'title': "Vaccination Program Reaches Rural Areas",
            'excerpt': "Mobile clinics bring essential vaccines to underserved communities.",
            'image': "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d",
            'date': "2023-06-08"
        },
        {
            'id': 5,
            'title': "New Fitness Initiative Promotes Community Health",
            'excerpt': "Program encourages physical activity and healthy living in local neighborhoods.",
            'image': "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
            'date': "2023-06-05"
        },
        {
            'id': 6,
            'title': "Breakthrough in Alzheimer's Research",
            'excerpt': "Scientists discover new potential treatment for Alzheimer's disease.",
            'image': "https://images.unsplash.com/photo-1576091160550-2173dba999ef",
            'date': "2023-06-03"
        },
        {
            'id': 7,
            'title': "Community Nutrition Program Expands",
            'excerpt': "Initiative helps families access healthy food and nutrition education.",
            'image': "https://images.unsplash.com/photo-1541643600914-78b084683601",
            'date': "2023-05-29"
        },
        {
            'id': 8,
            'title': "New Telemedicine Service Launches",
            'excerpt': "Program provides remote healthcare access to rural communities.",
            'image': "https://images.unsplash.com/photo-1579684385127-1ef15d508118",
            'date': "2023-05-27"
        },
        {
            'id': 9,
            'title': "Mental Health Awareness Campaign Shows Impact",
            'excerpt': "Community initiative reduces stigma and increases access to mental health services.",
            'image': "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d",
            'date': "2023-05-25"
        }
    ],
    'education': [
        {
            'id': 1,
            'title': "Digital Learning Platform Reaches 1 Million Students",
            'excerpt': "An innovative online education platform is making quality education accessible worldwide.",
            'image': "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
            'date': "2023-06-13"
        },
        {
            'id': 2,
            'title': "New Scholarship Program Launches",
            'excerpt': "Initiative provides financial support to students from underserved communities.",
            'image': "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
            'date': "2023-06-11"
        },
        {
            'id': 3,
            'title': "Community Library Expansion Complete",
            'excerpt': "Renovated facility offers new resources and programs for all ages.",
            'image': "https://images.unsplash.com/photo-1521587760476-6c2a5912ba33",
            'date': "2023-06-09"
        },
        {
            'id': 4,
            'title': "STEM Education Initiative Shows Success",
            'excerpt': "Program increases student interest and achievement in science and technology.",
            'image': "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
            'date': "2023-06-07"
        },
        {
            'id': 5,
            'title': "New Early Childhood Education Center Opens",
            'excerpt': "Facility provides quality care and education for young children.",
            'image': "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
            'date': "2023-06-05"
        },
        {
            'id': 6,
            'title': "Adult Education Program Expands",
            'excerpt': "Initiative helps adults complete their education and gain new skills.",
            'image': "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
            'date': "2023-06-03"
        },
        {
            'id': 7,
            'title': "New Arts Education Initiative Launches",
            'excerpt': "Program brings arts education to schools that lack resources.",
            'image': "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
            'date': "2023-05-29"
        },
        {
            'id': 8,
            'title': "Community Tutoring Program Shows Results",
            'excerpt': "Volunteer initiative helps students improve their academic performance.",
            'image': "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
            'date': "2023-05-27"
        },
        {
            'id': 9,
            'title': "New Language Learning Program Launches",
            'excerpt': "Initiative helps students learn new languages and understand different cultures.",
            'image': "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
            'date': "2023-05-25"
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
    
    # Get all articles for the category
    all_articles = ARTICLES.get(category, [])
    
    # If we have 9 or more articles, randomly select 9 unique articles
    if len(all_articles) >= 9:
        articles = random.sample(all_articles, 9)
    else:
        # If we have fewer than 9 articles, use all available articles
        articles = all_articles
    
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