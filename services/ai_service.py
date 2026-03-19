import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en las variables de entorno.")
        
        genai.configure(api_key=api_key)
        # Usamos 1.5 Flash por ser rápido y tener un tier gratis generoso
        self.model = genai.GenerativeModel('gemini-flash-latest')

    async def process_text_with_requirements(self, raw_text: str, requirements: str):
        """
        Envía el texto extraído a Gemini para que lo procese según los requerimientos.
        """
        prompt = f"""
        Actúa como un experto en extracción de datos. A continuación te proporciono un texto extraído mediante OCR.
        
        TEXTO EXTRAÍDO:
        ---
        {raw_text}
        ---
        
        REQUERIMIENTOS DEL USUARIO:
        {requirements}
        
        INSTRUCCIONES:
        1. Extrae la información solicitada basándote en el texto.
        2. Responde ÚNICAMENTE en formato JSON válido.
        """
        
        response = self.model.generate_content(prompt)
        return self._clean_and_parse_json(response.text)

    async def process_image_with_requirements(self, image_data: bytes, requirements: str):
        """
        Envía una imagen directamente a Gemini (Vision) para OCR y extracción estructurada.
        """
        prompt = f"""
        Actúa como un experto en procesamiento de documentos y OCR. 
        Analiza la imagen adjunta y extrae la información según los siguientes requerimientos:
        
        REQUERIMIENTOS:
        {requirements}
        
        INSTRUCCIONES:
        1. Realiza el OCR de la imagen.
        2. Extrae y estructura los datos solicitados.
        3. Si es un documento de identidad (pasaporte, visa, etc.), extrae nombres, fechas y números con total precisión.
        4. Responde ÚNICAMENTE en formato JSON válido.
        """
        
        # Preparar la parte de la imagen para la API de Gemini
        image_part = {
            "mime_type": "image/jpeg", # La mayoría de nuestras conversiones son a JPEG
            "data": image_data
        }
        
        response = self.model.generate_content([prompt, image_part])
        return self._clean_and_parse_json(response.text)

    def _clean_and_parse_json(self, text: str):
        """
        Limpia bloques markdown y parsea el JSON de la respuesta.
        """
        clean_response = text.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response.replace("```json", "").replace("```", "").strip()
        elif clean_response.startswith("```"):
            clean_response = clean_response.replace("```", "").strip()
            
        try:
            return json.loads(clean_response)
        except json.JSONDecodeError:
            return {"error": "No se pudo formatear la respuesta como JSON", "raw_response": text}

ai_service = AIService()
