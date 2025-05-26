import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # Load .env từ cùng thư mục car-ai-backend

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

print("✅ Loaded API key:", api_key[:10] + "...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content("What is the capital of Japan?")
print("✅ Gemini Response:", response.text)
