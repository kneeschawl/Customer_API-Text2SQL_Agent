from fastapi import FastAPI
import database
import models
import router
from logger import logger

# Initialize DB tables (Verifies connection to Docker)
try:
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Main: Database tables checked/verified successfully.")
except Exception as e:
    logger.error(f"Main: Database connection failed! Error: {e}")

app = FastAPI(title="Customer API")

# Include the router
app.include_router(router.router)

@app.get("/")
def root():
    logger.info("Main: Root endpoint accessed.")
    return {"message": "Customer API is online and running!"}