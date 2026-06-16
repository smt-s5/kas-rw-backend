from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date
import mysql.connector
import os
from dotenv import load_dotenv

# Membaca file .env
load_dotenv()

# Membuat aplikasi FastAPI
app = FastAPI(title="Kas RW API")

# Mengaktifkan CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fungsi koneksi database
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


# Model data transaksi untuk POST
class TransaksiBase(BaseModel):
    tanggal: date
    keterangan: str
    jenis: str
    jumlah: float


# Model data transaksi untuk UPDATE
class TransaksiUpdate(BaseModel):
    tanggal: Optional[date] = None
    keterangan: Optional[str] = None
    jenis: Optional[str] = None
    jumlah: Optional[float] = None


# Endpoint root
@app.get("/")
def root():
    return {"message": "Kas RW API berjalan"}


# Mengambil semua transaksi
@app.get("/transaksi")
def get_all():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM transaksi ORDER BY tanggal DESC"
    )

    rows = cursor.fetchall()

    db.close()

    return rows


# Mengambil satu transaksi berdasarkan ID
@app.get("/transaksi/{id}")
def get_one(id: int):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM transaksi WHERE id=%s",
        (id,)
    )

    row = cursor.fetchone()

    db.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Transaksi tidak ditemukan"
        )

    return row


# Menambah transaksi
@app.post("/transaksi", status_code=201)
def create(data: TransaksiBase):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO transaksi
        (tanggal, keterangan, jenis, jumlah)
        VALUES (%s,%s,%s,%s)
        """,
        (
            data.tanggal,
            data.keterangan,
            data.jenis,
            data.jumlah
        )
    )

    db.commit()

    new_id = cursor.lastrowid

    db.close()

    return {
        "id": new_id,
        "message": "Transaksi berhasil ditambahkan"
    }


# Update transaksi
@app.put("/transaksi/{id}")
def update(id: int, data: TransaksiUpdate):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM transaksi WHERE id=%s",
        (id,)
    )

    row = cursor.fetchone()

    if not row:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="Transaksi tidak ditemukan"
        )

    updated = {
        **row,
        **{
            k: v
            for k, v in data.dict().items()
            if v is not None
        }
    }

    cursor.execute(
        """
        UPDATE transaksi
        SET
        tanggal=%s,
        keterangan=%s,
        jenis=%s,
        jumlah=%s
        WHERE id=%s
        """,
        (
            updated["tanggal"],
            updated["keterangan"],
            updated["jenis"],
            updated["jumlah"],
            id
        )
    )

    db.commit()

    db.close()

    return {
        "message": "Transaksi berhasil diperbarui"
    }


# Menghapus transaksi
@app.delete("/transaksi/{id}")
def delete(id: int):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM transaksi WHERE id=%s",
        (id,)
    )

    db.commit()

    affected = cursor.rowcount

    db.close()

    if affected == 0:
        raise HTTPException(
            status_code=404,
            detail="Transaksi tidak ditemukan"
        )

    return {
        "message": "Transaksi berhasil dihapus"
    }