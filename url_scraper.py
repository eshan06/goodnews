import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

class URLScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_article(self, url):
        """Extract article content from a URL"""
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return None, "Invalid URL format"
            
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to get the title
            title = self._extract_title(soup)
            
            # Try to get the main content
            content = self._extract_content(soup)
            
            if not content:
                return None, "Could not extract article content from this URL"
            
            return {
                'title': title,
                'content': content,
                'url': url
            }, None
            
        except requests.exceptions.RequestException as e:
            return None, f"Error fetching URL: {str(e)}"
        except Exception as e:
            return None, f"Error processing article: {str(e)}"
    
    def _extract_title(self, soup):
        """Extract the article title"""
        # First try meta tags
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content']
        
        # Then try the page title
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # Finally try h1 tags
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Article"
    
    def _extract_content(self, soup):
        """Extract the main content of the article"""
        # Remove script, style, and nav elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try to find article content using common selectors
        article_selectors = [
            'article', 
            '[itemprop="articleBody"]',
            '.post-content',
            '.article-content',
            '.entry-content',
            '.story-content',
            '.story-body',
            '#article-body',
            '.content-body',
            '.article_body'
        ]
        
        # Try each selector
        for selector in article_selectors:
            article = soup.select_one(selector)
            if article:
                return self._clean_content(article.get_text())
        
        # If no specific article container, try to extract paragraphs from the main body
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            # Filter out very short paragraphs or likely navigation/footer text
            if len(text) > 50 and not re.search(r'copyright|contact us|privacy policy', text, re.I):
                paragraphs.append(text)
        
        if paragraphs:
            return '\n\n'.join(paragraphs)
        
        # As a last resort, just get all text
        return self._clean_content(soup.get_text())
    
    def _clean_content(self, text):
        """Clean up the extracted content"""
        # Remove excess whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove repeated newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip() 