#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Simple test of OpenAI 0.28 with completely ASCII content
import os
import sys

# Force UTF-8 encoding
if 'PYTHONIOENCODING' not in os.environ:
    os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    import openai
    print(f"✅ OpenAI version: {openai.__version__}")
    
    # Set a test API key (empty for testing structure)
    openai.api_key = "test-key"
    
    # Test completely ASCII content
    test_prompt = """Write a short article about robots in English.
    
    Response structure:
    TITLE: [Article title]
    CONTENT: [Article content]
    
    Requirements:
    - Write about modern robotics
    - Keep it short and simple
    - Use only ASCII characters"""
    
    print("✅ Test prompt prepared (ASCII only)")
    print(f"Prompt length: {len(test_prompt)} characters")
    print("Prompt preview:", test_prompt[:100] + "...")
    
    # Test the API call structure (will fail without real API key but should show encoding issues)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": test_prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        print("✅ API call successful!")
    except Exception as e:
        print(f"❌ API call failed: {e}")
        if "latin-1" in str(e) or "encode" in str(e):
            print("🔍 This is an encoding issue!")
        elif "Incorrect API key" in str(e) or "invalid" in str(e).lower():
            print("✅ Encoding is OK, just need real API key")
        
except Exception as e:
    print(f"❌ Error: {e}")
