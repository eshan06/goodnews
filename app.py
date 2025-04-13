from flask import Flask, render_template
from news_service import NewsService
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

news_service = NewsService()

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

if __name__ == '__main__':
    app.run(debug=True) 