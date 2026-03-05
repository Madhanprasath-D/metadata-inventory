from fastapi import FastAPI
from app.api.router import router
from app.db.mongo import ensure_indexing, wait_for_mongo, close_client
from contextlib import asynccontextmanager
import logging

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
  logger.info("Inventory server started...")
  await wait_for_mongo()
  await ensure_indexing()
  logger.info("Server ready")
  yield
  await close_client()

app = FastAPI(title="Metadata Inventory", version="1.0.0", lifespan=lifespan)

app.include_router(router=router)

@app.get('/health')
async def check() -> dict:
  return {"status": "ok"}