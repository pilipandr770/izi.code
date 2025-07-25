#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
print(f"Python path: {sys.path}")

try:
    import openai
    print(f"OpenAI module path: {openai.__file__}")
    print(f"OpenAI version: {openai.__version__}")
    
    # Test if ChatCompletion exists (0.28.x) or not (1.x+)
    if hasattr(openai, 'ChatCompletion'):
        print("✅ OpenAI 0.28.x detected - ChatCompletion available")
        try:
            # Test the actual API call structure
            print("Testing ChatCompletion.create method...")
            # Don't actually call it, just check if method exists
            method = openai.ChatCompletion.create
            print(f"✅ ChatCompletion.create method found: {method}")
        except Exception as e:
            print(f"❌ Error with ChatCompletion.create: {e}")
    else:
        print("❌ OpenAI 1.x+ detected - ChatCompletion NOT available")
        
    # Check what's actually in the openai module
    print("\nOpenAI module attributes:")
    for attr in sorted(dir(openai)):
        if not attr.startswith('_'):
            print(f"  - {attr}")
            
except ImportError as e:
    print(f"❌ Failed to import openai: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
