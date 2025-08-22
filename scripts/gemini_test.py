"""
Simple Gemini API test using google-genai client.

Usage:
  - Set environment variable GEMINI_API_KEY with your API key, or embed it (not recommended).
  - Run: python scripts/gemini_test.py

The script will print a short explanation from Gemini or inform if the API key is missing.
"""
import os
import sys

try:
    from google import genai
    from google.genai import types
except Exception as e:
    print("google-genai not installed or import failed:", e)
    print("Install with: python -m pip install -U google-genai")
    sys.exit(1)

API_KEY = os.environ.get('GEMINI_API_KEY')
if not API_KEY:
    print("GEMINI_API_KEY not set. Please set the environment variable to call the Gemini API.")
    print("You can still run this script after setting the key to see a real response.")
    sys.exit(0)

# Initialize client (it will pick GEMINI_API_KEY automatically, but we pass it explicitly here)
client = genai.Client(api_key=API_KEY)

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain how AI works in a few words",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # disable thinking for speed
        ),
    )
    print("Gemini response text:\n", response.text)
except Exception as exc:
    print("Error calling Gemini API:", exc)
    sys.exit(2)
