#!/usr/bin/env python3
"""
Populate initial data for categories and products with Russian translations
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db

def add_sample_data():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Adding sample data to schema: {schema_name}')
        
        # Sample categories with multilingual content
        categories_data = [
            {
                'name': 'Web Development',
                'slug': 'web-development', 
                'description': 'Professional web development services',
                'name_uk': 'Веб-розробка',
                'name_ru': 'Веб-разработка',
                'name_de': 'Webentwicklung',
                'name_en': 'Web Development',
                'description_uk': 'Професійні послуги веб-розробки',
                'description_ru': 'Профессиональные услуги веб-разработки',
                'description_de': 'Professionelle Webentwicklungsdienstleistungen',
                'description_en': 'Professional web development services',
                'is_active': True,
                'sort_order': 1
            },
            {
                'name': 'Mobile Apps',
                'slug': 'mobile-apps',
                'description': 'Native and cross-platform mobile applications',
                'name_uk': 'Мобільні додатки',
                'name_ru': 'Мобильные приложения', 
                'name_de': 'Mobile Apps',
                'name_en': 'Mobile Apps',
                'description_uk': 'Нативні та кросплатформенні мобільні додатки',
                'description_ru': 'Нативные и кроссплатформенные мобильные приложения',
                'description_de': 'Native und plattformübergreifende mobile Anwendungen',
                'description_en': 'Native and cross-platform mobile applications',
                'is_active': True,
                'sort_order': 2
            },
            {
                'name': 'AI Solutions',
                'slug': 'ai-solutions',
                'description': 'Artificial Intelligence and Machine Learning solutions',
                'name_uk': 'AI рішення',
                'name_ru': 'AI решения',
                'name_de': 'KI-Lösungen', 
                'name_en': 'AI Solutions',
                'description_uk': 'Рішення штучного інтелекту та машинного навчання',
                'description_ru': 'Решения искусственного интеллекта и машинного обучения',
                'description_de': 'Künstliche Intelligenz und Machine Learning Lösungen',
                'description_en': 'Artificial Intelligence and Machine Learning solutions',
                'is_active': True,
                'sort_order': 3
            }
        ]
        
        try:
            # Insert categories
            for cat_data in categories_data:
                # Check if category already exists
                check_query = f"""
                SELECT id FROM "{schema_name}".categories WHERE slug = :slug
                """
                with db.engine.connect() as conn:
                    result = conn.execute(db.text(check_query), {"slug": cat_data['slug']})
                    existing = result.fetchone()
                    
                    if not existing:
                        insert_query = f"""
                        INSERT INTO "{schema_name}".categories 
                        (name, slug, description, name_uk, name_ru, name_de, name_en, 
                         description_uk, description_ru, description_de, description_en, 
                         is_active, sort_order)
                        VALUES 
                        (:name, :slug, :description, :name_uk, :name_ru, :name_de, :name_en,
                         :description_uk, :description_ru, :description_de, :description_en,
                         :is_active, :sort_order)
                        """
                        conn.execute(db.text(insert_query), cat_data)
                        conn.commit()
                        print(f"✅ Added category: {cat_data['name']}")
                    else:
                        print(f"ℹ️ Category already exists: {cat_data['name']}")
            
            # Now add sample products
            products_data = [
                {
                    'name': 'E-commerce Website',
                    'slug': 'ecommerce-website',
                    'description': 'Full-featured online store with payment integration',
                    'price': 2999.99,
                    'currency': 'EUR',
                    'stock': 1,
                    'is_active': True,
                    'category_slug': 'web-development',
                    'name_uk': 'Інтернет-магазин',
                    'name_ru': 'Интернет-магазин',
                    'name_de': 'E-Commerce-Website',
                    'name_en': 'E-commerce Website',
                    'description_uk': 'Повнофункціональний інтернет-магазин з інтеграцією платежів',
                    'description_ru': 'Полнофункциональный интернет-магазин с интеграцией платежей',
                    'description_de': 'Vollwertiger Online-Shop mit Zahlungsintegration',
                    'description_en': 'Full-featured online store with payment integration',
                    'sort_order': 1
                },
                {
                    'name': 'iOS Mobile App',
                    'slug': 'ios-mobile-app',
                    'description': 'Native iOS application development',
                    'price': 4999.99,
                    'currency': 'EUR',
                    'stock': 1,
                    'is_active': True,
                    'category_slug': 'mobile-apps',
                    'name_uk': 'iOS мобільний додаток',
                    'name_ru': 'iOS мобильное приложение',
                    'name_de': 'iOS Mobile App',
                    'name_en': 'iOS Mobile App',
                    'description_uk': 'Розробка нативного iOS додатку',
                    'description_ru': 'Разработка нативного iOS приложения',
                    'description_de': 'Native iOS-Anwendungsentwicklung',
                    'description_en': 'Native iOS application development',
                    'sort_order': 1
                },
                {
                    'name': 'AI Chatbot',
                    'slug': 'ai-chatbot',
                    'description': 'Intelligent chatbot with natural language processing',
                    'price': 1999.99,
                    'currency': 'EUR',
                    'stock': 1,
                    'is_active': True,
                    'category_slug': 'ai-solutions',
                    'name_uk': 'AI чатбот',
                    'name_ru': 'AI чатбот',
                    'name_de': 'KI-Chatbot',
                    'name_en': 'AI Chatbot',
                    'description_uk': 'Інтелектуальний чатбот з обробкою природної мови',
                    'description_ru': 'Интеллектуальный чатбот с обработкой естественного языка',
                    'description_de': 'Intelligenter Chatbot mit natürlicher Sprachverarbeitung',
                    'description_en': 'Intelligent chatbot with natural language processing',
                    'sort_order': 1
                }
            ]
            
            for prod_data in products_data:
                # Get category ID
                cat_query = f"""
                SELECT id FROM "{schema_name}".categories WHERE slug = :slug
                """
                with db.engine.connect() as conn:
                    result = conn.execute(db.text(cat_query), {"slug": prod_data['category_slug']})
                    category = result.fetchone()
                    
                    if category:
                        category_id = category[0]
                        
                        # Check if product exists
                        check_query = f"""
                        SELECT id FROM "{schema_name}".products WHERE slug = :slug
                        """
                        result = conn.execute(db.text(check_query), {"slug": prod_data['slug']})
                        existing = result.fetchone()
                        
                        if not existing:
                            insert_query = f"""
                            INSERT INTO "{schema_name}".products 
                            (name, slug, description, price, currency, stock, is_active, category_id,
                             name_uk, name_ru, name_de, name_en, description_uk, description_ru, 
                             description_de, description_en, sort_order)
                            VALUES 
                            (:name, :slug, :description, :price, :currency, :stock, :is_active, :category_id,
                             :name_uk, :name_ru, :name_de, :name_en, :description_uk, :description_ru,
                             :description_de, :description_en, :sort_order)
                            """
                            prod_data['category_id'] = category_id
                            del prod_data['category_slug']  # Remove this as it's not a column
                            
                            conn.execute(db.text(insert_query), prod_data)
                            conn.commit()
                            print(f"✅ Added product: {prod_data['name']}")
                        else:
                            print(f"ℹ️ Product already exists: {prod_data['name']}")
                    else:
                        print(f"❌ Category not found for product: {prod_data['name']}")
            
            print('\\n✅ Sample data added successfully!')
                
        except Exception as e:
            print(f'❌ Error adding sample data: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_sample_data()
