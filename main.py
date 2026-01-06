from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from features.rpp_generator import RPPGenerator, generate_rpp
from features.quiz_generator import QuizRequest, generate_quiz_content
from features.admin_generator import RaportRequest, generate_raport
from database import check_db_connection, users_collection
from security import verify_password, get_password_hash, create_access_token
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from bson import ObjectId

import uvicorn

app = FastAPI(title="API EduPlan AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ENDPOINT AUTH

@app.post("/api/auth/register")
async def register(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")

    hashed_password = get_password_hash(user.password)

    new_user = {
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_password,
        "coins": 50,
        "low_balance_since": None,
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

# ENDPOINT HOME
@app.get("/")
def home():
    is_connected = check_db_connection()
    return {
        "status": "online", 
        "db_connected": is_connected, 
        "message": "EduPlan AI Ready 🚀"
    }

#ENDPOINT RPP GENERATOR
@app.post("/api/generate-rpp")
async def endpoint_rpp(request:RPPGenerator, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token tidak ditemukan")

    token = authorization.split(" ")[1]
    user = users_collection.find_one({})

    if not user: raise HTTPException(status_code=401, detail="User tidak valid.")

    is_pro = user.get("is_pro", False)
    cost = 10
    final_cost = 0 if is_pro else cost

    if not is_pro and user.get("coins", 0) < cost:
        raise HTTPException(status_code=400, detail=f"Koin tidak cukup! Butuh {cost} koin.")

    try:
        rpp_content = generate_rpp(request)
        
        # C. POTONG KOIN & UPDATE DB
        if final_cost > 0:
            users_collection.update_one(
                {"_id": user["_id"]}, 
                {"$inc": {"coins": -final_cost}}
            )
            # Ambil koin terbaru setelah dipotong
            updated_user = users_collection.find_one({"_id": user["_id"]})
            remaining_coins = updated_user["coins"]
        else:
            remaining_coins = user.get("coins", 0)

        # D. RETURN HASIL + SISA KOIN (PENTING AGAR UI BERUBAH)
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

#ENDPOINT QUIZ GENERATOR
@app.post("/api/generate-quiz")
async def endpoint_quiz(request: QuizRequest, authorization: str = Header(None)):
    # A. VALIDASI USER & KOIN
    if not authorization:
        raise HTTPException(status_code=401, detail="Token tidak ditemukan.")
    
    token = authorization.split(" ")[1]
    user = users_collection.find_one({}) # Simulasi user
    
    if not user: raise HTTPException(status_code=401, detail="User tidak valid.")

    is_pro = user.get("is_pro", False)
    cost = 10 # Harga Quiz
    final_cost = 0 if is_pro else cost
    
    if not is_pro and user.get("coins", 0) < cost:
        raise HTTPException(status_code=400, detail=f"Koin tidak cukup! Butuh {cost} koin.")

    # B. GENERATE CONTENT
    try:
        quiz_content = generate_quiz_content(request)
        
        # C. POTONG KOIN
        if final_cost > 0:
            users_collection.update_one(
                {"_id": user["_id"]}, 
                {"$inc": {"coins": -final_cost}}
            )
            updated_user = users_collection.find_one({"_id": user["_id"]})
            remaining_coins = updated_user["coins"]
        else:
            remaining_coins = user.get("coins", 0)

        # D. RETURN
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

# SIMPAN HISTORY
def save_history(user_id, type, title, content, is_pro):
    history_data = {
        "user_id": ObjectId(user_id),
        "type": type,
        "title": title,
        "content": content,
        "created_at": datetime.utcnow(),
        "expires_at": None if is_pro else datetime.utcnow() + timedelta(days=30)
    }
    print(f"✅ History disimpan. Expired: {history_data['expires_at']}")

@app.post("/api/generate-raport")
async def endpoint_raport(request: RaportRequest, authorize: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token tidak ditemukan")

    token = authorization.split(" ")[1]

    user = users_collection.find_one({})
    if not user: raise HTTPException(status_code=401, detail="User tidak ditemukan")

    is_pro = user.get("is_pro", False)
    current_coins = user.get("coins", 0)

    # LOGIKA BIAYA
    cost = 30

    if is_pro:
        print("👑 User PRO: Gratis & Pakai Model Canggih")
        final_cost = 0
    else:
        print(f"👤 User FREE: Bayar {cost} Koin")
        if current_coins < cost:
            raise HTTPException(status_code=400, detail="Koin tidak cukup (Butuh 30 Koin). Upgrade ke Pro untuk akses tanpa batas!")
        final_cost = cost

    # GENERATE RAPORT
    try:
        result = generate_raport(request, is_pro_user=is_pro)

        if final_cost > 0:
            users_collection.update_one(
                {"_id": user["_id"]},
                {"$inc": {"coins": -final_cost}}
            )

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
                "remaining_coins": current_coins - final_cost
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)