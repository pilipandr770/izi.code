#!/usr/bin/env python3
"""
Test PostgreSQL connection and check schema
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db

def test_connection():
    app = create_app()
    with app.app_context():
        print(f'Database URI: {app.config["SQLALCHEMY_DATABASE_URI"]}')        
        print(f'Schema: {app.config.get("DB_SCHEMA", "public")}')
        
        try:
            # Test connection using SQLAlchemy 2.0 syntax
            with db.engine.connect() as connection:
                result = connection.execute(db.text('SELECT 1'))
                print('✅ Successfully connected to PostgreSQL!')
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            schema_name = app.config.get('DB_SCHEMA', 'public')
            
            # Check if schema exists
            schemas = inspector.get_schema_names()
            print(f'Available schemas: {schemas}')
            
            if schema_name in schemas:
                tables = inspector.get_table_names(schema=schema_name)
                print(f'Existing tables in schema "{schema_name}": {tables}')
            else:
                print(f'❌ Schema "{schema_name}" does not exist!')
                
        except Exception as e:
            print(f'❌ Connection error: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_connection()
