import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import hashlib

load_dotenv()

class NewsService:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.guardian_api_key = os.getenv('GUARDIAN_API_KEY')
        self.nyt_api_key = os.getenv('NYT_API_KEY')
        
    def get_positive_news(self, category, page_size=9):
        try:
            # Try NewsAPI first
            articles = self._fetch_from_newsapi(category, page_size)
            if articles and len(articles) >= page_size:
                return articles
                
            # If NewsAPI fails or doesn't return enough articles, try The Guardian
            guardian_articles = self._fetch_from_guardian(category, page_size)
            if guardian_articles:
                if articles:
                    articles.extend(guardian_articles)
                else:
                    articles = guardian_articles
                    
            # If we still don't have enough articles, try NYT
            if len(articles) < page_size:
                nyt_articles = self._fetch_from_nyt(category, page_size)
                if nyt_articles:
                    articles.extend(nyt_articles)
                    
            # Remove duplicates and ensure we have the right number of articles
            articles = self._remove_duplicates(articles)
            if len(articles) > page_size:
                articles = random.sample(articles, page_size)
                
            return articles
            
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return self._get_fallback_articles(category, page_size)
    
    def _fetch_from_newsapi(self, category, page_size):
        if not self.news_api_key:
            return []
            
        # Map our categories to NewsAPI categories and keywords
        category_map = {
            'climate': {
                'category': 'environment',
                'keywords': ['renewable energy', 'sustainability', 'environmental progress', 
                           'climate solution', 'green technology', 'conservation success',
                           'clean energy', 'carbon reduction', 'eco-friendly']
            },
            'social-justice': {
                'category': 'politics',
                'keywords': ['social progress', 'equality', 'community initiative', 
                           'human rights', 'inclusion', 'diversity success',
                           'social change', 'community development', 'empowerment']
            },
            'health': {
                'category': 'health',
                'keywords': ['medical breakthrough', 'healthcare innovation', 'wellness', 
                           'medical research', 'treatment success', 'health initiative',
                           'public health', 'medical advancement', 'healthcare access']
            },
            'education': {
                'category': 'education',
                'keywords': ['education access', 'learning innovation', 'student success', 
                           'educational program', 'scholarship', 'digital learning',
                           'educational technology', 'student achievement', 'learning initiative']
            }
        }
        
        category_info = category_map.get(category, {'category': 'general', 'keywords': []})
        
        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Build the query with category-specific keywords
        query = f"({category}) AND ({' OR '.join(category_info['keywords'])}) AND (positive OR good OR progress OR success OR breakthrough)"
        
        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'sortBy': 'relevancy',
            'language': 'en',
            'pageSize': page_size * 2,
            'apiKey': self.news_api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            return self._process_articles(articles, page_size)
        return []
    
    def _fetch_from_guardian(self, category, page_size):
        if not self.guardian_api_key:
            return []
            
        # Map our categories to Guardian sections and keywords
        category_map = {
            'climate': {
                'section': 'environment',
                'keywords': ['climate change', 'environment', 'sustainability', 'renewable energy']
            },
            'social-justice': {
                'section': 'society',
                'keywords': ['social justice', 'equality', 'community', 'human rights']
            },
            'health': {
                'section': 'health',
                'keywords': ['health', 'medicine', 'wellness', 'healthcare']
            },
            'education': {
                'section': 'education',
                'keywords': ['education', 'schools', 'learning', 'students']
            }
        }
        
        category_info = category_map.get(category, {'section': 'world', 'keywords': []})
        
        url = f"https://content.guardianapis.com/search"
        params = {
            'section': category_info['section'],
            'q': f"({' OR '.join(category_info['keywords'])}) AND (positive OR good OR progress OR success)",
            'show-fields': 'thumbnail,trailText',
            'page-size': page_size * 2,
            'api-key': self.guardian_api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            articles = response.json().get('response', {}).get('results', [])
            return self._process_guardian_articles(articles, page_size)
        return []
    
    def _fetch_from_nyt(self, category, page_size):
        if not self.nyt_api_key:
            return []
            
        # Map our categories to NYT sections and keywords
        category_map = {
            'climate': {
                'section': 'climate',
                'keywords': ['climate', 'environment', 'sustainability', 'energy']
            },
            'social-justice': {
                'section': 'politics',
                'keywords': ['social justice', 'equality', 'community', 'rights']
            },
            'health': {
                'section': 'health',
                'keywords': ['health', 'medicine', 'wellness', 'healthcare']
            },
            'education': {
                'section': 'education',
                'keywords': ['education', 'schools', 'learning', 'students']
            }
        }
        
        category_info = category_map.get(category, {'section': 'world', 'keywords': []})
        
        url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json"
        params = {
            'q': f"({' OR '.join(category_info['keywords'])}) AND (positive OR good OR progress OR success)",
            'fq': f'section_name:("{category_info["section"]}")',
            'sort': 'newest',
            'page-size': page_size * 2,
            'api-key': self.nyt_api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            articles = response.json().get('response', {}).get('docs', [])
            return self._process_nyt_articles(articles, page_size)
        return []
    
    def _process_articles(self, articles, page_size):
        processed = []
        for article in articles:
            if not article.get('title') or not article.get('description'):
                continue
                
            # Generate a unique ID based on the article URL
            article_id = hashlib.md5(article.get('url', '').encode()).hexdigest()
            
            processed.append({
                'id': article_id,
                'title': article.get('title'),
                'excerpt': article.get('description'),
                'image': article.get('urlToImage', ''),
                'date': article.get('publishedAt', ''),
                'url': article.get('url', '')
            })
            
            if len(processed) >= page_size:
                break
                
        return processed
    
    def _process_guardian_articles(self, articles, page_size):
        processed = []
        for article in articles:
            fields = article.get('fields', {})
            
            # Generate a unique ID based on the article URL
            article_id = hashlib.md5(article.get('webUrl', '').encode()).hexdigest()
            
            processed.append({
                'id': article_id,
                'title': article.get('webTitle'),
                'excerpt': fields.get('trailText', ''),
                'image': fields.get('thumbnail', ''),
                'date': article.get('webPublicationDate', ''),
                'url': article.get('webUrl', '')
            })
            
            if len(processed) >= page_size:
                break
                
        return processed
    
    def _process_nyt_articles(self, articles, page_size):
        processed = []
        for article in articles:
            multimedia = article.get('multimedia', [])
            image_url = ''
            if multimedia:
                image_url = f"https://www.nytimes.com/{multimedia[0].get('url', '')}"
            
            # Generate a unique ID based on the article URL
            article_id = hashlib.md5(article.get('web_url', '').encode()).hexdigest()
            
            processed.append({
                'id': article_id,
                'title': article.get('headline', {}).get('main'),
                'excerpt': article.get('snippet', ''),
                'image': image_url,
                'date': article.get('pub_date', ''),
                'url': article.get('web_url', '')
            })
            
            if len(processed) >= page_size:
                break
                
        return processed
    
    def _remove_duplicates(self, articles):
        seen_ids = set()
        unique_articles = []
        
        for article in articles:
            if article['id'] not in seen_ids:
                seen_ids.add(article['id'])
                unique_articles.append(article)
                
        return unique_articles
    
    def _get_fallback_articles(self, category, page_size):
        # Fallback to a simple web scraping approach if APIs fail
        # This is a placeholder - you would need to implement actual web scraping
        return [] 