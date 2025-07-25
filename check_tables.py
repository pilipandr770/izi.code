#!/usr/bin/env python3
"""
Check existing table structures in PostgreSQL
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
        
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            # Check categories table structure
            print('\n=== CATEGORIES TABLE ===')
            try:
                columns = inspector.get_columns('categories', schema=schema_name)
                for col in columns:
                    print(f"- {col['name']}: {col['type']}")
            except Exception as e:
                print(f"Error reading categories: {e}")
            
            # Check products table structure  
            print('\n=== PRODUCTS TABLE ===')
            try:
                columns = inspector.get_columns('products', schema=schema_name)
                for col in columns:
                    print(f"- {col['name']}: {col['type']}")
            except Exception as e:
                print(f"Error reading products: {e}")
                
            # Check users table structure
            print('\n=== USERS TABLE ===')  
            try:
                columns = inspector.get_columns('users', schema=schema_name)
                for col in columns:
                    print(f"- {col['name']}: {col['type']}")
            except Exception as e:
                print(f"Error reading users: {e}")
            
            # Raw query to see what's actually in categories
            print('\n=== RAW CATEGORIES DATA ===')
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(text(f'SELECT * FROM "{schema_name}".categories LIMIT 3'))
                    rows = result.fetchall()
                    if rows:
                        columns = result.keys()
                        print(f"Columns: {list(columns)}")
                        for i, row in enumerate(rows):
                            print(f"Row {i+1}: {dict(zip(columns, row))}")
                    else:
                        print("No data in categories table")
            except Exception as e:
                print(f"Error querying categories: {e}")
                
        except Exception as e:
            print(f'❌ Error checking structure: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_table_structure()
