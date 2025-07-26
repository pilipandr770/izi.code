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
                'system': 'Ти досвідчений копірайтер українською мовою, який пише для веб-блогу. Твої статті мають природну структуру з заголовками HTML (h1, h2, h3) та абзацами, без використання символів Markdown або спеціальних позначень для форматування. Твої тексти читаються як написані людиною, з плавними переходами між абзацами.',
                'user': f'Напиши інформативну та привабливу статтю про "{topic}" для блогу. Використай ключові слова: {keywords}. Дотримуйся цих важливих правил:\n\n1. Використовуй тільки HTML-теги для форматування: <h1> для головного заголовка, <h2> для підзаголовків, <p> для абзаців.\n2. НЕ ДОДАВАЙ фрази "Назва:", "Заголовок:", "Тема:" на початку заголовків.\n3. НЕ використовуй зірочки (**), підкреслення (_ _) або інші Markdown символи.\n4. НЕ ПОВТОРЮЙ заголовок статті в першому абзаці.\n5. Пиши природньо як досвідчений журналіст, щоб не було помітно, що текст написав AI.\n6. Забезпеч плавні переходи між абзацами та логічну структуру.\n\nСтаття має бути інформативною, цікавою і читатися як написана людиною, а не AI.'
            },
            'ru': {
                'system': 'Ты опытный копирайтер на русском языке, который пишет для веб-блога. Твои статьи имеют естественную структуру с заголовками HTML (h1, h2, h3) и абзацами, без использования символов Markdown или специальных обозначений для форматирования. Твои тексты читаются как написанные человеком, с плавными переходами между абзацами.',
                'user': f'Напиши информативную и привлекательную статью о "{topic}" для блога. Используй ключевые слова: {keywords}. Соблюдай эти важные правила:\n\n1. Используй только HTML-теги для форматирования: <h1> для главного заголовка, <h2> для подзаголовков, <p> для абзацев.\n2. НЕ ДОБАВЛЯЙ фразы "Название:", "Заголовок:", "Тема:" в начале заголовков.\n3. НЕ используй звездочки (**), подчеркивания (_ _) или другие Markdown символы.\n4. НЕ ПОВТОРЯЙ заголовок статьи в первом абзаце.\n5. Пиши естественно как опытный журналист, чтобы не было заметно, что текст написал AI.\n6. Обеспечь плавные переходы между абзацами и логичную структуру.\n\nСтатья должна быть информативной, интересной и читаться как написанная человеком, а не AI.'
            },
            'de': {
                'system': 'Du bist ein erfahrener Copywriter auf Deutsch, der für einen Web-Blog schreibt. Deine Artikel haben eine natürliche Struktur mit HTML-Überschriften (h1, h2, h3) und Absätzen, ohne Markdown-Symbole oder spezielle Kennzeichnungen für die Formatierung zu verwenden. Deine Texte lesen sich wie von Menschen geschrieben, mit fließenden Übergängen zwischen den Absätzen.',
                'user': f'Schreibe einen informativen und ansprechenden Artikel über "{topic}" für einen Blog. Verwende die Schlüsselwörter: {keywords}. Befolge diese wichtigen Regeln:\n\n1. Verwende nur HTML-Tags für die Formatierung: <h1> für die Hauptüberschrift, <h2> für Unterüberschriften, <p> für Absätze.\n2. FÜGE NICHT die Wörter "Titel:", "Überschrift:", "Thema:" am Anfang der Überschriften hinzu.\n3. Verwende KEINE Sternchen (**), Unterstriche (_ _) oder andere Markdown-Symbole.\n4. WIEDERHOLE NICHT den Artikeltitel im ersten Absatz.\n5. Schreibe natürlich wie ein erfahrener Journalist, damit der Text nicht wie von einer KI geschrieben wirkt.\n6. Sorge für fließende Übergänge zwischen Absätzen und eine logische Struktur.\n\nDer Artikel sollte informativ, interessant und wie von einem Menschen geschrieben sein, nicht von einer KI.'
            },
            'en': {
                'system': 'You are an experienced copywriter in English who writes for a web blog. Your articles have a natural structure with HTML headings (h1, h2, h3) and paragraphs, without using Markdown symbols or special markings for formatting. Your texts read as if written by a human, with smooth transitions between paragraphs.',
                'user': f'Write an informative and engaging article about "{topic}" for a blog. Use the keywords: {keywords}. Follow these important rules:\n\n1. Use only HTML tags for formatting: <h1> for main title, <h2> for subheadings, <p> for paragraphs.\n2. DO NOT ADD phrases like "Title:", "Heading:", "Topic:" at the beginning of headings.\n3. DO NOT use asterisks (**), underscores (_ _), or other Markdown symbols.\n4. DO NOT REPEAT the article title in the first paragraph.\n5. Write naturally like an experienced journalist so that it's not obvious the text was written by AI.\n6. Ensure smooth transitions between paragraphs and a logical structure.\n\nThe article should be informative, interesting, and read as if written by a human, not AI.'
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
        
        # Clean up any Markdown-style formatting or special markers that might remain
        # Remove *Название:* style prefixes and other common variations
        content = re.sub(r'\*([^*]*?)\*\s*', r'\1 ', content)  # Remove *text* style formatting
        content = re.sub(r'[\*_]{2}([^*_]*?)[\*_]{2}', r'\1', content)  # Remove **text** or __text__ style formatting
        content = re.sub(r'#{1,3} (.*?)$', r'\1', content, flags=re.MULTILINE)  # Remove # style headings
        
        # Handle various title prefixes before HTML formatting
        prefixes = ['Название', 'Заголовок', 'Тема', 'Назва', 'Title', 'Titel', 'Überschrift', 'Heading', 'Topic']
        for prefix in prefixes:
            # Remove prefix from any line (with colon)
            content = re.sub(fr'^{prefix}:\s*(.+?)$', r'\1', content, flags=re.MULTILINE|re.IGNORECASE)
            # Remove prefix from HTML headings (with colon)
            content = re.sub(fr'<h([1-3])>{prefix}:\s*', r'<h\1>', content, flags=re.IGNORECASE)
            # Also handle case where the word might be part of the heading but not at the beginning
            content = re.sub(fr'<h([1-3])>([^<]{0,3}){prefix}[^<]{0,3}:\s*', r'<h\1>\2', content, flags=re.IGNORECASE)
        
        # General prefix cleanup - any word followed by colon at beginning of heading
        content = re.sub(r'<h([1-3])>([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', r'<h\1>', content, flags=re.IGNORECASE)
        
        # Extract the main title (either from h1 or first line)
        h1_match = re.search(r'<h1>(.*?)</h1>', content)
        first_line = content.split('\n')[0] if content.split('\n') else ""
        title = ""
        
        # List of common title prefixes we want to remove
        title_prefixes = [
            'Название', 'Заголовок', 'Тема', 'Назва', 'Title', 'Titel', 'Überschrift', 
            'Heading', 'Topic', 'Тематика', 'Subject', 'Thema'
        ]
        
        if h1_match:
            # Get raw title text
            title = h1_match.group(1).strip()
            
            # Remove any prefix with colon
            for prefix in title_prefixes:
                title = re.sub(fr'^{prefix}:\s*', '', title, flags=re.IGNORECASE)
            
            # Remove any generic "word:" at start of title
            title = re.sub(r'^([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', '', title, flags=re.IGNORECASE)
        elif first_line:
            # Clean up any formatting from the first line to get the title
            title = first_line.replace('#', '').replace('*', '').replace('<h1>', '').replace('</h1>', '').strip()
            
            # Remove any prefix with colon
            for prefix in title_prefixes:
                title = re.sub(fr'^{prefix}:\s*', '', title, flags=re.IGNORECASE)
                
            # Remove any generic "word:" at start of title
            title = re.sub(r'^([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', '', title, flags=re.IGNORECASE)
        else:
            title = topic
            
        # Final cleanup - ensure title is properly capitalized and doesn't end with punctuation
        title = title.strip('.:!?;,-')
        title = title.strip()
            
        # Ensure the content has proper HTML formatting
        if not re.search(r'<h[1-3]>', content):
            # Convert any markdown-like headings to HTML if they exist
            content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
            content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
            content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
            
        # Ensure paragraphs have <p> tags
        if not re.search(r'<p>', content):
            # Split by empty lines and wrap paragraphs in <p> tags if they don't already have them
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            processed_paragraphs = []
            
            for p in paragraphs:
                if not re.match(r'^<(h[1-6]|p|ul|ol|div|blockquote)', p):
                    p = f"<p>{p}</p>"
                processed_paragraphs.append(p)
                
            content = '\n\n'.join(processed_paragraphs)
            
        # Before setting full content, ensure all h1/h2/h3 tags are cleaned of prefixes
        prefixes = ['Название', 'Заголовок', 'Тема', 'Назва', 'Title', 'Titel', 'Überschrift', 
                   'Heading', 'Topic', 'Тематика', 'Subject', 'Thema']
        
        # Function to clean headings in HTML content
        def clean_heading(match):
            tag = match.group(1)
            text = match.group(2)
            # Remove any prefix from heading
            for prefix in prefixes:
                text = re.sub(fr'^{prefix}:\s*', '', text, flags=re.IGNORECASE)
            # Remove any generic word+colon prefix
            text = re.sub(r'^([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', '', text, flags=re.IGNORECASE)
            return f"<h{tag}>{text.strip()}</h{tag}>"
        
        # Apply cleaning to all headings
        content = re.sub(r'<h([1-3])>(.*?)</h\1>', clean_heading, content)
        
        full_content = content
        
        # Find the first paragraph after the main heading and check for title repetition
        content_parts = re.split(r'<h1>.*?</h1>', content, 1)
        if len(content_parts) > 1 and content_parts[1].strip():
            # Look at content after the main h1 heading
            after_h1_content = content_parts[1].strip()
            
            # Find the first paragraph
            first_p_match = re.search(r'<p>(.*?)</p>', after_h1_content)
            if first_p_match:
                first_p_text = first_p_match.group(1)
                
                # Check if paragraph begins with the title or variations of title prefixes
                for prefix in [title] + [f"{p}: {title}" for p in prefixes]:
                    if prefix and first_p_text.startswith(prefix):
                        # Remove the title repetition from the paragraph
                        new_p_text = first_p_text[len(prefix):].strip()
                        # Capitalize the first letter if it's not already
                        if new_p_text and not new_p_text[0].isupper() and new_p_text[0].isalpha():
                            new_p_text = new_p_text[0].upper() + new_p_text[1:]
                        
                        # Replace the paragraph in content
                        content = content.replace(f"<p>{first_p_text}</p>", f"<p>{new_p_text}</p>", 1)
                        break
                
                # Also handle case where paragraph starts with just a prefix word
                for prefix in prefixes:
                    prefix_pattern = fr'^{prefix}:\s*'
                    if re.match(prefix_pattern, first_p_text, flags=re.IGNORECASE):
                        # Remove the prefix
                        new_p_text = re.sub(prefix_pattern, '', first_p_text, flags=re.IGNORECASE)
                        # Capitalize the first letter if it's not already
                        if new_p_text and not new_p_text[0].isupper() and new_p_text[0].isalpha():
                            new_p_text = new_p_text[0].upper() + new_p_text[1:]
                        
                        # Replace the paragraph in content
                        content = content.replace(f"<p>{first_p_text}</p>", f"<p>{new_p_text}</p>", 1)
                        break
        
        # Create excerpt from first paragraph (without HTML tags)
        first_p_match = re.search(r'<p>(.*?)</p>', content)
        if first_p_match:
            excerpt_text = first_p_match.group(1)
        else:
            paragraphs = [re.sub(r'<.*?>', '', p.strip()) for p in content.split('\n\n') if p.strip()]
            excerpt_text = paragraphs[0] if paragraphs else f"Статья о {topic}"
            
        # Clean excerpt from any prefixes
        prefixes = ['Название', 'Заголовок', 'Тема', 'Назва', 'Title', 'Titel', 'Überschrift', 
                   'Heading', 'Topic', 'Тематика', 'Subject', 'Thema']
        
        # Remove title prefixes from excerpt
        for prefix in prefixes:
            excerpt_text = re.sub(fr'^{prefix}:\s*', '', excerpt_text, flags=re.IGNORECASE)
        
        # Remove any generic word+colon prefix
        excerpt_text = re.sub(r'^([a-zA-Z0-9а-яА-ЯіІїЇєЄёЁ]{2,15}):\s*', '', excerpt_text, flags=re.IGNORECASE)
            
        # Remove any markdown formatting that might remain
        excerpt_text = re.sub(r'[\*#_]+', '', excerpt_text)
        
        # Remove the title itself from the beginning of the excerpt
        if title and excerpt_text.startswith(title):
            excerpt_text = excerpt_text[len(title):].strip()
            # Capitalize first letter if needed
            if excerpt_text and not excerpt_text[0].isupper() and excerpt_text[0].isalpha():
                excerpt_text = excerpt_text[0].upper() + excerpt_text[1:]
        
        excerpt = excerpt_text[:200] + '...' if len(excerpt_text) > 200 else excerpt_text
        
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
