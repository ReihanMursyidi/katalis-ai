from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from features.rpp_generator import RPPGenerator, generate_rpp
from features.quiz_generator import QuizRequest, generate_quiz_content
from database import check_db_connection, users_collection
from security import verify_password, get_password_hash, create_access_token
from pydantic import BaseModel, EmailStr
from datetime import datetime

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
async def endpoint_rpp(request:RPPGenerator):
    try:
        rpp_content = generate_rpp(request)
        return {"status": "success", "data": rpp_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#ENDPOINT QUIZ GENERATOR
@app.post("/api/generate-quiz")
async def endpoint_quiz(request:QuizRequest):
    try:
        quiz_content = generate_quiz_content(request)
        return {"status": "success", "data": quiz_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)