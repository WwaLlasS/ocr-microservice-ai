import os
import traceback
# Configurar variables de entorno para evitar cuelgues en macOS con PaddlePaddle
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import time

class OCREngine:
    def __init__(self):
        # Inicializa PaddleOCR con lo mínimo indispensable para evitar conflictos en macOS
        print("Iniciando motor PaddleOCR v3...")
        try:
            # En v3.4.0, simplificamos al máximo para evitar ValueError: Unknown argument
            self.ocr = PaddleOCR(
                lang='es',
                device='cpu'
            )
            print("Motor PaddleOCR listo.")
        except Exception as e:
            print("!!! Error crítico al inicializar PaddleOCR !!!")
            traceback.print_exc()
            self.ocr = None

    def extract_text(self, image_path_or_array):
        """
        Extrae texto de una imagen (ruta o array de numpy).
        Retorna el texto concatenado.
        """
        if self.ocr is None:
            return "Error: Motor OCR no inicializado"

        start_time = time.time()
        print(f"--- [DEBUG] Iniciando ocr.ocr (predict) ---")
        
        try:
            # En PaddleOCR 3.4.0, ocr() es un alias de predict()
            # Quitamos 'cls' porque genera error en v3
            result = self.ocr.ocr(image_path_or_array)
            
            end_time = time.time()
            print(f"--- [DEBUG] ocr.ocr finalizado en {end_time - start_time:.2f}s ---")
            
            if result:
                print(f"--- [DEBUG] Estructura de resultado: {type(result)} ---")
            
            full_text = []
            if result and len(result) > 0:
                # En v3, si es una lista de resultados (uno por imagen)
                # cada resultado puede ser una lista de líneas o un objeto Result
                for res in result:
                    if res is None: continue
                    # Si es el formato clásico de PaddleOCR [[box, [text, score]], ...]
                    for line in res:
                        if isinstance(line, list) and len(line) > 1:
                            text = line[1][0]
                            full_text.append(text)
            
            return " ".join(full_text)
        except Exception as e:
            print(f"Error durante la extracción OCR: {e}")
            return f"Error en OCR: {str(e)}"

# Instancia global
ocr_service = OCREngine()
