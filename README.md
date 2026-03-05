# Metadata Inventory

---

## Prerequisites

1. Docker and Docker Compose
2. Python 3.11+ *(only needed for running tests locally outside Docker)*

---

## Quick Start

**1. Clone the repository**

git clone https://github.com/Madhanprasath-D/metadata-inventory
cd metadata-inventory


**2. Run with Docker**

docker-compose -f docker-compose.yml up --build


This starts:
- **API** → `http://localhost:5004`
- **MongoDB** → internal container

**3. Verify the service is running**

curl http://localhost:5004/health
# {"status": "ok"}


---

## Swagger API Docs

FastAPI auto-generates interactive docs:

**http://localhost:5004/docs**

---

## Endpoints

### `POST /metadata/add`

Fetches and stores metadata for a given URL.

- If the URL already exists in the database, returns the existing record.
- If not, fetches headers, cookies, and page source, then stores them in the database.

**Request:**

curl -X POST http://localhost:5004/metadata/add \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'


**Response (201 Created):**

{
  "url": "https://example.com",
  "status": "success",
  "message": "URL metadata stored"
}


---

### `GET /metadata/fetch?url={url}`

Retrieves stored metadata for a given URL.

- If the record **exists**, returns the full dataset immediately.
- If the record **does not exist**, triggers an async background task to fetch it and returns `202 Accepted`.

**Request:**

curl "http://localhost:5004/metadata/fetch?url=https://example.com"


**Response (200 OK):**

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


**Response (202 Accepted):**

{
  "status": "pending",
  "url": "https://example.com",
  "message": "Metadata not found, will be available shortly"
}


---

## Database Schema


{
  "url": "https://example.com",
  "status": "success | failed | pending",
  "headers": {},
  "cookies": {},
  "page_source": "",
  "error": null,
  "created_at": "",
  "updated_at": ""
}


---

## Design Notes

### `POST /metadata/add`
- Accepts a URL in the request body `{ "url": "https://example.com" }`
- Checks if the record already exists in the database
  - If present → returns existing record
  - If not → fetches metadata and stores it

### `GET /metadata/fetch`
- Accepts a URL as a query parameter
- Checks the database for an existing record
  - If present → returns the data
  - If not → creates an async background task to fetch and store the metadata, returns `202 Accepted`
