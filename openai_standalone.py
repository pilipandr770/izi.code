#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Standalone OpenAI function for Flask app
"""

import os
import sys

def call_openai_standalone(api_key: str, topic: str, language: str, keywords: str = '') -> dict:
    """Standalone OpenAI call function isolated from Flask context"""
    
    # Set environment variables for proper encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSFSENCODING'] = '0'
    
    # Ensure proper locale for Windows
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass
    
    # Force reload openai to ensure clean state
    if 'openai' in sys.modules:
        del sys.modules['openai']
        
    import openai
    
    try:
        # Set API key
        openai.api_key = api_key
        
        # Ensure all strings are properly encoded as UTF-8
        topic_safe = str(topic).encode('utf-8').decode('utf-8')
        keywords_safe = str(keywords).encode('utf-8').decode('utf-8')
        language_safe = str(language).encode('utf-8').decode('utf-8')
        
        # Language-specific prompts with proper encoding
        prompts = {
            'uk': {
                'system': 'Ти досвідчений копірайтер, який пише SEO-оптимізовані статті українською мовою.',
                'user': f'Напиши детальну статтю про "{topic_safe}". Ключові слова: {keywords_safe}. Стаття повинна бути структурованою, корисною та цікавою. Створи заголовок, короткий опис та повний контент з HTML розміткою.'
            },
            'ru': {
                'system': 'Ты опытный копирайтер, который пишет SEO-оптимизированные статьи на русском языке.',
                'user': f'Напиши подробную статью про "{topic_safe}". Ключевые слова: {keywords_safe}. Статья должна быть структурированной, полезной и интересной. Создай заголовок, краткое описание и полный контент с HTML разметкой.'
            },
            'de': {
                'system': 'Du bist ein erfahrener Copywriter, der SEO-optimierte Artikel auf Deutsch schreibt.',
                'user': f'Schreibe einen detaillierten Artikel über "{topic_safe}". Schlüsselwörter: {keywords_safe}. Der Artikel sollte strukturiert, nützlich und interessant sein. Erstelle einen Titel, eine kurze Beschreibung und den vollständigen Inhalt mit HTML-Markup.'
            },
            'en': {
                'system': 'You are an experienced copywriter who writes SEO-optimized articles in English.',
                'user': f'Write a detailed article about "{topic_safe}". Keywords: {keywords_safe}. The article should be structured, useful and interesting. Create a title, brief description and full content with HTML markup.'
            }
        }
        
        prompt = prompts.get(language_safe, prompts['uk'])
        
        # Make the API call with proper encoding
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt['system']},
                {"role": "user", "content": prompt['user']}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse the response to extract title, excerpt, and content
        lines = content.split('\n')
        title = topic_safe  # Default title
        excerpt = f"Стаття про {topic_safe}"  # Default excerpt
        
        # Try to extract title from first line if it looks like a title
        if lines and (lines[0].startswith('#') or len(lines[0]) < 100):
            title = lines[0].replace('#', '').strip()
            content = '\n'.join(lines[1:]).strip()
        
        # Extract excerpt from first paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if paragraphs:
            excerpt = paragraphs[0][:200] + '...' if len(paragraphs[0]) > 200 else paragraphs[0]
        
        return {
            'success': True,
            'title': title,
            'excerpt': excerpt,
            'content': content
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'title': f"Article about {topic}",
            'excerpt': f"Learn about {topic}",
            'content': f"<h2>About {topic}</h2><p>This is a comprehensive guide about {topic}. Keywords: {keywords}</p>"
        }

if __name__ == "__main__":
    # Test the function
    api_key = "your-openai-api-key-here"
    
    result = call_openai_standalone(api_key, "роботи", "uk", "AI")
    print("Result:", result)
