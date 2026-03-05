# Business logic for storing/retrieving metadata
import logging
from app.db.mongo import get_database
from app.model.schemas import MetadataInfo
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)
COLLECTION = "metadata"

# fetching data from db
async def get_record(url: str):
  db = get_database()
  doc = await db[COLLECTION].find_one({"url": url}, {"_id": 0})
  if doc in None:
    return None
  logger.info("Metadata founded")
  return MetadataInfo(**doc)

async def create_pending(url: str) -> MetadataInfo:
  db = get_database()
  record = MetadataInfo(url=url, status="pending")
  try:
    await db[COLLECTION].insert_one(record.model_dump())
  except DuplicateKeyError:
    exist = await get_record(url=url)
    return exist
  return record

# updating success metadata in db 
async def update_record_success(url: str, headers: dict, cookies: dict, page_source: str) -> None:
  db = get_database()
  now = datetime.now(timezone.utc)
  logger.info("updating metadata")
  await db[COLLECTION].update_one(
    {"url":url},
    {
      "$set": {
        "status": "success",
        "headers": headers,
        "cookies": cookies,
        "page_source": page_source,
        "error": None,
        "updated_at": now,
      }
    }
  )

# updating failed status in db 
async def update_record_failure(url: str, err_msg: str) -> None:
  db = get_database()
  now = datetime.now(timezone.utc)
  logger.warn("updating metadata")
  await db[COLLECTION].update_one(
    {"url":url},
    {
      "$set":{
        "status": "failed",
        "error": err_msg,
        "updated_at": now,
      }
    }
  )
