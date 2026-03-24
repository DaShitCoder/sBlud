from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services.gemini_service import get_chat_response, get_sos_chat_response
from pydantic import BaseModel

app = FastAPI(title="StressBud API")

# Update CORS according to your setup in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    response = get_chat_response(request.message)
    return {"reply": response}

@app.post("/api/sos-chat")
async def sos_chat(request: ChatRequest):
    response = get_sos_chat_response(request.message)
    return {"reply": response}

