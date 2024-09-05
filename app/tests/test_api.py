import pytest
import psycopg2
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock,MagicMock, patch
from main import app

client = TestClient(app)

"""
Test suite for API endpoints.

This file contains tests for the `/rates` endpoint, including:
- Successful fetching of rates with valid parameters.
- Handling of database connection errors during the fetching process.

Mocks are used to simulate database behavior and control the responses.
"""

# Mock response for fetch_average_prices
mocked_fetch_average_prices = [
    {"day": "2023-01-01", "average_price": 1000},
    {"day": "2023-01-02", "average_price": 1100},
    {"day": "2023-01-03", "average_price": None},
]

@pytest.mark.asyncio
@patch("database.db.get_pool", new_callable=AsyncMock)  # Correct path to mock db.get_pool
@patch("routes.validate_port_or_region", new_callable=AsyncMock)  # Mock validate_port_or_region
@patch("routes.fetch_average_prices", new_callable=AsyncMock)  # Mock fetch_average_prices
async def test_get_rates_success(mock_fetch_average_prices, mock_validate_port_or_region, mock_get_pool):
    # Setup mocks
    mock_fetch_average_prices.return_value = mocked_fetch_average_prices
    mock_validate_port_or_region.return_value = True
    
    # Simulated connection object (no actual database involved)
    mock_conn = AsyncMock()

    # Mock the pool acquire and connection methods properly
    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_get_pool.return_value = mock_pool  # get_pool returns the mock pool

    # Make a GET request to the /rates endpoint
    response = client.get(
        "/rates?date_from=2023-01-01&date_to=2023-01-03&origin=valid_origin&destination=valid_destination"
    )

    # Assert that the status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response matches the mocked fetch_average_prices
    assert response.json() == mocked_fetch_average_prices

client = TestClient(app)

@pytest.mark.asyncio
@patch("database.db.get_pool", new_callable=AsyncMock)  # Correct path to mock db.get_pool
@patch("routes.validate_port_or_region", new_callable=AsyncMock)  # Mock validate_port_or_region
@patch("routes.fetch_average_prices", new_callable=AsyncMock)  # Mock fetch_average_prices
async def test_get_rates_database_error(mock_fetch_average_prices, mock_validate_port_or_region, mock_get_pool):
    # Simulate psycopg2.DatabaseError when fetching prices
    mock_fetch_average_prices.side_effect = psycopg2.DatabaseError("Database connection error.")

    # Mock validate_port_or_region to succeed
    mock_validate_port_or_region.return_value = True

    # Mock connection pool acquire method
    mock_conn = AsyncMock()
    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_get_pool.return_value = mock_pool

    # Make a GET request
    response = client.get(
        "/rates?date_from=2023-01-01&date_to=2023-01-03&origin=valid_origin&destination=valid_destination"
    )

    # Assert status code and error message
    assert response.status_code == 500
    assert response.json()["detail"] == "A database error occurred while fetching rates."

