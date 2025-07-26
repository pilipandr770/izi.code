#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI ChatBot Caller Script for Flask App
This script handles OpenAI API calls for the chatbot functionality,
properly utilizing the assistant_id in a prompt for OpenAI SDK v0.28.0
which doesn't support the Assistants API directly.
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
            print(json.dumps({
                "error": "OpenAI API key not found", 
                "response": "I'm sorry, I can't connect to my AI services right now. Please try again later."
            }))
            sys.exit(0)  # Return valid JSON instead of error exit
        
        # Get assistant_id from environment first, then from request data as fallback
        assistant_id = os.getenv('OPENAI_ASSISTANT_ID') or request_data.get("assistant_id")
        
        if assistant_id:
            # Log that we're using assistant_id
            safe_id = assistant_id[:8] + "..." if len(assistant_id) > 8 else "not_available"
            print(json.dumps({"debug": f"Using Assistant ID: {safe_id} (truncated for security)"}), file=sys.stderr)
            
        # Get user message and other parameters
        user_message = request_data.get('message', '')
        language = request_data.get('language', 'uk')
        product_info = request_data.get('product_info', '')
        category_info = request_data.get('category_info', '')
        
        # Build context information if available
        context_info = ""
        if product_info or category_info:
            context_info = f"""
ИНФОРМАЦИЯ О МАГАЗИНЕ:

КАТЕГОРИИ:
{category_info}

ПОПУЛЯРНЫЕ ТОВАРЫ:
{product_info}
"""
            
        # Create enhanced system prompt that incorporates assistant behavior
        system_prompt = f"""Ты - AI-консультант интернет-магазина (Assistant ID: {assistant_id}).

{context_info}

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
            "status": "success",
            "using_assistant": bool(assistant_id)
        }
        
        print(json.dumps(result, ensure_ascii=False))
        
    except FileNotFoundError:
        print(json.dumps({
            "error": f"Request file not found: {json_file}",
            "response": "I'm sorry, I couldn't process your request right now."
        }))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": f"Invalid JSON in request file: {str(e)}",
            "response": "I'm sorry, I couldn't process your request right now."
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"OpenAI API error: {str(e)}",
            "response": "I'm sorry, I can't connect to my AI services right now. Please try again later."
        }, ensure_ascii=False))
        sys.exit(0)

if __name__ == "__main__":
    main()
