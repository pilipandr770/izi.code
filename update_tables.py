#!/usr/bin/env python3
"""
Update existing tables to match our models
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
        
        try:
            with db.engine.connect() as conn:
                # Add missing columns to categories table
                print('Adding missing columns to categories table...')
                
                # Check and add name_ru column
                try:
                    conn.execute(db.text(f'ALTER TABLE "{schema_name}".categories ADD COLUMN name_ru VARCHAR(100)'))
                    print('✅ Added name_ru column')
                except Exception as e:
                    if 'already exists' in str(e):
                        print('ℹ️ name_ru column already exists')
                    else:
                        print(f'❌ Error adding name_ru: {e}')
                
                # Check and add description_ru column
                try:
                    conn.execute(db.text(f'ALTER TABLE "{schema_name}".categories ADD COLUMN description_ru TEXT'))
                    print('✅ Added description_ru column')
                except Exception as e:
                    if 'already exists' in str(e):
                        print('ℹ️ description_ru column already exists')
                    else:
                        print(f'❌ Error adding description_ru: {e}')
                
                # Check and add is_active column
                try:
                    conn.execute(db.text(f'ALTER TABLE "{schema_name}".categories ADD COLUMN is_active BOOLEAN DEFAULT TRUE'))
                    print('✅ Added is_active column')
                except Exception as e:
                    if 'already exists' in str(e):
                        print('ℹ️ is_active column already exists')
                    else:
                        print(f'❌ Error adding is_active: {e}')
                
                # Check and add sort_order column
                try:
                    conn.execute(db.text(f'ALTER TABLE "{schema_name}".categories ADD COLUMN sort_order INTEGER DEFAULT 0'))
                    print('✅ Added sort_order column')
                except Exception as e:
                    if 'already exists' in str(e):
                        print('ℹ️ sort_order column already exists')
                    else:
                        print(f'❌ Error adding sort_order: {e}')
                
                # Check and add missing columns to products table
                print('\\nUpdating products table...')
                
                # Check for missing columns in products
                missing_product_columns = [
                    ('name_ru', 'VARCHAR(100)'),
                    ('description_ru', 'TEXT'),
                    ('currency', 'VARCHAR(10)'),
                    ('sort_order', 'INTEGER DEFAULT 0')
                ]
                
                for col_name, col_type in missing_product_columns:
                    try:
                        conn.execute(db.text(f'ALTER TABLE "{schema_name}".products ADD COLUMN {col_name} {col_type}'))
                        print(f'✅ Added {col_name} column to products')
                    except Exception as e:
                        if 'already exists' in str(e):
                            print(f'ℹ️ {col_name} column already exists in products')
                        else:
                            print(f'❌ Error adding {col_name} to products: {e}')
                
                # Update users table if needed
                print('\\nUpdating users table...')
                try:
                    # Update password_hash column length
                    conn.execute(db.text(f'ALTER TABLE "{schema_name}".users ALTER COLUMN password_hash TYPE VARCHAR(255)'))
                    print('✅ Updated password_hash column length')
                except Exception as e:
                    print(f'ℹ️ Users table update: {e}')
                
                # Commit changes
                conn.commit()
                print('\\n✅ All table updates completed!')
                
        except Exception as e:
            print(f'❌ Error updating tables: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    update_table_structure()
