from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app


client = TestClient(app)

@patch('app.services.inventory.update_record_success', new_callable=AsyncMock)
@patch('app.services.inventory.create_pending', new_callable=AsyncMock)
@patch('app.services.retriever.retrieve_metadata', new_callable=AsyncMock)
@patch('app.services.inventory.get_record', new_callable=AsyncMock)
def test_add_metadata(
    mock_get_record,
    mock_retrieve_metadata,
    mock_create_pending,
    mock_update_success
):
    mock_get_record.return_value = None
    mock_retrieve_metadata.return_value = ({}, {}, "<html></html>")
    responce = client.post(
        '/metadata/add',
        json={'url': "https://example.com/"}
    )
    assert responce.status_code == 201
    data = responce.json()
    assert data['status'] == "success"
    assert data['url'] == 'https://example.com/'


@patch("app.services.inventory.get_record", new_callable=AsyncMock)
def test_get_record_exist(mock_get_record):
    mock_get_record.return_value = {
        "url": "https://example.com/",
        "status": "success",
        "headers": {},
        "cookies": {},
        "page_source": "<html></html>"
    }

    responce = client.get(
        '/metadata/fetch',
        params={'url': 'https://example.com/'}

    )
    assert responce.status_code == 200
    data = responce.json()
    assert data['status'] == "success"

@patch("app.service.inventory.get_record", new_callable=AsyncMock)
@patch("app.services.inventory.create_pending", new_callable=AsyncMock)
@patch("app.worker.worker.schedule_collection")
def est_get_record_not_exist(
    mock_get_record,
    mock_create_pending,
    mock_schedule_collection
):
    mock_get_record.return_value = None
    response = client.get(
        "/metadata/fetch",
        params={"url": "https://example.com/"}
    )

    assert response.status_code == 202
    assert response.json()["status"] == "pending"