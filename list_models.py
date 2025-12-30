from google import genai
import json
import os

def list_models():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        client = genai.Client(api_key=config['google_api_key'])
        print("Listing available models from google-genai SDK:")
        for m in client.models.list():
             print(f"- {m.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
