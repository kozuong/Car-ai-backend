import os
from dotenv import load_dotenv
import google.generativeai as genai
from app.config.config import Config
import logging
import base64
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        self.text_model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
    def analyze_image(self, base64_image: Optional[str], prompt: str) -> str:
        """
        Analyze an image using Gemini Vision API
        
        Args:
            base64_image: Base64 encoded image string
            prompt: Prompt for the model
            
        Returns:
            str: Model's response
        """
        try:
            if base64_image:
                image_parts = [
                    {
                        "mime_type": "image/jpeg",
                        "data": base64_image
                    }
                ]
                response = self.model.generate_content([prompt, *image_parts])
            else:
                response = self.text_model.generate_content(prompt)
                
            return response.text
            
        except Exception as e:
            logger.error(f"Error analyzing image with Gemini: {str(e)}")
            raise
            
    def translate_text(self, text: str) -> str:
        """
        Translate text to Vietnamese using Gemini
        
        Args:
            text: Text to translate
            
        Returns:
            str: Translated text
        """
        try:
            prompt = f"""
            Translate this text to Vietnamese. Keep technical terms and car model names in English.
            Only return the translated text, no explanations.
            
            Text to translate:
            {text}
            """
            
            response = self.text_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error translating text with Gemini: {str(e)}")
            raise 