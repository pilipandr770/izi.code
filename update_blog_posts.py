#!/usr/bin/env python3
"""
Update blog_posts table to match our models
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db

def update_blog_posts_table():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Updating blog_posts table in schema: {schema_name}')
        
        # List of SQL commands to execute for blog_posts
        commands = [
            # Check if table exists first
            f'CREATE TABLE IF NOT EXISTS "{schema_name}".blog_posts (id SERIAL PRIMARY KEY)',
            
            # Add all required columns with proper types
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS title_uk VARCHAR(200)',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS title_ru VARCHAR(200)',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS title_de VARCHAR(200)',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS title_en VARCHAR(200)',
            
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS content_uk TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS content_ru TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS content_de TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS content_en TEXT',
            
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS excerpt_uk TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS excerpt_ru TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS excerpt_de TEXT',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS excerpt_en TEXT',
            
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS image VARCHAR(255)',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS slug VARCHAR(200)',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT FALSE',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS author_id INTEGER',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
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
                
            print('\\n✅ Blog posts table updated successfully!')
                
        except Exception as e:
            print(f'❌ Error updating blog_posts table: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    update_blog_posts_table()
