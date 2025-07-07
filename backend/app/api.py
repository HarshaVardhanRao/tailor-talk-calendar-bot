from fastapi import APIRouter

from .agent import process_message
from .schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    response = await process_message(request.message)
    return ChatResponse(response=response)
