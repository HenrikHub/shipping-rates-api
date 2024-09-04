from app.utils import validate_date, fetch_average_prices
from app.database import get_db_pool
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Any
import logging
import psycopg2

# Assuming validate_date and fetch_average_prices are defined elsewhere
# f

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/rates")
async def get_rates(
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    origin: str = Query(..., description="Origin port code or region slug"),
    destination: str = Query(..., description="Destination port code or region slug"),
    db_pool: Any = Depends(get_db_pool),
) -> List[dict]:
    """
    Fetches average freight rates between specified origin and destination ports or regions
    within a given date range.

    Parameters:
    - date_from (str): Start date in YYYY-MM-DD format.
    - date_to (str): End date in YYYY-MM-DD format.
    - origin (str): Origin port code or region slug.
    - destination (str): Destination port code or region slug.
    - db_pool (Any): Database connection pool, injected via dependency.

    Returns:
    - List[dict]: A list of dictionaries containing average prices and other relevant data.

    Raises:
    - HTTPException: If any error occurs during the data fetching process.
    """

    # Validate dates
    date_from = validate_date(date_from)
    date_to = validate_date(date_to)

    try:
        async with db_pool.acquire() as conn:
            data = await fetch_average_prices(conn, date_from, date_to, origin, destination)
            return data
    except psycopg2.DatabaseError as e:
        logger.error(f"Database error fetching rates: {e}")
        raise HTTPException(status_code=500, detail="A database error occurred while fetching rates.")
    except ValueError as e:
        logger.error(f"Validation error fetching rates: {e}")
        raise HTTPException(status_code=400, detail="Invalid input provided for fetching rates.")
    except Exception as e:
        logger.error(f"Unexpected error fetching rates: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching rates.")
