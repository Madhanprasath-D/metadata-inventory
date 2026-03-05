# Background task for async URL processing
import asyncio
import httpx
import logging
from app.services import inventory, retriever

logger = logging.getLogger(__name__)

async def fetch_and_save(url: str) -> None:
  try:
    headers, cookies, page_source = await retriever.retrieve_metadata(url=url)
    logger.info("metadata addes sucessfully")
    await inventory.update_record_success(url, headers, cookies, page_source)
  except httpx.TimeoutException as toe:
    msg = "Request time out"
    await inventory.update_record_failure(url, msg)
    logger.error(msg)
  except httpx.HTTPStatusError as exc:
    msg = f"http {exc.response.status_code} revived"
    await inventory.update_record_failure(url, msg)
    logger.error(msg)
  except httpx.HTTPError as nte:
    msg = f"Network error: {nte}"
    await inventory.update_record_failure(url, msg)
    logger.error(msg)
  except Exception as e:
    msg = f"Unexpected error: {e}"
    await inventory.update_record_failure(url, msg)
    logger.error(msg)


# sheduler that can run async in background task to retreive and store metadata in inventory
def schedule_collection(url: str) -> asyncio.Task:
  logger.info(f"Background work sheduled for url {url}")
  task = asyncio.create_task(fetch_and_save(url), name=f"collect:{url}")
  task.add_done_callback(task_exception)
  return task


def task_exception(task: asyncio.Task) -> None:
  if not task.cancelled() and task_exception():
    print("error", task.get_name(), " :", task.exception())