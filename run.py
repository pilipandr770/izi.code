import os
import time
import sqlalchemy
from app import create_app
from app.extensions import db
from app.models import User, Category, Product, BlogPost, HomePageBlock, SocialLink, Order, OrderItem
from app.utils import init_default_data
from config import Config
from sqlalchemy.exc import OperationalError, SQLAlchemyError

app = create_app()

def create_tables():
    """Create database tables and initialize default data with fallback mechanism"""
    with app.app_context():
        # Try to connect to the primary database
        try:
            # Test the connection before proceeding
            engine = db.engine
            connection = engine.connect()
            connection.close()
            
            # If connection successful, create tables and initialize data
            db.create_all()
            init_default_data()
            print("Database initialized successfully!")
        except (OperationalError, SQLAlchemyError) as e:
            print(f"Primary database connection error: {e}")
            
            # Try fallback database if primary fails
            try:
                fallback_url = Config.fallback_database_url
                print(f"Attempting to use fallback database: {fallback_url}")
                
                # Change the database URI to fallback
                app.config['SQLALCHEMY_DATABASE_URI'] = fallback_url
                
                # Recreate engine with new connection settings
                db.engine.dispose()
                db.get_engine(app)
                
                # Create tables and initialize data on fallback database
                db.create_all()
                init_default_data()
                print("Database initialized with fallback successfully!")
            except Exception as fallback_error:
                print(f"Error initializing fallback database: {fallback_error}")
        except Exception as e:
            print(f"Error initializing database: {e}")

@app.shell_context_processor
def make_shell_context():
    """Shell context processor for Flask shell"""
    return {
        'db': db,
        'User': User,
        'Category': Category,
        'Product': Product,
        'BlogPost': BlogPost,
        'HomePageBlock': HomePageBlock,
        'SocialLink': SocialLink,
        'Order': Order,
        'OrderItem': OrderItem
    }

if __name__ == '__main__':
    # Initialize database on startup
    create_tables()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
