import asyncio
import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Any, Optional
import crud, database
from logger import logger

from sql_agent import run_agent

router = APIRouter(tags=["Dashboard"])

# --- Pydantic Validation Models for the Agentic Endpoint ---
class AgentRequest(BaseModel):
    question: str

class AgentResponse(BaseModel):
    sql: Optional[str] = None
    result: Any = None
    summary: str
    status: str

# --- EXISTING: Concurrent Dashboard Endpoint (Factor VIII) ---
@router.get("/overall_counts")
async def get_overall_counts(db: AsyncSession = Depends(database.get_db)):
    logger.info("Router: Aggregated dashboard request received.")
    start_time = time.perf_counter()

    # START 8 TASKS SIMULTANEOUSLY (Factor VIII: Concurrency)
    logger.info("Router: Dispatching 8 concurrent database tasks...")
    
    tasks = [
        crud.get_customers_count(db),
        crud.get_orders_count(db),
        crud.get_products_count(db),
        crud.get_employees_count(db),
        crud.get_offices_count(db),
        crud.get_payments_count(db),
        crud.get_orderdetails_count(db),
        crud.get_productlines_count(db)
    ]

    # Await all results at once
    results = await asyncio.gather(*tasks)

    end_time = time.perf_counter()
    total_duration = end_time - start_time
    logger.info(f"Router: Concurrency gather complete in {total_duration:.4f} seconds.")

    return {
        "customers": results[0],
        "orders": results[1],
        "products": results[2],
        "employees": results[3],
        "offices": results[4],
        "payments": results[5],
        "orderdetails": results[6],
        "productlines": results[7],
        "performance_metrics": f"{total_duration:.4f}s"
    }

# --- EXISTING: Individual Customer Count Endpoint ---
@router.get("/customers/count")
async def read_customer_count(db: AsyncSession = Depends(database.get_db)):
    logger.info("Router: Individual customer count request.")
    count = await crud.get_customers_count(db)
    return {"customers": count}


# --- NEW: Mini SQL Agent Execution Endpoint ---
@router.post("/agent/sql", response_model=AgentResponse)
async def execute_agent_sql(payload: AgentRequest):
    logger.info("Router: Web application POST endpoint invoked with question string.")
    
    # Calls the unified single engine workflow managing logs, loops, and safety checks
    response_data = await run_agent(payload.question)
    
    return response_data