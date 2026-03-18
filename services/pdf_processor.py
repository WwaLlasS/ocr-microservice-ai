import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import numpy as np
import io

class PDFProcessor:
    @staticmethod
    def extract_native_text(pdf_content: bytes):
        """
        Intenta extraer texto nativo directamente del PDF.
        Retorna el texto o una cadena vacía si no hay texto (escaneo).
        """
        text = ""
        try:
            # Abrimos el PDF desde memoria
            with fitz.open(stream=pdf_content, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text() + "\n"
        except Exception as e:
            print(f"Error extrayendo texto nativo: {e}")
        
        return text.strip()

    @staticmethod
    def pdf_to_images(pdf_content: bytes):
        """
        Convierte un archivo PDF a una lista de arrays de numpy con alta resolución (300 DPI).
        """
        # Aumentamos el DPI a 300 para mayor precisión en el OCR posterior
        images = convert_from_bytes(pdf_content, dpi=300)
        
        numpy_images = []
        for img in images:
            # Convertimos PIL Image a numpy array para PaddleOCR
            numpy_images.append(np.array(img))
            
        return numpy_images

pdf_processor = PDFProcessor()
