import os
import traceback
import time
import multiprocessing
import threading
import uuid

# Configurar variables de entorno globales (para el proceso principal y el worker)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def _ocr_worker_process(task_queue, result_queue):
    """
    Proceso aislado que carga PaddleOCR y ejecuta la inferencia OCR.
    Esto previene los deadlocks críticos de OpenMP/MKL generados por ASGI (FastAPI) 
    y ThreadPoolExecutors en macOS.
    """
    print("[OCR Worker] Inicializando motor PaddleOCR v3 en proceso aislado...")
    try:
        from paddleocr import PaddleOCR
        # Minimizar parámetros para evitar conflictos de compatibilidad en v3.4.x
        ocr = PaddleOCR(lang='es', device='cpu')
        print("[OCR Worker] Motor PaddleOCR listo para recibir tareas.")
    except Exception as e:
        print("[OCR Worker] !!! Error crítico al inicializar PaddleOCR !!!")
        traceback.print_exc()
        # En caso de error crítico, informar e interbloquear el worker
        return

    while True:
        try:
            task = task_queue.get()
            if task is None:
                print("[OCR Worker] Recibida señal de apagado. Saliendo...")
                break
            
            task_id, image_array = task
            start_time = time.time()
            # En PaddleOCR 3.4.0, ocr() es un alias de predict()
            result = ocr.ocr(image_array)
            # print(f"[OCR Worker] Estructura de resultado: {type(result)}") # Opcional: silenciar si se desea
            
            full_text = []
            if result and len(result) > 0:
                for res in result:
                    if res is None:
                        continue
                        
                    # Caso 1: Estructura de diccionario (común en PaddleX / versiones nuevas)
                    if isinstance(res, dict) and 'rec_texts' in res:
                        full_text.extend(res['rec_texts'])
                        
                    # Caso 2: Estructura clásica [[box, [text, score]], ...]
                    elif isinstance(res, list):
                        for line in res:
                            if isinstance(line, list) and len(line) > 1:
                                text_part = line[1]
                                if isinstance(text_part, (list, tuple)):
                                    full_text.append(str(text_part[0]))
            
            final_text = " ".join(full_text)
            elapsed = time.time() - start_time
            print(f"[OCR Worker] Tarea {task_id} finalizada en {elapsed:.2f}s. Texto detectado: {final_text[:50]}...")
            result_queue.put((task_id, final_text, None))
        except Exception as e:
            print(f"[OCR Worker] Error procesando OCR: {e}")
            result_queue.put((task_id, None, str(e)))

class OCREngine:
    def __init__(self):
        print("Iniciando manager de OCREngine (Lazy Mode)...")
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.worker = None
        self.results = {}
        self.events = {}
        self.lock = threading.Lock()
        self.collector_thread = None

    def _ensure_worker_started(self):
        """
        Asegura que el proceso trabajador y el hilo recolector estén iniciados.
        Se llama de forma 'lazy' al primer requerimiento de OCR.
        """
        with self.lock:
            if self.worker is not None and self.worker.is_alive():
                return

            # Solo el proceso principal debe iniciar trabajadores
            if multiprocessing.current_process().name != 'MainProcess':
                return

            print("[OCR Manager] Iniciando proceso trabajador de forma perezosa...")
            
            # Forzar el método spawn en macOS para aislar completamente PaddleOCR
            try:
                multiprocessing.set_start_method('spawn', force=True)
            except RuntimeError:
                pass # Ya estaba configurado o ya se inició un proceso
                
            self.worker = multiprocessing.Process(
                target=_ocr_worker_process, 
                args=(self.task_queue, self.result_queue),
                name="PaddleOCR-Worker"
            )
            self.worker.daemon = True # Morir con el proceso principal
            self.worker.start()
            
            # Iniciar hilo recolector (seguro porque las operaciones de Queue no invocan C++)
            self.collector_thread = threading.Thread(target=self._result_collector, name="OCR-ResultCollector")
            self.collector_thread.daemon = True
            self.collector_thread.start()

    def _result_collector(self):
        while True:
            try:
                task_id, text, error = self.result_queue.get()
                with self.lock:
                    self.results[task_id] = (text, error)
                    if task_id in self.events:
                        self.events[task_id].set()
            except Exception as e:
                print(f"[OCR Manager] Error en recolector: {e}")

    def extract_text(self, image_path_or_array):
        """
        Extrae texto encolando la imagen al proceso de PaddleOCR.
        Es thread-safe e infinitamente más estable en macOS.
        """
        self._ensure_worker_started()
        
        if not self.worker or not self.worker.is_alive():
            return "Error: El proceso OCR no pudo ser iniciado o se detuvo."

        task_id = str(uuid.uuid4())
        event = threading.Event()
        
        with self.lock:
            self.events[task_id] = event
            
        print(f"--- [DEBUG] Enviando imagen a Worker OCR (ID: {task_id}) ---")
        self.task_queue.put((task_id, image_path_or_array))
        
        # Bloquear el hilo de Python hasta obtener respuesta (Seguro para run_in_threadpool)
        if not event.wait(timeout=120): # 2 min max
            with self.lock:
                self.events.pop(task_id, None)
            return "Error: Timeout esperando respuesta del motor OCR."
        
        with self.lock:
            result = self.results.pop(task_id, (None, "Resultado no encontrado tras evento."))
            self.events.pop(task_id, None)
            
        text, error = result
        if error:
            return f"Error en OCR: {error}"
        return text

# Instancia global
# IMPORTANTE: No inicia procesos aquí, solo prepara las colas.
ocr_service = OCREngine()

