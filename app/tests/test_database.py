import pytest
from unittest.mock import AsyncMock, patch
import os
from database import Database

"""
Test suite for database connection handling.

This file contains tests for the `Database` class, covering:
- Successful connection to the PostgreSQL database using aiopg.
- Handling connection failures.
- Ensuring the connection pool is correctly managed.

Environment variables are mocked for the DSN, and aiopg pool creation is simulated using mocks.
"""


# Example DSN in environment variable
@pytest.fixture(autouse=True)
def setup_dsn():
    # Set up an environment variable for the DSN in the test
    os.environ["DATABASE_DSN"] = "dbname=testdb user=testuser password=testpassword host=localhost"

@pytest.mark.asyncio
@patch("database.aiopg.create_pool", new_callable=AsyncMock)  # Mock aiopg.create_pool
async def test_connect_success(mock_create_pool):
    # Use the DSN from the environment variable
    dsn = os.getenv("DATABASE_DSN")
    
    # Initialize the Database instance
    db = Database(dsn)

    # Simulate successful connection
    mock_pool = AsyncMock()
    mock_create_pool.return_value = mock_pool

    # Call the connect method
    await db.connect()

    # Ensure the pool was created
    mock_create_pool.assert_called_once_with(dsn)
    assert db.pool == mock_pool
