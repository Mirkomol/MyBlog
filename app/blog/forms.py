# Blog Forms

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    """Form for creating and editing blog posts."""
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    excerpt = TextAreaField('Excerpt', validators=[
        Length(max=500, message='Excerpt must be less than 500 characters')
    ], render_kw={'rows': 3, 'placeholder': 'Brief description of your post...'})
    content = TextAreaField('Content', render_kw={'rows': 20})  # No required attr - EasyMDE handles validation
    cover_image = FileField('Cover Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    tags = StringField('Tags', render_kw={
        'placeholder': 'Comma-separated tags (e.g., python, web, tutorial)'
    })
    is_published = BooleanField('Publish')
    is_featured = BooleanField('Featured Post')
    submit = SubmitField('Save Post')


class SearchForm(FlaskForm):
    """Search form."""
    query = StringField('Search', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ], render_kw={'placeholder': 'Search posts...'})
    submit = SubmitField('Search')


class AboutForm(FlaskForm):
    """Form for editing the About page."""
    about_title = StringField('Page Title', validators=[
        Length(max=200)
    ], render_kw={'placeholder': 'Welcome to my blog'})
    about_intro = TextAreaField('Introduction', validators=[
        Length(max=500)
    ], render_kw={'rows': 3, 'placeholder': 'A brief introduction about yourself...'})
    about_content = TextAreaField('Main Content (Markdown supported)', render_kw={
        'rows': 10, 'placeholder': 'Tell your story...'
    })
    twitter_url = StringField('Twitter/X URL', render_kw={'placeholder': 'https://twitter.com/yourhandle'})
    github_url = StringField('GitHub URL', render_kw={'placeholder': 'https://github.com/yourusername'})
    linkedin_url = StringField('LinkedIn URL', render_kw={'placeholder': 'https://linkedin.com/in/yourprofile'})
    submit = SubmitField('Save Changes')

