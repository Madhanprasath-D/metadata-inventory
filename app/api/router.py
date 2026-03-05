import httpx
import logging
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from app.model.schemas import RequestInfo, ResponseInfo
from app.services import retriever, inventory
from app.worker import worker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/metadata", tags=["inventory"])


# POST /url/add -> endpoint for adding metadata in inventory
@router.post('/add', response_model=ResponseInfo, status_code=status.HTTP_201_CREATED)
async def add_metadata(req: RequestInfo):
  
  url = str(req.url)
  exist = await inventory.get_record(url=url)
  # check for presnr of data in db
  if exist and exist.status == "success":
    return ResponseInfo(
      message="Record already exists.",
      url=url,
      status=exist.status,
    )
  # creating a initial pending state and update it once successfull got the metadata.
  await inventory.create_pending(url)

  try:
    headers, cookies, page_source = await retriever.retrieve_metadata(url=url)
  except httpx.TimeoutException as toe:
    await inventory.update_record_failure(url, "Request time out")
    logger.info(f"{url} Request time out")
    raise HTTPException(
      status_code=status.HTTP_504_GATEWAY_TIMEOUT,
      detail="Request time out"
    ) from toe
  except httpx.HTTPStatusError as exc:
    msg = f"HTTP {exc.response.status_code} recevied form target"
    logger.info(msg)
    raise HTTPException(
      status_code=status.HTTP_502_BAD_GATEWAY,
      detail=msg
    ) from exc
  except httpx.HTTPError as exc:
    msg = f"Network error: {exc}"
    await inventory.update_record_failure(url, msg)
    logger.info(msg)
    raise HTTPException(
      status_code=status.HTTP_502_BAD_GATEWAY,
      detail=msg
    ) from  exc
  # succesfull data update
  await inventory.update_record_success(url, headers, cookies, page_source)
  logger.info(f"Metadata for {url} added successfully")
  return ResponseInfo(
    url=url,
    message="Url metadata stored",
    status= "success"
  )


# /metadata/fetch -> endpoint for get the metadata from inventory
@router.get('/fetch', response_model=ResponseInfo, responses={
  200: {"model": ResponseInfo, "description": "Record found"},
  202: {"model": ResponseInfo, "description": "Metadata scheduled for collection"},
})
async def get_metadata(
  url: str = Query(..., description="the url that metadata will retrive")
):
  # get the data from db
  record = await inventory.get_record(url)

  if record is not None:
    logger.info(f"url {url} Record founded")
    return ResponseInfo(
      url=url,
      message="Record founded",
      status= "success",
      metadata = record,
    )
  logger.info(f"url {url} Record not founded")
  # creating a initial pending state and update it once successfull got the metadata.
  await inventory.create_pending(url)
  # background sheduler
  worker.schedule_collection(url)

  response = ResponseInfo(
    status="pending",
    url=url,
    message="Metadata not found, will be available shortly"
  )
  return JSONResponse(
    status_code=status.HTTP_202_ACCEPTED,
    content=response.model_dump()
  )