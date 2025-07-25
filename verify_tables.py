#!/usr/bin/env python3
"""
Verify table structure after updates
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db

def check_table_structure():
    app = create_app()
    with app.app_context():
        schema_name = app.config.get('DB_SCHEMA', 'public')
        print(f'Checking table structure in schema: {schema_name}')
        
        # Query to get column information
        tables_to_check = ['categories', 'products']
        
        for table_name in tables_to_check:
            print(f'\\n📋 Table: {table_name}')
            print('-' * 50)
            
            try:
                query = f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = '{schema_name}' 
                AND table_name = '{table_name}'
                ORDER BY ordinal_position;
                """
                
                with db.engine.connect() as conn:
                    result = conn.execute(db.text(query))
                    columns = result.fetchall()
                    
                    if columns:
                        for col in columns:
                            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                            default = f" DEFAULT {col[3]}" if col[3] else ""
                            print(f"  {col[0]} ({col[1]}) {nullable}{default}")
                    else:
                        print(f"  ❌ Table {table_name} not found!")
                        
            except Exception as e:
                print(f"  ❌ Error checking {table_name}: {e}")

if __name__ == "__main__":
    check_table_structure()
