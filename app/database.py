from fastapi import HTTPException
import os
import aiopg
import psycopg2
import logging


# Create a logger instance for this module
logger = logging.getLogger(__name__)


class Database:
    """
    Manages a PostgreSQL database connection pool.
    """

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        """
        Establish a connection pool to the database.
        """
        if self.pool is None:
            try:
                self.pool = await aiopg.create_pool(self.dsn)
                logging.info("Successfully connected to the database.")
            except psycopg2.Error as e:
                logging.error(f"Failed to connect to the database: {e}")
                raise

    async def disconnect(self):
        """
        Close the database connection pool.
        """
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logging.info("Connection pool closed.")
            self.pool = None

    async def get_pool(self):
        """
        Get the connection pool or raise an error if unavailable.
        """
        if not self.pool:
            logging.error("No active database connection.")
            raise ConnectionError("No active database connection.")
        return self.pool


# Database connection settings
dsn = os.getenv("DATABASE_URL")
db = Database(dsn)

async def get_db_pool():
    """
        Get the current database connection pool.
        """
    try:
        return await db.get_pool()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error.")
    

async def startup():
    """
    Connect to the database on application startup.
    """
    await db.connect()

async def shutdown():
    """
    Disconnect from the database on application shutdown.
    """
    await db.disconnect()
