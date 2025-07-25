# Добавим эти маршруты в файл routes.py

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
