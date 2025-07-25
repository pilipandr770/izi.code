"""
Скрипт для пересоздания базы данных с правильной схемой
"""
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Category, Product, BlogPost, HomePageBlock, SocialLink
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone


def recreate_database():
    """Пересоздаем базу данных"""
    app = create_app()
    
    with app.app_context():
        # Удаляем все таблицы
        print("Удаляем старые таблицы...")
        db.drop_all()
        
        # Создаем новые таблицы
        print("Создаем новые таблицы...")
        db.create_all()
        
        # Создаем администраторов
        print("Создаем администраторов...")
        admin1 = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin1)
        
        admin2 = User(
            username='test',
            email='test@admin.com', 
            password_hash=generate_password_hash('test'),
            is_admin=True
        )
        db.session.add(admin2)
        
        # Создаем категории
        print("Создаем категории...")
        categories = [
            Category(
                name_uk='Електроніка',
                name_ru='Электроника',
                name_de='Elektronik',
                description_uk='Сучасні електронні пристрої',
                description_ru='Современные электронные устройства',
                description_de='Moderne elektronische Geräte',
                slug='electronics',
                is_active=True,
                sort_order=1
            ),
            Category(
                name_uk='Одяг',
                name_ru='Одежда',
                name_de='Kleidung',
                description_uk='Модний одяг для всіх',
                description_ru='Модная одежда для всех',
                description_de='Modische Kleidung für alle',
                slug='clothing',
                is_active=True,
                sort_order=2
            ),
            Category(
                name_uk='Дім і сад',
                name_ru='Дом и сад',
                name_de='Haus und Garten',
                description_uk='Товари для дому та саду',
                description_ru='Товары для дома и сада',
                description_de='Produkte für Haus und Garten',
                slug='home-garden',
                is_active=True,
                sort_order=3
            )
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        db.session.commit()
        
        # Получаем созданные категории
        electronics = Category.query.filter_by(slug='electronics').first()
        clothing = Category.query.filter_by(slug='clothing').first()
        
        # Создаем товары
        print("Создаем товары...")
        products = [
            Product(
                name_uk='iPhone 15 Pro',
                name_ru='iPhone 15 Pro',
                name_de='iPhone 15 Pro',
                description_uk='Найновіший iPhone з передовими технологіями та потужним чіпом A17 Pro',
                description_ru='Новейший iPhone с передовыми технологиями и мощным чипом A17 Pro',
                description_de='Das neueste iPhone mit fortschrittlichen Technologien und leistungsstarkem A17 Pro Chip',
                price=1199.99,
                currency='USD',
                category_id=electronics.id,
                slug='iphone-15-pro',
                is_active=True,
                sort_order=1
            ),
            Product(
                name_uk='Samsung Galaxy S24',
                name_ru='Samsung Galaxy S24',
                name_de='Samsung Galaxy S24',
                description_uk='Флагманський смартфон Samsung з AI-функціями',
                description_ru='Флагманский смартфон Samsung с AI-функциями',
                description_de='Samsung Flaggschiff-Smartphone mit AI-Funktionen',
                price=899.99,
                currency='USD',
                category_id=electronics.id,
                slug='samsung-galaxy-s24',
                is_active=True,
                sort_order=2
            ),
            Product(
                name_uk='Стильна куртка',
                name_ru='Стильная куртка',
                name_de='Stylische Jacke',
                description_uk='Модна куртка для прохолодної погоди',
                description_ru='Модная куртка для прохладной погоды',
                description_de='Modische Jacke für kühles Wetter',
                price=89.99,
                currency='EUR',
                category_id=clothing.id,
                slug='stylish-jacket',
                is_active=True,
                sort_order=1
            )
        ]
        
        for product in products:
            db.session.add(product)
        
        # Создаем блог-посты
        print("Создаем блог-посты...")
        blog_posts = [
            BlogPost(
                title_uk='Привіт, світ!',
                title_ru='Привет, мир!',
                title_de='Hallo, Welt!',
                content_uk='Це наш перший пост у блозі. Ласкаво просимо до нашого онлайн-магазину!',
                content_ru='Это наш первый пост в блоге. Добро пожаловать в наш интернет-магазин!',
                content_de='Das ist unser erster Blog-Post. Willkommen in unserem Online-Shop!',
                slug='hello-world',
                is_published=True,
                author_id=admin1.id
            ),
            BlogPost(
                title_uk='Топ-5 технологічних трендів 2025',
                title_ru='Топ-5 технологических трендов 2025',
                title_de='Top 5 Technologie-Trends 2025',
                content_uk='Розглядаємо найгарячіші технологічні тренди цього року...',
                content_ru='Рассматриваем самые горячие технологические тренды этого года...',
                content_de='Wir betrachten die heißesten Technologie-Trends dieses Jahres...',
                slug='tech-trends-2025',
                is_published=True,
                author_id=admin1.id
            )
        ]
        
        for post in blog_posts:
            db.session.add(post)
        
        # Создаем блоки главной страницы
        print("Создаем блоки главной страницы...")
        homepage_blocks = [
            HomePageBlock(
                title_uk='Наші продукти',
                title_ru='Наши продукты',
                title_de='Unsere Produkte',
                block_type='shop',
                css_class='bg-light py-5',
                is_active=True,
                sort_order=1
            ),
            HomePageBlock(
                title_uk='Останні новини',
                title_ru='Последние новости',
                title_de='Neueste Nachrichten',
                block_type='blog',
                css_class='bg-white py-5',
                is_active=True,
                sort_order=2
            )
        ]
        
        for block in homepage_blocks:
            db.session.add(block)
        
        # Создаем социальные ссылки
        print("Создаем социальные ссылки...")
        social_links = [
            SocialLink(
                platform='facebook',
                url='https://facebook.com/yourstore',
                icon_class='fab fa-facebook-f',
                is_active=True,
                sort_order=1
            ),
            SocialLink(
                platform='instagram',
                url='https://instagram.com/yourstore',
                icon_class='fab fa-instagram',
                is_active=True,
                sort_order=2
            ),
            SocialLink(
                platform='telegram',
                url='https://t.me/yourstore',
                icon_class='fab fa-telegram-plane',
                is_active=True,
                sort_order=3
            )
        ]
        
        for link in social_links:
            db.session.add(link)
        
        # Сохраняем все изменения
        db.session.commit()
        
        print("✅ База данных успешно пересоздана!")
        print("🔐 Администраторы:")
        print("   - admin / admin123")
        print("   - test / test")
        print(f"📦 Создано {len(categories)} категорий")
        print(f"🛍️ Создано {len(products)} товаров")
        print(f"📝 Создано {len(blog_posts)} блог-постов")
        print(f"🏠 Создано {len(homepage_blocks)} блоков главной страницы")
        print(f"📱 Создано {len(social_links)} социальных ссылок")


if __name__ == '__main__':
    recreate_database()
