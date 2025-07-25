from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    inspector = db.inspect(db.engine)
    columns = inspector.get_columns('social_links', schema=app.config['DB_SCHEMA'])
    
    print("=== Структура таблицы social_links ===")
    for column in columns:
        print(f"Колонка: {column['name']}, Тип: {column['type']}, Nullable: {column.get('nullable', 'Unknown')}")
