from fastAPI import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Kas RW Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

class TransactionBase(BaseModel):
    tanggal : date
    keterangan : str
    jenis : str
    jumlah : float

class updateTransaction(BaseModel):
    tanggal : Optional[date] = None
    keterangan : Optional[str] = None
    jenis : Optional[str] = None
    jumlah : Optional[float] = None

@app.get("/")
def root ():
    return {"message": "Welcome to Kas RW Backend API!"}

@app.post("/transactions", status_code=201)
def create_transaction(transaction: TransactionBase):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO transactions (tanggal, keterangan, jenis, jumlah) VALUES (%s, %s, %s, %s)"
    values = (transaction.tanggal, transaction.keterangan, transaction.jenis, transaction.jumlah)
    cursor.execute(query, values)
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"message": "Transaction created successfully!", "id": new_id}