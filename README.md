# OCR Microservice AI

Este es un microservicio construido con **FastAPI** diseñado para extraer texto de diversos tipos de documentos (PDF, Imágenes, Word) utilizando **PaddleOCR** y librerías nativas, para luego refinar y estructurar la información extraída según requerimientos específicos utilizando Inteligencia Artificial (**Google Gemini 2.5 Flash**).

## 🚀 Características Principales

*   **API RESTful:** Expone un endpoint `/extract` preparado para recibir múltiples archivos simultáneamente.
*   **Soporte Multiformato:**
    *   **Imágenes** (PNG, JPEG, JPG): Extracción visual mediante el motor de redes neuronales de **PaddleOCR**.
    *   **Documentos PDF**: Extracción de texto nativo rápido (fast path). Si el PDF es un escaneo (sin texto seleccionable), realiza una conversión automática de las páginas a imágenes y aplica OCR.
    *   **Documentos Word** (.docx): Extracción de texto y tablas usando `python-docx`.
*   **Procesamiento de IA (Gemini):** Una vez extraído el texto crudo (raw text), el microservicio se comunica con Google Gemini para interpretar el texto y extraer únicamente la información solicitada en formato **JSON estructurado**.
*   **Optimizado para macOS:** Incluye configuraciones específicas para evitar "deadlocks" de `OpenMP` con PaddleOCR en sistemas macOS e hilos (threads) de FastAPI.

## 🛠️ Tecnologías Utilizadas

*   **Python 3**
*   **FastAPI** & **Uvicorn** (Servidor web asíncrono)
*   **PaddleOCR** & **PaddlePaddle** (Motor de Reconocimiento Óptico de Caracteres)
*   **Google Generative AI SDK** (Integración con modelos Gemini)
*   **Pillow (PIL)** & **pdf2image** (Procesamiento de imágenes y PDFs)
*   **python-docx** (Extracción de archivos de Word)

## 📋 Requisitos Previos

1.  Python 3.9 o superior.
2.  Tener instalada la herramienta `poppler` (necesaria para `pdf2image`):
    *   En macOS: `brew install poppler`
    *   En Ubuntu: `sudo apt-get install poppler-utils`
3.  Una API Key de Google Gemini válida.

## ⚙️ Puesta a Punto (Instalación)

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
   Crea un archivo llamado `.env` en la raíz del proyecto y agrega tu clave de API de Gemini:
   ```env
   GEMINI_API_KEY=tu_api_key_aqui
   ```

## 🏃 Modo de Uso

Para levantar el servidor de desarrollo, simplemente ejecuta el archivo principal:

```bash
python3 main.py
```
*El sistema iniciará el servidor `uvicorn` en `http://127.0.0.1:8000`.*

### Endpoint: `POST /extract`

Este es el endpoint habilitado para procesar los documentos. Acepta requests tipo `multipart/form-data`.

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
