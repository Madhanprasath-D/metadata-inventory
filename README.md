**Metadata inventory**

Quick Start
-> Clone the repository
  1. git clone https://github.com/Madhanprasath-D/metadata-inventory
  2. cd metadata-inventory

-> Run with Docker
  1. docker-compose -f docker-compose.yml  up --build

This starts:
  API → port 5004
  MongoDB → internal container

verify 
Open:
  http://localhost:8000/health

Response:
  {"status": "ok"}


**Swagger API Docs**

FastAPI auto-generates docs:
  http://localhost:5004/docs





Design space

post -> /metadata/add
  - take the URL in request body {url: "http://example.com"}
  approach
  - check for data present allready
  if present:
    return deta already exist
  not present:
    fetch the metadata for the given url and store it.
get -> /metadata/fetch
  - take the URL from query and return the metadata
  approach
  - check for data in database
  if present:
    return the data
  not present:
    create a async task to fetch the metadata and store it in db
    return 202 Accepted with msg

database model
{
  "url": "https://example.com",
  "status": "success" | "failed" | "pending",
  "headers": {},
  "cookies": {},
  "page_source": "",
  "error": null,
  "created_at": "",
  "updated_at": ""
}
