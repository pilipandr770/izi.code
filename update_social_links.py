#!/usr/bin/env python3
"""
Fix database schema issues - make 'name' column nullable and update orders table
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

def fix_database_schema():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Fixing database schema in schema: {schema_name}')
        
        # List of SQL commands to execute
        commands = [
            # Fix categories table - make name column nullable
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN name DROP NOT NULL',
            
            # Fix products table - make name column nullable
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN name DROP NOT NULL',
            
            # Increase name field sizes for long product names
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN name_uk TYPE VARCHAR(500)',
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN name_ru TYPE VARCHAR(500)',
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN name_de TYPE VARCHAR(500)',
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN name_en TYPE VARCHAR(500)',
            
            # Increase description field sizes
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN description_uk TYPE VARCHAR(1000)',
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN description_ru TYPE VARCHAR(1000)',
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN description_de TYPE VARCHAR(1000)',
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN description_en TYPE VARCHAR(1000)',
            
            # Increase slug field size for long product names (crucial for URLs)
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN slug TYPE VARCHAR(1000)',
            
            # Categories table name field size increases
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN name_uk TYPE VARCHAR(500)',
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN name_ru TYPE VARCHAR(500)',
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN name_de TYPE VARCHAR(500)',
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN name_en TYPE VARCHAR(500)',
            
            # Categories description and slug field size increases
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN description_uk TYPE VARCHAR(1000)',
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN description_ru TYPE VARCHAR(1000)',
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN description_de TYPE VARCHAR(1000)',
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN description_en TYPE VARCHAR(1000)',
            f'ALTER TABLE "{schema_name}".categories ALTER COLUMN slug TYPE VARCHAR(1000)',
            
            # Orders table updates
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS stripe_session_id VARCHAR(255)',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS customer_email VARCHAR(255)',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS total_amount DECIMAL(10,2)',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT \'EUR\'',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT \'pending\'',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            
            # Allow NULL for stripe_price_id to handle cases where Stripe integration is not configured
            f'ALTER TABLE "{schema_name}".products ALTER COLUMN stripe_price_id DROP NOT NULL',
            
            # Social links table updates 
            f'ALTER TABLE "{schema_name}".social_links ADD COLUMN IF NOT EXISTS platform VARCHAR(50)',
            f'ALTER TABLE "{schema_name}".social_links ADD COLUMN IF NOT EXISTS url VARCHAR(255)',
            f'ALTER TABLE "{schema_name}".social_links ADD COLUMN IF NOT EXISTS icon_class VARCHAR(100)',
            f'ALTER TABLE "{schema_name}".social_links ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE',
            f'ALTER TABLE "{schema_name}".social_links ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0',
        ]
        
        try:
            for cmd in commands:
                try:
                    with db.engine.connect() as conn:
                        conn.execute(db.text(cmd))
                        conn.commit()
                    print(f'✅ Executed: {cmd}')
                except Exception as e:
                    if 'already exists' in str(e).lower() or 'does not exist' in str(e).lower():
                        print(f'ℹ️ Column already exists or missing: {cmd}')
                    else:
                        print(f'❌ Error with command: {cmd}')
                        print(f'   Error: {e}')
            
            # Create admin user if doesn't exist
            print('\\n🔧 Creating admin user...')
            try:
                admin = User.query.filter_by(email='admin@izi.soft').first()
                if admin:
                    print('ℹ️ Admin user already exists!')
                    print('📧 Email: admin@izi.soft')
                    print('🔑 Password: admin123')
                else:
                    admin = User(
                        username='admin',
                        email='admin@izi.soft',
                        password_hash=generate_password_hash('admin123'),
                        is_admin=True
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print('✅ Admin user created successfully!')
                    print('📧 Email: admin@izi.soft')
                    print('🔑 Password: admin123')
            except Exception as e:
                if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                    print('ℹ️ Admin user already exists (duplicate key)!')
                    print('📧 Email: admin@izi.soft')
                    print('🔑 Password: admin123')
                    # Rollback the failed transaction
                    db.session.rollback()
                else:
                    print(f'❌ Error creating admin user: {e}')
                    db.session.rollback()
                
            print('\\n✅ All schema fixes completed!')
                
        except Exception as e:
            print(f'❌ Error fixing schema: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_database_schema()
