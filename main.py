import os
from dotenv import load_dotenv

# Configuración de variables de entorno ANTES de importar servicios
load_dotenv()
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import io
from starlette.concurrency import run_in_threadpool
# from services.ocr_engine import ocr_service # Eliminado: Usamos Gemini Vision
from services.pdf_processor import pdf_processor
from services.word_processor import word_processor
from services.ai_service import ai_service
from utils.schemas import MultiOCRResponse, OCRResponse

app = FastAPI(title="OCR Microservice with Gemini Vision")

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
    return {"message": "OCR Microservice (Gemini Vision) is running"}

@app.post("/extract", response_model=MultiOCRResponse)
async def extract_data(
    files: List[UploadFile] = File(...),
    requirements: str = Form("Extrae toda la información relevante")
):
    results = []
    
    for file in files:
        try:
            content = await file.read()
            refined_data = {}
            
            if file.content_type == "application/pdf":
                print(f"[{file.filename}] Intentando extracción de texto nativo...")
                raw_text = pdf_processor.extract_native_text(content)
                
                if len(raw_text.strip()) < 20:
                    print(f"[{file.filename}] No se detectó texto nativo. Iniciando Gemini Vision por página...")
                    images = pdf_processor.pdf_to_images(content)
                    print(f"[{file.filename}] PDF convertido. {len(images)} páginas encontradas.")
                    
                    # Para PDFs escaneados, procesamos cada página con Vision y combinamos
                    # Nota: Gemini también puede recibir múltiples imágenes, pero por ahora seguimos el flujo de páginas
                    combined_data = {}
                    for i, img_bytes in enumerate(images):
                        print(f"[{file.filename}] Procesando página {i+1}/{len(images)} con Gemini Vision...")
                        page_data = await ai_service.process_image_with_requirements(img_bytes, requirements)
                        combined_data.update(page_data)
                    refined_data = combined_data
                else:
                    print(f"[{file.filename}] Texto nativo extraído con éxito. Refinando con Gemini...")
                    refined_data = await ai_service.process_text_with_requirements(raw_text, requirements)
            
            elif file.content_type in ["image/png", "image/jpeg", "image/jpg"]:
                print(f"[{file.filename}] Procesando imagen directamente con Gemini Vision...")
                # No necesitamos redimensionar localmente, Gemini soporta alta resolución
                refined_data = await ai_service.process_image_with_requirements(content, requirements)
                print(f"[{file.filename}] Procesamiento Vision finalizado.")
            
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                print(f"[{file.filename}] Procesando Word...")
                raw_text = word_processor.extract_text(content)
                refined_data = await ai_service.process_text_with_requirements(raw_text, requirements)
            
            else:
                results.append(OCRResponse(
                    filename=file.filename,
                    status="error",
                    extracted_data={},
                    error=f"Tipo de archivo no soportado: {file.content_type}"
                ))
                continue

            results.append(OCRResponse(
                filename=file.filename,
                status="success",
                extracted_data=refined_data
            ))

        except Exception as e:
            print(f"Error procesando {file.filename}: {e}")
            results.append(OCRResponse(
                filename=file.filename,
                status="error",
                extracted_data={},
                error=str(e)
            ))

    return MultiOCRResponse(results=results)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
