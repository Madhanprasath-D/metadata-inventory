# Initialize Mongo client once during startup
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from pymongo import ASCENDING
from app.core.config import settings

logger = logging.getLogger(__name__)

# Module level client
_client: Optional[AsyncIOMotorClient] = None

def get_client() -> AsyncIOMotorClient:
  global _client
  if _client == None:
    _client = AsyncIOMotorClient(settings.mongo_uri)
  return _client


def get_database() -> AsyncIOMotorDatabase:
  return get_client()[settings.mongo_db] 


async def ensure_indexing() -> None:
  db = get_database()
  # create index will help to incress the speed of reading data in O(log n)
  await db.metadata.create_index([("url", ASCENDING)], unique=True)

async def wait_for_mongo(reties: int = 5, delay: float = 2.0) -> None:
  client = get_client()
  for attempt in range(reties):
    try:
      logger.info("Attempting to connect")
      await client.admin.command('ping')
      return
    except Exception as exc:
      if attempt == reties - 1:
        logger.error("Could not connect to the database")
        raise RuntimeError("Could not connect to the database") from exc
      await asyncio.sleep(delay=delay)
      

async def close_client() -> None:
  global _client
  if _client is not None:
    _client.close()
    _client = None