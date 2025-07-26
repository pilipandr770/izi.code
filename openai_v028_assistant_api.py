#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI Assistant API Caller Script for Flask App - v0.28.0 Specific
This script handles OpenAI Assistant API calls for OpenAI SDK v0.28.0
"""

import sys
import json
import openai
import os
import time

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
        
        if not assistant_id:
            print(json.dumps({
                "error": "OpenAI Assistant ID not found", 
                "response": "I'm sorry, I can't connect to my assistant services right now. Please try again later."
            }))
            sys.exit(0)
            
        # Debug the assistant ID (showing only partial for security)
        safe_id = assistant_id[:8] + "..." if len(assistant_id) > 8 else "not_available"
        print(json.dumps({"debug": f"Using Assistant ID: {safe_id} (truncated for security)"}), file=sys.stderr)
            
        # Get user message and other parameters
        context = request_data.get('context', '')
        user_message = request_data.get('message', '')
        language = request_data.get('language', 'uk')
        product_info = request_data.get('product_info', '')
        category_info = request_data.get('category_info', '')
        
        # Prepare user message with context
        user_content = user_message
        if product_info or category_info:
            user_content = f"""
ИНФОРМАЦИЯ О МАГАЗИНЕ:

КАТЕГОРИИ:
{category_info}

ПОПУЛЯРНЫЕ ТОВАРЫ:
{product_info}

Используй эту информацию при ответах пользователю.

Пользователь спрашивает: {user_message}
"""
        
        try:
            print(json.dumps({"debug": "Starting OpenAI Assistant API call with v0.28.0 syntax"}), file=sys.stderr)
            
            # Create a thread with the correct v0.28.0 syntax
            thread = openai.Thread.create()
            print(json.dumps({"debug": f"Thread created with ID: {thread.id}"}), file=sys.stderr)
            
            # Add user message to thread
            openai.Message.create(
                thread_id=thread.id,
                role="user",
                content=user_content
            )
            print(json.dumps({"debug": "User message added to thread"}), file=sys.stderr)
            
            # Run the assistant on the thread
            run = openai.Run.create(
                thread_id=thread.id,
                assistant_id=assistant_id,
                instructions=f"Пользователь общается на языке: {language}. Отвечай на том же языке."
            )
            print(json.dumps({"debug": f"Assistant run created with ID: {run.id}, initial status: {run.status}"}), file=sys.stderr)
            
            # Wait for the run to complete
            max_attempts = 30
            attempts = 0
            
            while run.status in ["queued", "in_progress"] and attempts < max_attempts:
                time.sleep(0.5)
                run = openai.Run.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                attempts += 1
                
            print(json.dumps({"debug": f"Run completed with status: {run.status} after {attempts} attempts"}), file=sys.stderr)
            
            # Get the assistant's response
            if run.status == "completed":
                # Retrieve messages from thread
                messages = openai.Message.list(thread_id=thread.id)
                print(json.dumps({"debug": f"Retrieved {len(messages.data)} messages from thread"}), file=sys.stderr)
                
                # Find the assistant's message
                for message in messages.data:
                    if message.role == "assistant":
                        # In v0.28.0, content structure might be different from v1.x
                        try:
                            # Try the v0.28.0 structure
                            if hasattr(message.content[0], 'text'):
                                ai_response = message.content[0].text.value
                            else:
                                ai_response = message.content[0].value
                                
                            print(json.dumps({"debug": "Successfully extracted assistant response"}), file=sys.stderr)
                            print(json.dumps({
                                "response": ai_response,
                                "status": "success"
                            }, ensure_ascii=False))
                            break
                        except (AttributeError, IndexError) as e:
                            print(json.dumps({"debug": f"Error extracting message content: {str(e)}"}), file=sys.stderr)
                            raise e
                else:
                    # No assistant message found
                    print(json.dumps({"debug": "No assistant messages found in thread"}), file=sys.stderr)
                    print(json.dumps({
                        "error": "No assistant response received",
                        "response": "I'm sorry, I couldn't process your request right now."
                    }))
            else:
                # Run failed or timed out
                print(json.dumps({"debug": f"Run failed with status: {run.status}"}), file=sys.stderr)
                print(json.dumps({
                    "error": f"Assistant run failed with status: {run.status}",
                    "response": "I'm sorry, I couldn't process your request right now."
                }))
                
        except Exception as e:
            # Log the error and fall back to ChatCompletion
            print(json.dumps({"debug": f"Error using Assistant API: {str(e)}"}), file=sys.stderr)
            print(json.dumps({"debug": "Falling back to ChatCompletion"}), file=sys.stderr)
            
            # Build system prompt based on assistant configuration
            system_prompt = f"""Ты - AI-консультант интернет-магазина (Assistant ID: {assistant_id}).

КАТЕГОРИИ:
{category_info}

ПОПУЛЯРНЫЕ ТОВАРЫ:
{product_info}

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
            
            print(json.dumps({
                "response": ai_response,
                "status": "success"
            }, ensure_ascii=False))
            
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
