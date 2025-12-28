from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from features.rpp_generator import RPPGenerator, generate_rpp
from features.quiz_generator import QuizRequest, generate_quiz_content
import uvicorn

app = FastAPI(title="API Asisten Guru AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Server Asisten Guru AI siap melayani! 🚀"
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)