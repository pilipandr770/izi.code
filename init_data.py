#!/usr/bin/env python3
"""
Initialize basic data for the IZI.SOFT shop
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db
from app.models import User, Category, Product, BlogPost, SocialLink, HomePageBlock

def init_basic_data():
    app = create_app()
    with app.app_context():
        print('Initializing basic data for IZI.SOFT...')
        
        try:
            # Create admin user
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@izi-soft.com',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                print('✅ Admin user created')
            else:
                print('ℹ️ Admin user already exists')
            
            # Create categories
            categories_data = [
                {
                    'name_uk': 'AI рішення',
                    'name_ru': 'AI решения', 
                    'name_de': 'AI Lösungen',
                    'name_en': 'AI Solutions',
                    'description_uk': 'Готові рішення на базі штучного інтелекту для вашого бізнесу',
                    'description_ru': 'Готовые решения на базе искусственного интеллекта для вашего бизнеса',
                    'description_de': 'Fertige KI-Lösungen für Ihr Unternehmen',
                    'description_en': 'Ready-made AI solutions for your business',
                    'slug': 'ai-solutions'
                },
                {
                    'name_uk': 'Веб-розробка',
                    'name_ru': 'Веб-разработка',
                    'name_de': 'Webentwicklung', 
                    'name_en': 'Web Development',
                    'description_uk': 'Індивідуальна розробка веб-додатків та сайтів',
                    'description_ru': 'Индивидуальная разработка веб-приложений и сайтов',
                    'description_de': 'Individuelle Entwicklung von Webanwendungen und Websites',
                    'description_en': 'Custom web application and website development',
                    'slug': 'web-development'
                }
            ]
            
            for cat_data in categories_data:
                if not Category.query.filter_by(slug=cat_data['slug']).first():
                    category = Category(**cat_data)
                    db.session.add(category)
                    print(f'✅ Category "{cat_data["name_en"]}" created')
            
            # Create products
            ai_category = Category.query.filter_by(slug='ai-solutions').first()
            web_category = Category.query.filter_by(slug='web-development').first()
            
            products_data = [
                {
                    'name_uk': 'AI Чатбот для сайту',
                    'name_ru': 'AI Чатбот для сайта',
                    'name_de': 'AI Chatbot für Website',
                    'name_en': 'AI Website Chatbot',
                    'description_uk': 'Розумний чатбот що відповідає на питання клієнтів 24/7',
                    'description_ru': 'Умный чатбот, отвечающий на вопросы клиентов 24/7',
                    'description_de': 'Intelligenter Chatbot für 24/7 Kundensupport',
                    'description_en': 'Smart chatbot for 24/7 customer support',
                    'price': 299.0,
                    'currency': 'EUR',
                    'category_id': ai_category.id if ai_category else 1,
                    'slug': 'ai-chatbot'
                },
                {
                    'name_uk': 'CRM система',
                    'name_ru': 'CRM система',
                    'name_de': 'CRM System',
                    'name_en': 'CRM System',
                    'description_uk': 'Система управління клієнтами з AI аналітикою',
                    'description_ru': 'Система управления клиентами с AI аналитикой',
                    'description_de': 'Kundenverwaltungssystem mit KI-Analytics',
                    'description_en': 'Customer management system with AI analytics',
                    'price': 599.0,
                    'currency': 'EUR',
                    'category_id': ai_category.id if ai_category else 1,
                    'slug': 'crm-system'
                },
                {
                    'name_uk': 'Індивідуальний сайт',
                    'name_ru': 'Индивидуальный сайт',
                    'name_de': 'Individuelle Website',
                    'name_en': 'Custom Website',
                    'description_uk': 'Розробка унікального веб-сайту під ваші потреби',
                    'description_ru': 'Разработка уникального веб-сайта под ваши потребности',
                    'description_de': 'Entwicklung einer einzigartigen Website nach Ihren Bedürfnissen',
                    'description_en': 'Development of a unique website tailored to your needs',
                    'price': 1299.0,
                    'currency': 'EUR',
                    'category_id': web_category.id if web_category else 2,
                    'slug': 'custom-website'
                }
            ]
            
            for prod_data in products_data:
                if not Product.query.filter_by(slug=prod_data['slug']).first():
                    product = Product(**prod_data)
                    db.session.add(product)
                    print(f'✅ Product "{prod_data["name_en"]}" created')
            
            # Create social links
            social_links_data = [
                {
                    'name': 'Telegram',
                    'url': 'https://t.me/izi_soft',
                    'icon_class': 'fab fa-telegram-plane',
                    'sort_order': 1
                },
                {
                    'name': 'Email',
                    'url': 'mailto:info@izi-soft.com',
                    'icon_class': 'fas fa-envelope',
                    'sort_order': 2
                }
            ]
            
            for social_data in social_links_data:
                if not SocialLink.query.filter_by(name=social_data['name']).first():
                    social_link = SocialLink(**social_data)
                    db.session.add(social_link)
                    print(f'✅ Social link "{social_data["name"]}" created')
            
            # Commit all changes
            db.session.commit()
            print('✅ All basic data initialized successfully!')
            
        except Exception as e:
            print(f'❌ Error initializing data: {e}')
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    init_basic_data()
