#!/usr/bin/env python3
"""
Update orders table and create admin user
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

def update_orders_and_create_admin():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Updating orders table and creating admin in schema: {schema_name}')
        
        # Update orders table
        commands = [
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS stripe_session_id VARCHAR(255)',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS customer_email VARCHAR(255)',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS total_amount DECIMAL(10,2)',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT \'EUR\'',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT \'pending\'',
            f'ALTER TABLE "{schema_name}".orders ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        ]
        
        try:
            # Update orders table
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
            
            # Create admin user
            print('\\n🔧 Creating admin user...')
            
            # Check if admin already exists
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
                
            print('\\n✅ All updates completed!')
                
        except Exception as e:
            print(f'❌ Error: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    update_orders_and_create_admin()
