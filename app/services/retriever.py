import httpx
from typing import Tuple, Dict


async def retrieve_metadata(
  url: str
) -> Tuple[Dict[str, str], Dict[str, str], str]:
  
  async with httpx.AsyncClient(
    follow_redirects=True,
    timeout=5 # todo: need to take for settings
  ) as client:
    res = await client.get(url=url)
    res.raise_for_status()
    headers: Dict[str, str] = dict(res.headers)
    cookies: Dict[str, str] = dict(res.cookies)
    page_source: str = res.text
    return headers, cookies, page_source
