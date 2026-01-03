from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import certifi
from dotenv import load_dotenv

# 1. Load konfigurasi dari file .env
load_dotenv()

# 2. Ambil URL Koneksi
MONGO_URI = os.getenv("MONGODB_URI")

# Validasi: Pastikan URL ada
if not MONGO_URI:
    print("❌ PERINGATAN: MONGO_URI tidak ditemukan di file .env")

client = None
db = None
users_collection = None

# 3. Inisialisasi Client
try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client["eduplan_db"]
    users_collection = db["users"]
    client.admin.command('ping')

    print("✅ Koneksi Database Siap!")

except Exception as e:
    print(f"❌ Terjadi kesalahan saat inisialisasi database: {e}")

# Fungsi Helper untuk mengecek status koneksi (dipanggil di main.py)
def check_db_connection():
    try:
        if client:
            client.admin.command('ping')
            return True
        return False
    except Exception:
        return False