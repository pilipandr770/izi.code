import os
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from flask_babel import gettext as _, ngettext
from app.extensions import db
from app.models import Category, Product, BlogPost, HomePageBlock, SocialLink, Order, OrderItem, User, ChatThread
from app.forms import ContactForm, LoginForm
from app.utils import get_current_language, create_checkout_session, ChatbotAssistant
from werkzeug.security import check_password_hash

# Create blueprints
main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__)
api_bp = Blueprint('api', __name__)

# Main routes
@main_bp.route('/')
def index():
    """Home page with customizable blocks"""
    language = get_current_language()
    
    # Get active home page blocks
    blocks = HomePageBlock.query.filter_by(is_active=True).order_by(HomePageBlock.sort_order).all()
    
    # Get latest blog posts for preview
    latest_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    
    # Get featured products
    featured_products = Product.query.filter_by(is_active=True).order_by(Product.sort_order).limit(6).all()
    
    # Get social links
    social_links = SocialLink.query.filter_by(is_active=True).order_by(SocialLink.sort_order).all()
    
    return render_template('index.html',
                         blocks=blocks,
                         latest_posts=latest_posts,
                         featured_products=featured_products,
                         social_links=social_links,
                         language=language)

@main_bp.route('/set_language/<language>')
def set_language(language):
    """Set user language"""
    if language in current_app.config['LANGUAGES']:
        session['language'] = language
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/shop')
def shop():
    """Shop page with categories"""
    language = get_current_language()
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template('shop/categories.html', categories=categories, language=language)

@main_bp.route('/shop/category/<int:category_id>')
def category_products(category_id):
    """Products in category"""
    language = get_current_language()
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id, is_active=True).order_by(Product.sort_order).all()
    return render_template('shop/products.html', category=category, products=products, language=language)

@main_bp.route('/shop/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    language = get_current_language()
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter_by(category_id=product.category_id, is_active=True).filter(Product.id != product_id).limit(4).all()
    return render_template('shop/product_detail.html', product=product, related_products=related_products, language=language)

@main_bp.route('/blog')
def blog():
    """Blog page"""
    language = get_current_language()
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('blog/index.html', posts=posts, language=language, categories=categories)

@main_bp.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post"""
    language = get_current_language()
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    categories = Category.query.all()
    recent_posts = BlogPost.query.filter_by(is_published=True).filter(BlogPost.id != post.id).order_by(BlogPost.created_at.desc()).limit(5).all()
    return render_template('blog/post.html', post=post, language=language, categories=categories, recent_posts=recent_posts)

@main_bp.route('/blog/category/<category_slug>')
def blog_category(category_slug):
    """Blog posts by category - redirecting to all blog posts since posts don't have categories"""
    return redirect(url_for('main.blog'))

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    language = get_current_language()
    form = ContactForm()
    
    if form.validate_on_submit():
        # Here you would typically send an email or save to database
        flash(_('Thank you for your message! We will get back to you soon.'), 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html', form=form, language=language)

@main_bp.route('/checkout', methods=['POST'])
def checkout():
    """Create Stripe checkout session"""
    try:
        cart_items = request.json.get('items', [])
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Prepare items for Stripe
        stripe_items = []
        for item in cart_items:
            product = Product.query.get(item['product_id'])
            if product and product.is_active:
                stripe_items.append({
                    'name': product.get_name(get_current_language()),
                    'description': product.get_description(get_current_language())[:100],
                    'price': product.price,
                    'currency': product.currency,
                    'quantity': item.get('quantity', 1)
                })
        
        if not stripe_items:
            return jsonify({'error': 'No valid items in cart'}), 400
        
        # Create checkout session
        session_id = create_checkout_session(
            items=stripe_items,
            success_url=url_for('main.checkout_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.shop', _external=True)
        )
        
        if session_id:
            # Handle demo mode
            if session_id.startswith('demo_'):
                # For demo mode, redirect immediately to success page
                return jsonify({
                    'session_id': session_id,
                    'demo_mode': True,
                    'redirect_url': url_for('main.checkout_success', _external=True) + f'?session_id={session_id}'
                })
            else:
                # Real Stripe session
                return jsonify({'session_id': session_id})
        else:
            return jsonify({'error': 'Failed to create checkout session'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Checkout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/checkout/success')
def checkout_success():
    """Checkout success page"""
    session_id = request.args.get('session_id')
    return render_template('checkout/success.html', session_id=session_id)

# Admin routes
@admin_bp.route('/')
def index():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    # Get statistics
    stats = {
        'total_products': Product.query.count(),
        'total_categories': Category.query.count(),
        'total_blog_posts': BlogPost.query.count(),
        'total_orders': Order.query.count()
    }
    
    return render_template('admin/index.html', stats=stats)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Прямая проверка без формы
        if username == 'admin' and password == 'admin123':
            user = User.query.filter_by(username='admin', is_admin=True).first()
            if user:
                session['admin_logged_in'] = True
                session['admin_user_id'] = user.id
                flash('Успешный вход в администрацию!', 'success')
                return redirect(url_for('admin.index'))
        
        flash('Неверные учетные данные', 'error')
    
    form = LoginForm()
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_user_id', None)
    flash(_('Logged out successfully'), 'success')
    return redirect(url_for('main.index'))

@admin_bp.route('/categories')
def categories():
    """Admin categories list"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/products')
def products():
    """Admin products list"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    products = Product.query.order_by(Product.sort_order).all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/blog')
def blog():
    """Admin blog posts list"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog.html', posts=posts)

@admin_bp.route('/homepage')
def homepage():
    """Admin homepage blocks"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    blocks = HomePageBlock.query.order_by(HomePageBlock.sort_order).all()
    return render_template('admin/homepage.html', blocks=blocks)

@admin_bp.route('/social')
def social():
    """Admin social links"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    links = SocialLink.query.order_by(SocialLink.sort_order).all()
    return render_template('admin/social.html', links=links)

@admin_bp.route('/chatbot')
def chatbot_admin():
    """Admin chatbot management"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    # Get chatbot statistics
    total_threads = ChatThread.query.count()
    active_threads = ChatThread.query.filter_by(is_active=True).count()
    recent_threads = ChatThread.query.order_by(ChatThread.updated_at.desc()).limit(10).all()
    
    stats = {
        'total_threads': total_threads,
        'active_threads': active_threads,
        'recent_threads': recent_threads
    }
    
    return render_template('admin/chatbot.html', stats=stats)

@admin_bp.route('/chatbot/cleanup', methods=['POST'])
def chatbot_cleanup():
    """Clean up old chat threads"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    try:
        from app.utils import cleanup_old_chat_threads
        cleanup_old_chat_threads(days_old=7)
        flash('Старые чаты успешно очищены!', 'success')
    except Exception as e:
        flash(f'Ошибка при очистке: {str(e)}', 'error')
    
    return redirect(url_for('admin.chatbot_admin'))

# API routes
@api_bp.route('/chatbot', methods=['POST'])
def chatbot():
    """Chatbot API endpoint"""
    try:
        data = request.json
        message = data.get('message', '')
        language = data.get('language', 'uk')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Generate or get session ID for thread management
        session_id = request.cookies.get('session_id') or request.headers.get('X-Session-ID')
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        chatbot = ChatbotAssistant()
        response = chatbot.get_response(message, session_id, language)
        
        return jsonify({
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Chatbot API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/products')
def products():
    """API endpoint for products"""
    language = request.args.get('language', 'uk')
    category_id = request.args.get('category_id', type=int)
    
    query = Product.query.filter_by(is_active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.order_by(Product.sort_order).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.get_name(language),
        'description': p.get_description(language),
        'price': p.price,
        'currency': p.currency,
        'image': p.image,
        'category_id': p.category_id
    } for p in products])

@api_bp.route('/categories')
def categories():
    """API endpoint for categories"""
    language = request.args.get('language', 'uk')
    
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.get_name(language),
        'description': c.get_description(language),
        'image': c.image
    } for c in categories])


@main_bp.route('/privacy')
def privacy():
    """Privacy Policy page"""
    language = get_current_language()
    social_links = SocialLink.query.filter_by(is_active=True).order_by(SocialLink.sort_order).all()
    return render_template('privacy.html', language=language, social_links=social_links)


@main_bp.route('/terms')
def terms():
    """Terms and Conditions page"""
    language = get_current_language()
    social_links = SocialLink.query.filter_by(is_active=True).order_by(SocialLink.sort_order).all()
    return render_template('terms.html', language=language, social_links=social_links)


@main_bp.route('/impressum')
def impressum():
    """Impressum page"""
    language = get_current_language()
    social_links = SocialLink.query.filter_by(is_active=True).order_by(SocialLink.sort_order).all()
    return render_template('impressum.html', language=language, social_links=social_links)
