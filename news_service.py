from newsapi import NewsApiClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class NewsService:
    def __init__(self):
        self.api = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        
    def get_positive_news(self, category, page_size=10):
        # Map our categories to NewsAPI categories and keywords
        category_mapping = {
            'climate': {
                'keywords': ['renewable energy', 'sustainability', 'environmental progress', 
                           'climate solution', 'green technology', 'conservation success'],
                'exclude_keywords': ['climate crisis', 'disaster', 'emergency', 'catastrophe']
            },
            'social-justice': {
                'keywords': ['social progress', 'equality', 'community initiative', 
                           'human rights', 'inclusion', 'diversity success'],
                'exclude_keywords': ['protest', 'violence', 'conflict', 'discrimination']
            },
            'health': {
                'keywords': ['medical breakthrough', 'healthcare innovation', 'wellness', 
                           'medical research', 'treatment success', 'health initiative'],
                'exclude_keywords': ['disease outbreak', 'pandemic', 'health crisis']
            },
            'education': {
                'keywords': ['education access', 'learning innovation', 'student success', 
                           'educational program', 'scholarship', 'digital learning'],
                'exclude_keywords': ['education crisis', 'school closure', 'learning gap']
            }
        }
        
        if category not in category_mapping:
            return []
            
        # Get news from the last 7 days
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Build the query
        query = ' OR '.join(category_mapping[category]['keywords'])
        exclude_query = ' OR '.join(category_mapping[category]['exclude_keywords'])
        
        try:
            # Get news articles
            response = self.api.get_everything(
                q=query,
                language='en',
                from_param=from_date,
                sort_by='relevancy',
                page_size=page_size
            )
            
            # Filter articles
            articles = []
            for article in response['articles']:
                # Skip if title contains negative keywords
                if any(keyword.lower() in article['title'].lower() 
                       for keyword in category_mapping[category]['exclude_keywords']):
                    continue
                    
                # Format article for our template
                formatted_article = {
                    'id': hash(article['url']),  # Simple way to generate an ID
                    'title': article['title'],
                    'excerpt': article['description'] or article['title'],
                    'image': article['urlToImage'] or 'https://via.placeholder.com/400x200?text=No+Image',
                    'date': article['publishedAt'].split('T')[0],
                    'url': article['url']
                }
                articles.append(formatted_article)
                
            return articles
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return [] 