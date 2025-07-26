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
        
        # Language-specific prompts with improved structure guidance
        prompts = {
            'uk': {
                'system': 'Ти досвідчений копірайтер українською мовою. Твої статті мають природну структуру з HTML-тегами (h1, h2, h3) без Markdown-форматування. Твої тексти читаються як написані людиною.',
                'user': f'Напиши статтю про "{topic}" з ключовими словами: {keywords}. Правила: 1) Тільки HTML-теги для форматування; 2) НЕ додавай "Назва:", "Заголовок:" тощо на початку заголовків; 3) НЕ використовуй Markdown; 4) НЕ повторюй заголовок у першому абзаці; 5) Пиши як людина-журналіст; 6) Забезпеч плавні переходи між абзацами.'
            },
            'ru': {
                'system': 'Ты опытный копирайтер на русском языке. Твои статьи имеют естественную структуру с HTML-тегами (h1, h2, h3) без Markdown-форматирования. Твои тексты читаются как написанные человеком.',
                'user': f'Напиши статью о "{topic}" с ключевыми словами: {keywords}. Правила: 1) Только HTML-теги для форматирования; 2) НЕ добавляй "Название:", "Заголовок:" и т.п. в начале заголовков; 3) НЕ используй Markdown; 4) НЕ повторяй заголовок в первом абзаце; 5) Пиши как человек-журналист; 6) Обеспечь плавные переходы между абзацами.'
            },
            'de': {
                'system': 'Du bist ein erfahrener Copywriter auf Deutsch. Deine Artikel haben eine natürliche Struktur mit HTML-Tags (h1, h2, h3) ohne Markdown-Formatierung. Deine Texte lesen sich wie von Menschen geschrieben.',
                'user': f'Schreibe einen Artikel über "{topic}" mit Schlüsselwörtern: {keywords}. Regeln: 1) Nur HTML-Tags zur Formatierung; 2) KEINE "Titel:", "Überschrift:" am Anfang der Überschriften; 3) KEIN Markdown; 4) KEINE Wiederholung des Titels im ersten Absatz; 5) Schreibe wie ein Journalist; 6) Sorge für fließende Übergänge zwischen Absätzen.'
            },
            'en': {
                'system': 'You are an experienced copywriter in English. Your articles have a natural structure with HTML tags (h1, h2, h3) without Markdown formatting. Your texts read as if written by a human.',
                'user': f'Write an article about "{topic}" with keywords: {keywords}. Rules: 1) Only HTML tags for formatting; 2) NO "Title:", "Heading:" etc. at the beginning of headings; 3) NO Markdown; 4) DO NOT repeat the title in the first paragraph; 5) Write like a human journalist; 6) Ensure smooth transitions between paragraphs.'
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
        
        # Enhanced parsing with HTML-awareness
        import re
        
        # Clean up any formatting
        content = re.sub(r'\*([^*]*?)\*\s*', r'\1 ', content)  # Remove *text* formatting
        content = re.sub(r'[\*_]{2}([^*_]*?)[\*_]{2}', r'\1', content)  # Remove **text** formatting
        content = re.sub(r'#{1,3} (.*?)$', r'\1', content, flags=re.MULTILINE)  # Remove # headings
        
        # Remove title prefixes
        prefixes = ['Название', 'Заголовок', 'Тема', 'Назва', 'Title', 'Titel', 'Überschrift', 'Heading', 'Topic']
        for prefix in prefixes:
            # Remove prefix from lines
            content = re.sub(fr'^{prefix}:\s*(.+?)$', r'\1', content, flags=re.MULTILINE|re.IGNORECASE)
            # Remove prefix from HTML headings
            content = re.sub(fr'<h([1-3])>{prefix}:\s*', r'<h\1>', content, flags=re.IGNORECASE)
            # Clean heading parts
            content = re.sub(fr'<h([1-3])>([^<]{{0,3}}){prefix}[^<]{{0,3}}:\s*', r'<h\1>\2', content, flags=re.IGNORECASE)
        
        # Clean any word+colon at start of heading
        content = re.sub(r'<h([1-3])>([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', r'<h\1>', content, flags=re.IGNORECASE)
        
        # Extract the title
        h1_match = re.search(r'<h1>(.*?)</h1>', content)
        first_line = content.split('\n')[0] if content.split('\n') else ""
        title = ""
        
        # Clean the title
        if h1_match:
            title_text = h1_match.group(1).strip()
            for prefix in prefixes:
                title_text = re.sub(fr'^{prefix}:\s*', '', title_text, flags=re.IGNORECASE)
            title_text = re.sub(r'^([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', '', title_text, flags=re.IGNORECASE)
            title = title_text.strip('.:!?;,-')
        elif first_line:
            title = first_line.replace('#', '').replace('*', '').replace('<h1>', '').replace('</h1>', '').strip()
            for prefix in prefixes:
                title = re.sub(fr'^{prefix}:\s*', '', title, flags=re.IGNORECASE)
            title = re.sub(r'^([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', '', title, flags=re.IGNORECASE)
            title = title.strip('.:!?;,-')
        else:
            title = topic
        
        # Clean all headings
        def clean_heading(match):
            tag = match.group(1)
            text = match.group(2)
            for prefix in prefixes:
                text = re.sub(fr'^{prefix}:\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'^([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', '', text, flags=re.IGNORECASE)
            return f"<h{tag}>{text.strip()}</h{tag}>"
        
        content = re.sub(r'<h([1-3])>(.*?)</h\1>', clean_heading, content)
        
        # Ensure HTML formatting
        if not re.search(r'<h[1-3]>', content):
            content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
            content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
            content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        
        # Ensure paragraph tags
        if not re.search(r'<p>', content):
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            processed = []
            for p in paragraphs:
                if not re.match(r'^<(h[1-6]|p|ul|ol|div|blockquote)', p):
                    p = f"<p>{p}</p>"
                processed.append(p)
            content = '\n\n'.join(processed)
        
        # Clean first paragraph if it repeats the title
        content_parts = re.split(r'<h1>.*?</h1>', content, 1)
        if len(content_parts) > 1 and content_parts[1].strip():
            after_h1 = content_parts[1].strip()
            first_p_match = re.search(r'<p>(.*?)</p>', after_h1)
            if first_p_match:
                p_text = first_p_match.group(1)
                if p_text.startswith(title) or any(p_text.startswith(f"{p}: {title}") for p in prefixes):
                    new_text = re.sub(r'^' + re.escape(title) + r'\s*', '', p_text)
                    new_text = re.sub(r'^([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*' + re.escape(title) + r'\s*', '', p_text)
                    if new_text and new_text[0].islower() and new_text[0].isalpha():
                        new_text = new_text[0].upper() + new_text[1:]
                    content = content.replace(f"<p>{p_text}</p>", f"<p>{new_text}</p>", 1)
        
        # Create excerpt
        first_p_match = re.search(r'<p>(.*?)</p>', content)
        if first_p_match:
            excerpt_text = first_p_match.group(1)
        else:
            paragraphs = [re.sub(r'<.*?>', '', p.strip()) for p in content.split('\n\n') if p.strip()]
            excerpt_text = paragraphs[0] if paragraphs else f"Статья о {topic}"
        
        # Clean excerpt
        for prefix in prefixes:
            excerpt_text = re.sub(fr'^{prefix}:\s*', '', excerpt_text, flags=re.IGNORECASE)
        excerpt_text = re.sub(r'^([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', '', excerpt_text, flags=re.IGNORECASE)
        excerpt_text = re.sub(r'[\*#_]+', '', excerpt_text)
        
        # Remove title from excerpt start
        if title and excerpt_text.startswith(title):
            excerpt_text = excerpt_text[len(title):].strip()
            if excerpt_text and excerpt_text[0].islower() and excerpt_text[0].isalpha():
                excerpt_text = excerpt_text[0].upper() + excerpt_text[1:]
        
        excerpt = excerpt_text[:200] + '...' if len(excerpt_text) > 200 else excerpt_text
        
        # Return results
        result = {
            "success": True,
            "title": title,
            "excerpt": excerpt,
            "content": content
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
