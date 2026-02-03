# Flask Application Factory

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config
import os
import markdown

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.auth import auth_bp
    from app.blog import blog_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    
    # Context processor for templates
    @app.context_processor
    def inject_settings():
        return {
            'blog_title': app.config['BLOG_TITLE'],
            'blog_subtitle': app.config['BLOG_SUBTITLE'],
            'blog_author': app.config['BLOG_AUTHOR']
            'blog_author': app.config['BLOG_AUTHOR']
        }
    
    # Register Markdown filter
    @app.template_filter('markdown')
    def markdown_filter(content):
        if not content:
            return ""
        return markdown.markdown(content, extensions=['fenced_code', 'tables'])
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        from app.models import User
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this!
            db.session.add(admin)
            db.session.commit()
    
    return app
