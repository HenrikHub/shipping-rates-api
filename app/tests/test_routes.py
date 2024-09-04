import pytest
import psycopg2
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.utils import get_db_pool  # Assuming the functions are in app.utils
from app.routes import router, get_rates

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def db_pool_mock(mocker):
    db_pool = AsyncMock()
    mocker.patch('app.utils.get_db_pool', return_value=db_pool)
    return db_pool

def test_get_rates_happy_path(client, db_pool_mock):
    # Mocking fetch_average_prices to return a known value
    db_pool_mock.acquire.return_value.__aenter__.return_value.cursor.return_value.__aenter__.return_value.fetchall.return_value = [
        ('2024-01-01', 100.0),
        ('2024-01-02', 150.0)
    ]

    response = client.get("/rates", params={
        "date_from": "2024-01-01",
        "date_to": "2024-01-02",
        "origin": "XYZ",
        "destination": "ABC"
    })

    assert response.status_code == 200
    assert response.json() == [
        {"day": "2024-01-01", "average_price": 100.0},
        {"day": "2024-01-02", "average_price": 150.0}
    ]

def test_get_rates_validation_error(client):
    response = client.get("/rates", params={
        "date_from": "invalid-date",
        "date_to": "2024-01-02",
        "origin": "XYZ",
        "destination": "ABC"
    })

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid input provided."}

def test_get_rates_database_error(client, db_pool_mock):
    db_pool_mock.acquire.side_effect = psycopg2.DatabaseError("Database connection failed")

    response = client.get("/rates", params={
        "date_from": "2024-01-01",
        "date_to": "2024-01-02",
        "origin": "XYZ",
        "destination": "ABC"
    })

    assert response.status_code == 500
    assert response.json() == {"detail": "A database error occurred while fetching rates."}
