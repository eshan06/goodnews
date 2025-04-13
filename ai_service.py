import os
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
        
    def summarize_article(self, article_text):
        """Generate a summary of an article using OpenAI GPT model"""
        try:
            if not self.api_key:
                return self._get_mock_summary(article_text)
                
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
                    {"role": "user", "content": f"Please provide a concise summary of this article in 3-4 paragraphs:\n\n{article_text}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return self._get_mock_summary(article_text)
    
    def get_article_title(self, article_text):
        """Extract or generate a title for the article"""
        try:
            if not self.api_key:
                return "Article Analysis"
                
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts or generates titles for news articles."},
                    {"role": "user", "content": f"Please extract or generate a short, catchy title for this article. Response should be just the title, no explanations or quotes:\n\n{article_text[:1000]}"}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip().replace('"', '').replace("'", "")
        except Exception as e:
            print(f"Error generating title: {str(e)}")
            return "Article Analysis"
    
    def chat_about_article(self, article_text, messages):
        """Chat with the AI about the article"""
        try:
            if not self.api_key:
                return self._get_mock_response(article_text, messages)
                
            # Prepare the conversation history
            conversation = [
                {"role": "system", "content": f"You are a helpful assistant answering questions about a news article. Here is the article:\n\n{article_text}\n\nAnswer questions based on this article only. If you don't know the answer from the article, say so."}
            ]
            
            # Add previous messages
            for msg in messages:
                role = "user" if msg.is_user else "assistant"
                conversation.append({"role": role, "content": msg.content})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversation,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return self._get_mock_response(article_text, messages)
    
    def _get_mock_summary(self, article_text):
        """Provide a mock summary when API key is not available"""
        words = article_text.split()
        if len(words) > 100:
            # Take some sentences from beginning, middle, and end
            first_part = ' '.join(words[:50])
            middle_part = ' '.join(words[len(words)//2-25:len(words)//2+25])
            last_part = ' '.join(words[-50:])
            
            return f"Summary (AI key not configured):\n\n{first_part}...\n\n{middle_part}...\n\n{last_part}"
        else:
            return article_text
    
    def _get_mock_response(self, article_text, messages):
        """Provide a mock response when API key is not available"""
        last_message = messages[-1].content if messages else "Tell me about this article"
        return f"I'd be happy to help with '{last_message}', but the OpenAI API key is not configured. Please add your API key to the .env file to enable AI responses." 