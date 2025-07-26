# -*- coding: utf-8 -*-
import os
import uuid
import stripe
import sys
import locale
import importlib
import openai
import re
import requests
import random
import time
import json
import tempfile
import subprocess
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app, session

# Add project root to Python path to ensure modules can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set default encoding to UTF-8 for the entire application
if sys.platform.startswith('win'):
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass

# Force reload openai module to ensure we get the correct version
if 'openai' in sys.modules:
    del sys.modules['openai']

# Double check that we have the right version
if hasattr(openai, '__version__'):
    print(f"DEBUG: OpenAI version detected: {openai.__version__}")
else:
    print("DEBUG: OpenAI version attribute not found")

from app.extensions import db
from app.models import Product, Category, BlogPost, User

# Ensure proper Unicode handling
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder: str = 'general') -> Optional[str]:
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add unique prefix to avoid naming conflicts
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return f"{folder}/{unique_filename}"
    return None

def delete_file(filename: str) -> bool:
    """Delete uploaded file"""
    if filename:
        try:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            current_app.logger.error(f"Error deleting file {filename}: {str(e)}")
    return False

def get_current_language() -> str:
    """Get current language from session or default"""
    return session.get('language', current_app.config['BABEL_DEFAULT_LOCALE'])

def create_stripe_price(product_name: str, price: float, currency: str = 'eur') -> Optional[str]:
    """Create Stripe price and return price ID"""
    try:
        stripe_secret_key = current_app.config.get('STRIPE_SECRET_KEY')
        
        # Check if Stripe is configured
        if not stripe_secret_key or stripe_secret_key.startswith('sk_test_your_stripe'):
            current_app.logger.warning("Stripe not configured - skipping price creation")
            return None
            
        stripe.api_key = stripe_secret_key
        
        # Create product first
        stripe_product = stripe.Product.create(name=product_name)
        
        # Create price
        stripe_price = stripe.Price.create(
            unit_amount=int(price * 100),  # Convert to cents
            currency=currency.lower(),
            product=stripe_product.id,
        )
        
        return stripe_price.id
    except Exception as e:
        current_app.logger.error(f"Error creating Stripe price: {str(e)}")
        return None

def create_checkout_session(items: List[Dict[str, Any]], success_url: str, cancel_url: str) -> Optional[str]:
    """Create Stripe checkout session"""
    try:
        stripe_secret_key = current_app.config.get('STRIPE_SECRET_KEY')
        
        # Check if Stripe is configured
        if not stripe_secret_key or stripe_secret_key.startswith('sk_test_your_stripe'):
            current_app.logger.warning("Stripe not configured - using demo mode")
            # Return a demo session ID for testing
            return "demo_session_12345"
        
        stripe.api_key = stripe_secret_key
        
        line_items = []
        for item in items:
            line_items.append({
                'price_data': {
                    'currency': item.get('currency', 'eur').lower(),
                    'product_data': {
                        'name': item['name'],
                        'description': item.get('description', ''),
                    },
                    'unit_amount': int(item['price'] * 100),  # Convert to cents
                },
                'quantity': item.get('quantity', 1),
            })
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'source': 'saas_shop'
            }
        )
        
        return session.id
    except Exception as e:
        current_app.logger.error(f"Error creating checkout session: {str(e)}")
        # Return demo session ID as fallback
        return "demo_session_fallback"

def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    # Remove special characters and convert to lowercase
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    # Replace spaces and multiple hyphens with single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug

class AIContentGenerator:
    """AI content generator for blog posts"""
    
    def __init__(self):
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            self.client = None
            self.assistant_id = None
            current_app.logger.warning("OpenAI API key not configured")
        else:
            try:
                # Log OpenAI version for debugging
                current_app.logger.info(f"OpenAI version: {openai.__version__}")
                
                # Ensure proper environment setup for Unicode handling
                if 'PYTHONIOENCODING' not in os.environ:
                    os.environ['PYTHONIOENCODING'] = 'utf-8'
                
                # Set locale for proper encoding
                try:
                    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
                except:
                    try:
                        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
                    except:
                        pass  # Keep default if neither works
                
                # For OpenAI 0.28, we set the API key globally
                openai.api_key = api_key
                
                self.client = True  # Just a flag to indicate it's configured
                self.assistant_id = current_app.config.get('OPENAI_ASSISTANT_ID')
                current_app.logger.info("OpenAI client initialized successfully (v0.28)")
            except Exception as e:
                current_app.logger.error(f"Error initializing OpenAI client: {str(e)}")
                self.client = None
                self.assistant_id = None
    
    def generate_blog_post(self, topic: str, language: str = 'uk', keywords: str = '') -> Dict[str, str]:
        """Generate SEO-optimized blog post using OpenAI"""
        current_app.logger.info(f"Generating blog post for topic: {topic}, language: {language}")
        
        if not self.client:
            current_app.logger.info("No OpenAI client - using fallback")
            return self._get_fallback_template(topic, language, keywords)
        
        try:
            # Use temporary file approach to avoid encoding issues in subprocess
                        
            current_app.logger.info("Calling OpenAI via temporary file...")
            
            # Create temporary file with arguments in system temp directory to avoid path issues
            # Use C:\Temp instead of user directory to avoid Cyrillic characters
            temp_dir = "C:\\Temp"
            current_app.logger.info(f"Using temp directory: {temp_dir}")
            
            # Create temp file manually with unique name
            temp_filename = f"openai_args_{uuid.uuid4().hex}.json"
            temp_file = os.path.join(temp_dir, temp_filename)
            
            current_app.logger.info(f"Creating temp file: {temp_file}")
            
            try:
                # Write arguments to temp file
                args_data = {
                    'api_key': current_app.config.get('OPENAI_API_KEY'),
                    'topic': topic,
                    'language': language,
                    'keywords': keywords
                }
                
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(args_data, f, ensure_ascii=False, indent=2)
                
                current_app.logger.info("Temp file created successfully")
                
                # Path to our caller script - use ASCII-safe location
                script_path = "C:\\Temp\\openai_caller_file.py"
                current_app.logger.info(f"Script path: {script_path}")
                
                # Call external script with temp file
                cmd = ["python", script_path, temp_file]  # Use system python instead of full path
                current_app.logger.info(f"Running command: {' '.join(cmd)}")
                
                # Run with UTF-8 encoding and clean environment
                env = os.environ.copy()  # Copy current environment
                env.update({
                    'PYTHONIOENCODING': 'utf-8',
                    'PYTHONLEGACYWINDOWSFSENCODING': '0'
                })
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    encoding='utf-8',
                    env=env,
                    cwd=os.path.dirname(os.path.dirname(__file__))  # Set working directory
                )
                
                current_app.logger.info(f"Subprocess return code: {result.returncode}")
                current_app.logger.info(f"Subprocess stdout length: {len(result.stdout) if result.stdout else 0}")
                current_app.logger.info(f"Subprocess stderr: {result.stderr}")
                
                if result.returncode == 0:
                    try:
                        current_app.logger.info(f"Raw stdout first 200 chars: {result.stdout[:200]}")
                        data = json.loads(result.stdout.strip())
                        if data.get('success', False):
                            current_app.logger.info("✅ File-based OpenAI script successful!")
                            return {
                                'title': data['title'],
                                'excerpt': data['excerpt'], 
                                'content': data['content']
                            }
                        else:
                            current_app.logger.error(f"File-based OpenAI failed: {data.get('error', 'Unknown error')}")
                    except json.JSONDecodeError as e:
                        current_app.logger.error(f"Failed to parse JSON response: {e}")
                        current_app.logger.error(f"Raw output: {result.stdout[:500]}")
                    except Exception as parse_error:
                        current_app.logger.error(f"Error parsing response: {parse_error}")
                        current_app.logger.error(f"Raw output: {result.stdout[:500]}")
                else:
                    current_app.logger.error(f"File-based script failed with code {result.returncode}")
                    current_app.logger.error(f"Error output: {result.stderr}")
                    
            finally:
                # Clean up temp file
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        current_app.logger.info("Temp file cleaned up")
                except Exception as cleanup_error:
                    current_app.logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
                
        except Exception as e:
            current_app.logger.error(f"Error calling file-based OpenAI script: {str(e)}")
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Fallback if everything fails
        current_app.logger.info("Using fallback template")
        return self._get_fallback_template(topic, language, keywords)
    
    def _get_fallback_template(self, topic: str, language: str, keywords: str) -> Dict[str, str]:
        """Get fallback template for when OpenAI fails"""
        language_templates = {
            'uk': {
                'title': f"Все про {topic}: повний гід",
                'excerpt': f"Детальний огляд теми '{topic}' з практичними рекомендаціями."
            },
            'ru': {
                'title': f"Все о {topic}: полное руководство", 
                'excerpt': f"Подробный обзор темы '{topic}' с практическими рекомендациями."
            },
            'de': {
                'title': f"Alles über {topic}: Vollständige Anleitung",
                'excerpt': f"Umfassender Überblick über '{topic}' mit praktischen Empfehlungen."
            },
            'en': {
                'title': f"Everything about {topic}: Complete Guide",
                'excerpt': f"Comprehensive overview of '{topic}' with practical recommendations."
            }
        }
        
        template = language_templates.get(language, language_templates['uk'])
        return {
            'title': template['title'],
            'excerpt': template['excerpt'],
            'content': f'<h2>About {topic}</h2><p>Detailed content about {topic} with keywords: {keywords}. This article includes practical recommendations and expert advice.</p>'
        }
    
    def generate_multilingual_post(self, topics: Dict[str, str], keywords: str = '') -> Dict[str, Dict[str, str]]:
        """Generate blog post in all supported languages"""
        result = {}
        for lang, topic in topics.items():
            if topic.strip():
                result[lang] = self.generate_blog_post(topic, lang, keywords)
        return result

class ChatbotAssistant:
    """AI Chatbot for customer support using OpenAI Assistants API"""
    
    def __init__(self):
        api_key = current_app.config.get('OPENAI_API_KEY')
        
        # Check for the external chatbot script
        script_dir = os.path.abspath(os.path.join(current_app.root_path, '..'))
        script_path = os.path.join(script_dir, 'openai_izi_chatbot.py')
        
        if os.path.exists(script_path):
            current_app.logger.info(f"Found chatbot script at: {script_path}")
        else:
            current_app.logger.error(f"Chatbot script not found at: {script_path}")
        
        if not api_key:
            self.client = None
            self.assistant_id = None
            current_app.logger.warning("OpenAI API key not configured")
        else:
            try:
                # For OpenAI 0.28, we set the API key globally
                openai.api_key = api_key
                self.client = True  # Just a flag to indicate it's configured
                
                # Get assistant_id from config or environment
                self.assistant_id = current_app.config.get('OPENAI_ASSISTANT_ID') or os.environ.get('OPENAI_ASSISTANT_ID')
                if not self.assistant_id or not isinstance(self.assistant_id, str) or not self.assistant_id.startswith('asst_'):
                    current_app.logger.warning(f"Invalid or missing Assistant ID: {self.assistant_id}. Check your configuration.")
                else:
                    current_app.logger.info(f"Using OpenAI Assistant ID: {self.assistant_id}")
                
                # Add API key to env for external script
                os.environ['OPENAI_API_KEY'] = api_key
                
                current_app.logger.info("OpenAI ChatBot client initialized successfully (v0.28)")
            except Exception as e:
                current_app.logger.error(f"Error initializing OpenAI client: {str(e)}")
                self.client = None
                self.assistant_id = None
    
    def generate_response(self, user_message, language='ru'):
        """Simple wrapper for backward compatibility"""
        return self.get_response(user_message, "default_session", language)
    
    def get_response(self, message: str, session_id: str, language: str = 'uk') -> str:
        """Get chatbot response using OpenAI Assistant API with stored assistant_id"""
        if not self.client:
            return self._get_fallback_response(language)
        
        try:
            # Get product context for chat
            from app.models import Product, Category
            products = Product.query.filter_by(is_active=True).limit(10).all()
            categories = Category.query.filter_by(is_active=True).limit(5).all()
            
            product_info = "\n".join([
                f"- {p.get_name(language)}: {p.price} {p.currency} - {p.get_description(language)[:100] if p.get_description(language) else 'Качественный цифровой продукт'}..."
                for p in products
            ])
            
            category_info = "\n".join([
                f"- {c.get_name(language)}: {c.get_description(language)[:100] if c.get_description(language) else 'Профессиональные ИТ-услуги'}..."
                for c in categories
            ])
            
            # Prepare OpenAI Assistant request
            assistant_request = {
                "message": message,
                "language": language,
                "product_info": product_info,
                "category_info": category_info,
                "assistant_id": self.assistant_id
            }
            
            # Log debug info about Assistant ID
            current_app.logger.info(f"Using OpenAI Assistant ID: {self.assistant_id}")
            
            # Save request to temp file
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(assistant_request, f, ensure_ascii=False, indent=2)
                temp_file = f.name
            
            try:
                # Get absolute path to script
                script_dir = os.path.abspath(os.path.join(current_app.root_path, '..'))
                
                # Try to use our custom script for v0.28.0 that properly integrates assistant_id
                script_path = os.path.join(script_dir, 'openai_izi_assistant.py')
                
                # Setup environment with OpenAI API key and force UTF-8 encoding
                env = os.environ.copy()
                env['OPENAI_API_KEY'] = current_app.config.get('OPENAI_API_KEY', '')
                env['OPENAI_ASSISTANT_ID'] = self.assistant_id
                env['PYTHONIOENCODING'] = 'utf-8'  # Force UTF-8 for all IO operations
                
                # Log useful debug info
                current_app.logger.info(f"Running Assistant chatbot script from: {script_dir}")
                current_app.logger.info(f"Full script path: {script_path}")
                
                # Use full paths for everything to avoid any path resolution issues
                python_executable = sys.executable
                
                try:
                    # Set up a process with pipes and explicit encoding
                    process = subprocess.Popen(
                        [python_executable, script_path, temp_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=env,
                        universal_newlines=True,
                        encoding='utf-8',
                        errors='replace'  # Replace invalid characters instead of failing
                    )
                    
                    # Get output with proper encoding
                    stdout, stderr = process.communicate()
                    
                    # Create a result object similar to subprocess.run
                    result = type('Result', (), {
                        'returncode': process.returncode,
                        'stdout': stdout,
                        'stderr': stderr
                    })
                    
                except Exception as e:
                    current_app.logger.error(f"Error running Assistant chatbot process: {str(e)}")
                    result = type('Result', (), {
                        'returncode': 1,
                        'stdout': '',
                        'stderr': f"Error: {str(e)}"
                    })
                
                if result.returncode == 0:
                    try:
                        response_data = json.loads(result.stdout)
                        if 'error' in response_data:
                            current_app.logger.error(f"OpenAI Assistant API error: {response_data['error']}")
                            # Fall back to direct approach if Assistant API fails
                            current_app.logger.info("Falling back to direct OpenAI API call")
                            return self._direct_openai_call(message, language)
                        return response_data.get('response', self._get_fallback_response(language))
                    except json.JSONDecodeError:
                        current_app.logger.error(f"Invalid JSON response: {result.stdout}")
                        # Try direct approach instead
                        current_app.logger.info("Falling back to direct OpenAI API call")
                        return self._direct_openai_call(message, language)
                else:
                    current_app.logger.error(f"OpenAI Assistant script error: {result.stderr}")
                    current_app.logger.error(f"Script stdout: {result.stdout}")
                    # Try direct approach instead
                    current_app.logger.info("Falling back to direct OpenAI API call")
                    return self._direct_openai_call(message, language)
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
            
        except Exception as e:
            current_app.logger.error(f"Error getting OpenAI Assistant response: {str(e)}")
            return self._get_fallback_response(language)
    
    def _get_demo_response(self, message: str, language: str, products, categories) -> str:
        """Generate demo responses based on message content and available products"""
        message_lower = message.lower()
        
        # Response templates by language
        responses = {
            'uk': {
                'greeting': ['Привіт! Ласкаво просимо до нашого магазину! Як я можу вам допомогти?', 
                           'Вітаю! Що вас цікавить з наших товарів?',
                           'Доброго дня! Чим можу бути корисний?'],
                'products': ['У нас є чудові продукти! Рекомендую звернути увагу на {}. Ціна всього {} {}.',
                           'Маю для вас відмінну пропозицію - {}. Коштує {} {}, дуже якісний продукт!',
                           'Ось що я раджу: {}. За {} {} ви отримаєте високоякісний товар.'],
                'categories': ['У нас є такі категорії: {}. Що вас найбільше цікавить?',
                             'Ми спеціалізуємося на: {}. Можу розповісти детальніше про будь-яку категорію.',
                             'Наші основні напрями: {}. В якій області шукаєте рішення?'],
                'help': ['Я тут, щоб допомогти вам знайти ідеальний продукт! Що саме вас цікавить?',
                        'Розкажіть, що шукаєте, і я підберу найкращі варіанти для вас.',
                        'Чим можу допомогти? Можу розповісти про наші товари і послуги.'],
                'price': ['Наші ціни дуже конкурентні! {} коштує всього {} {}.',
                         'Чудова ціна на {}: {} {}. Рекомендую!',
                         'За {} {} ви отримаєте {}. Вигідна пропозиція!'],
                'default': ['Цікаве питання! Наші товари точно можуть вам допомогти. Рекомендую {}.',
                          'Дякую за запитання! Можливо, вас зацікавить {}?',
                          'Розумію. У нас є {} - це може бути саме те, що ви шукаєте!']
            },
            'ru': {
                'greeting': ['Привет! Добро пожаловать в наш магазин! Как могу помочь?',
                           'Здравствуйте! Что вас интересует из наших товаров?',
                           'Добро пожаловать! Чем могу быть полезен?'],
                'products': ['У нас есть отличные продукты! Рекомендую обратить внимание на {}. Цена всего {} {}.',
                           'Могу предложить отличный вариант - {}. Стоит {} {}, очень качественный продукт!',
                           'Вот что советую: {}. За {} {} вы получите высококачественный товар.'],
                'categories': ['У нас есть такие категории: {}. Что вас больше всего интересует?',
                             'Мы специализируемся на: {}. Могу рассказать подробнее о любой категории.',
                             'Наши основные направления: {}. В какой области ищете решения?'],
                'help': ['Я здесь, чтобы помочь найти идеальный продукт! Что именно интересует?',
                        'Расскажите, что ищете, и я подберу лучшие варианты.',
                        'Чем могу помочь? Могу рассказать о наших товарах и услугах.'],
                'price': ['Наши цены очень конкурентные! {} стоит всего {} {}.',
                         'Отличная цена на {}: {} {}. Рекомендую!',
                         'За {} {} вы получите {}. Выгодное предложение!'],
                'default': ['Интересный вопрос! Наши товары точно могут помочь. Рекомендую {}.',
                          'Спасибо за вопрос! Возможно, вас заинтересует {}?',
                          'Понимаю. У нас есть {} - это может быть то, что ищете!']
            },
            'de': {
                'greeting': ['Hallo! Willkommen in unserem Shop! Wie kann ich helfen?',
                           'Guten Tag! Was interessiert Sie aus unserem Sortiment?',
                           'Willkommen! Womit kann ich behilflich sein?'],
                'products': ['Wir haben tolle Produkte! Ich empfehle {}. Preis nur {} {}.',
                           'Ich kann ein großartiges Produkt empfehlen - {}. Kostet {} {}, sehr hochwertig!',
                           'Das empfehle ich: {}. Für {} {} erhalten Sie ein hochwertiges Produkt.'],
                'categories': ['Wir haben diese Kategorien: {}. Was interessiert Sie am meisten?',
                             'Wir spezialisieren uns auf: {}. Ich kann mehr über jede Kategorie erzählen.',
                             'Unsere Hauptrichtungen: {}. In welchem Bereich suchen Sie Lösungen?'],
                'help': ['Ich bin hier, um das perfekte Produkt zu finden! Was interessiert Sie?',
                        'Erzählen Sie, was Sie suchen, und ich wähle die besten Optionen aus.',
                        'Womit kann ich helfen? Ich kann über unsere Produkte und Services erzählen.'],
                'price': ['Unsere Preise sind sehr konkurrenzfähig! {} kostet nur {} {}.',
                         'Toller Preis für {}: {} {}. Sehr empfehlenswert!',
                         'Für {} {} erhalten Sie {}. Ein vorteilhaftes Angebot!'],
                'default': ['Interessante Frage! Unsere Produkte können sicher helfen. Ich empfehle {}.',
                          'Danke für die Frage! Vielleicht interessiert Sie {}?',
                          'Verstehe. Wir haben {} - das könnte sein, was Sie suchen!']
            },
            'en': {
                'greeting': ['Hello! Welcome to our shop! How can I help?',
                           'Hi there! What interests you from our products?',
                           'Welcome! How may I assist you?'],
                'products': ['We have great products! I recommend {}. Price only {} {}.',
                           'I can suggest an excellent option - {}. Costs {} {}, very high quality!',
                           'Here\'s what I recommend: {}. For {} {} you get a high-quality product.'],
                'categories': ['We have these categories: {}. What interests you most?',
                             'We specialize in: {}. I can tell you more about any category.',
                             'Our main directions: {}. In which area are you looking for solutions?'],
                'help': ['I\'m here to help find the perfect product! What interests you?',
                        'Tell me what you\'re looking for, and I\'ll select the best options.',
                        'How can I help? I can tell you about our products and services.'],
                'price': ['Our prices are very competitive! {} costs only {} {}.',
                         'Great price for {}: {} {}. Highly recommended!',
                         'For {} {} you get {}. A great deal!'],
                'default': ['Interesting question! Our products can definitely help. I recommend {}.',
                          'Thanks for the question! Maybe you\'d be interested in {}?',
                          'I understand. We have {} - this might be what you\'re looking for!']
            }
        }
        
        lang_responses = responses.get(language, responses['uk'])
        
        # Determine response type based on message content
        
        if any(word in message_lower for word in ['привет', 'привіт', 'hello', 'hallo', 'hi', 'добро', 'доброго']):
            return random.choice(lang_responses['greeting'])
        
        elif any(word in message_lower for word in ['товар', 'продукт', 'product', 'купить', 'купити', 'buy', 'kaufen']):
            if products:
                product = random.choice(products)
                return random.choice(lang_responses['products']).format(
                    product.get_name(language), product.price, product.currency
                )
        
        elif any(word in message_lower for word in ['категории', 'категорії', 'categories', 'kategorien', 'раздел']):
            if categories:
                cat_names = [c.get_name(language) for c in categories[:3]]
                return random.choice(lang_responses['categories']).format(', '.join(cat_names))
        
        elif any(word in message_lower for word in ['цена', 'ціна', 'price', 'preis', 'стоимость', 'коштує', 'стоит']):
            if products:
                product = random.choice(products)
                return random.choice(lang_responses['price']).format(
                    product.get_name(language), product.price, product.currency
                )
        
        elif any(word in message_lower for word in ['помощь', 'допомога', 'help', 'hilfe', 'помогите', 'допоможіть']):
            return random.choice(lang_responses['help'])
        
        else:
            if products:
                product = random.choice(products)
                return random.choice(lang_responses['default']).format(product.get_name(language))
            else:
                return random.choice(lang_responses['help'])
    
    def _get_context_message(self, language: str, category_info: str, product_info: str) -> str:
        """Get context message in specified language"""
        context_messages = {
            'uk': f"""КОНТЕКСТ МАГАЗИНУ:
Ти — AI-консультант інтернет-магазину. Твоя мета — допомогти клієнтам і рекомендувати товари.

Наші категорії:
{category_info}

Наші топ-товари:
{product_info}

Відповідай українською мовою, будь дружнім і корисним. Намагайся направити розмову до покупки відповідних товарів.""",
            
            'ru': f"""КОНТЕКСТ МАГАЗИНА:
Ты — AI-консультант интернет-магазина. Твоя цель — помочь клиентам и рекомендовать товары.

Наши категории:
{category_info}

Наши топ-товары:
{product_info}

Отвечай на русском языке, будь дружелюбным и полезным. Старайся направить разговор к покупке соответствующих товаров.""",
            
            'de': f"""SHOP-KONTEXT:
Du bist ein AI-Berater für einen Online-Shop. Dein Ziel ist es, Kunden zu helfen und Produkte zu empfehlen.

Unsere Kategorien:
{category_info}

Unsere Top-Produkte:
{product_info}

Antworte auf Deutsch, sei freundlich und hilfsreich. Versuche das Gespräch zu entsprechenden Produktkäufen zu lenken.""",
            
            'en': f"""SHOP CONTEXT:
You are an AI consultant for an online shop. Your goal is to help customers and recommend products.

Our categories:
{category_info}

Our top products:
{product_info}

Reply in English, be friendly and helpful. Try to direct the conversation towards purchasing relevant products."""
        }
        
        return context_messages.get(language, context_messages['uk'])
    
    def _direct_openai_call(self, message: str, language: str) -> str:
        """Make a direct OpenAI API call as a fallback, using Assistant API if possible"""
        try:
            # Check if we have an assistant_id to use
            if self.assistant_id:
                try:
                    # Try to use imported OpenAI module structure to detect version
                    openai_version = "unknown"
                    try:
                        import openai
                        try:
                            from openai import version
                            openai_version = version.__version__
                        except:
                            openai_version = "0.x"  # Older version doesn't have version module
                    except:
                        pass
                    
                    current_app.logger.info(f"Using direct assistant call with OpenAI version {openai_version}")
                    
                    # Try to use Assistant API directly
                    if openai_version.startswith("1"):
                        # For v1.x API
                        from openai import OpenAI
                        client = OpenAI(api_key=openai.api_key)
                        
                        # Create thread and message
                        thread = client.beta.threads.create()
                        client.beta.threads.messages.create(
                            thread_id=thread.id,
                            role="user",
                            content=message
                        )
                        
                        # Run the assistant with properly validated assistant_id
                        current_app.logger.info(f"Using Assistant ID for direct API call: {self.assistant_id}")
                        run = client.beta.threads.runs.create(
                            thread_id=thread.id,
                            assistant_id=self.assistant_id,
                            instructions=f"Пользователь общается на языке: {language}. Отвечай на том же языке."
                        )
                        
                        # Wait for completion
                        import time
                        while run.status in ["queued", "in_progress"]:
                            time.sleep(0.5)
                            run = client.beta.threads.runs.retrieve(
                                thread_id=thread.id,
                                run_id=run.id
                            )
                        
                        # Get messages
                        messages = client.beta.threads.messages.list(thread_id=thread.id)
                        for message in messages.data:
                            if message.role == "assistant":
                                return message.content[0].text.value
                    else:
                        # For v0.x API - special handling for 0.28.0
                        # Build enhanced system prompt with assistant_id
                        system_prompt = f"""Ты - AI-консультант интернет-магазина (Assistant ID: {self.assistant_id}).
                        
Отвечай на языке пользователя ({language}).
Будь дружелюбным и полезным.
Помогай с выбором товаров и услуг.
"""
                        
                        # Make direct OpenAI call with ChatCompletion API
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": message}
                            ],
                            max_tokens=800,
                            temperature=0.7
                        )
                        
                        return response.choices[0].message.content.strip()
                
                except Exception as assistant_error:
                    current_app.logger.error(f"Assistant API call failed, falling back to ChatCompletion: {str(assistant_error)}")
                    # Fall through to ChatCompletion if Assistant API fails
            
            # Fallback to ChatCompletion API
            simple_prompt = f"You are a professional sales assistant for IZI.SOFT. Respond in {language} language. Be helpful and concise."
            
            # Make direct OpenAI call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": simple_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            current_app.logger.error(f"Direct OpenAI API call failed: {str(e)}")
            return self._get_static_fallback(language)
    
    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response when AI is unavailable"""
        # Try direct API call first
        if self.client:
            try:
                return self._direct_openai_call(
                    "Hello, can you help me with information about your products?", 
                    language
                )
            except:
                pass
                
        # Fall back to static responses if direct call fails
        return self._get_static_fallback(language)
    
    def _get_static_fallback(self, language: str) -> str:
        """Get static fallback responses"""
        fallback_responses = {
            'uk': "Вибачте, зараз я не можу відповісти. Спробуйте пізніше або зв'яжіться з нашою підтримкою.",
            'ru': "Извините, сейчас я не могу ответить. Попробуйте позже или свяжитесь с нашей поддержкой.",
            'de': "Entschuldigung, ich kann momentan nicht antworten. Versuchen Sie es später oder kontaktieren Sie unseren Support.",
            'en': "Sorry, I can't respond right now. Please try later or contact our support team."
        }
        
        return fallback_responses.get(language, fallback_responses['uk'])

def init_default_data():
    """Initialize default data for the application"""
    try:
        from app.extensions import db
        from app.models import SocialLink
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email=current_app.config['ADMIN_EMAIL'],
                is_admin=True
            )
            admin.set_password(current_app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
        
        # Create default categories if not exist
        if Category.query.count() == 0:
            default_categories = [
                {
                    'name_uk': 'Електроніка',
                    'name_ru': 'Электроника',
                    'name_de': 'Elektronik',
                    'name_en': 'Electronics',
                    'description_uk': 'Сучасні електронні пристрої та гаджети',
                    'description_ru': 'Современные электронные устройства и гаджеты',
                    'description_de': 'Moderne elektronische Geräte und Gadgets',
                    'description_en': 'Modern electronic devices and gadgets'
                },
                {
                    'name_uk': 'Одяг',
                    'name_ru': 'Одежда',
                    'name_de': 'Kleidung',
                    'name_en': 'Clothing',
                    'description_uk': 'Модний та стильний одяг для всіх',
                    'description_ru': 'Модная и стильная одежда для всех',
                    'description_de': 'Modische und stilvolle Kleidung für alle',
                    'description_en': 'Fashionable and stylish clothing for everyone'
                }
            ]
            
            for cat_data in default_categories:
                category = Category()
                category.name_uk = cat_data['name_uk']
                category.name_ru = cat_data['name_ru']
                category.name_de = cat_data['name_de'] 
                category.name_en = cat_data['name_en']
                category.description_uk = cat_data['description_uk']
                category.description_ru = cat_data['description_ru']
                category.description_de = cat_data['description_de']
                category.description_en = cat_data['description_en']
                category.slug = generate_slug(cat_data['name_en'])
                category.is_active = True
                db.session.add(category)
        
        # Create default social links if not exist
        if SocialLink.query.count() == 0:
            default_social_links = [
                {
                    'name': 'Facebook', 
                    'url': 'https://facebook.com', 
                    'icon': 'fab fa-facebook'
                },
                {
                    'name': 'Twitter', 
                    'url': 'https://twitter.com', 
                    'icon': 'fab fa-twitter'
                },
                {
                    'name': 'Instagram', 
                    'url': 'https://instagram.com', 
                    'icon': 'fab fa-instagram'
                }
            ]
            
            for link_data in default_social_links:
                link = SocialLink()
                link.name = link_data['name']
                link.url = link_data['url']
                link.icon = link_data['icon']
                db.session.add(link)
        
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Error initializing default data: {str(e)}")
        db.session.rollback()


def cleanup_old_chat_threads(days_old: int = 7):
    """Clean up chat threads older than specified days"""
    try:
        from app.models import ChatThread
        from app.extensions import db
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days_old)
        old_threads = ChatThread.query.filter(ChatThread.updated_at < cutoff_date).all()
        
        for thread in old_threads:
            db.session.delete(thread)
        
        db.session.commit()
        return len(old_threads)
    except Exception as e:
        current_app.logger.error(f"Error cleaning up old chat threads: {str(e)}")
        return 0
