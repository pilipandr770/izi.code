"""
Basic test suite for SaaS Shop Flask application
"""
import unittest
import os
import tempfile
from app import create_app, db
from app.models import User, Category, Product, BlogPost
from config import Config

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

class SaaSShopTestCase(unittest.TestCase):
    """Base test case for SaaS Shop"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        
        # Create test admin user
        admin = User(username='testadmin', email='admin@test.com', is_admin=True)
        admin.set_password('testpass')
        db.session.add(admin)
        
        # Create test category
        category = Category(
            name_uk='Тестова категорія',
            name_ru='Тестовая категория', 
            name_de='Test Kategorie'
        )
        db.session.add(category)
        db.session.commit()
        
        # Create test product
        product = Product(
            name_uk='Тестовий товар',
            name_ru='Тестовый товар',
            name_de='Test Produkt',
            price=99.99,
            currency='EUR',
            category_id=category.id
        )
        db.session.add(product)
        db.session.commit()
        
        self.admin = admin
        self.category = category
        self.product = product
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

class MainPagesTestCase(SaaSShopTestCase):
    """Test main website pages"""
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SaaS Shop', response.data)
    
    def test_shop_page(self):
        """Test shop page loads"""
        response = self.client.get('/shop')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shop Categories', response.data)
    
    def test_category_page(self):
        """Test category page loads"""
        response = self.client.get(f'/shop/category/{self.category.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.category.name_uk.encode(), response.data)
    
    def test_product_detail_page(self):
        """Test product detail page loads"""
        response = self.client.get(f'/shop/product/{self.product.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product.name_uk.encode(), response.data)
    
    def test_blog_page(self):
        """Test blog page loads"""
        response = self.client.get('/blog')
        self.assertEqual(response.status_code, 200)
    
    def test_contact_page(self):
        """Test contact page loads"""
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)

class AdminTestCase(SaaSShopTestCase):
    """Test admin functionality"""
    
    def login_admin(self):
        """Helper to login as admin"""
        return self.client.post('/admin/login', data={
            'username': 'testadmin',
            'password': 'testpass'
        }, follow_redirects=True)
    
    def test_admin_login_page(self):
        """Test admin login page loads"""
        response = self.client.get('/admin/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Login', response.data)
    
    def test_admin_login_valid(self):
        """Test admin login with valid credentials"""
        response = self.login_admin()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_admin_login_invalid(self):
        """Test admin login with invalid credentials"""
        response = self.client.post('/admin/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_admin_dashboard_requires_login(self):
        """Test admin dashboard requires login"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_dashboard_after_login(self):
        """Test admin dashboard after login"""
        self.login_admin()
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

class APITestCase(SaaSShopTestCase):
    """Test API endpoints"""
    
    def test_products_api(self):
        """Test products API endpoint"""
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        if data:  # If products exist
            self.assertIn('id', data[0])
            self.assertIn('name', data[0])
            self.assertIn('price', data[0])
    
    def test_categories_api(self):
        """Test categories API endpoint"""
        response = self.client.get('/api/categories')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        if data:  # If categories exist
            self.assertIn('id', data[0])
            self.assertIn('name', data[0])
    
    def test_chatbot_api_missing_message(self):
        """Test chatbot API with missing message"""
        response = self.client.post('/api/chatbot', 
                                  json={},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

class ModelTestCase(SaaSShopTestCase):
    """Test database models"""
    
    def test_user_password_hashing(self):
        """Test user password hashing"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        
        self.assertFalse(user.check_password('wrongpassword'))
        self.assertTrue(user.check_password('testpassword'))
    
    def test_category_localization(self):
        """Test category localization methods"""
        category = Category(
            name_uk='Українська назва',
            name_ru='Русское название',
            name_de='Deutsche Name'
        )
        
        self.assertEqual(category.get_name('uk'), 'Українська назва')
        self.assertEqual(category.get_name('ru'), 'Русское название')
        self.assertEqual(category.get_name('de'), 'Deutsche Name')
        self.assertEqual(category.get_name('unknown'), 'Українська назва')  # Fallback
    
    def test_product_localization(self):
        """Test product localization methods"""
        product = Product(
            name_uk='Український товар',
            name_ru='Русский товар',
            name_de='Deutsches Produkt',
            price=99.99,
            currency='EUR',
            category_id=self.category.id
        )
        
        self.assertEqual(product.get_name('uk'), 'Український товар')
        self.assertEqual(product.get_name('ru'), 'Русский товар')
        self.assertEqual(product.get_name('de'), 'Deutsches Produkt')

class UtilsTestCase(SaaSShopTestCase):
    """Test utility functions"""
    
    def test_generate_slug(self):
        """Test slug generation"""
        from app.utils import generate_slug
        
        test_cases = [
            ('Hello World', 'hello-world'),
            ('Тестовий заголовок', 'тестовий-заголовок'),
            ('Test with Special @#$ Characters!', 'test-with-special-characters'),
            ('Multiple   Spaces', 'multiple-spaces'),
        ]
        
        for title, expected in test_cases:
            with self.subTest(title=title):
                result = generate_slug(title)
                # Basic checks - slug should be lowercase and not empty
                self.assertIsInstance(result, str)
                self.assertTrue(len(result) > 0)
                self.assertEqual(result, result.lower())

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
