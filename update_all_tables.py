#!/usr/bin/env python3
"""
Complete database structure update for all missing tables
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db

def update_all_tables():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Updating all tables in schema: {schema_name}')
        
        # Commands for all remaining tables
        commands = [
            # Users table
            f'CREATE TABLE IF NOT EXISTS "{schema_name}".users (id SERIAL PRIMARY KEY)',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS username VARCHAR(80) UNIQUE',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS email VARCHAR(120) UNIQUE',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100)',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100)',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS phone VARCHAR(20)',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            
            # Orders table
            f'CREATE TABLE IF NOT EXISTS "{schema_name}".orders (id SERIAL PRIMARY KEY)',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS user_id INTEGER',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT \'pending\'',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS total_amount FLOAT NOT NULL DEFAULT 0',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT \'EUR\'',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS shipping_address TEXT',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS billing_address TEXT',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            
            # Order items table
            f'CREATE TABLE IF NOT EXISTS "{schema_name}".order_items (id SERIAL PRIMARY KEY)',
            f'ALTER TABLE "{schema_name}".order_items ADD COLUMN IF NOT EXISTS order_id INTEGER',
            f'ALTER TABLE "{schema_name}".order_items ADD COLUMN IF NOT EXISTS product_id INTEGER',
            f'ALTER TABLE "{schema_name}".order_items ADD COLUMN IF NOT EXISTS quantity INTEGER NOT NULL DEFAULT 1',
            f'ALTER TABLE "{schema_name}".order_items ADD COLUMN IF NOT EXISTS price FLOAT NOT NULL DEFAULT 0',
            
            # Contact messages table
            f'CREATE TABLE IF NOT EXISTS "{schema_name}".contact_messages (id SERIAL PRIMARY KEY)',
            f'ALTER TABLE "{schema_name}".contact_messages ADD COLUMN IF NOT EXISTS name VARCHAR(100) NOT NULL',
            f'ALTER TABLE "{schema_name}".contact_messages ADD COLUMN IF NOT EXISTS email VARCHAR(120) NOT NULL',
            f'ALTER TABLE "{schema_name}".contact_messages ADD COLUMN IF NOT EXISTS subject VARCHAR(200)',
            f'ALTER TABLE "{schema_name}".contact_messages ADD COLUMN IF NOT EXISTS message TEXT NOT NULL',
            f'ALTER TABLE "{schema_name}".contact_messages ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE',
            f'ALTER TABLE "{schema_name}".contact_messages ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        ]
        
        try:
            for i, cmd in enumerate(commands):
                try:
                    with db.engine.connect() as conn:
                        conn.execute(db.text(cmd))
                        conn.commit()
                    print(f'✅ [{i+1}/{len(commands)}] {cmd[:80]}...')
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f'ℹ️ [{i+1}/{len(commands)}] Already exists: {cmd[:80]}...')
                    else:
                        print(f'❌ [{i+1}/{len(commands)}] Error: {cmd[:80]}...')
                        print(f'   {e}')
                
            print('\\n✅ All tables updated successfully!')
                
        except Exception as e:
            print(f'❌ Error updating tables: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    update_all_tables()
