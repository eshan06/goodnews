# GoodNews

A web application that curates and delivers positive news content with AI-powered article analysis.
Try the demo: https://goodnews-lac.vercel.app/

## Project Overview

GoodNews is designed to counter the negative bias in traditional news media by focusing exclusively on uplifting, positive news stories. The application aggregates content from various news sources, categorizes it, and presents it in an accessible format. It features an integrated AI assistant that can analyze articles, generate summaries, and engage in meaningful conversations about the content.

## Key Features

- **Curated News Feed**: Categorized positive news content from multiple reliable sources
- **AI Article Analysis**: Intelligent summarization of article content
- **Interactive Chat**: Conversational AI that answers questions about the articles
- **User Submissions**: Community contribution through story submissions
- **Comment System**: User engagement through comment threads on stories
- **Category Filtering**: Browse news by topics like Technology, Science, Health, and Education

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML, CSS (Tailwind CSS for styling), JavaScript
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **AI Integration**: OpenAI API for intelligent article analysis and chat functionality
- **News Aggregation**: Integration with multiple news APIs (NewsAPI, Guardian, NYT)
- **URL Scraping**: Beautiful Soup for content extraction
- **Forms**: WTForms for form validation and processing
- **Authentication**: User registration and login functionality

## Problems Solved

1. **News Negativity Bias**: Counters the overwhelming focus on negative events in mainstream media
2. **Information Overload**: Curates relevant positive content to reduce information fatigue
3. **Context Understanding**: Uses AI to help readers better understand article content through summaries and interactive Q&A
4. **Digital Accessibility**: Provides a clean, responsive interface accessible across devices
5. **Community Engagement**: Enables users to contribute their own positive stories and engage in discussions

## How It Relates to the Theme

GoodNews tackles the problem of negative news bias by creating a platform exclusively dedicated to positive stories. By highlighting achievements, innovations, and uplifting events, it aims to provide a more balanced perspective of world events and foster a sense of hope and possibility. The AI assistant further enhances this mission by helping users extract deeper insights from the content.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/goodnews.git
   cd goodnews
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On MacOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   OPENAI_API_KEY=your_openai_api_key
   NEWS_API_KEY=your_newsapi_key
   GUARDIAN_API_KEY=your_guardian_api_key
   NYT_API_KEY=your_nyt_api_key
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```

7. Access the application at http://localhost:5000

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
