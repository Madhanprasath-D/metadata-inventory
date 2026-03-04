from fastapi import FastAPI
from app.api.router import router
from app.db.mongo import ensure_indexing, wait_for_mango, close_client
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
  await wait_for_mango()
  await ensure_indexing()

  yield
  await close_client()

app = FastAPI(title="Metadata Inventory", version="1.0.0", lifespan=lifespan)

app.include_router(router=router)

@app.get('/health')
async def check() -> dict:
  return {"status": "ok"}