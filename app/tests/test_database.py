import pytest
from unittest.mock import patch, AsyncMock
from app.database import Database  # Replace 'your_module' with the actual module name

@pytest.mark.asyncio
async def test_database_initialization():
    db = Database("dbname=ratesdb user=postgres password=ratestask host=127.0.0.1")
    assert db.dsn == "dbname=ratesdb user=postgres password=ratestask host=127.0.0.1"
    assert db.pool is None

@pytest.mark.asyncio
@patch('aiopg.create_pool', new_callable=AsyncMock)
async def test_database_connect_success(mock_create_pool):
    db = Database("dsn")
    await db.connect()
    mock_create_pool.assert_called_once_with("dsn")
    assert db.pool is mock_create_pool.return_value

@pytest.mark.asyncio
@patch('aiopg.create_pool', new_callable=AsyncMock, side_effect=Exception("Connection failed"))
async def test_database_connect_failure(mock_create_pool):
    db = Database("dsn")
    with pytest.raises(Exception, match="Connection failed"):
        await db.connect()

@pytest.mark.asyncio
async def test_database_disconnect():
    db = Database("dsn")
    db.pool = AsyncMock()
    await db.disconnect()
    db.pool.close.assert_called_once()
    db.pool.wait_closed.assert_called_once()
    assert db.pool is None

@pytest.mark.asyncio
async def test_get_pool_success():
    db = Database("dsn")
    db.pool = AsyncMock()
    pool = await db.get_pool()
    assert pool is db.pool

@pytest.mark.asyncio
async def test_get_pool_failure():
    db = Database("dsn")
    with pytest.raises(ConnectionError, match="Database connection not available"):
        await db.get_pool()
