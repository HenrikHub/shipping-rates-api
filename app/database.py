from fastapi import HTTPException
import os
import aiopg
import psycopg2
import logging


# Create a logger instance for this module
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        if self.pool is None:
            try:
                self.pool = await aiopg.create_pool(self.dsn)
                logging.info("Successfully connected to the database.")
            except psycopg2.Error as e:  # Catch psycopg2 database errors
                logging.error(f"Failed to connect to the database: {e}")
                raise

    async def disconnect(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logging.info("Database connection pool closed.")
            self.pool = None  # Ensure the pool is set to None after closing

    async def get_pool(self):
        if not self.pool:
            logging.error("Database connection not available.")
            raise ConnectionError("Database connection not available.")
        return self.pool


# Database connection settings
dsn = os.getenv("DATABASE_URL")
db = Database(dsn)

async def get_db_pool():
    try:
        return await db.get_pool()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error.")
    

async def startup():
    await db.connect()

async def shutdown():
    await db.disconnect()
    