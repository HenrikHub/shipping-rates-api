import pytest
from app.utils import validate_date
from app.utils import validate_port_or_region

from unittest.mock import AsyncMock, MagicMock

"""
Test suite for utility functions.

This file contains:
- Validation tests for date format and value correctness.
- Tests for validating port or region existence, mocking database responses.

These tests ensure the utility functions behave as expected, including error handling for invalid inputs.
"""



#########################################################################################################
# validation tests
#########################################################################################################

def test_validate_date_success():
    # Test with a valid date string
    date_str = "2023-01-01"
    assert validate_date(date_str) == date_str

def test_validate_date_invalid_format():
    # Test with an invalid date string (wrong format)
    invalid_date_str = "01-2023-01"
    with pytest.raises(ValueError) as exc_info:
        validate_date(invalid_date_str)

def test_validate_date_invalid_value():
    # Test with an invalid date string (non-existent date)
    invalid_date_str = "2023-02-30"
    with pytest.raises(ValueError) as exc_info:
        validate_date(invalid_date_str)


#########################################################################################################

@pytest.mark.asyncio
async def test_validate_port_or_region_success():
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = AsyncMock()
    
    # Simulate the cursor's behavior when querying the database
    mock_cursor.fetchone.return_value = [True]
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    
    # Call the function with a valid slug
    result = await validate_port_or_region(mock_conn, "valid_slug", "origin")
    
    # Ensure the result is True
    assert result is True

@pytest.mark.asyncio
async def test_validate_port_or_region_not_found():
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = AsyncMock()

    # Simulate the cursor returning False (slug not found)
    mock_cursor.fetchone.return_value = [False]
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    
    # Call the function with an invalid slug and expect a ValueError
    with pytest.raises(ValueError) as exc_info:
        await validate_port_or_region(mock_conn, "invalid_slug", "origin")
    
    # Assert that the correct error message is raised
    assert str(exc_info.value) == "The origin 'invalid_slug' does not exist."