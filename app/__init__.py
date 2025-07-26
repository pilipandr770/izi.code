import os
from flask import Flask
from flask_babel import Babel
from config import config
from app.extensions import db, migrate, babel

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Babel language selector function
    def get_locale():
        from flask import request, session
        # Check if language is set in session
        if 'language' in session:
            return session['language']
        # Otherwise try to guess the language from the user accept header
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'uk'
    
    # Initialize Babel with locale selector
    babel.init_app(app, locale_selector=get_locale)
    
    # Simple translations dictionary
    TRANSLATIONS = {
        'SaaS Shop': {
            'uk': 'SaaS Магазин',
            'ru': 'SaaS Магазин', 
            'de': 'SaaS Shop',
            'en': 'SaaS Shop'
        },
        'Home': {
            'uk': 'Головна',
            'ru': 'Главная',
            'de': 'Startseite',
            'en': 'Home'
        },
        'Shop': {
            'uk': 'Магазин',
            'ru': 'Магазин',
            'de': 'Shop',
            'en': 'Shop'
        },
        'Blog': {
            'uk': 'Блог',
            'ru': 'Блог',
            'de': 'Blog',
            'en': 'Blog'
        },
        'Contact': {
            'uk': 'Контакт',
            'ru': 'Контакт',
            'de': 'Kontakt',
            'en': 'Contact'
        },
        'Your trusted online store for quality products and services.': {
            'uk': 'Ваш надійний інтернет-магазин якісних товарів та послуг.',
            'ru': 'Ваш надежный интернет-магазин качественных товаров и услуг.',
            'de': 'Ihr vertrauenswürdiger Online-Shop für hochwertige Produkte und Dienstleistungen.',
            'en': 'Your trusted online store for quality products and services.'
        },
        'Quick Links': {
            'uk': 'Швидкі посилання',
            'ru': 'Быстрые ссылки',
            'de': 'Schnelle Links',
            'en': 'Quick Links'
        },
        'Follow Us': {
            'uk': 'Слідкуйте за нами',
            'ru': 'Следите за нами',
            'de': 'Folgen Sie uns',
            'en': 'Follow Us'
        },
        'All rights reserved.': {
            'uk': 'Всі права захищені.',
            'ru': 'Все права защищены.',
            'de': 'Alle Rechte vorbehalten.',
            'en': 'All rights reserved.'
        },
        'Shopping Cart': {
            'uk': 'Кошик покупок',
            'ru': 'Корзина покупок',
            'de': 'Warenkorb',
            'en': 'Shopping Cart'
        },
        'Your cart is empty': {
            'uk': 'Ваш кошик порожній',
            'ru': 'Ваша корзина пуста',
            'de': 'Ihr Warenkorb ist leer',
            'en': 'Your cart is empty'
        },
        'Total:': {
            'uk': 'Всього:',
            'ru': 'Итого:',
            'de': 'Gesamt:',
            'en': 'Total:'
        },
        'Checkout': {
            'uk': 'Оформити замовлення',
            'ru': 'Оформить заказ',
            'de': 'Zur Kasse',
            'en': 'Checkout'
        },
        'AI Assistant': {
            'uk': 'AI Асистент',
            'ru': 'AI Ассистент',
            'de': 'AI Assistent',
            'en': 'AI Assistant'
        },
        'Hello! How can I help you today?': {
            'uk': 'Привіт! Як я можу вам допомогти сьогодні?',
            'ru': 'Привет! Как я могу вам помочь сегодня?',
            'de': 'Hallo! Wie kann ich Ihnen heute helfen?',
            'en': 'Hello! How can I help you today?'
        },
        'Type your message...': {
            'uk': 'Введіть ваше повідомлення...',
            'ru': 'Введите ваше сообщение...',
            'de': 'Geben Sie Ihre Nachricht ein...',
            'en': 'Type your message...'
        },
        'Send': {
            'uk': 'Надіслати',
            'ru': 'Отправить',
            'de': 'Senden',
            'en': 'Send'
        },
        'Privacy Policy': {
            'uk': 'Політика конфіденційності',
            'ru': 'Политика конфиденциальности',
            'de': 'Datenschutzerklärung',
            'en': 'Privacy Policy'
        },
        'Terms & Conditions': {
            'uk': 'Умови використання',
            'ru': 'Условия использования',
            'de': 'AGB',
            'en': 'Terms & Conditions'
        },
        'Impressum': {
            'uk': 'Імпресум',
            'ru': 'Импрессум',
            'de': 'Impressum',
            'en': 'Impressum'
        }
    }
    
    # Custom translation function
    def translate(text):
        from flask import session
        current_lang = session.get('language', 'uk')
        if text in TRANSLATIONS and current_lang in TRANSLATIONS[text]:
            return TRANSLATIONS[text][current_lang]
        return text
    
    # Template context processor
    @app.context_processor
    def inject_template_vars():
        from flask import session
        from app.models import SocialLink
        
        # Get social links for all pages
        social_links = SocialLink.query.filter_by(is_active=True).order_by(SocialLink.sort_order).all()
        
        return {
            'language': session.get('language', 'uk'),
            '_': translate,  # Custom translation function
            'social_links': social_links  # Social links for footer
        }
    
    # Import models
    from app import models
    
    # Register blueprints
    from app.routes import main_bp, admin_bp, api_bp
    from app.admin_routes import admin_routes
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(admin_routes, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create upload directory
    upload_dir = os.path.join(app.instance_path, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Register CLI commands
    from app.cli import init_cli_commands
    init_cli_commands(app)
    
    return app
