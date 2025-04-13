from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, URLField
from wtforms.validators import DataRequired, Email, Length, Optional

class SubmissionForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=200)
    ])
    content = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=50, max=5000)
    ])
    category = SelectField('Category', choices=[
        ('climate', 'Climate & Sustainability'),
        ('social-justice', 'Social Justice & Equity'),
        ('health', 'Health & Well-being'),
        ('education', 'Education & Access')
    ], validators=[DataRequired()])
    author_name = StringField('Your Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    author_email = StringField('Your Email', validators=[
        DataRequired(),
        Email()
    ])
    image_url = URLField('Image URL (optional)', validators=[
        Optional(),
        Length(max=500)
    ])

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    author_name = StringField('Your Name', validators=[DataRequired(), Length(max=100)]) 