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
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def process_text_with_requirements(self, raw_text: str, requirements: str):
        """
        Envía el texto extraído a Gemini para que lo procese según los requerimientos.
        """
        prompt = f"""
        Actúa como un experto en extracción de datos. A continuación te proporciono un texto extraído mediante OCR de uno o varios documentos.
        
        TEXTO EXTRAÍDO:
        ---
        {raw_text}
        ---
        
        REQUERIMIENTOS DEL USUARIO:
        {requirements}
        
        INSTRUCCIONES:
        1. Extrae la información solicitada en los requerimientos.
        2. Si no encuentras alguna información, indícalo como nulo o no encontrado.
        3. Responde ÚNICAMENTE en formato JSON válido. No incluyas explicaciones adicionales.
        """
        
        response = self.model.generate_content(prompt)
        
        # Intentamos limpiar la respuesta si Gemini incluye bloques de código markdown
        clean_response = response.text.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response.replace("```json", "").replace("```", "").strip()
        elif clean_response.startswith("```"):
            clean_response = clean_response.replace("```", "").strip()
            
        try:
            return json.loads(clean_response)
        except json.JSONDecodeError:
            return {"error": "No se pudo formatear la respuesta como JSON", "raw_response": response.text}

ai_service = AIService()
