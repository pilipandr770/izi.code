from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, current_app
from flask_babel import gettext as _
from app.extensions import db
from app.models import Category, Product, BlogPost, HomePageBlock, SocialLink, User
from app.forms import CategoryForm, ProductForm, BlogPostForm, AIBlogPostForm, HomePageBlockForm, SocialLinkForm
from app.utils import save_uploaded_file, delete_file, AIContentGenerator, generate_slug, create_stripe_price
from app.content_generator import ContentGenerator
import os

admin_routes = Blueprint('admin_routes', __name__)

def require_admin():
    """Decorator to require admin login"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    return None

@admin_routes.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            # Save image if uploaded
            image_filename = None
            if form.image.data and hasattr(form.image.data, 'filename'):
                image_filename = save_uploaded_file(form.image.data, 'categories')
            
            # Generate slug from Ukrainian name as primary
            slug = generate_slug(form.name_uk.data)
            
            # Ensure slug is unique
            existing_category = Category.query.filter_by(slug=slug).first()
            if existing_category:
                counter = 1
                while Category.query.filter_by(slug=f"{slug}-{counter}").first():
                    counter += 1
                slug = f"{slug}-{counter}"
            
            category = Category(
                name_uk=form.name_uk.data,
                name_ru=form.name_ru.data,
                name_de=form.name_de.data,
                name_en=form.name_en.data,
                description_uk=form.description_uk.data,
                description_ru=form.description_ru.data,
                description_de=form.description_de.data,
                description_en=form.description_en.data,
                slug=slug,
                image=image_filename,
                is_active=form.is_active.data,
                sort_order=form.sort_order.data
            )
            
            db.session.add(category)
            db.session.commit()
            
            flash(_('Category created successfully!'), 'success')
            return redirect(url_for('admin.categories'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating category: {str(e)}")
            flash(_('Error creating category'), 'error')
    
    return render_template('admin/category_form.html', form=form, action='add')

@admin_routes.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        try:
            # Handle image upload/update
            if form.image.data and hasattr(form.image.data, 'filename'):
                # Delete old image if exists
                if category.image:
                    delete_file(category.image)
                category.image = save_uploaded_file(form.image.data, 'categories')
            
            # Update category fields
            category.name_uk = form.name_uk.data
            category.name_ru = form.name_ru.data
            category.name_de = form.name_de.data
            category.name_en = form.name_en.data
            category.description_uk = form.description_uk.data
            category.description_ru = form.description_ru.data
            category.description_de = form.description_de.data
            category.description_en = form.description_en.data
            
            # Update slug only if name changed
            new_slug = generate_slug(form.name_uk.data)
            if new_slug != category.slug:
                # Ensure slug is unique
                existing_category = Category.query.filter_by(slug=new_slug).filter(Category.id != category.id).first()
                if existing_category:
                    counter = 1
                    while Category.query.filter_by(slug=f"{new_slug}-{counter}").filter(Category.id != category.id).first():
                        counter += 1
                    new_slug = f"{new_slug}-{counter}"
                category.slug = new_slug
            
            category.is_active = form.is_active.data
            category.sort_order = form.sort_order.data
            
            db.session.commit()
            
            flash(_('Category updated successfully!'), 'success')
            return redirect(url_for('admin.categories'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating category: {str(e)}")
            flash(_('Error updating category'), 'error')
    
    return render_template('admin/category_form.html', form=form, category=category, action='edit')

@admin_routes.route('/products/add', methods=['GET', 'POST'])
def add_product():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    form = ProductForm()
    # Populate category choices
    form.category_id.choices = [(c.id, c.name_uk) for c in Category.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        try:
            # Save image if uploaded
            image_filename = None
            if form.image.data and hasattr(form.image.data, 'filename'):
                image_filename = save_uploaded_file(form.image.data, 'products')
            
            # Create Stripe price
            stripe_price_id = create_stripe_price(
                form.name_uk.data,
                form.price.data,
                form.currency.data
            )
            
            # Generate slug from Ukrainian name
            slug = generate_slug(form.name_uk.data)
            
            # Ensure slug is unique
            existing_product = Product.query.filter_by(slug=slug).first()
            if existing_product:
                counter = 1
                while Product.query.filter_by(slug=f"{slug}-{counter}").first():
                    counter += 1
                slug = f"{slug}-{counter}"
            
            product = Product(
                name_uk=form.name_uk.data,
                name_ru=form.name_ru.data,
                name_de=form.name_de.data,
                name_en=form.name_en.data,
                description_uk=form.description_uk.data,
                description_ru=form.description_ru.data,
                description_de=form.description_de.data,
                description_en=form.description_en.data,
                price=form.price.data,
                currency=form.currency.data,
                slug=slug,
                category_id=form.category_id.data,
                image=image_filename,
                is_active=form.is_active.data,
                sort_order=form.sort_order.data,
                stripe_price_id=stripe_price_id
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash(_('Product created successfully!'), 'success')
            return redirect(url_for('admin.products'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating product: {str(e)}")
            flash(_('Error creating product'), 'error')
    
    return render_template('admin/product_form.html', form=form, action='add')

@admin_routes.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    # Populate category choices
    form.category_id.choices = [(c.id, c.name_uk) for c in Category.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        try:
            # Handle image upload/update
            if form.image.data and hasattr(form.image.data, 'filename'):
                # Delete old image if exists
                if product.image:
                    delete_file(product.image)
                product.image = save_uploaded_file(form.image.data, 'products')
            
            # Update product fields
            product.name_uk = form.name_uk.data
            product.name_ru = form.name_ru.data
            product.name_de = form.name_de.data
            product.name_en = form.name_en.data
            product.description_uk = form.description_uk.data
            product.description_ru = form.description_ru.data
            product.description_de = form.description_de.data
            product.description_en = form.description_en.data
            product.price = form.price.data
            product.currency = form.currency.data
            product.category_id = form.category_id.data
            product.is_active = form.is_active.data
            product.sort_order = form.sort_order.data
            
            # Update slug only if name changed
            new_slug = generate_slug(form.name_uk.data)
            if new_slug != product.slug:
                # Ensure slug is unique
                existing_product = Product.query.filter_by(slug=new_slug).filter(Product.id != product.id).first()
                if existing_product:
                    counter = 1
                    while Product.query.filter_by(slug=f"{new_slug}-{counter}").filter(Product.id != product.id).first():
                        counter += 1
                    new_slug = f"{new_slug}-{counter}"
                product.slug = new_slug
            
            # Update Stripe price if price changed
            if product.stripe_price_id and product.price != form.price.data:
                new_stripe_price_id = create_stripe_price(
                    form.name_uk.data,
                    form.price.data,
                    form.currency.data
                )
                if new_stripe_price_id:
                    product.stripe_price_id = new_stripe_price_id
            
            db.session.commit()
            
            flash(_('Product updated successfully!'), 'success')
            return redirect(url_for('admin.products'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating product: {str(e)}")
            flash(_('Error updating product'), 'error')
    
    return render_template('admin/product_form.html', form=form, product=product, action='edit')

@admin_routes.route('/blog/add', methods=['GET', 'POST'])
def add_blog_post():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    ai_mode = request.args.get('ai', '0') == '1'
    
    if ai_mode:
        form = AIBlogPostForm()
        if form.validate_on_submit():
            current_app.logger.info("AI form submitted, processing...")
            try:
                # Определяем основной язык и тему
                primary_language = 'en' if form.topic_en.data else 'uk'
                topic = form.topic_en.data or form.topic_uk.data
                keywords = form.keywords.data or ''
                auto_publish = form.auto_publish.data
                
                generator = ContentGenerator()
                all_langs = generator.generate_multilingual_post(primary_language, topic, keywords)
                
                slug = generate_slug(all_langs['en']['title'] if all_langs.get('en') else topic)
                existing_post = BlogPost.query.filter_by(slug=slug).first()
                if existing_post:
                    counter = 1
                    while BlogPost.query.filter_by(slug=f"{slug}-{counter}").first():
                        counter += 1
                    slug = f"{slug}-{counter}"
                
                blog_post = BlogPost(
                    # Основные поля берем из primary_language
                    title=all_langs[primary_language]['title'],
                    content=all_langs[primary_language]['content'],
                    excerpt=all_langs[primary_language]['excerpt'],
                    # Мультиязычные поля
                    title_uk=all_langs['uk']['title'],
                    title_ru=all_langs['ru']['title'],
                    title_de=all_langs['de']['title'],
                    title_en=all_langs['en']['title'],
                    content_uk=all_langs['uk']['content'],
                    content_ru=all_langs['ru']['content'],
                    content_de=all_langs['de']['content'],
                    content_en=all_langs['en']['content'],
                    excerpt_uk=all_langs['uk']['excerpt'],
                    excerpt_ru=all_langs['ru']['excerpt'],
                    excerpt_de=all_langs['de']['excerpt'],
                    excerpt_en=all_langs['en']['excerpt'],
                    slug=slug,
                    is_published=auto_publish,
                    author_id=session.get('admin_user_id')
                )
                db.session.add(blog_post)
                db.session.commit()
                current_app.logger.info(f"AI blog post created and translated with ID: {blog_post.id}")
                flash(_('AI blog post created and translated!'), 'success')
                return redirect(url_for('admin.blog'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error creating AI blog post: {str(e)}")
                flash(_('Error creating AI blog post'), 'error')
        return render_template('admin/ai_blog_form.html', form=form, action='add')
    else:
        # Regular blog post form
        form = BlogPostForm()
    
    if form.validate_on_submit():
        try:
            # Save image if uploaded
            image_filename = None
            if form.image.data and hasattr(form.image.data, 'filename'):
                image_filename = save_uploaded_file(form.image.data, 'blog')
            
            # Generate slug if not provided
            slug = form.slug.data
            if not slug:
                slug = generate_slug(form.title_uk.data)
            
            # Ensure slug is unique
            existing_post = BlogPost.query.filter_by(slug=slug).first()
            if existing_post:
                counter = 1
                while BlogPost.query.filter_by(slug=f"{slug}-{counter}").first():
                    counter += 1
                slug = f"{slug}-{counter}"
            
            current_app.logger.info(f"Creating blog post with title: {form.title_uk.data}")
            current_app.logger.info(f"Published status: {form.is_published.data}")
            
            blog_post = BlogPost(
                # Основные поля (обычно будем использовать украинский как основной)
                title=form.title_uk.data,
                content=form.content_uk.data,
                excerpt=form.excerpt_uk.data,
                # Мультиязычные поля
                title_uk=form.title_uk.data,
                title_ru=form.title_ru.data,
                title_de=form.title_de.data,
                title_en=form.title_en.data,
                content_uk=form.content_uk.data,
                content_ru=form.content_ru.data,
                content_de=form.content_de.data,
                content_en=form.content_en.data,
                excerpt_uk=form.excerpt_uk.data,
                excerpt_ru=form.excerpt_ru.data,
                excerpt_de=form.excerpt_de.data,
                excerpt_en=form.excerpt_en.data,
                slug=slug,
                image=image_filename,
                is_published=form.is_published.data,
                author_id=session.get('admin_user_id')
            )
            
            db.session.add(blog_post)
            db.session.commit()
            
            current_app.logger.info(f"Blog post created successfully with ID: {blog_post.id}")
            flash(_('Blog post created successfully!'), 'success')
            return redirect(url_for('admin.blog'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating blog post: {str(e)}")
            flash(_('Error creating blog post'), 'error')
    
    return render_template('admin/blog_post_form.html', form=form, action='add')

@admin_routes.route('/generate-ai-post', methods=['POST'])
def generate_ai_post():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        current_app.logger.info("Starting AI post generation...")
        
        # Get form data
        topics = {
            'uk': request.form.get('topic_uk', ''),
            'ru': request.form.get('topic_ru', ''),
            'de': request.form.get('topic_de', ''),
            'en': request.form.get('topic_en', '')
        }
        keywords = request.form.get('keywords', '')
        auto_publish = request.form.get('auto_publish') == 'on'
        
        current_app.logger.info(f"Topics: {topics}")
        current_app.logger.info(f"Auto publish: {auto_publish}")
        
        # Generate AI content
        ai_generator = AIContentGenerator()
        generated_content = ai_generator.generate_multilingual_post(topics, keywords)
        
        current_app.logger.info(f"Generated content keys: {generated_content.keys()}")
        
        # Create blog post
        slug = generate_slug(generated_content.get('uk', {}).get('title', topics['uk']))
        
        # Ensure slug is unique
        existing_post = BlogPost.query.filter_by(slug=slug).first()
        if existing_post:
            counter = 1
            while BlogPost.query.filter_by(slug=f"{slug}-{counter}").first():
                counter += 1
            slug = f"{slug}-{counter}"
        
        blog_post = BlogPost(
            # Основные поля
            title=generated_content.get('uk', {}).get('title', topics['uk']),
            content=generated_content.get('uk', {}).get('content', ''),
            excerpt=generated_content.get('uk', {}).get('excerpt', ''),
            # Мультиязычные поля
            title_uk=generated_content.get('uk', {}).get('title', topics['uk']),
            title_ru=generated_content.get('ru', {}).get('title', topics['ru']),
            title_de=generated_content.get('de', {}).get('title', topics['de']),
            title_en=generated_content.get('en', {}).get('title', topics['en']),
            content_uk=generated_content.get('uk', {}).get('content', ''),
            content_ru=generated_content.get('ru', {}).get('content', ''),
            content_de=generated_content.get('de', {}).get('content', ''),
            content_en=generated_content.get('en', {}).get('content', ''),
            excerpt_uk=generated_content.get('uk', {}).get('excerpt', ''),
            excerpt_ru=generated_content.get('ru', {}).get('excerpt', ''),
            excerpt_de=generated_content.get('de', {}).get('excerpt', ''),
            excerpt_en=generated_content.get('en', {}).get('excerpt', ''),
            slug=slug,
            is_published=auto_publish,
            author_id=session.get('admin_user_id')
        )
        
        db.session.add(blog_post)
        db.session.commit()
        
        current_app.logger.info(f"AI blog post created successfully with ID: {blog_post.id}")
        return jsonify({'success': True, 'post_id': blog_post.id})
        
    except Exception as e:
        current_app.logger.error(f"Error generating AI post: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@admin_routes.route('/homepage/add', methods=['GET', 'POST'])
def add_homepage_block():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    form = HomePageBlockForm()
    
    if form.validate_on_submit():
        try:
            # Save image if uploaded
            image_filename = None
            if form.image.data and hasattr(form.image.data, 'filename'):
                image_filename = save_uploaded_file(form.image.data, 'homepage')
            
            block = HomePageBlock(
                title_uk=form.title_uk.data,
                title_ru=form.title_ru.data,
                title_de=form.title_de.data,
                title_en=form.title_en.data,
                block_type=form.block_type.data,
                css_class=form.css_class.data,
                image=image_filename,
                is_active=form.is_active.data,
                sort_order=form.sort_order.data
            )
            
            db.session.add(block)
            db.session.commit()
            
            flash(_('Homepage block created successfully!'), 'success')
            return redirect(url_for('admin.homepage'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating homepage block: {str(e)}")
            flash(_('Error creating homepage block'), 'error')
    
    return render_template('admin/homepage_form.html', form=form, action='add')

@admin_routes.route('/social', methods=['GET'])
def social():
    """Social links management page"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    links = SocialLink.query.order_by(SocialLink.sort_order).all()
    return render_template('admin/social.html', links=links)

@admin_routes.route('/social/add', methods=['GET', 'POST'])
def add_social_link():
    """Add new social link"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    form = SocialLinkForm()
    
    if form.validate_on_submit():
        try:
            # Determine icon class if standard platform selected
            icon_class = form.icon_class.data
            if not icon_class and form.platform.data != 'other':
                # Default icons for common platforms
                platform_icons = {
                    'facebook': 'fab fa-facebook',
                    'instagram': 'fab fa-instagram',
                    'twitter': 'fab fa-twitter',
                    'youtube': 'fab fa-youtube',
                    'tiktok': 'fab fa-tiktok',
                    'linkedin': 'fab fa-linkedin',
                    'pinterest': 'fab fa-pinterest',
                    'telegram': 'fab fa-telegram',
                    'whatsapp': 'fab fa-whatsapp',
                    'viber': 'fab fa-viber',
                    'snapchat': 'fab fa-snapchat',
                    'discord': 'fab fa-discord'
                }
                icon_class = platform_icons.get(form.platform.data, 'fas fa-link')
            
            social_link = SocialLink(
                name=form.name.data,
                platform=form.platform.data,
                url=form.url.data,
                icon_class=icon_class,
                is_active=form.is_active.data,
                sort_order=form.sort_order.data
            )
            
            db.session.add(social_link)
            db.session.commit()
            
            flash(_('Social link created successfully!'), 'success')
            return redirect(url_for('admin_routes.social'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating social link: {str(e)}")
            flash(_('Error creating social link'), 'error')
    
    return render_template('admin/social_form.html', form=form, action='add')

@admin_routes.route('/social/edit/<int:id>', methods=['GET', 'POST'])
def edit_social_link(id):
    """Edit existing social link"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    social_link = SocialLink.query.get_or_404(id)
    form = SocialLinkForm(obj=social_link)
    
    if form.validate_on_submit():
        try:
            social_link.name = form.name.data
            social_link.platform = form.platform.data
            social_link.url = form.url.data
            social_link.icon_class = form.icon_class.data
            social_link.is_active = form.is_active.data
            social_link.sort_order = form.sort_order.data
            
            db.session.commit()
            
            flash(_('Social link updated successfully!'), 'success')
            return redirect(url_for('admin_routes.social'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating social link: {str(e)}")
            flash(_('Error updating social link'), 'error')
    
    return render_template('admin/social_form.html', form=form, action='edit')

@admin_routes.route('/social/delete/<int:id>', methods=['POST'])
def delete_social_link(id):
    """Delete social link"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    social_link = SocialLink.query.get_or_404(id)
    
    try:
        db.session.delete(social_link)
        db.session.commit()
        flash(_('Social link deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting social link: {str(e)}")
        flash(_('Error deleting social link'), 'error')
    
    return redirect(url_for('admin_routes.social'))

# Delete routes
@admin_routes.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        category = Category.query.get_or_404(category_id)
        
        # Delete associated image
        if category.image:
            delete_file(category.image)
        
        db.session.delete(category)
        db.session.commit()
        
        flash(_('Category deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting category: {str(e)}")
        flash(_('Error deleting category'), 'error')
    
    return redirect(url_for('admin.categories'))

@admin_routes.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        product = Product.query.get_or_404(product_id)
        
        # Delete associated image
        if product.image:
            delete_file(product.image)
        
        db.session.delete(product)
        db.session.commit()
        
        flash(_('Product deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting product: {str(e)}")
        flash(_('Error deleting product'), 'error')
    
    return redirect(url_for('admin.products'))

@admin_routes.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_blog_post(post_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    post = BlogPost.query.get_or_404(post_id)
    form = BlogPostForm()
    
    if form.validate_on_submit():
        try:
            # Save image if uploaded
            image_filename = post.image
            if form.image.data and hasattr(form.image.data, 'filename'):
                image_filename = save_uploaded_file(form.image.data, 'blog')
            
            # Generate slug from title_uk if provided
            slug = post.slug
            if form.title_uk.data and form.title_uk.data != post.title_uk:
                slug = generate_slug(form.title_uk.data)
                # Check for duplicate slugs
                existing_post = BlogPost.query.filter_by(slug=slug).filter(BlogPost.id != post_id).first()
                if existing_post:
                    counter = 1
                    while BlogPost.query.filter_by(slug=f"{slug}-{counter}").filter(BlogPost.id != post_id).first():
                        counter += 1
                    slug = f"{slug}-{counter}"
            
            # Update post fields
            post.title_uk = form.title_uk.data
            post.title_ru = form.title_ru.data
            post.title_de = form.title_de.data
            post.content_uk = form.content_uk.data
            post.content_ru = form.content_ru.data
            post.content_de = form.content_de.data
            post.excerpt_uk = form.excerpt_uk.data
            post.excerpt_ru = form.excerpt_ru.data
            post.excerpt_de = form.excerpt_de.data
            post.slug = slug
            post.image = image_filename
            post.is_published = form.is_published.data
            
            db.session.commit()
            
            flash(_('Blog post updated successfully!'), 'success')
            return redirect(url_for('admin.blog'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating blog post: {str(e)}")
            flash(_('Error updating blog post'), 'error')
    else:
        # Populate form with existing data
        form.title_uk.data = post.title_uk
        form.title_ru.data = post.title_ru
        form.title_de.data = post.title_de
        form.content_uk.data = post.content_uk
        form.content_ru.data = post.content_ru
        form.content_de.data = post.content_de
        form.excerpt_uk.data = post.excerpt_uk
        form.excerpt_ru.data = post.excerpt_ru
        form.excerpt_de.data = post.excerpt_de
        form.is_published.data = post.is_published
    
    return render_template('admin/blog_post_form.html', form=form, post=post, action='edit')

@admin_routes.route('/blog/delete/<int:post_id>', methods=['POST'])
def delete_blog_post(post_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        post = BlogPost.query.get_or_404(post_id)
        
        # Delete associated image file if exists
        if post.image:
            try:
                image_path = os.path.join(current_app.static_folder, 'uploads', 'blog', post.image)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                current_app.logger.warning(f"Could not delete image file: {str(e)}")
        
        db.session.delete(post)
        db.session.commit()
        
        flash(_('Blog post deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting blog post: {str(e)}")
        flash(_('Error deleting blog post'), 'error')
    
    return redirect(url_for('admin.blog'))
