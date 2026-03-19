# OCR Microservice (Gemini Vision)

Este es un microservicio construido con **FastAPI** diseñado para extraer información estructurada de diversos tipos de documentos (PDF, Imágenes, Word). Utiliza **Gemini Vision** de Google para la extracción de documentos visuales y librerías nativas para documentos de texto, refinando los datos en formato JSON según requerimientos específicos del usuario.

## 🚀 Características Principales

- 📸 **Extracción de Imágenes**: Usa las capacidades del modelo **Gemini Vision** (`gemini-flash-latest`) para procesar JPG, PNG y JPEG con altísima precisión, entendiendo el contexto visual completo.
- 📄 **Procesamiento de PDFs**: 
    - **Fast Path (Nativo)**: Extracción nativa de texto con `pdf2image`/`PyPDF` si el PDF contiene texto digital puro.
    - **OCR Path (Vision)**: Si el PDF es un escaneo (no seleccionable), se convierte automáticamente cada página a imagen y se procesa mediante Gemini Vision de forma asíncrona.
- 📝 **Soporte Word**: Extracción directa de texto de archivos `.docx` usando `python-docx`.
- 🤖 **Extracción JSON Inmediata**: Gemini no solo lee el texto, sino que se le instruye para que devuelva directamente la información estructurada solicitada por el usuario en formato JSON.
- ⚡ **Ligero y Optimizado para macOS**: **Cero dependencias locales de OCR** (como PaddleOCR, PyTorch o Tesseract). Esto elimina masivamente el peso del proyecto, problemas de compatibilidad y los bloqueos o *deadlocks* históricos relacionados con el multihilo en Apple Silicon.

## 🛠️ Tecnologías Utilizadas

- **FastAPI** & **Uvicorn** (Servidor web asíncrono)
- **Google Generative AI SDK** (Motor principal de "Vision OCR" y LLM)
- **Pillow (PIL)** & **pdf2image** (Procesamiento y conversión de imágenes y PDFs)
- **python-docx** (Extracción de archivos de Word)

## 📋 Requisitos y Puesta a Punto

1.  Python 3.9 o superior.
2.  Tener instalada la herramienta `poppler` (necesaria para `pdf2image`):
    *   En macOS: `brew install poppler`
    *   En Ubuntu: `sudo apt-get install poppler-utils`
3.  Una API Key de Google Gemini válida.

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone git@github.com:WwaLlasS/ocr-microservice-ai.git
   cd ocr-microservice-ai
   ```

2. **Crear y activar un entorno virtual (Recomendado):**
   ```bash
   python3 -m venv .venvs/ocr-service-env
   source .venvs/ocr-service-env/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Crea un archivo llamado `.env` en la raíz del proyecto y agrega tu clave de API:
   ```env
   GEMINI_API_KEY=tu_api_key_aqui
   ```

## 🏃 Modo de Uso

Para levantar el servidor de desarrollo, ejecuta el archivo principal:

```bash
python3 main.py
```
*El sistema iniciará el servidor `uvicorn` en `http://127.0.0.1:8000`.*

---

## 📡 Uso del API

### Endpoint: `POST /extract`

Este es el endpoint principal habilitado para procesar los documentos. Acepta requests tipo `multipart/form-data`.

**Parámetros:**
*   `files` (lista de `File`): Los archivos que deseas procesar (Puedes subir múltiples archivos de diferente extensión a la vez).
*   `requirements` (`Form`): Una cadena de texto natural con las instrucciones concretas de lo que deseas extraer de esos documentos.

**Ejemplo usando cURL:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/extract' \
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
      }
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
├── main.py                 # Entrypoint de FastAPI y declaración de rutas principal
├── requirements.txt        # Dependencias de Python
├── .env                    # Variables de entorno (No se debe commitear)
├── services/               # Lógica de negocio
│   ├── ai_service.py       # Controlador principal interactuando con Gemini Vision
│   ├── pdf_processor.py    # Extracción de texto nativo y conversión a imágenes para PDF
│   └── word_processor.py   # Lógica de extracción para documentos .docx
└── utils/
    └── schemas.py          # Definición de modelos Pydantic de respuesta
```

## 🔄 Nota sobre la Migración desde Motores Locales (Histórico)
Las versiones previas de este servicio dependían de motores nativos de OCR como **PaddleOCR**. Para solucionar problemas intrínsecos de estabilidad (deadlocks en FastAPI al procesar librerías de C++) detectados principalmente en macOS, así como los pesados requisitos de instalación (PyTorch/PaddlePaddle), la arquitectura **se migró un 100% a la nube utilizando Gemini Vision**. Esto resulta en un servicio más ligero, más estable, y con un nivel de comprensión contextual (por ejemplo, para extraer datos de identificaciones) muy superior a los OCR tradicionales.
