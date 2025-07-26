#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI Assistant API integration for IZI.SOFT
Uses Assistant API with Assistant ID from environment variables
"""

import sys
import json
import openai
import os
import time
import io

# Force UTF-8 encoding for stdout/stderr
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Set UTF-8 environment
os.environ['PYTHONIOENCODING'] = 'utf-8'

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Missing JSON file argument"}))
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    try:
        # Set UTF-8 encoding
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Debug info for troubleshooting
        print(json.dumps({"debug": f"Processing file: {json_file}"}), file=sys.stderr)
        
        # Load request data
        with open(json_file, 'r', encoding='utf-8') as f:
            request_data = json.load(f)
        
        # Set OpenAI API key from environment
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Debug info for troubleshooting
        print(json.dumps({"debug": f"API key present: {bool(openai.api_key)}"}), file=sys.stderr)
        
        if not openai.api_key:
            print(json.dumps({"error": "OpenAI API key not found in environment variables", 
                             "response": "I'm sorry, I can't connect to my AI services right now. Please try again later."}))
            sys.exit(0)  # Return valid JSON instead of error exit
        
        # Get assistant_id from environment first, then from request data as fallback
        assistant_id = os.getenv('OPENAI_ASSISTANT_ID') or request_data.get("assistant_id")
        
        # Log the assistant_id to verify it's being used
        if assistant_id:
            safe_id = assistant_id[:8] + "..." if len(assistant_id) > 8 else "not_available"
            print(json.dumps({"debug": f"Using Assistant ID: {safe_id} (truncated for security)"}), file=sys.stderr)
            print(json.dumps({"debug": f"Assistant ID source: {'Environment' if os.getenv('OPENAI_ASSISTANT_ID') else 'Request data'}"}), file=sys.stderr)
        
        if not assistant_id:
            print(json.dumps({"error": "OpenAI Assistant ID not found", 
                             "response": "I'm sorry, I can't connect to my assistant services right now. Please try again later."}))
            sys.exit(0)
        
        # Get user message
        message = request_data.get("message", "")
        language = request_data.get("language", "uk")
        
        # Get optional product and category info for context
        product_info = request_data.get("product_info", "")
        category_info = request_data.get("category_info", "")
        context = ""
        
        if product_info or category_info:
            context = f"""
ИНФОРМАЦИЯ О МАГАЗИНЕ:

КАТЕГОРИИ:
{category_info}

ПОПУЛЯРНЫЕ ТОВАРЫ:
{product_info}

Используй эту информацию при ответах пользователю.
"""
        
        try:
            # First check if we're using OpenAI API v1.x or 0.x
            try:
                from openai import version
                api_version = version.__version__[0]
                print(json.dumps({"debug": f"OpenAI Python SDK version: {version.__version__}"}), file=sys.stderr)
            except:
                # Assume v0.x as it doesn't have a version module
                api_version = "0"
                print(json.dumps({"debug": f"OpenAI Python SDK assumed version 0.x"}), file=sys.stderr)
                
            # For v1.x API (new client-based approach)
            if api_version.startswith("1"):
                from openai import OpenAI
                client = OpenAI(api_key=openai.api_key)
                
                # Create a new thread
                thread = client.beta.threads.create()
                
                # Add user message to thread
                user_message_content = message
                if context:
                    # Add context only for the first message
                    user_message_content = f"{context}\n\nПользователь спрашивает: {message}"
                
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_message_content
                )
                
                # Run Assistant
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant_id,
                    instructions=f"Пользователь общается на языке: {language}. Отвечай на том же языке."
                )
                
                # Wait for the run to complete
                max_attempts = 30  # Prevent infinite loops
                attempts = 0
                
                while run.status in ["queued", "in_progress"] and attempts < max_attempts:
                    time.sleep(0.5)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    attempts += 1
                    
                # Log final status
                print(json.dumps({"debug": f"Assistant run completed with status: {run.status}"}), file=sys.stderr)
                
                # Get the response
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                
                # Take the latest assistant message
                for message in messages.data:
                    if message.role == "assistant":
                        assistant_response = message.content[0].text.value
                        print(json.dumps({
                            "response": assistant_response,
                            "status": "success"
                        }, ensure_ascii=False))
                        break
                else:
                    print(json.dumps({
                        "error": "No assistant response received",
                        "response": "I'm sorry, I couldn't process your request right now."
                    }, ensure_ascii=False))
            
            # For v0.x API (old global module approach)
            else:
                # Use threads API via the module-level client
                thread = openai.Thread.create()
                
                # Add user message to thread
                user_message_content = message
                if context:
                    # Add context only for the first message
                    user_message_content = f"{context}\n\nПользователь спрашивает: {message}"
                
                openai.ThreadMessage.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_message_content
                )
                
                # Run Assistant
                run = openai.ThreadRun.create(
                    thread_id=thread.id,
                    assistant_id=assistant_id,
                    instructions=f"Пользователь общается на языке: {language}. Отвечай на том же языке."
                )
                
                # Wait for the run to complete
                max_attempts = 30  # Prevent infinite loops
                attempts = 0
                
                while run.status in ["queued", "in_progress"] and attempts < max_attempts:
                    time.sleep(0.5)
                    run = openai.ThreadRun.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    attempts += 1
                
                # Log final status
                print(json.dumps({"debug": f"Assistant run completed with status: {run.status}"}), file=sys.stderr)
                
                # Get the response
                messages = openai.ThreadMessage.list(thread_id=thread.id)
                
                # Take the latest assistant message
                for message in messages.data:
                    if message.role == "assistant":
                        assistant_response = message.content[0].text.value
                        print(json.dumps({
                            "response": assistant_response,
                            "status": "success"
                        }, ensure_ascii=False))
                        break
                else:
                    print(json.dumps({
                        "error": "No assistant response received",
                        "response": "I'm sorry, I couldn't process your request right now."
                    }, ensure_ascii=False))
                
        except Exception as e:
            # Return a friendly error with fallback response
            error_result = {
                "error": f"OpenAI API error: {str(e)}",
                "response": "I'm sorry, I can't connect to my AI services right now. Please try again later or contact our support team."
            }
            # Use ensure_ascii=False to properly handle UTF-8 characters
            print(json.dumps(error_result, ensure_ascii=False))
        
    except FileNotFoundError:
        print(json.dumps({"error": f"Request file not found: {json_file}"}))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON in request file: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Error: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
