from fastapi import FastAPI
from app.routes import router
from app.database import startup, shutdown
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])

# Include the routes
app.include_router(router)
