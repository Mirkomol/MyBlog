# Blog Platform Configuration

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Pagination
    POSTS_PER_PAGE = 10
    
    # Blog settings
    BLOG_TITLE = os.environ.get('BLOG_TITLE') or 'AGIBLOG'
    BLOG_SUBTITLE = os.environ.get('BLOG_SUBTITLE') or 'Thoughts, stories and ideas'
    BLOG_AUTHOR = os.environ.get('BLOG_AUTHOR') or 'Mirkamol Rahimov'
    
    # AI Generation (Gemini)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or ''


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Always use SQLite - simple like Django!
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'blog.db')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # SQLite database - works in Docker with volume mount at /app/data
    # Falls back to local blog.db if /app/data doesn't exist
    DATA_DIR = '/app/data' if os.path.exists('/app/data') else basedir
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DATA_DIR, 'blog.db')
    
    # Security settings for production
    SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
