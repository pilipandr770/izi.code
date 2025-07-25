#!/usr/bin/env python3
"""
Final comprehensive table updates for all missing columns
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db

def final_table_updates():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Final table updates in schema: {schema_name}')
        
        # All missing columns for all tables
        commands = [
            # Users table
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            f'ALTER TABLE "{schema_name}".users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            
            # Newsletter subscribers
            f'ALTER TABLE "{schema_name}".newsletter_subscribers ADD COLUMN IF NOT EXISTS subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            f'ALTER TABLE "{schema_name}".newsletter_subscribers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE',
            
            # Contact messages
            f'ALTER TABLE "{schema_name}".contact_messages ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            f'ALTER TABLE "{schema_name}".contact_messages ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE',
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
                        print(f'ℹ️ Column/table already exists or missing: {cmd}')
                    else:
                        print(f'❌ Error with command: {cmd}')
                        print(f'   Error: {e}')
                
            print('\\n✅ All final table updates completed!')
                
        except Exception as e:
            print(f'❌ Error in final updates: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    final_table_updates()
