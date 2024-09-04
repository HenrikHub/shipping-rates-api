import pytest
# from app.utils import get_db_pool, startup, shutdown
from app.utils import validate_date
from app.utils import fetch_average_prices

import pytest
#########################################################################################################
# fetch_average_prices tests
#########################################################################################################

@pytest.mark.asyncio
#########################################################################################################
# validate_date tests
#########################################################################################################

def test_validate_date_valid_format():
    assert validate_date("2024-09-03") == "2024-09-03"

def test_validate_date_invalid_format():
    with pytest.raises(ValueError):
        validate_date("2024/09/03")

def test_validate_date_empty_string():
    with pytest.raises(ValueError):
        validate_date("")

def test_validate_date_invalid_day():
    with pytest.raises(ValueError):
        validate_date("2024-09-31")  # September has only 30 days

def test_validate_date_invalid_month():
    with pytest.raises(ValueError):
        validate_date("2024-13-01")  # There is no 13th month
