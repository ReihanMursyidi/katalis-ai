from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from features.rpp_generator import RPPGenerator, generate_rpp
from features.quiz_generator import QuizRequest, generate_quiz_content
from features.admin_generator import RaportRequest, generate_raport # Pastikan nama class sesuai
from database import check_db_connection, users_collection
from security import verify_password, get_password_hash, create_access_token
from pydantic import BaseModel
from datetime import datetime, timedelta
from bson import ObjectId
import os
from jose import jwt, JWTError # PENTING: Untuk decode token
from dotenv import load_dotenv
import uvicorn

# Load Env untuk ambil SECRET_KEY
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

app = FastAPI(title="API EduPlan AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# --- HELPER FUNCTION: AMBIL USER DARI TOKEN ---
def get_user_from_token(authorization: str):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token tidak ditemukan")
    
    try:
        # Format: "Bearer <token>"
        token = authorization.split(" ")[1]
        
        # Decode Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        if not email:
            raise HTTPException(status_code=401, detail="Token tidak valid")
            
        # Cari User Berdasarkan Email yang ada di Token
        user = users_collection.find_one({"email": email})
        
        if not user:
            raise HTTPException(status_code=401, detail="User tidak ditemukan di database")
            
        return user
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Token kadaluwarsa atau tidak valid")
    except IndexError:
        raise HTTPException(status_code=401, detail="Format token salah")

# --- ENDPOINTS AUTH ---

@app.post("/api/auth/register")
async def register(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")

    hashed_password = get_password_hash(user.password)

    new_user = {
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_password,
        "coins": 50, # Bonus awal
        "is_pro": False, # Default Free
        "created_at": datetime.utcnow()
    }

    users_collection.insert_one(new_user)
    return {"status": "success", "message": "Registrasi berhasil! Silahkan login."}

@app.post("/api/auth/login")
async def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Email atau password salah.")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Email atau password salah.")

    # Buat Token
    access_token = create_access_token(data={"sub": user.email, "id": str(db_user['_id'])})

    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "full_name": db_user["full_name"],
            "coins": db_user.get('coins', 0)
        }
    }

@app.get("/")
def home():
    is_connected = check_db_connection()
    return {"status": "online", "db_connected": is_connected, "message": "EduPlan AI Ready 🚀"}

# --- ENDPOINT RPP GENERATOR ---
@app.post("/api/generate-rpp")
async def endpoint_rpp(request: RPPGenerator, authorization: str = Header(None)):
    # 1. Ambil User ASLI dari Token (Bukan user sembarang)
    user = get_user_from_token(authorization)

    is_pro = user.get("is_pro", False)
    cost = 10
    final_cost = 0 if is_pro else cost

    # Cek Saldo
    if not is_pro and user.get("coins", 0) < cost:
        raise HTTPException(status_code=400, detail=f"Koin tidak cukup! Butuh {cost} koin.")

    try:
        rpp_content = generate_rpp(request)
        
        # Potong Koin
        if final_cost > 0:
            users_collection.update_one(
                {"_id": user["_id"]}, 
                {"$inc": {"coins": -final_cost}}
            )
            # Ambil Data Terbaru
            updated_user = users_collection.find_one({"_id": user["_id"]})
            remaining_coins = updated_user["coins"]
        else:
            remaining_coins = user.get("coins", 0)

        return {
            "status": "success", 
            "data": rpp_content,
            "meta": {
                "cost_deducted": final_cost,
                "remaining_coins": remaining_coins
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ENDPOINT QUIZ GENERATOR ---
@app.post("/api/generate-quiz")
async def endpoint_quiz(request: QuizRequest, authorization: str = Header(None)):
    user = get_user_from_token(authorization)

    is_pro = user.get("is_pro", False)
    cost = 10
    final_cost = 0 if is_pro else cost
    
    if not is_pro and user.get("coins", 0) < cost:
        raise HTTPException(status_code=400, detail=f"Koin tidak cukup! Butuh {cost} koin.")

    try:
        quiz_content = generate_quiz_content(request)
        
        if final_cost > 0:
            users_collection.update_one(
                {"_id": user["_id"]}, 
                {"$inc": {"coins": -final_cost}}
            )
            updated_user = users_collection.find_one({"_id": user["_id"]})
            remaining_coins = updated_user["coins"]
        else:
            remaining_coins = user.get("coins", 0)

        return {
            "status": "success", 
            "data": quiz_content,
             "meta": {
                "cost_deducted": final_cost,
                "remaining_coins": remaining_coins
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- HISTORY HELPER ---
def save_history(user_id, type, title, content, is_pro):
    history_data = {
        "user_id": ObjectId(user_id),
        "type": type,
        "title": title,
        "content": content,
        "created_at": datetime.utcnow(),
        "expires_at": None if is_pro else datetime.utcnow() + timedelta(days=30)
    }
    # Jika punya collection history, uncomment baris bawah:
    # db.history.insert_one(history_data)
    print(f"✅ History disimpan. Expired: {history_data['expires_at']}")

# --- ENDPOINT RAPORT GENERATOR ---
@app.post("/api/generate-raport")
# Perbaikan Typo: 'authorize' diganti 'authorization' agar konsisten dengan Header
async def endpoint_raport(request: RaportRequest, authorization: str = Header(None)):
    user = get_user_from_token(authorization)

    is_pro = user.get("is_pro", False)
    cost = 30
    final_cost = 0 if is_pro else cost

    if not is_pro and user.get("coins", 0) < cost:
        raise HTTPException(status_code=400, detail="Koin tidak cukup (Butuh 30 Koin). Upgrade ke Pro!")

    try:
        # Generate pakai logic yang sudah ada
        result = generate_raport(request, is_pro_user=is_pro)

        if final_cost > 0:
            users_collection.update_one(
                {"_id": user["_id"]}, 
                {"$inc": {"coins": -final_cost}}
            )
            updated_user = users_collection.find_one({"_id": user["_id"]})
            remaining_coins = updated_user["coins"]
        else:
            remaining_coins = user.get("coins", 0)

        save_history(
            user_id=str(user["_id"]),
            type="raport",
            title=f"Rapor {request.nama_siswa}",
            content=result["content"],
            is_pro=is_pro
        )

        return {
            "status": "success",
            "data": result["content"],
            "meta": {
                "model": result["model_used"],
                "cost_deducted": final_cost,
                "remaining_coins": remaining_coins
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)