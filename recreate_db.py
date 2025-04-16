from api.app import app, db, User, Submission, Comment
from datetime import datetime

with app.app_context():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    
    # Create a test user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    
    # Create a test submission
    submission = Submission(
        title='Test Story',
        content='This is a test story with plenty of content. It provides good news about climate change initiatives that are helping to reduce global warming.',
        category='climate',
        name='Test User',
        email='test@example.com'
    )
    db.session.add(submission)
    
    # Create a test comment
    comment = Comment(
        content='Great story! Thanks for sharing this positive news.',
        name='Comment User',
        story_id=1
    )
    db.session.add(comment)
    
    # Commit changes
    db.session.commit()
    
    print("Database recreated with test data") 