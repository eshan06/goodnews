import os
import openai
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables!")
        else:
            openai.api_key = self.api_key

    def summarize_article(self, article_text):
        """Generate a summary of an article using OpenAI GPT model"""
        try:
            if not self.api_key:
                return self._get_mock_summary(article_text)
                
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specializing in summarizing news articles."},
                    {"role": "user", "content": (
                        "Please provide a concise summary of the following news article in 3-4 paragraphs. "
                        "The summary should be in your own words, avoid repeating long excerpts, and do not include any HTML or extraneous formatting:\n\n"
                        f"{article_text}"
                    )}
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
                
            response = openai.ChatCompletion.create(
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
                
            conversation = [
                {
                    "role": "system", 
                    "content": (
                        "You are a knowledgeable and objective assistant specialized in discussing news articles. "
                        "Your responses should be clear, concise, and based solely on the provided article content. "
                        "If a question goes beyond the details in the article, state that the information isn't available instead of guessing. "
                        "Ensure your tone is neutral and factual."
                    )
                },
            ]
            
            for msg in messages:
                role = "user" if msg.is_user else "assistant"
                conversation.append({"role": role, "content": msg.content})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation,
                max_tokens=500,
                temperature=0.5,
                top_p=1.0,
                frequency_penalty=0,
                presence_penalty=0 
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return self._get_mock_response(article_text, messages)
    
    def _get_mock_summary(self, article_text):
        """Provide a mock summary when API key is not available"""
        words = article_text.split()
        if len(words) > 100:
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
