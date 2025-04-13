from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, URLField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email address is already registered.')

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
    name = StringField('Your Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    email = StringField('Your Email', validators=[
        DataRequired(),
        Email()
    ])
    image_url = URLField('Image URL (optional)', validators=[
        Optional(),
        Length(max=500)
    ])

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])

class ArticleAnalysisForm(FlaskForm):
    article_url = URLField('Enter Article URL', validators=[DataRequired()])
    submit = SubmitField('Analyze Article')
    
    def validate(self, extra_validators=None):
        return super().validate(extra_validators)

class ChatMessageForm(FlaskForm):
    message = TextAreaField('Your Question', validators=[DataRequired()])
    submit = SubmitField('Send') 