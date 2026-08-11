import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
print(API_KEY)

genai.configure(api_key=API_KEY)

print("Available Models:")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f"{m.name}")
