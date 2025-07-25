import os
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import openai
from flask import current_app

class ContentGenerator:
    """Class for generating and translating blog content using OpenAI API"""
    
    def __init__(self):
        """Initialize ContentGenerator with OpenAI client"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        
        if not api_key:
            self.client = None
            current_app.logger.warning("OpenAI API key not configured")
            return
            
        try:
            # For OpenAI module
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
            self.api_key = api_key
            current_app.logger.info("OpenAI client initialized successfully")
        except Exception as e:
            current_app.logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.client = None
            self.api_key = None
    
    def generate_content(self, topic: str, language: str = 'en', keywords: str = '') -> Dict[str, str]:
        """Generate blog post content using OpenAI API directly"""
        current_app.logger.info(f"Generating content for topic: {topic} in {language}")
        
        if not self.client:
            current_app.logger.warning("OpenAI client not available, using fallback")
            return self._get_fallback_content(topic, language, keywords)
            
        try:
            # Language-specific prompts
            prompts = {
                'uk': {
                    'system': 'Ти досвідчений копірайтер українською мовою, який пише SEO-оптимізовані статті для блогу.',
                    'user': f'Напиши детальну статтю про "{topic}". Ключові слова для SEO: {keywords}. '
                           f'Стаття повинна мати структуру з заголовком, вступом, 3-5 підзаголовками, '
                           f'та висновком. Використовуй HTML-теги для форматування: <h2> для підзаголовків, '
                           f'<p> для параграфів, <ul> і <li> для списків.'
                },
                'ru': {
                    'system': 'Ты опытный копирайтер на русском языке, который пишет SEO-оптимизированные статьи для блога.',
                    'user': f'Напиши подробную статью о "{topic}". Ключевые слова для SEO: {keywords}. '
                           f'Статья должна иметь структуру с заголовком, введением, 3-5 подзаголовками, '
                           f'и заключением. Используй HTML-теги для форматирования: <h2> для подзаголовков, '
                           f'<p> для параграфов, <ul> и <li> для списков.'
                },
                'de': {
                    'system': 'Du bist ein erfahrener Copywriter auf Deutsch, der SEO-optimierte Blogbeiträge schreibt.',
                    'user': f'Schreibe einen detaillierten Artikel über "{topic}". SEO-Keywords: {keywords}. '
                           f'Der Artikel sollte eine Struktur mit einem Titel, einer Einleitung, 3-5 Untertiteln '
                           f'und einem Fazit haben. Verwende HTML-Tags für die Formatierung: <h2> für Untertitel, '
                           f'<p> für Absätze, <ul> und <li> für Listen.'
                },
                'en': {
                    'system': 'You are an experienced copywriter in English who writes SEO-optimized blog articles.',
                    'user': f'Write a detailed article about "{topic}". SEO keywords: {keywords}. '
                           f'The article should have a structure with a title, introduction, 3-5 subheadings, '
                           f'and conclusion. Use HTML tags for formatting: <h2> for subheadings, '
                           f'<p> for paragraphs, <ul> and <li> for lists.'
                }
            }
            
            prompt = prompts.get(language, prompts['en'])
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt['system']},
                    {"role": "user", "content": prompt['user']}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract title, content, and excerpt
            lines = content.split('\n')
            title = lines[0].replace('#', '').replace('*', '').strip() if lines else topic
            
            # Create excerpt from first paragraph
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            excerpt = paragraphs[1][:200] + '...' if len(paragraphs) > 1 and len(paragraphs[1]) > 200 else (
                      paragraphs[1] if len(paragraphs) > 1 else f"Article about {topic}")
            
            # Format content as HTML
            formatted_content = self._format_content(content)
            
            return {
                "title": title,
                "excerpt": excerpt,
                "content": formatted_content
            }
            
        except Exception as e:
            current_app.logger.error(f"Error generating content with OpenAI: {str(e)}")
            return self._get_fallback_content(topic, language, keywords)
    
    def translate_content(self, content: Dict[str, str], from_lang: str, to_lang: str) -> Dict[str, str]:
        """Translate blog post content from one language to another"""
        current_app.logger.info(f"Translating content from {from_lang} to {to_lang}")
        
        if not self.client:
            current_app.logger.warning("OpenAI client not available, using simple translation")
            return self._get_simple_translation(content, from_lang, to_lang)
        
        try:
            # Get title, excerpt, and content to translate
            title = content.get("title", "")
            excerpt = content.get("excerpt", "")
            original_content = content.get("content", "")
            
            # Language-specific prompts
            language_names = {
                'uk': 'Ukrainian',
                'ru': 'Russian',
                'de': 'German',
                'en': 'English'
            }
            
            from_lang_name = language_names.get(from_lang, 'English')
            to_lang_name = language_names.get(to_lang, 'English')
            
            # Translate title
            title_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a professional translator from {from_lang_name} to {to_lang_name}."},
                    {"role": "user", "content": f"Translate the following title from {from_lang_name} to {to_lang_name}. Keep it concise and catchy:\n\n{title}"}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            translated_title = title_response.choices[0].message.content.strip()
            
            # Translate excerpt
            excerpt_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a professional translator from {from_lang_name} to {to_lang_name}."},
                    {"role": "user", "content": f"Translate the following excerpt from {from_lang_name} to {to_lang_name}. Keep the same tone and style:\n\n{excerpt}"}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            translated_excerpt = excerpt_response.choices[0].message.content.strip()
            
            # Translate content
            content_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": f"You are a professional translator from {from_lang_name} to {to_lang_name}."},
                    {"role": "user", "content": f"Translate the following HTML content from {from_lang_name} to {to_lang_name}. Keep all HTML tags intact and maintain the same structure. Keep the same tone and style:\n\n{original_content}"}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            translated_content = content_response.choices[0].message.content.strip()
            
            return {
                "title": translated_title,
                "excerpt": translated_excerpt,
                "content": translated_content
            }
            
        except Exception as e:
            current_app.logger.error(f"Error translating content with OpenAI: {str(e)}")
            return self._get_simple_translation(content, from_lang, to_lang)
    
    def generate_multilingual_post(self, primary_language: str, topic: str, keywords: str = '') -> Dict[str, Dict[str, str]]:
        """Generate blog post in primary language and translate to others"""
        current_app.logger.info(f"Generating multilingual post from {primary_language} with topic: {topic}")
        
        # Available languages
        languages = ['uk', 'ru', 'de', 'en']
        
        # First generate content in the primary language
        primary_content = self.generate_content(topic, primary_language, keywords)
        
        # Then translate to other languages
        result = {primary_language: primary_content}
        
        for lang in languages:
            if lang != primary_language:
                translated = self.translate_content(primary_content, primary_language, lang)
                result[lang] = translated
        
        return result
    
    def _format_content(self, content: str) -> str:
        """Format raw content to proper HTML"""
        # Replace markdown-style headers with HTML
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Skip the first line which is the title
            if line == lines[0]:
                continue
                
            # Format headers
            if line.startswith('# '):
                formatted_lines.append(f"<h1>{line[2:].strip()}</h1>")
            elif line.startswith('## '):
                formatted_lines.append(f"<h2>{line[3:].strip()}</h2>")
            elif line.startswith('### '):
                formatted_lines.append(f"<h3>{line[4:].strip()}</h3>")
            # If line already has HTML tags, keep as is
            elif '<h' in line or '<p>' in line or '<ul>' in line or '<li>' in line:
                formatted_lines.append(line)
            # Format paragraphs
            elif line.strip():
                formatted_lines.append(f"<p>{line.strip()}</p>")
            else:
                formatted_lines.append('')
        
        return '\n'.join(formatted_lines)
    
    def _get_fallback_content(self, topic: str, language: str, keywords: str) -> Dict[str, str]:
        """Get fallback content when OpenAI API fails"""
        language_templates = {
            'uk': {
                'title': f"Все про {topic}: повний гід",
                'excerpt': f"Детальний огляд теми '{topic}' з практичними рекомендаціями."
            },
            'ru': {
                'title': f"Все о {topic}: полное руководство", 
                'excerpt': f"Подробный обзор темы '{topic}' с практическими рекомендациями."
            },
            'de': {
                'title': f"Alles über {topic}: Vollständige Anleitung",
                'excerpt': f"Umfassender Überblick über '{topic}' mit praktischen Empfehlungen."
            },
            'en': {
                'title': f"Everything about {topic}: Complete Guide",
                'excerpt': f"Comprehensive overview of '{topic}' with practical recommendations."
            }
        }
        
        template = language_templates.get(language, language_templates['en'])
        fallback_content = f"""
        <h2>About {topic}</h2>
        <p>This article discusses everything you need to know about {topic}. It includes valuable information and insights about this important subject.</p>
        
        <h2>Key Points</h2>
        <ul>
            <li>Important aspect 1 of {topic}</li>
            <li>Critical feature 2 related to {topic}</li>
            <li>Essential consideration 3 about {topic}</li>
        </ul>
        
        <h2>Conclusion</h2>
        <p>In conclusion, {topic} represents an important area of knowledge with many applications and benefits. Keywords: {keywords}</p>
        """
        
        return {
            'title': template['title'],
            'excerpt': template['excerpt'],
            'content': fallback_content
        }
    
    def _get_simple_translation(self, content: Dict[str, str], from_lang: str, to_lang: str) -> Dict[str, str]:
        """Get simple translation when OpenAI API fails"""
        # Simple prefix-based translation
        prefix = {
            'uk': '[УКР] ',
            'ru': '[РУС] ',
            'de': '[DE] ',
            'en': '[EN] '
        }.get(to_lang, '')
        
        title = content.get('title', '')
        excerpt = content.get('excerpt', '')
        original_content = content.get('content', '')
        
        return {
            'title': f"{prefix}{title}",
            'excerpt': f"{prefix}{excerpt}",
            'content': original_content
        }
