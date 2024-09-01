import aiopg
import logging

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            self.pool = await aiopg.create_pool(
                dsn="dbname=ratesdb user=postgres password=ratestask host=127.0.0.1"
            )
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            raise

    async def disconnect(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def get_pool(self):
        if self.pool is None:
            raise Exception("Database connection not available.")
        return self.pool

db = Database()
