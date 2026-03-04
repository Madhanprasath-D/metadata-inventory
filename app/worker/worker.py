import asyncio
import httpx
from app.services import inventory, retriever

async def fetch_and_save(url: str) -> None:
  try:
    headers, cookies, page_source = await retriever.retrieve_metadata(url=url)
    await inventory.update_record_success(url, headers, cookies, page_source)
  except httpx.TimeoutException as toe:
    msg = "Request time out"
    await inventory.update_record_failure(url, msg)
  except httpx.HTTPStatusError as exc:
    msg = f"http {exc.response.status_code} revived"
    await inventory.update_record_failure(url, msg)
  except httpx.HTTPError as nte:
    msg = f"Network error: {nte}"
    await inventory.update_record_failure(url, msg)
  except Exception as e:
    msg = f"Unexpected error: {e}"
    await inventory.update_record_failure(url, msg)



def schedule_collection(url: str) -> asyncio.Task:
  task = asyncio.create_task(fetch_and_save(url), name=f"collect:{url}")
  task.add_done_callback(task_exception)
  return task


def task_exception(task: asyncio.Task) -> None:
  if not task.cancelled() and task_exception():
    print("error", task.get_name(), " :", task.exception())