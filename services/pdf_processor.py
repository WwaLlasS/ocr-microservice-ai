from pdf2image import convert_from_path, convert_from_bytes
import numpy as np
from PIL import Image
import io

class PDFProcessor:
    @staticmethod
    def pdf_to_images(pdf_content: bytes):
        """
        Convierte un archivo PDF (en bytes) a una lista de arrays de numpy (imágenes).
        """
        # Convertimos el PDF a imágenes (una por página)
        images = convert_from_bytes(pdf_content)
        
        numpy_images = []
        for img in images:
            # Convertimos PIL Image a numpy array para PaddleOCR
            numpy_images.append(np.array(img))
            
        return numpy_images

pdf_processor = PDFProcessor()
