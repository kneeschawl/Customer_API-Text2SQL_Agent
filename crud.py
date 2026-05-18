from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import models
from logger import logger

async def get_count(db: AsyncSession, model):
    """Generic helper to count rows in any table"""
    table_name = model.__tablename__
    logger.info(f"CRUD: Starting count query for {table_name}")
    try:
        result = await db.execute(select(func.count()).select_from(model))
        count = result.scalar()
        logger.info(f"CRUD: Completed count for {table_name}: {count}")
        return count
    except Exception as e:
        logger.error(f"CRUD: Error counting {table_name}: {e}")
        return 0

# Modular wrappers for clarity
async def get_customers_count(db: AsyncSession): return await get_count(db, models.Customer)
async def get_orders_count(db: AsyncSession): return await get_count(db, models.Order)
async def get_products_count(db: AsyncSession): return await get_count(db, models.Product)
async def get_employees_count(db: AsyncSession): return await get_count(db, models.Employee)
async def get_offices_count(db: AsyncSession): return await get_count(db, models.Office)
async def get_payments_count(db: AsyncSession): return await get_count(db, models.Payment)
async def get_orderdetails_count(db: AsyncSession): return await get_count(db, models.OrderDetail)
async def get_productlines_count(db: AsyncSession): return await get_count(db, models.ProductLine)