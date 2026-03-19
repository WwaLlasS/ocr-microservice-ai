from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import time
import os

class OCREngine:
    def __init__(self):
        # Inicializa PaddleOCR con lo mínimo indispensable para evitar conflictos en macOS
        print("Iniciando motor PaddleOCR v3...")
        try:
            # En v3.4.0 (PaddleX), a veces menos es más para estabilidad en CPU
            self.ocr = PaddleOCR(
                lang='es',
                device='cpu'
            )
            print("Motor PaddleOCR listo.")
        except Exception as e:
            print(f"Error al inicializar PaddleOCR: {e}")
            self.ocr = None

    def extract_text(self, image_path_or_array):
        """
        Extrae texto de una imagen (ruta o array de numpy).
        Retorna el texto concatenado.
        """
        if self.ocr is None:
            return "Error: Motor OCR no inicializado"

        start_time = time.time()
        print(f"--- [DEBUG] Iniciando ocr.predict ---")
        
        try:
            # En PaddleOCR 3.4.0, ocr() es un alias de predict()
            # Si se cuelga aquí, es un problema interno de PaddlePaddle 3.0.0 en macOS
            result = self.ocr.ocr(image_path_or_array)
            
            end_time = time.time()
            print(f"--- [DEBUG] ocr.predict finalizado en {end_time - start_time:.2f}s ---")
            
            full_text = []
            if result and len(result) > 0:
                # El formato de salida puede variar en v3, pero intentamos mantener compatibilidad
                # result[0] suele ser la lista de líneas detectadas
                for line in result[0]:
                    if isinstance(line, list) and len(line) > 1:
                        text = line[1][0]
                        full_text.append(text)
            
            return " ".join(full_text)
        except Exception as e:
            print(f"Error durante la extracción OCR: {e}")
            return f"Error en OCR: {str(e)}"

# Instancia global
ocr_service = OCREngine()
