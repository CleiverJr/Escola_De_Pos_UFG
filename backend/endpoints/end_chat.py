from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Importar o dicionário de sessões do chat
from utils.chat_utils import chat_sessions

router = APIRouter()

# Definindo formato da requisição
class Message(BaseModel):
    chat_id: str  # Agora o chat_id será enviado pelo frontend

@router.post("/api/end_chat")
async def end_chat(data: Message):
    try:
        chat_id = data.chat_id
        session_id = "abc123"  # Ajuste conforme necessário
        
        # Remove o chat_id da sessão ativa
        if session_id in chat_sessions and chat_sessions[session_id] == chat_id:
            del chat_sessions[session_id]
        
        return {"message": "Chat encerrado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
