import os
from dotenv import load_dotenv

# Configuración de variables de entorno ANTES de importar servicios
load_dotenv()
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import io
from services.ocr_engine import ocr_service
from services.pdf_processor import pdf_processor
from services.ai_service import ai_service
from utils.schemas import MultiOCRResponse, OCRResponse

app = FastAPI(title="OCR Microservice with PaddleOCR and Gemini")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "OCR Microservice is running"}

@app.post("/extract", response_model=MultiOCRResponse)
async def extract_data(
    files: List[UploadFile] = File(...),
    requirements: str = Form("Extrae toda la información relevante")
):
    results = []
    
    for file in files:
        try:
            content = await file.read()
            raw_text = ""
            
            if file.content_type == "application/pdf":
                images = pdf_processor.pdf_to_images(content)
                page_texts = []
                for img in images:
                    page_texts.append(ocr_service.extract_text(img))
                raw_text = "\n".join(page_texts)
                
            elif file.content_type in ["image/png", "image/jpeg", "image/jpg"]:
                from PIL import Image
                import numpy as np
                image = Image.open(io.BytesIO(content))
                raw_text = ocr_service.extract_text(np.array(image))
            
            else:
                results.append(OCRResponse(
                    filename=file.filename,
                    status="error",
                    extracted_data={},
                    error=f"Tipo de archivo no soportado: {file.content_type}"
                ))
                continue

            refined_data = await ai_service.process_text_with_requirements(raw_text, requirements)
            
            results.append(OCRResponse(
                filename=file.filename,
                status="success",
                extracted_data=refined_data
            ))

        except Exception as e:
            results.append(OCRResponse(
                filename=file.filename,
                status="error",
                extracted_data={},
                error=str(e)
            ))

    return MultiOCRResponse(results=results)

if __name__ == "__main__":
    # Usamos 127.0.0.1 para evitar problemas de resolución de nombres en macOS
    uvicorn.run(app, host="127.0.0.1", port=8000)
