#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple OpenAI 0.28 test script
"""

import os
import sys

# Set environment
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Force reload openai module
if 'openai' in sys.modules:
    del sys.modules['openai']

import openai

# Check version
print(f"OpenAI version: {openai.__version__}")

# Set API key
openai.api_key = "your-openai-api-key-here"

def test_simple_call():
    """Test simple OpenAI call with ASCII only"""
    try:
        print("Testing simple ASCII-only call...")
        
        # Ultra-simple ASCII-only prompt
        system_msg = "You are a writer."
        user_msg = "Write short article about robots. Return: TITLE: title here EXCERPT: excerpt here CONTENT: content here"
        
        print(f"System: {repr(system_msg)}")
        print(f"User: {repr(user_msg)}")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        print("✅ SUCCESS!")
        print(f"Response: {response.choices[0].message.content[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_unicode_content():
    """Test with Unicode content"""
    try:
        print("\nTesting with Unicode content...")
        
        # Test with Ukrainian text in prompt
        system_msg = "You are a writer."
        user_msg = "Write short article about роботи (robots in Ukrainian). Use English only in response."
        
        print(f"System: {repr(system_msg)}")
        print(f"User: {repr(user_msg)}")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        print("✅ SUCCESS with Unicode!")
        print(f"Response: {response.choices[0].message.content[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ ERROR with Unicode: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("OpenAI 0.28 Compatibility Test")
    print("=" * 50)
    
    # Test 1: ASCII only
    test1 = test_simple_call()
    
    # Test 2: Unicode content
    test2 = test_unicode_content()
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    print(f"ASCII test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Unicode test: {'✅ PASS' if test2 else '❌ FAIL'}")
    print("=" * 50)
