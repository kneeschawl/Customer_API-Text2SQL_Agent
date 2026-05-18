import os
import time
import json
import datetime
import requests
import asyncio
import re
import decimal
from sqlalchemy import text
from database import engine
from dotenv import load_dotenv
from decimal import Decimal
from logger import logger

load_dotenv()


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
        
    # Add this handler for Date and Datetime objects
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()  # Converts date objects to "YYYY-MM-DD" strings
        
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

SCHEMA_CONTEXT = """
### ROLE ###
Senior PostgreSQL Architect. Return ONLY raw SQL.

### DATABASE SCHEMA ###
1. customers: "customerNumber" (PK), "customerName", "contactLastName", "contactFirstName", "phone", "addressLine1", "addressLine2", "city", "state", "postalCode", "country", "salesRepEmployeeNumber" (FK), "creditLimit"
2. orders: "orderNumber" (PK), "orderDate", "requiredDate", "shippedDate", "status", "comments", "customerNumber" (FK)
3. orderdetails: "orderNumber" (FK), "productCode" (FK), "quantityOrdered", "priceEach", "orderLineNumber"
4. products: "productCode" (PK), "productName", "productLine", "productScale", "productVendor", "productDescription", "quantityInStock", "buyPrice", "MSRP"
5. employees: "employeeNumber" (PK), "lastName", "firstName", "extension", "email", "officeCode" (FK), "reportsTo" (FK), "jobTitle"
6. offices: "officeCode" (PK), "city", "phone", "addressLine1", "addressLine2", "state", "country", "postalCode", "territory"
7. payments: "customerNumber" (FK), "checkNumber", "paymentDate", "amount"

### SYNTAX LAWS (MANDATORY) ###
1. DOUBLE QUOTES: Every column name with CamelCase MUST be in double quotes (e.g., "customerNumber", "productName", "priceEach"). Lowercase, single-word columns do not need quotes (e.g., status, country, city, amount).
2. NO QUOTES ON TABLES: Table names must be lowercase and unquoted (e.g., FROM orders, FROM customers).
3. NO EXPLANATIONS: Do not say "Here is the query" or "The error was". Output SQL only.

### CRITICAL JOIN PATHS ###
- EMPLOYEES to ORDERS: You MUST use customers as a bridge.
  (employees."employeeNumber" -> customers."salesRepEmployeeNumber") 
  THEN (customers."customerNumber" -> orders."customerNumber")
- PRODUCTS to ORDERS: You MUST use orderdetails as a bridge.
  (products."productCode" -> orderdetails."productCode")
  THEN (orderdetails."orderNumber" -> orders."orderNumber")

### EXAMPLES ###
User: Total payments per customer?
SQL: SELECT c."customerName", SUM(p.amount) FROM customers c JOIN payments p ON c."customerNumber" = p."customerNumber" GROUP BY c."customerName";

User: Who are the sales reps for 'On Hold' orders?
SQL: SELECT DISTINCT e."firstName", e."lastName" FROM employees e JOIN customers c ON e."employeeNumber" = c."salesRepEmployeeNumber" JOIN orders o ON c."customerNumber" = o."customerNumber" WHERE o.status = 'On Hold';
"""

def clean_sql(sql_from_ai):
    """Forcefully cleans the AI output to ensure only executable SQL remains."""
    # 1. Remove markdown backticks
    sql = sql_from_ai.replace("```sql", "").replace("```", "")
    
    # 2. Extract only the first SQL statement
    # We look for the first semicolon and discard everything after it
    if ";" in sql:
        sql = sql.split(";")[0] + ";"
    
    # 3. Final cleanup of whitespace and problematic quotes
    sql = sql.strip().replace("`", "")
    
    # 4. Emergency check: If AI still says "The error was...", 
    # find the last SELECT and start from there.
    if "SELECT" in sql.upper():
        start_idx = sql.upper().find("SELECT")
        sql = sql[start_idx:]

    return sql

def query_local_llm(user_question, error_msg=None, original_sql=None):
    url = "http://localhost:11434/api/generate"
    
    if error_msg:
        # The 'Strict Correction' prompt
        prompt = f"""
{SCHEMA_CONTEXT}
CRITICAL: The previous SQL failed. 
FAILED SQL: {original_sql}
ERROR: {error_msg}

TASK: Identify the error and provide the FIXED SQL.
- If a column wasn't found, you likely forgot "Double Quotes".
- If a join failed, you likely missed a bridge table.
- OUTPUT ONLY THE SQL. NO EXPLANATIONS.
FIXED SQL:"""
    else:
        prompt = f"{SCHEMA_CONTEXT}\nQuestion: {user_question}\nSQL:"

    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0} # Critical for logic
    }
    
    response = requests.post(url, json=payload)
    raw_sql = response.json().get('response', '').strip()
    return clean_sql(raw_sql)

def query_llm_for_summary(user_question, data_result):
    """Converts raw database results into a conversational, natural language response."""
    url = "http://localhost:11434/api/generate"
    prompt = f"""You are a helpful data assistant. Convert the following raw database result into a single, cohesive, natural language summary sentence that directly answers the user's question. Do not explain the SQL logic or output data code blocks.
    
    Question: {user_question}
    Database Result: {data_result}
    
    Summary Sentence:"""
    
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    }
    try:
        response = requests.post(url, json=payload)
        return response.json().get('response', '').strip()
    except Exception as e:
        logger.error(f"Summary Generation Engine Failed: {e}")
        return "Here is the retrieved data from your requested question."
    
    
# Add 'question=None' to allow passing automated strings
async def run_agent(question=None):
    if question is None:
        question = input("What would you like to ask? ")
    
    logger.info("==================================================")
    # --- STEP 1: Understand Query (Decomposition Step Logging Requirement) ---
    logger.info(f"[Step 1: Decomposition] Parsing intent, identifying target tables, and schema maps for question: '{question}'")
    
    max_attempts = 3
    error_msg = None
    generated_sql = None
    final_result = None
    
    for attempt in range(1, max_attempts + 1):
        # --- STEP 2: Generate SQL (Logging Requirement) ---
        logger.info(f"[Step 2: SQL Generation] Attempt {attempt}/{max_attempts} - Formulating query syntax...")
        generated_sql = query_local_llm(question, error_msg=error_msg, original_sql=generated_sql)
        logger.info(f"-> Formulated SQL Query:\n{generated_sql}")
        
        # --- RULES: Safe Query Validation ---
        if not generated_sql.strip().upper().startswith("SELECT"):
            logger.warning(f"[Security Check Blocked]: Malicious intent intercepted.")
            
            # CRITICAL HALT: Don't retry, don't pass go. Return a clear denial immediately.
            return {
                "sql": "BLOCKED_BY_GUARDRAIL",
                "result": None,
                "summary": "Security Policy Violation: I am authorized to perform read-only analytical queries. Data modification commands are strictly prohibited.",
                "status": "failed"
            }
            
        # --- STEP 3: Execute Query & Timing Metric (Logging Requirement) ---
        start_time = time.perf_counter()
        try:
            logger.info(f"Attempt {attempt} - Executing SQL command against database connection...")
            async with engine.connect() as connection:
                result = await connection.execute(text(generated_sql))
                rows = result.fetchall()
                rows_output = [list(row) for row in rows]
                
                # Unpack scalars cleanly if it's a single metric answer (e.g. [[42]] -> 42)
                if len(rows_output) == 1 and len(rows_output[0]) == 1:
                    final_result = rows_output[0][0]
                else:
                    final_result = rows_output
            
            execution_time = time.perf_counter() - start_time
            logger.info(f"[Step 3: Execution Time] Completed successfully in {execution_time:.4f} seconds.")
            
            # --- STEP 5: Final Output & Summary Generation ---
            logger.info("[Step 5: Final Output] Converting raw database rows to natural language statement...")
            summary = query_llm_for_summary(question, final_result)
            logger.info(f"-> Summary Compiled: '{summary}'")
            logger.info("==================================================")
            
            return {
                "sql": generated_sql,
                "result": final_result,
                "summary": summary,
                "status": "success"
            }
            
        except Exception as e:
            # --- STEP 4: Error Handling & Retry State Compiler ---
            execution_time = time.perf_counter() - start_time
            error_msg = str(e)
            logger.error(f"[Failure on Attempt {attempt}] Code aborted in {execution_time:.4f}s. Error: {error_msg}")
            logger.info("Forwarding trace logs to LLM prompt self-correction loop...")

    # --- RULES: Fallback response if all 3 retries completely fail ---
    logger.critical(f"[Fallback Activated] System could not auto-correct query errors after {max_attempts} runs.")
    logger.info("==================================================")
    return {
        "sql": generated_sql if generated_sql else None,
        "result": None,
        "summary": "I'm sorry, I encountered persistent database complications and could not safely process this request.",
        "status": "failed"
    }

if __name__ == "__main__":
    asyncio.run(run_agent())