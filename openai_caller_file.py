#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenAI caller script that reads arguments from file
"""

import sys
import json
import os

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"success": False, "error": "Invalid arguments"}))
        return
    
    args_file = sys.argv[1]
    
    try:
        # Read arguments from file with BOM handling
        with open(args_file, 'r', encoding='utf-8-sig') as f:
            args = json.load(f)
        
        api_key = args['api_key']
        topic = args['topic']
        language = args['language']
        keywords = args['keywords']
        
        # Set UTF-8 environment
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Force reload openai
        if 'openai' in sys.modules:
            del sys.modules['openai']
        
        import openai
        openai.api_key = api_key
        
        # Language-specific prompts
        prompts = {
            'uk': {
                'system': 'Ти досвідчений копірайтер українською мовою.',
                'user': f'Напиши статтю про "{topic}". Ключові слова: {keywords}. Структуруй текст з заголовком та абзацами.'
            },
            'ru': {
                'system': 'Ты опытный копирайтер на русском языке.',
                'user': f'Напиши статью про "{topic}". Ключевые слова: {keywords}. Структурируй текст с заголовком и абзацами.'
            },
            'de': {
                'system': 'Du bist ein erfahrener Copywriter auf Deutsch.',
                'user': f'Schreibe einen Artikel über "{topic}". Schlüsselwörter: {keywords}. Strukturiere den Text mit Titel und Absätzen.'
            },
            'en': {
                'system': 'You are an experienced copywriter in English.',
                'user': f'Write an article about "{topic}". Keywords: {keywords}. Structure the text with title and paragraphs.'
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
        lines = content.split('\n')
        title = lines[0].replace('#', '').replace('*', '').strip() if lines else topic
        full_content = content
        
        # Create excerpt from first paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        excerpt = paragraphs[0][:200] + '...' if paragraphs and len(paragraphs[0]) > 200 else (paragraphs[0] if paragraphs else f"Стаття про {topic}")
        
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
            "title": f"Article about {topic if 'topic' in locals() else 'technology'}",
            "excerpt": f"Learn about {topic if 'topic' in locals() else 'technology'}",
            "content": f"<h2>About {topic if 'topic' in locals() else 'technology'}</h2><p>Content about {topic if 'topic' in locals() else 'technology'} with keywords: {keywords if 'keywords' in locals() else 'tech'}</p>"
        }
        print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
