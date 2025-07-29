import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration with PostgreSQL URL processing
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///shop.db'
    fallback_database_url = os.environ.get('FALLBACK_DATABASE_URL') or 'sqlite:///app.db'
    
    # Fix PostgreSQL URL format for SQLAlchemy 2.0+
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PostgreSQL schema support
    DB_SCHEMA = os.environ.get('DB_SCHEMA', 'public')
    
    # Connection timeout in seconds
    DATABASE_CONNECT_TIMEOUT = int(os.environ.get('DATABASE_CONNECT_TIMEOUT', 5))
    
    # SQLAlchemy engine options with improved connection handling
    if 'postgresql://' in database_url:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': DATABASE_CONNECT_TIMEOUT,
            'connect_args': {
                'options': f'-csearch_path={os.environ.get("DB_SCHEMA", "public")}',
                'connect_timeout': DATABASE_CONNECT_TIMEOUT
            }
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {}
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stripe configuration
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_ASSISTANT_ID = os.environ.get('OPENAI_ASSISTANT_ID')
    
    # Languages configuration
    LANGUAGES = {
        'uk': 'Українська',
        'ru': 'Русский', 
        'de': 'Deutsch',
        'en': 'English'
    }
    BABEL_DEFAULT_LOCALE = 'uk'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Admin configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
