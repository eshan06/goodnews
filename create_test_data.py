from app import app, db, User, Submission

with app.app_context():
    # Check if test user exists
    existing_user = User.query.filter_by(email='test@example.com').first()
    if not existing_user:
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        print("Created test user")
    else:
        print("Test user already exists")
    
    # Create a test submission
    submission = Submission(
        title='Test Story',
        content='This is a test story with plenty of content. It provides good news about climate change initiatives.',
        category='climate',
        name='Test User',
        email='test@example.com'
    )
    db.session.add(submission)
    
    # Commit changes
    db.session.commit()
    
    print("Created test submission") 