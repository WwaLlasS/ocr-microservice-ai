import os
from dotenv import load_dotenv

# Environment variables configuration BEFORE importing services
load_dotenv()
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import io
from starlette.concurrency import run_in_threadpool
# from services.ocr_engine import ocr_service # Removed: Using Gemini Vision
from services.pdf_processor import pdf_processor
from services.word_processor import word_processor
from services.ai_service import ai_service
from utils.schemas import MultiOCRResponse, OCRResponse

app = FastAPI(title="OCR Microservice with Gemini Vision")

# Configure CORS
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
    requirements: str = Form("Extract all relevant information")
):
    results = []
    
    for file in files:
        try:
            content = await file.read()
            refined_data = {}
            
            if file.content_type == "application/pdf":
                print(f"[{file.filename}] Attempting native text extraction...")
                raw_text = pdf_processor.extract_native_text(content)
                
                if len(raw_text.strip()) < 20:
                    print(f"[{file.filename}] No native text detected. Starting Gemini Vision by page...")
                    images = pdf_processor.pdf_to_images(content)
                    print(f"[{file.filename}] PDF converted. {len(images)} pages found.")
                    
                    # For scanned PDFs, process each page with Vision and combine
                    # Note: Gemini can also receive multiple images, but for now we follow the page flow
                    combined_data = {}
                    for i, img_bytes in enumerate(images):
                        print(f"[{file.filename}] Processing page {i+1}/{len(images)} with Gemini Vision...")
                        page_data = await ai_service.process_image_with_requirements(img_bytes, requirements)
                        combined_data.update(page_data)
                    refined_data = combined_data
                else:
                    print(f"[{file.filename}] Native text successfully extracted. Refining with Gemini...")
                    refined_data = await ai_service.process_text_with_requirements(raw_text, requirements)
            
            elif file.content_type in ["image/png", "image/jpeg", "image/jpg"]:
                print(f"[{file.filename}] Processing image directly with Gemini Vision...")
                # No need to resize locally, Gemini supports high resolution
                refined_data = await ai_service.process_image_with_requirements(content, requirements)
                print(f"[{file.filename}] Vision processing finished.")
            
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                print(f"[{file.filename}] Processing Word...")
                raw_text = word_processor.extract_text(content)
                refined_data = await ai_service.process_text_with_requirements(raw_text, requirements)
            
            else:
                results.append(OCRResponse(
                    filename=file.filename,
                    status="error",
                    extracted_data={},
                    error=f"Unsupported file type: {file.content_type}"
                ))
                continue

            results.append(OCRResponse(
                filename=file.filename,
                status="success",
                extracted_data=refined_data
            ))

        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
            results.append(OCRResponse(
                filename=file.filename,
                status="error",
                extracted_data={},
                error=str(e)
            ))

    return MultiOCRResponse(results=results)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
