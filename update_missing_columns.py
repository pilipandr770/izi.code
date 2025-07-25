#!/usr/bin/env python3
"""
Add missing columns to existing tables
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db

def add_missing_columns():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Adding missing columns in schema: {schema_name}')
        
        # List of SQL commands to execute
        commands = [
            # Products table - add missing columns
            f'ALTER TABLE "{schema_name}".products ADD COLUMN IF NOT EXISTS stripe_price_id VARCHAR(100)',
            f'ALTER TABLE "{schema_name}".products ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            
            # Blog posts table - add missing columns
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS title_ru VARCHAR(200)',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS title_de VARCHAR(200)', 
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS title_en VARCHAR(200)',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS content_ru TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS content_de TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS content_en TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS excerpt_ru TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS excerpt_de TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS excerpt_en TEXT',
            
            # Categories table - add missing timestamps
            f'ALTER TABLE "{schema_name}".categories ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            f'ALTER TABLE "{schema_name}".categories ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            
            # Add users table if it doesn't exist
            f'''CREATE TABLE IF NOT EXISTS "{schema_name}".users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128),
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Add newsletter_subscribers table if it doesn't exist
            f'''CREATE TABLE IF NOT EXISTS "{schema_name}".newsletter_subscribers (
                id SERIAL PRIMARY KEY,
                email VARCHAR(120) UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Add contact_messages table if it doesn't exist
            f'''CREATE TABLE IF NOT EXISTS "{schema_name}".contact_messages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) NOT NULL,
                subject VARCHAR(200),
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        ]
        
        try:
            for cmd in commands:
                try:
                    with db.engine.connect() as conn:
                        conn.execute(db.text(cmd))
                        conn.commit()
                    print(f'✅ Executed: {cmd[:80]}...')
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f'ℹ️ Already exists: {cmd[:80]}...')
                    else:
                        print(f'❌ Error with command: {cmd[:80]}...')
                        print(f'   Error: {e}')
                
            print('\\n✅ All missing columns added!')
                
        except Exception as e:
            print(f'❌ Error adding columns: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_missing_columns()
