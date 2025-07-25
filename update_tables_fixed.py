#!/usr/bin/env python3
"""
Update existing tables to match our models - with autocommit
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db

def update_table_structure():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Updating table structure in schema: {schema_name}')
        
        # List of SQL commands to execute
        commands = [
            # Categories table updates
            f'ALTER TABLE "{schema_name}".categories ADD COLUMN IF NOT EXISTS name_ru VARCHAR(100)',
            f'ALTER TABLE "{schema_name}".categories ADD COLUMN IF NOT EXISTS description_ru TEXT', 
            f'ALTER TABLE "{schema_name}".categories ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE',
            f'ALTER TABLE "{schema_name}".categories ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0',
            
            # Products table updates
            f'ALTER TABLE "{schema_name}".products ADD COLUMN IF NOT EXISTS name_ru VARCHAR(100)',
            f'ALTER TABLE "{schema_name}".products ADD COLUMN IF NOT EXISTS description_ru TEXT',
            f'ALTER TABLE "{schema_name}".products ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT \'EUR\'',
            f'ALTER TABLE "{schema_name}".products ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0',
        ]
        
        try:
            for cmd in commands:
                try:
                    with db.engine.connect() as conn:
                        conn.execute(db.text(cmd))
                        conn.commit()
                    print(f'✅ Executed: {cmd}')
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f'ℹ️ Column already exists: {cmd}')
                    else:
                        print(f'❌ Error with command: {cmd}')
                        print(f'   Error: {e}')
                
            print('\\n✅ All table updates completed!')
                
        except Exception as e:
            print(f'❌ Error updating tables: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    update_table_structure()
