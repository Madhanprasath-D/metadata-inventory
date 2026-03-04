from app.db.mongo import get_database
from app.model.schemas import MetadataInfo
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

COLLECTION = "metadata"

async def get_record(url: str):
  db = get_database()
  doc = await db[COLLECTION].find_one({"url": url}, {"_id": 0})
  if doc in None:
    return None
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


async def update_record_success(url: str, headers: dict, cookies: dict, page_source: str) -> None:
  db = get_database()
  now = datetime.now(timezone.utc)
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


async def update_record_failure(url: str, err_msg: str) -> None:
  db = get_database()
  now = datetime.now(timezone.utc)
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
