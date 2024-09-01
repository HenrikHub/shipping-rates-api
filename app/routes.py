from fastapi import APIRouter, Depends, HTTPException, Query
from .database import db
from datetime import datetime
from typing import List, Optional

router = APIRouter()

async def get_db_pool():
    try:
        return await db.get_pool()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

def validate_date(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD.")

async def fetch_average_prices(
    conn,
    date_from: str,
    date_to: str,
    origin: str,
    destination: str
) -> List[dict]:
    query = """
    SELECT 
        date_trunc('day', p.date) AS day,
        AVG(p.price) AS average_price
    FROM 
        prices p
    JOIN 
        ports po_origin ON po_origin.code = p.origin
    JOIN 
        ports po_dest ON po_dest.code = p.destination
    WHERE 
        (po_origin.code = %s OR po_origin.slug = %s)
        AND (po_dest.code = %s OR po_dest.slug = %s)
        AND p.date BETWEEN %s AND %s
    GROUP BY day
    HAVING COUNT(p.price) >= 3
    ORDER BY day;
    """
    async with conn.cursor() as cur:
        await cur.execute(
            query, (origin, origin, destination, destination, date_from, date_to)
        )
        results = await cur.fetchall()
        
        return [{"day": str(row[0]), "average_price": row[1]} for row in results]

@router.get("/rates")
async def get_rates(
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    origin: str = Query(..., description="Origin port code or region slug"),
    destination: str = Query(..., description="Destination port code or region slug"),
    db_pool=Depends(get_db_pool),
):
    # Validate dates
    date_from = validate_date(date_from)
    date_to = validate_date(date_to)
    
    async with db_pool.acquire() as conn:
        try:
            data = await fetch_average_prices(conn, date_from, date_to, origin, destination)
            return data
        except Exception as e:
            logging.error(f"Error fetching rates: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while fetching rates.")
