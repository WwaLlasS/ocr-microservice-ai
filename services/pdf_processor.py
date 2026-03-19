import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import numpy as np
import io

class PDFProcessor:
    @staticmethod
    def extract_native_text(pdf_content: bytes):
        """
        Attempts to extract native text directly from the PDF.
        Returns the text or an empty string if there is no text (e.g., a scan).
        """
        text = ""
        try:
            # Open the PDF from memory
            with fitz.open(stream=pdf_content, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text() + "\n"
        except Exception as e:
            print(f"Error extracting native text: {e}")
        
        return text.strip()

    @staticmethod
    def pdf_to_images(pdf_content: bytes):
        """
        Converts a PDF file to a list of high-resolution numpy arrays (300 DPI).
        """
        # Increase DPI to 300 for better OCR accuracy later
        images = convert_from_bytes(pdf_content, dpi=300)
        
        numpy_images = []
        for img in images:
            # Convert PIL Image to numpy array
            numpy_images.append(np.array(img))
            
        return numpy_images

pdf_processor = PDFProcessor()
