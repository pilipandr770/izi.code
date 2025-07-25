#!/bin/bash
# initialize.sh - Script to initialize database with proper schema before app starts

echo "Creating schema if it doesn't exist..."
python - << EOF
import os
import psycopg2
from urllib.parse import urlparse

# Parse DATABASE_URL to extract connection parameters
db_url = os.environ.get('DATABASE_URL')
parsed = urlparse(db_url)
dbname = parsed.path[1:]
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port

# Create schema if it doesn't exist
conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)

conn.autocommit = True
cursor = conn.cursor()

schema_name = os.environ.get('DB_SCHEMA', 'AndriIT')
cursor.execute(f"CREATE SCHEMA IF NOT EXISTS \"{schema_name}\"")

cursor.close()
conn.close()

print(f"Schema '{schema_name}' created or verified successfully.")
EOF

echo "Running database migrations..."
flask db upgrade

echo "Initialization complete!"
