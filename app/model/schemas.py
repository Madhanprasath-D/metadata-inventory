# Pydantic models for request validation and response serialisation.
from pydantic import BaseModel, AnyHttpUrl, Field
from typing import Dict, Any, Literal, Optional
from datetime import datetime, timezone

# Request model
class RequestInfo(BaseModel):
  url: AnyHttpUrl

# databse model
class MetadataInfo(BaseModel):
  url: str
  headers: Optional[Dict[str, Any]] = None
  cookies: Optional[Dict[str, Any]] = None
  page_source: Optional[str] = None
  created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  error: Optional[str] = None
  status:  Literal["success", "failed", "pending"]

# Resonce model for ack
class ResponseInfo(BaseModel):
    status: Literal["success", "failed", "pending"]
    url: str
    message: Optional[str] = None
    metadata: Optional[MetadataInfo] = None