from app import app, db, Submission, Comment

with app.app_context():
    # Delete all comments for the test story
    Comment.query.filter_by(story_id=1).delete()
    
    # Delete the test story
    Submission.query.filter_by(id=1).delete()
    
    # Commit changes
    db.session.commit()
    
    print("Test story and its comments deleted") 