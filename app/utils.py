
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
    WITH RECURSIVE all_origin_regions AS (
        -- Start with the provided origin region and recursively find child regions
        SELECT slug
        FROM regions
        WHERE slug = %s

        UNION ALL

        SELECT r.slug
        FROM regions r
        JOIN all_origin_regions aor ON r.parent_slug = aor.slug
    ),
    all_destination_regions AS (
        -- Start with the provided destination region and recursively find child regions
        SELECT slug
        FROM regions
        WHERE slug = %s

        UNION ALL

        SELECT r.slug
        FROM regions r
        JOIN all_destination_regions adr ON r.parent_slug = adr.slug
    ),
    relevant_origin_ports AS (
        -- Get all ports under the origin region or use the specific origin port code
        SELECT code
        FROM ports
        WHERE parent_slug IN (SELECT slug FROM all_origin_regions)
        OR code = %s
    ),
    relevant_destination_ports AS (
        -- Get all ports under the destination region or use the specific destination port code
        SELECT code
        FROM ports
        WHERE parent_slug IN (SELECT slug FROM all_destination_regions)
        OR code = %s
    ),
    date_series AS (
        -- Generate the list of dates within the provided range
        SELECT 
            generate_series(%s::date, %s::date, '1 day'::interval) AS day
    ),
    filtered_prices AS (
        -- Filter prices between the relevant origin and destination ports
        SELECT
            p.day,
            p.price
        FROM
            prices p
        WHERE
            p.orig_code IN (SELECT code FROM relevant_origin_ports)
            AND p.dest_code IN (SELECT code FROM relevant_destination_ports)
    )
    -- Calculate average prices per day, returning NULL if fewer than 3 prices
    SELECT
        ds.day,
        CASE 
            WHEN COUNT(fp.price) >= 3 THEN ROUND(AVG(fp.price), 2)
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
            query, (origin, destination, origin, destination, date_from, date_to)

        )
        results = await cur.fetchall()

    return [{"day": str(row[0]), "average_price": row[1]} for row in results]


#######################################################################################################################################################################################
# Validation
#######################################################################################################################################################################################


def validate_date(date_str: str) -> str:
    """
    Validates that the input string is in the format YYYY-MM-DD.
    If the format is incorrect, raises a ValueError with a clear message.
    """
    try:
        # Try to parse the date
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        # Log a warning and raise a ValueError with more specific feedback
        logger.warning(f"Invalid date format received: {date_str}")
        raise ValueError(f"Invalid date format: '{date_str}'. Expected format: YYYY-MM-DD.")
