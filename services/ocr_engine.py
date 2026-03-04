from paddleocr import PaddleOCR
import numpy as np
from PIL import Image

class OCREngine:
    def __init__(self):
        # Inicializa PaddleOCR con soporte para español e inglés
        # use_angle_cls=True permite detectar la orientación del texto
        self.ocr = PaddleOCR(use_angle_cls=True, lang='es')

    def extract_text(self, image_path_or_array):
        """
        Extrae texto de una imagen (ruta o array de numpy).
        Retorna el texto concatenado.
        """
        result = self.ocr.ocr(image_path_or_array)
        
        # result es una lista de listas (una por cada imagen procesada)
        full_text = []
        if result and result[0]:
            for line in result[0]:
                # line[1][0] contiene el texto reconocido
                full_text.append(line[1][0])
        
        return " ".join(full_text)

# Instancia global para evitar re-inicializar el modelo en cada petición
ocr_service = OCREngine()
