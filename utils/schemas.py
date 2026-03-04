from pydantic import BaseModel
from typing import List, Optional, Any

class OCRResponse(BaseModel):
    filename: str
    status: str
    extracted_data: Any
    error: Optional[str] = None

class MultiOCRResponse(BaseModel):
    results: List[OCRResponse]
    summary: Optional[str] = None
