# GoodNews - Positive News Platform

A Python-based news platform focused on sharing positive developments in four key areas:
- 🌍 Climate & Sustainability
- ⚖️ Social Justice & Equity
- 🏥 Health & Well-being
- 📚 Education & Access

## Features

- Clean, modern UI with responsive design
- Category-based news organization
- Featured articles section
- Dynamic category pages
- Mobile-friendly layout

## Tech Stack

- Python 3.x
- Flask
- Tailwind CSS (via CDN)

## Getting Started

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
python app.py
```

5. Open [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates
  - `base.html` - Base template with common layout
  - `home.html` - Home page template
  - `category.html` - Category page template
- `requirements.txt` - Python dependencies

## License

This project is licensed under the MIT License. 