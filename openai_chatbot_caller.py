#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI ChatCompletion Caller Script for Flask App
This script handles OpenAI ChatCompletion API calls for the chatbot functionality
to avoid encoding issues in Flask context.
"""

import sys
import json
import openai
import os

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Missing JSON file argument"}))
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    try:
        # Set UTF-8 encoding
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Load request data
        with open(json_file, 'r', encoding='utf-8') as f:
            request_data = json.load(f)
        
        # Set OpenAI API key from environment
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        if not openai.api_key:
            print(json.dumps({"error": "OpenAI API key not found"}))
            sys.exit(1)
        
        # Build system prompt based on assistant configuration
        assistant_id = request_data.get('assistant_id', '')
        context = request_data.get('context', '')
        user_message = request_data.get('message', '')
        language = request_data.get('language', 'uk')
        
        # Create enhanced system prompt that incorporates assistant behavior
        system_prompt = f"""Ты - AI-консультант интернет-магазина (Assistant ID: {assistant_id}). 

{context}

Дополнительные инструкции:
- Отвечай на языке пользователя ({language})
- Будь дружелюбным и полезным
- Рекомендуй товары из предоставленного списка
- Помогай с выбором и отвечай на вопросы о товарах
- Если пользователь спрашивает о конкретном товаре, предоставь детальную информацию
- Всегда старайся направить разговор к покупке подходящих товаров
"""
        
        # Prepare messages for chat completion
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Make OpenAI API call
        response = openai.ChatCompletion.create(
            model=request_data.get("model", "gpt-3.5-turbo"),
            messages=messages,
            max_tokens=request_data.get("max_tokens", 500),
            temperature=request_data.get("temperature", 0.7)
        )
        
        # Extract and return response
        ai_response = response.choices[0].message.content.strip()
        
        result = {
            "response": ai_response,
            "status": "success"
        }
        
        print(json.dumps(result, ensure_ascii=False))
        
    except FileNotFoundError:
        print(json.dumps({"error": f"Request file not found: {json_file}"}))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON in request file: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"OpenAI API error: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
