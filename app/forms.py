from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, SelectField, BooleanField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    """Admin login form"""
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField(_l('Password'), validators=[DataRequired()])

class CategoryForm(FlaskForm):
    """Category creation/edit form"""
    name_uk = StringField(_l('Name (Ukrainian)'), validators=[DataRequired(), Length(max=100)])
    name_ru = StringField(_l('Name (Russian)'), validators=[DataRequired(), Length(max=100)])
    name_de = StringField(_l('Name (German)'), validators=[DataRequired(), Length(max=100)])
    name_en = StringField(_l('Name (English)'), validators=[Optional(), Length(max=100)])
    description_uk = TextAreaField(_l('Description (Ukrainian)'))
    description_ru = TextAreaField(_l('Description (Russian)'))
    description_de = TextAreaField(_l('Description (German)'))
    description_en = TextAreaField(_l('Description (English)'))
    image = FileField(_l('Image'), validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    is_active = BooleanField(_l('Active'), default=True)
    sort_order = IntegerField(_l('Sort Order'), default=0, validators=[NumberRange(min=0)])

class ProductForm(FlaskForm):
    """Product creation/edit form"""
    name_uk = StringField(_l('Name (Ukrainian)'), validators=[DataRequired(), Length(max=200)])
    name_ru = StringField(_l('Name (Russian)'), validators=[DataRequired(), Length(max=200)])
    name_de = StringField(_l('Name (German)'), validators=[DataRequired(), Length(max=200)])
    name_en = StringField(_l('Name (English)'), validators=[Optional(), Length(max=200)])
    description_uk = TextAreaField(_l('Description (Ukrainian)'))
    description_ru = TextAreaField(_l('Description (Russian)'))
    description_de = TextAreaField(_l('Description (German)'))
    description_en = TextAreaField(_l('Description (English)'))
    price = FloatField(_l('Price'), validators=[DataRequired(), NumberRange(min=0.01)])
    currency = SelectField(_l('Currency'), choices=[('EUR', 'EUR'), ('USD', 'USD'), ('UAH', 'UAH')], default='EUR')
    category_id = SelectField(_l('Category'), coerce=int, validators=[DataRequired()])
    image = FileField(_l('Image'), validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    is_active = BooleanField(_l('Active'), default=True)
    sort_order = IntegerField(_l('Sort Order'), default=0, validators=[NumberRange(min=0)])

class BlogPostForm(FlaskForm):
    """Blog post creation/edit form"""
    title_uk = StringField(_l('Title (Ukrainian)'), validators=[DataRequired(), Length(max=200)])
    title_ru = StringField(_l('Title (Russian)'), validators=[DataRequired(), Length(max=200)])
    title_de = StringField(_l('Title (German)'), validators=[DataRequired(), Length(max=200)])
    title_en = StringField(_l('Title (English)'), validators=[Optional(), Length(max=200)])
    content_uk = TextAreaField(_l('Content (Ukrainian)'), validators=[DataRequired()])
    content_ru = TextAreaField(_l('Content (Russian)'), validators=[DataRequired()])
    content_de = TextAreaField(_l('Content (German)'), validators=[DataRequired()])
    content_en = TextAreaField(_l('Content (English)'))
    excerpt_uk = TextAreaField(_l('Excerpt (Ukrainian)'))
    excerpt_ru = TextAreaField(_l('Excerpt (Russian)'))
    excerpt_de = TextAreaField(_l('Excerpt (German)'))
    excerpt_en = TextAreaField(_l('Excerpt (English)'))
    slug = StringField(_l('URL Slug'), validators=[DataRequired(), Length(max=255)])
    image = FileField(_l('Image'), validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    is_published = BooleanField(_l('Published'), default=True)

class AIBlogPostForm(FlaskForm):
    """AI-generated blog post form"""
    topic_uk = StringField(_l('Topic (Ukrainian)'), validators=[DataRequired(), Length(max=200)])
    topic_ru = StringField(_l('Topic (Russian)'), validators=[DataRequired(), Length(max=200)])
    topic_de = StringField(_l('Topic (German)'), validators=[DataRequired(), Length(max=200)])
    topic_en = StringField(_l('Topic (English)'), validators=[Optional(), Length(max=200)])
    keywords = StringField(_l('SEO Keywords (comma separated)'), validators=[Optional()])
    auto_publish = BooleanField(_l('Auto Publish'), default=True)

class HomePageBlockForm(FlaskForm):
    """Home page block form"""
    title_uk = StringField(_l('Title (Ukrainian)'), validators=[DataRequired(), Length(max=200)])
    title_ru = StringField(_l('Title (Russian)'), validators=[DataRequired(), Length(max=200)])
    title_de = StringField(_l('Title (German)'), validators=[DataRequired(), Length(max=200)])
    title_en = StringField(_l('Title (English)'), validators=[Optional(), Length(max=200)])
    block_type = SelectField(_l('Block Type'), choices=[('blog', 'Blog'), ('shop', 'Shop')], validators=[DataRequired()])
    css_class = StringField(_l('CSS Class'), validators=[Optional(), Length(max=255)])
    image = FileField(_l('Image'), validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    is_active = BooleanField(_l('Active'), default=True)
    sort_order = IntegerField(_l('Sort Order'), default=0, validators=[NumberRange(min=0)])

class SocialLinkForm(FlaskForm):
    """Social media link form"""
    name = StringField(_l('Display Name'), validators=[DataRequired(), Length(max=50)])
    platform = SelectField(_l('Platform'), choices=[
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('linkedin', 'LinkedIn'),
        ('pinterest', 'Pinterest'),
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('viber', 'Viber'),
        ('snapchat', 'Snapchat'),
        ('discord', 'Discord'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    url = StringField(_l('URL'), validators=[DataRequired(), Length(max=255)])
    icon_class = StringField(_l('Icon CSS Class'), validators=[Length(max=100)])
    is_active = BooleanField(_l('Active'), default=True)
    sort_order = IntegerField(_l('Sort Order'), default=0, validators=[NumberRange(min=0)])

class ContactForm(FlaskForm):
    """Contact form"""
    name = StringField(_l('Name'), validators=[DataRequired(), Length(max=100)])
    email = StringField(_l('Email'), validators=[DataRequired(), Email(), Length(max=120)])
    subject = StringField(_l('Subject'), validators=[DataRequired(), Length(max=200)])
    message = TextAreaField(_l('Message'), validators=[DataRequired(), Length(max=1000)])
