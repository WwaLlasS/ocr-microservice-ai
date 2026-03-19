# OCR Microservice (Gemini Vision)

This is a microservice built with **FastAPI** designed to extract structured information from various types of documents (PDF, Images, Word). It uses Google's **Gemini Vision** for visual document extraction and native libraries for text documents, refining the data into JSON format according to specific user requirements.

## 🚀 Main Features

- 📸 **Image Extraction**: Uses **Gemini Vision** (`gemini-flash-latest`) capabilities to process JPG, PNG, and JPEG with extremely high precision, understanding the full visual context.
- 📄 **PDF Processing**: 
    - **Fast Path (Native)**: Native text extraction with `fitz` (PyMuPDF) if the PDF contains pure digital text.
    - **OCR Path (Vision)**: If the PDF is a scan (non-selectable text), each page is automatically converted to an image and asynchronously processed using Gemini Vision.
- 📝 **Word Support**: Direct text extraction from `.docx` files using `python-docx`.
- 🤖 **Immediate JSON Extraction**: Gemini doesn't just read text; it is instructed to directly return the structured information requested by the user in JSON format.
- ⚡ **Lightweight and macOS Optimized**: **Zero local OCR dependencies** (like PaddleOCR, PyTorch, or Tesseract). This massively removes project bloat, compatibility issues, and historical multithreading *deadlocks* related to Apple Silicon.

## 🛠️ Technologies Used

- **FastAPI** & **Uvicorn** (Asynchronous web server)
- **Google Generative AI SDK** (Main "Vision OCR" and LLM engine)
- **Pillow (PIL)** & **pdf2image** (Image and PDF processing and conversion)
- **python-docx** (Word file extraction)

## 📋 Requirements and Setup

1.  Python 3.9 or higher.
2.  Have the `poppler` tool installed (required for `pdf2image`):
    *   On macOS: `brew install poppler`
    *   On Ubuntu: `sudo apt-get install poppler-utils`
3.  A valid Google Gemini API Key.

### Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:WwaLlasS/ocr-microservice-ai.git
   cd ocr-microservice-ai
   ```

2. **Create and activate a virtual environment (Recommended):**
   ```bash
   python3 -m venv .venvs/ocr-service-env
   source .venvs/ocr-service-env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a file named `.env` in the project root and add your API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## 🏃 Usage

To start the development server, run the main file:

```bash
python3 main.py
```
*The system will start the `uvicorn` server at `http://127.0.0.1:8000`.*

---

## 📡 API Usage

### Endpoint: `POST /extract`

This is the main endpoint enabled to process documents. It accepts `multipart/form-data` requests.

**Parameters:**
*   `files` (list of `File`): The files you want to process (You can upload multiple files of different extensions at once).
*   `requirements` (`Form`): A natural text string with concrete instructions on what you want to extract from those documents.

**Example using cURL:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/extract' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'requirements="Extract the Full Name, Identity Number, and Date of Birth. Return JSON format."' \
  -F 'files=@passport.jpg' \
  -F 'files=@birth_certificate.pdf'
```

**Expected Response (JSON):**
```json
{
  "results": [
    {
      "filename": "passport.jpg",
      "status": "success",
      "extracted_data": {
        "Full Name": "Juan Perez",
        "Identity Number": "123456789",
        "Date of Birth": "1990-01-01"
      }
    },
    {
      "filename": "birth_certificate.pdf",
      "status": "success",
      "extracted_data": { ... }
    }
  ]
}
```

## 🏗️ Project Structure

```text
ocr-microservice-ai/
├── main.py                 # FastAPI entrypoint and main route declaration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (Should not be committed)
├── services/               # Business logic
│   ├── ai_service.py       # Main controller interacting with Gemini Vision
│   ├── pdf_processor.py    # Native text extraction and PDF to image conversion
│   └── word_processor.py   # Extraction logic for .docx documents
└── utils/
    └── schemas.py          # Definition of Pydantic response models
```

## 🔄 Historical Note on Migration from Local Engines
Previous versions of this service relied on native OCR engines like **PaddleOCR**. To solve intrinsic stability issues (deadlocks in FastAPI when processing C++ libraries) detected mainly on macOS, as well as heavy installation requirements (PyTorch/PaddlePaddle), the architecture **was migrated 100% to the cloud using Gemini Vision**. This results in a lighter, more stable service, with a much higher level of contextual understanding (e.g., to extract data from IDs) than traditional OCRs.
