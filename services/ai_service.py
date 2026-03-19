import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        # We use 1.5 Flash as it is fast and has a generous free tier
        self.model = genai.GenerativeModel('gemini-flash-latest')

    async def process_text_with_requirements(self, raw_text: str, requirements: str):
        """
        Sends the extracted text to Gemini to process it according to the requirements.
        """
        prompt = f"""
        Act as a data extraction expert. Below I provide text extracted via OCR.
        
        EXTRACTED TEXT:
        ---
        {raw_text}
        ---
        
        USER REQUIREMENTS:
        {requirements}
        
        INSTRUCTIONS:
        1. Extract the requested information based on the text.
        2. Respond ONLY in valid JSON format.
        """
        
        response = self.model.generate_content(prompt)
        return self._clean_and_parse_json(response.text)

    async def process_image_with_requirements(self, image_data: bytes, requirements: str):
        """
        Sends an image directly to Gemini (Vision) for OCR and structured extraction.
        """
        prompt = f"""
        Act as an expert in document processing and OCR. 
        Analyze the attached image and extract the information according to the following requirements:
        
        REQUIREMENTS:
        {requirements}
        
        INSTRUCTIONS:
        1. Perform OCR on the image.
        2. Extract and structure the requested data.
        3. If it is an identity document (passport, visa, etc.), extract names, dates, and numbers with total accuracy.
        4. Respond ONLY in valid JSON format.
        """
        
        # Prepare the image part for the Gemini API
        image_part = {
            "mime_type": "image/jpeg", # Most of our conversions are to JPEG
            "data": image_data
        }
        
        response = self.model.generate_content([prompt, image_part])
        return self._clean_and_parse_json(response.text)

    def _clean_and_parse_json(self, text: str):
        """
        Cleans markdown blocks and parses the JSON response.
        """
        clean_response = text.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response.replace("```json", "").replace("```", "").strip()
        elif clean_response.startswith("```"):
            clean_response = clean_response.replace("```", "").strip()
            
        try:
            return json.loads(clean_response)
        except json.JSONDecodeError:
            return {"error": "Could not format the response as JSON", "raw_response": text}

ai_service = AIService()
