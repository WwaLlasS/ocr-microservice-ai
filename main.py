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
from services.word_processor import word_processor
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
                print(f"[{file.filename}] Intentando extracción de texto nativo...")
                raw_text = pdf_processor.extract_native_text(content)
                
                # Si el texto es muy corto (ej: menos de 20 caracteres), 
                # probablemente es un escaneo y necesitamos OCR visual.
                if len(raw_text.strip()) < 20:
                    print(f"[{file.filename}] No se detectó texto nativo. Iniciando OCR visual (proceso lento)...")
                    images = pdf_processor.pdf_to_images(content)
                    print(f"[{file.filename}] PDF convertido. {len(images)} páginas encontradas.")
                    page_texts = []
                    for i, img in enumerate(images):
                        print(f"[{file.filename}] Procesando OCR de página {i+1}/{len(images)}...")
                        page_texts.append(ocr_service.extract_text(img))
                    raw_text = "\n".join(page_texts)
                    print(f"[{file.filename}] OCR finalizado.")
                else:
                    print(f"[{file.filename}] Texto nativo extraído con éxito (Fast Path).")
            
            elif file.content_type in ["image/png", "image/jpeg", "image/jpg"]:
                from PIL import Image
                import numpy as np
                image = Image.open(io.BytesIO(content))
                print(f"[{file.filename}] Procesando OCR de imagen...")
                raw_text = ocr_service.extract_text(np.array(image))
                print(f"[{file.filename}] OCR finalizado.")
            
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                print(f"[{file.filename}] Procesando Word...")
                raw_text = word_processor.extract_text(content)
            
            else:
                results.append(OCRResponse(
                    filename=file.filename,
                    status="error",
                    extracted_data={},
                    error=f"Tipo de archivo no soportado: {file.content_type}"
                ))
                continue

            print(f"[{file.filename}] Enviando texto a Gemini...")
            refined_data = await ai_service.process_text_with_requirements(raw_text, requirements)
            print(f"[{file.filename}] Respuesta de Gemini recibida.")
            
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
