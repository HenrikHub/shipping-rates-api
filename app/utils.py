
from datetime import datetime
from typing import List
import logging

# Create a logger instance for this module
logger = logging.getLogger(__name__)


#######################################################################################################################################################################################
# Queries 
#######################################################################################################################################################################################

async def fetch_average_prices(
    conn,
    date_from: str,
    date_to: str,
    origin: str,
    destination: str
) -> List[dict]:
    query = """
    WITH date_series AS (
        SELECT 
            generate_series(%s::date, %s::date, '1 day'::interval) AS day
    ),
    relevant_ports AS (
        SELECT 
            code 
        FROM 
            ports 
        WHERE 
            code = %s OR parent_slug = %s
    ),
    destination_ports AS (
        SELECT 
            code 
        FROM 
            ports 
        WHERE 
            code = %s OR parent_slug = %s
    ),
    filtered_prices AS (
        SELECT
            p.day,
            p.price
        FROM
            prices p
        WHERE
            p.orig_code IN (SELECT code FROM relevant_ports)
            AND p.dest_code IN (SELECT code FROM destination_ports)
    )
    SELECT
        ds.day,
        CASE 
            WHEN COUNT(fp.price) >= 3 THEN AVG(fp.price)
            ELSE NULL
        END AS average_price
    FROM
        date_series ds
    LEFT JOIN 
        filtered_prices fp ON fp.day = ds.day
    GROUP BY 
        ds.day
    ORDER BY 
        ds.day;
    """
    async with conn.cursor() as cur:
        await cur.execute(
            query, (date_from, date_to, origin, origin, destination, destination)
        )
        results = await cur.fetchall()

    return [{"day": str(row[0]), "average_price": row[1]} for row in results]


#######################################################################################################################################################################################
# Validation
#######################################################################################################################################################################################


def validate_date(date_str: str) -> str:
    """
    Validates that the input string is in the format YYYY-MM-DD.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        logger.warning(f"Invalid date format received: {date_str}")
        raise ValueError(f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD.")
