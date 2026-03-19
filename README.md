# OCR Microservice AI

Este es un microservicio construido con **FastAPI** diseñado para extraer texto de diversos tipos de documentos (PDF, Imágenes, Word) utilizando **PaddleOCR** y librerías nativas, para luego refinar y estructurar la información extraída según requerimientos específicos utilizando Inteligencia Artificial (**Google Gemini 2.5 Flash**).

## 🚀 Características Principales
# OCR Microservice (Gemini Vision)

Este microservicio permite extraer información estructurada de diversos tipos de documentos (PDF, Imágenes, Word) utilizando **Gemini Vision** de Google para documentos visuales y extracción nativa para documentos de texto.

## Características

- 📸 **Extracción de Imágenes**: Usa las capacidades de visión de Gemini para procesar JPG, PNG y JPEG con altísima precisión.
- 📄 **Procesamiento de PDFs**: 
    - **Fast Path**: Extracción nativa de texto si el PDF es digital.
    - **OCR Path (Vision)**: Si el PDF es un escaneo, se convierte a imagen y se procesa con Gemini Vision.
- 📝 **Soporte Word**: Extracción de texto de archivos `.docx`.
- 🤖 **IA Generativa**: Refinamiento y estructuración de datos mediante el modelo `gemini-flash-latest`.
- ⚡ **Optimizado para macOS**: Sin dependencias pesadas de C++ (PaddleOCR/PyTorch), eliminando bloqueos y problemas de memoria.

## Tecnologías

- **FastAPI**: Framwork web asíncrono.
- **Google Generative AI**: Motor de visión y procesamiento de lenguaje.
- **Pillow**: Procesamiento de imágenes.
- **pdf2image**: Conversión de PDFs a imágenes.
- **python-docx**: Manejo de archivos Word.

## Requisitos y Puesta a Punto

### 1. Variables de Entorno
Crea un archivo `.env` en la raíz con tu API Key:
```env
GEMINI_API_KEY=tu_api_key_aqui
```

### 2. Instalación de Dependencias
```bash
# Se recomienda usar el entorno virtual especificado
pip install -r requirements.txt
```

*Nota: Asegúrate de tener `poppler` instalado en tu sistema para el procesamiento de PDFs (`brew install poppler` en macOS).*

### 3. Ejecución
```bash
python3 main.py
```
El servicio estará disponible en `http://127.0.0.1:8000`.

## Uso del API

### Endpoint: `POST /extract`

Envía uno o más archivos mediante un formulario `multipart/form-data`.

**Parámetros:**
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'requirements="Extrae el Nombre Completo, Número de Identidad, y Fecha de Nacimiento. Devuelve formato JSON."' \
  -F 'files=@pasaporte.jpg' \
  -F 'files=@acta_nacimiento.pdf'
```

**Respuesta Esperada (JSON):**
```json
{
  "results": [
    {
      "filename": "pasaporte.jpg",
      "status": "success",
      "extracted_data": {
        "Nombre Completo": "Juan Perez",
        "Número de Identidad": "123456789",
        "Fecha de Nacimiento": "1990-01-01"
      },
      "error": null
    },
    {
      "filename": "acta_nacimiento.pdf",
      "status": "success",
      "extracted_data": { ... }
    }
  ]
}
```

## 🏗️ Estructura del Proyecto

```text
ocr-microservice-ai/
├── main.py                 # Entrypoint de FastAPI y declaración de rutas
├── requirements.txt        # Dependencias de Python
├── .env                    # Variables de entorno (No se debe commitear)
├── services/               # Lógica de negocio
│   ├── ai_service.py       # Cliente configurado con Gemini 2.5 Flash
│   ├── ocr_engine.py       # Inicialización y abstracción de PaddleOCR
│   ├── pdf_processor.py    # Extracción de texto nativo y conversión a imagen para PDF
│   └── word_processor.py   # Lógica de extracción para .docx
└── utils/
    └── schemas.py          # Definición de modelos Pydantic (MultiOCRResponse, etc.)
```

## 🐛 Notas de Desarrollo y Troubleshooting
* **Errores de OCR en macOS (`ocr.ocr` se queda pegado):** La inicialización de `PaddleOCR` no es *thread safe* en todos los sistemas. Para evitar colapsos ("deadlocks") con FastAPI en entornos Apple Silicon, la extracción visual de `ocr_engine` en `main.py` se ejecuta **síncronamente** sin utilizar `run_in_threadpool`. Las imágenes mayores de 2500px, por defecto, se redimensionan para asegurar un rendimiento óptimo en un único intento y así evitar errores internos en el motor nativo de PaddleOCR.
