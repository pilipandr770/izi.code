#!/usr/bin/env python3
"""
Add missing columns to blog_posts table
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db

def add_blog_columns():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'AndriIT')
        print(f'Adding missing columns to blog_posts table in schema: {schema_name}')
        
        # List of SQL commands to execute
        commands = [
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS title VARCHAR(200) NOT NULL DEFAULT \'\'',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS content TEXT NOT NULL DEFAULT \'\'',
            f'ALTER TABLE "{schema_name}".blog_posts ADD COLUMN IF NOT EXISTS excerpt TEXT'
        ]
        
        # Execute each command
        try:
            with db.engine.begin() as connection:
                for command in commands:
                    print(f'Executing: {command}')
                    connection.execute(db.text(command))
                print('✅ Successfully added missing columns to blog_posts table')
                
            # Verify columns were added
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('blog_posts', schema=schema_name)
            print(f'Columns in blog_posts table: {[col["name"] for col in columns]}')
                
        except Exception as e:
            print(f'❌ Error adding columns: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_blog_columns()
