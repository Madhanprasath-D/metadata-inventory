**Metadata inventory**

Prerequisites
1. Docker and Docker Compose
2. Python 3.11+ (only needed for running tests locally outside Docker)

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

**Endpoints**
-- POST /metadata/add --
Fetches and stores metadata for a given URL.
 - If the URL already exists in the database, returns the existing record.
 - If not, fetches headers, cookies, and page source, stores them in db.

Request
 curl -X POST http://localhost:5004/metadata/add \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

Response (201 Created)

  {
    "url": "https://example.com",
    "status": "success",
    "message": "rl metadata stored"
  }

-- GET /metadata/fetch?url={url} --
Retrieves stored metadata for a given URL.
 - If the record exists, returns the full dataset immediately.
 - If the record does not exist, async background task to fetch it and returns 202 Accepted.

Request 
 curl "http://localhost:5004/metadata/fetch?url=https://example.com"

Response(200 OK)
  {
    "url": "https://example.com",
    "status": "success",
    "headers": { "...": "..." },
    "cookies": {},
    "page_source": "<!doctype html>...",
    "error": null,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }

Response(202 ACCEPTED)
  {
    status: "pending",
    url: "https://example.com",
    message="Metadata not found, will be available shortly"
  }




  
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
