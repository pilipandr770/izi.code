#!/usr/bin/env python3
"""
Create missing tables in PostgreSQL schema
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db
from app.models import *

def create_missing_tables():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Working with schema: {schema_name}')
        
        try:
            # Get current tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names(schema=schema_name)
            print(f'Existing tables: {existing_tables}')
            
            # Our expected tables
            expected_tables = [
                'users', 'categories', 'products', 'blog_posts', 
                'home_page_blocks', 'social_links', 'orders', 
                'order_items', 'chat_threads'
            ]
            
            missing_tables = [table for table in expected_tables if table not in existing_tables]
            print(f'Missing tables: {missing_tables}')
            
            if missing_tables:
                print('Creating missing tables...')
                db.create_all()
                print('✅ All tables created successfully!')
                
                # Check again
                updated_tables = inspector.get_table_names(schema=schema_name)
                print(f'Updated tables in schema: {updated_tables}')
            else:
                print('✅ All required tables already exist!')
                
        except Exception as e:
            print(f'❌ Error creating tables: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_missing_tables()
