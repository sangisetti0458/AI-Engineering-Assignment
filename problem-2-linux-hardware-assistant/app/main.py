
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from app.ai.chat_service import HardwareChatService
from app.services.hardware_service import get_all_hardware_info


app = FastAPI(
    title="Linux Hardware Assistant",
    description="AI-powered Linux hardware Q&A assistant",
    version="1.0.0"
)

# One conversation instance for this application process.
assistant = HardwareChatService()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


class ChatRequest(BaseModel):
    message: str


@app.get("/api/health")
def health_check():
    return {
        "status": "running",
        "application": "Linux Hardware Assistant"
    }


@app.get("/api/hardware")
def hardware_info():
    try:
        return get_all_hardware_info()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to collect hardware information."
        )


@app.post("/api/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    try:
        answer = assistant.chat(request.message)

        return {
            "answer": answer
        }

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred."
        )


@app.post("/api/reset")
def reset_chat():
    assistant.reset_conversation()

    return {
        "message": "Conversation history cleared."
    }


# Serve the frontend.
app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend"
)
