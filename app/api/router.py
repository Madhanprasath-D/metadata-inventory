import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from fastapi.responses import JSONResponse
from app.model.schemas import RequestInfo, MetadataInfo, AcknowledgementResponse
from app.services import retriever, inventory
from app.worker import worker

router = APIRouter(prefix="/metadata", tags=["inventory"])

# POST /url/add -> the endpoint for adding metadata in inventory
@router.post('/add', response_model=AcknowledgementResponse, status_code=status.HTTP_201_CREATED)
async def add_metadata(req: RequestInfo):
  url = req.url
  exist = await inventory.get_record(url=url)
  if exist and exist.status == "success":
    return AcknowledgementResponse(
      message="Record already exists.",
      url=url,
      status=exist.status,
    )
  
  await inventory.create_pending(url)

  try:
    headers, cookies, page_source = await retriever.retrieve_metadata(url=url)
  except httpx.TimeoutException as toe:
    await inventory.update_record_failure(url, "Requset time out")
    raise HTTPException(
      status_code=status.HTTP_504_GATEWAY_TIMEOUT,
      detail="Request time out"
    ) from toe
  except httpx.HTTPError as exc:
    msg = f"Network error: {exc}"
    await inventory.update_record_failure(url, msg)
    raise HTTPException(
      status_code=status.HTTP_502_BAD_GATEWAY,
      detail=msg
    ) from  exc
  except httpx.HTTPStatusError as exc:
    msg = f"HTTP {exc.response.status_code} recevied form target"
    raise HTTPException(
      status_code=status.HTTP_502_BAD_GATEWAY,
      detail=msg
    ) from exc
  
  await inventory.update_record_success(url, headers, cookies, page_source)

  return AcknowledgementResponse(
    url=url,
    message="Url metadata stored",
    status= "success"
  )



@router.get('/fetch')
async def get_metadata(
  url: str = Query(..., description="the url that metadata will retrive")
):
  record = await inventory.get_record(url)

  if record is not None:
    return MetadataInfo(
      url=record.url,
      status=record.status,
      headers=record.headers,
      cookies=record.cookies,
      error=record.error,
      created_at=record.created_at,
      updated_at=record.updated_at,
    )
  
  await inventory.create_pending(url)
  worker.schedule_collection(url)

  responce = AcknowledgementResponse(
    url=url,
    message="Metadata for this URL was not founded in the inventory. It will be available shortly",
    status=status.HTTP_202_ACCEPT,
  )
  return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=responce.model_dump())