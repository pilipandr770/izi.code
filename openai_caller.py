#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenAI caller script for subprocess calls
"""

import sys
import json
import os

def main():
    if len(sys.argv) != 5:
        print(json.dumps({"success": False, "error": "Invalid arguments"}))
        return
    
    api_key = sys.argv[1]
    topic = sys.argv[2]
    language = sys.argv[3]
    keywords = sys.argv[4]
    
    # Set UTF-8 environment
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Force reload openai
    if 'openai' in sys.modules:
        del sys.modules['openai']
    
    try:
        import openai
        openai.api_key = api_key
        
        # Language-specific prompts
        prompts = {
            'uk': {
                'system': 'Ти досвідчений копірайтер українською мовою.',
                'user': f'Напиши статтю про {topic}. Ключові слова: {keywords}. Структуруй текст з заголовком.'
            },
            'ru': {
                'system': 'Ты опытный копирайтер на русском языке.',
                'user': f'Напиши статью про {topic}. Ключевые слова: {keywords}. Структурируй текст с заголовком.'
            },
            'de': {
                'system': 'Du bist ein erfahrener Copywriter auf Deutsch.',
                'user': f'Schreibe einen Artikel über {topic}. Schlüsselwörter: {keywords}. Strukturiere den Text mit Titel.'
            },
            'en': {
                'system': 'You are an experienced copywriter in English.',
                'user': f'Write an article about {topic}. Keywords: {keywords}. Structure the text with title.'
            }
        }
        
        prompt = prompts.get(language, prompts['en'])
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt['system']},
                {"role": "user", "content": prompt['user']}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        # Simple parsing
        lines = content.split('\n', 1)
        title = lines[0].replace('#', '').strip() if lines else topic
        full_content = content
        excerpt = content[:200] + '...' if len(content) > 200 else content
        
        result = {
            "success": True,
            "title": title,
            "excerpt": excerpt,
            "content": full_content
        }
        
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "title": f"Article about {topic}",
            "excerpt": f"Learn about {topic}",
            "content": f"<h2>About {topic}</h2><p>Content about {topic} with keywords: {keywords}</p>"
        }
        print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
