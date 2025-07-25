"""Flask extensions initialization"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
