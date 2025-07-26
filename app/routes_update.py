# Добавим эти маршруты в файл routes.py

@main_bp.route('/privacy')
def privacy():
    """Privacy Policy page"""
    language = get_current_language()
    return render_template('privacy.html', language=language)

@main_bp.route('/terms')
def terms():
    """Terms and Conditions page"""
    language = get_current_language()
    return render_template('terms.html', language=language)

@main_bp.route('/impressum')
def impressum():
    """Impressum page"""
    language = get_current_language()
    return render_template('impressum.html', language=language)
