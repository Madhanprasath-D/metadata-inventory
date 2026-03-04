# 
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Literal, Optional
from datetime import datetime


class RequestInfo(BaseModel):
  url: HttpUrl

class MetadataInfo(BaseModel):
  url: str
  headers: Optional[Dict[str, Any]] = None
  cookies: Optional[Dict[str, Any]] = None
  page_source: str
  created_at: datetime
  updated_at: datetime
  error: Optional[str] = None
  status:  Literal["success", "failed", "pending"]

class AcknowledgementResponse(BaseModel):
  message: str
  status: str
  url: str