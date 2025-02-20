import logging
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
import asyncpg
from pydantic import BaseModel, Field
from langchain_deepseek import ChatDeepSeek
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("api")

# Model for expense parsing
class ExpenseInfo(BaseModel):
    is_expense: bool
    description: Optional[str]
    amount: Optional[float]
    category: Optional[str]

class BaseResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    message: Optional[str] = None

class ExpenseResponse(BaseResponse):
    data: Optional[dict] = {"category": str, "amount": int, "description": str}

class ErrorResponse(BaseResponse):
    status: str = "error"
    message: str

# LangChain setup
predefined_categories = [
    "Housing", "Transportation", "Food", "Utilities", "Insurance", "Medical/Healthcare",
    "Savings", "Debt", "Education", "Entertainment", "Other"
]

parser = PydanticOutputParser(pydantic_object=ExpenseInfo)

prompt = ChatPromptTemplate.from_template(
    """You are an expense-tracking assistant. Your job is to analyze user messages, extract expense details, and classify them into predefined categories.
    
Categories: {cats}

Instructions:
- If the message contains an expense (e.g., "Pizza 20 bucks"), extract the **item**, **amount**, and **currency** (if specified).
- Categorize the expense correctly based on its description.
- If the message does **not** describe an expense, return **None**.
- Do not assume details that are not provided.

{format_instructions}

Message: {message}""",
    partial_variables={
        "cats": ", ".join(predefined_categories),
        "format_instructions": parser.get_format_instructions(),
    },
)
model = ChatDeepSeek(model="deepseek-chat", temperature=0, max_tokens=None, timeout=None, max_retries=2)
chain = prompt | model | parser

# API SETUP
app = FastAPI()
pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    try:
        pool = await asyncpg.create_pool(
            os.getenv("DATABASE_URL"), min_size=5, max_size=20, timeout=10
        )
        logger.info("Database connection pool created.")
        yield
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise
    finally:
        if pool:
            await pool.close()
            logger.info("Database connection pool closed.")

app = FastAPI(lifespan=lifespan)

class AddUserRequest(BaseModel):
    telegram_id: str = Field(..., min_length=5)

@app.post("/add_user", description="Add a user to the whitelist")
async def add_user(request: AddUserRequest):
    try:
        existing_user = await pool.fetchrow("SELECT id FROM users WHERE telegram_id = $1", request.telegram_id)
        if existing_user:
            return JSONResponse(status_code=400, content={"status": "error", "message": "User already exists"})

        await pool.execute("INSERT INTO users (telegram_id) VALUES ($1)", request.telegram_id)
        return {"status": "success", "message": "User added to whitelist"}
    except Exception as e:
        logger.error(f"Failed to add user: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Database error"})

class ProcessRequest(BaseModel):
    telegram_id: str = Field(..., min_length=5)
    message: str = Field(..., min_length=2)

@app.post("/process_message",
    responses={200: {"model": ExpenseResponse}, 500: {"model": ErrorResponse}},
    description="Process user messages for expense tracking"
)
async def process_message(request: ProcessRequest):
    logger.info(f"Received message processing request for telegram_id: {request.telegram_id}")
    
    # Check user exists
    try:
        user = await pool.fetchrow("SELECT id FROM users WHERE telegram_id = $1", request.telegram_id)
        if not user:
            logger.warning(f"User not found: {request.telegram_id}")
            return JSONResponse(status_code=200, content={"status": "ignored", "message": "User not found"})
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Database error"})
    
    # Parse message
    try:
        expense = await chain.ainvoke({"message": request.message})
        logger.info(f"Parsed expense: {expense}")
    except Exception as e:
        logger.error(f"Message analysis failed: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Analysis failed"})
    
    if not expense.is_expense:
        logger.info("Message not related to expense.")
        return {"status": "ignored", "message": "Not expense-related."}
    
    # Validate category
    category = expense.category if expense.category in predefined_categories else "Other"
    if not expense.description or not expense.amount:
        logger.warning("Invalid expense details detected.")
        return {"status": "error", "message": "Invalid expense details"}
    
    # Insert expense
    try:
        await pool.execute(
            """
            INSERT INTO expenses (user_id, description, amount, category, added_at)
            VALUES ($1, $2, $3::money, $4, NOW())
            """,
            user["id"],
            expense.description,
            f"{expense.amount:.2f}",
            category,
        )
        logger.info(f"Expense recorded: {expense.description}, Amount: {expense.amount}, Category: {category}")
    except Exception as e:
        logger.error(f"Database insert failed: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Database error"})
    
    return ExpenseResponse(
        status="success",
        data={"category": category, "description": expense.description, "amount": expense.amount},
    )