from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Float, Boolean, DateTime, ForeignKey, LargeBinary
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
import os

# Get schema from environment
SCHEMA_NAME = os.environ.get('DB_SCHEMA', 'public')

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def set_password(self, password: str) -> None:
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check password"""
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    """Product category model"""
    __tablename__ = 'categories'
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_uk: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    name_de: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[Optional[str]] = mapped_column(String(100))
    description_uk: Mapped[Optional[str]] = mapped_column(Text)
    description_ru: Mapped[Optional[str]] = mapped_column(Text)
    description_de: Mapped[Optional[str]] = mapped_column(Text)
    description_en: Mapped[Optional[str]] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def get_name(self, language: str = 'uk') -> str:
        """Get localized name"""
        name = getattr(self, f'name_{language}', None)
        return name or self.name_uk or ''
    
    def get_description(self, language: str = 'uk') -> str:
        """Get localized description"""
        description = getattr(self, f'description_{language}', None)
        return description or self.description_uk or ''

class Product(db.Model):
    """Product model"""
    __tablename__ = 'products'
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_uk: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(200), nullable=False)
    name_de: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[Optional[str]] = mapped_column(String(200))
    description_uk: Mapped[Optional[str]] = mapped_column(Text)
    description_ru: Mapped[Optional[str]] = mapped_column(Text)
    description_de: Mapped[Optional[str]] = mapped_column(Text)
    description_en: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='EUR')
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{SCHEMA_NAME}.categories.id' if SCHEMA_NAME != 'public' else 'categories.id'), nullable=False)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def get_name(self, language: str = 'uk') -> str:
        """Get localized name"""
        name = getattr(self, f'name_{language}', None)
        return name or self.name_uk or ''
    
    def get_description(self, language: str = 'uk') -> str:
        """Get localized description"""
        description = getattr(self, f'description_{language}', None)
        return description or self.description_uk or ''

class BlogPost(db.Model):
    """Blog post model"""
    __tablename__ = 'blog_posts'
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)  # Основное поле заголовка
    content: Mapped[str] = mapped_column(Text, nullable=False, default='')  # Основное поле контента
    excerpt: Mapped[Optional[str]] = mapped_column(Text)  # Основное поле отрывка
    title_uk: Mapped[str] = mapped_column(String(200), nullable=False)
    title_ru: Mapped[str] = mapped_column(String(200), nullable=False)
    title_de: Mapped[str] = mapped_column(String(200), nullable=False)
    title_en: Mapped[Optional[str]] = mapped_column(String(200))
    content_uk: Mapped[str] = mapped_column(Text, nullable=False)
    content_ru: Mapped[str] = mapped_column(Text, nullable=False)
    content_de: Mapped[str] = mapped_column(Text, nullable=False)
    content_en: Mapped[Optional[str]] = mapped_column(Text)
    excerpt_uk: Mapped[Optional[str]] = mapped_column(Text)
    excerpt_ru: Mapped[Optional[str]] = mapped_column(Text)
    excerpt_de: Mapped[Optional[str]] = mapped_column(Text)
    excerpt_en: Mapped[Optional[str]] = mapped_column(Text)
    image: Mapped[Optional[str]] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{SCHEMA_NAME}.users.id' if SCHEMA_NAME != 'public' else 'users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    author = db.relationship('User', backref='blog_posts')
    
    def get_title(self, language: str = 'uk') -> str:
        """Get localized title"""
        title = getattr(self, f'title_{language}', None)
        return title or self.title_uk or ''
    
    def get_content(self, language: str = 'uk') -> str:
        """Get localized content"""
        content = getattr(self, f'content_{language}', None)
        return content or self.content_uk or ''
    
    def get_excerpt(self, language: str = 'uk') -> str:
        """Get localized excerpt"""
        excerpt = getattr(self, f'excerpt_{language}', None)
        return excerpt or self.excerpt_uk or ''

class HomePageBlock(db.Model):
    """Home page customizable blocks"""
    __tablename__ = 'homepage_blocks'
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title_uk: Mapped[str] = mapped_column(String(200), nullable=False)
    title_ru: Mapped[str] = mapped_column(String(200), nullable=False)
    title_de: Mapped[str] = mapped_column(String(200), nullable=False)
    title_en: Mapped[Optional[str]] = mapped_column(String(200))
    block_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'blog' or 'shop'
    css_class: Mapped[Optional[str]] = mapped_column(String(255))
    image: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def get_title(self, language: str = 'uk') -> str:
        """Get localized title"""
        title = getattr(self, f'title_{language}', None)
        return title or self.title_uk or ''

class SocialLink(db.Model):
    """Social media links"""
    __tablename__ = 'social_links'
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # Display name
    platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # facebook, instagram, youtube, telegram
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Legacy icon field
    icon_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # CSS icon class
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    # Both order columns map to the same DB field
    order: Mapped[Optional[int]] = mapped_column('order', Integer, default=0)
    sort_order: Mapped[Optional[int]] = mapped_column('sort_order', Integer, default=0)

class Order(db.Model):
    """Order model for tracking purchases"""
    __tablename__ = 'orders'
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stripe_session_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='EUR')
    status: Mapped[str] = mapped_column(String(50), default='pending')  # pending, completed, failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    """Order item model"""
    __tablename__ = 'order_items'
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{SCHEMA_NAME}.orders.id' if SCHEMA_NAME != 'public' else 'orders.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{SCHEMA_NAME}.products.id' if SCHEMA_NAME != 'public' else 'products.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='order_items')


class ChatThread(db.Model):
    """Chat thread model for storing OpenAI assistant threads"""
    __tablename__ = 'chat_threads'
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)  # User session ID
    thread_id: Mapped[str] = mapped_column(String(255), nullable=False)  # OpenAI thread ID
    language: Mapped[str] = mapped_column(String(5), default='uk')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
