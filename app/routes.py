from utils import validate_date, fetch_average_prices, validate_port_or_region
from database import get_db_pool
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Any
import logging
import psycopg2

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

    Returns:
    - List[dict]: A list of dictionaries containing average prices and other relevant data.

    Raises:
    - HTTPException: If any error occurs during the data fetching process.
    """

    try:
        # Validate dates
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)

        async with db_pool.acquire() as conn:
            # Validate the existence of the origin and destination
            await validate_port_or_region(conn, origin, "origin")
            await validate_port_or_region(conn, destination, "destination")

            # Fetch data from the database
            data = await fetch_average_prices(conn, date_from, date_to, origin, destination)
            return data  # FastAPI will automatically return this as JSON
    except ValueError as e:
        # This captures validation errors such as invalid date format, origin, or destination
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except psycopg2.DatabaseError as e:
        logger.error(f"Database error fetching rates: {e}")
        raise HTTPException(status_code=500, detail="A database error occurred while fetching rates.")
    except Exception as e:
        logger.error(f"Unexpected error fetching rates: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching rates.")