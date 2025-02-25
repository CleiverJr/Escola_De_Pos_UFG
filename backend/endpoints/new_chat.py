from fastapi import APIRouter, HTTPException
from datetime import datetime

# Importar o dicionário de sessões do chat
from utils.chat_utils import chat_sessions

router = APIRouter()

@router.get("/api/new_chat")
async def new_chat():
    """Inicia um novo chat somente se não houver um chat_id existente."""
    try:
        session_id = "abc123"  # Este identificador pode vir do frontend se quiser associar a diferentes usuários

        # Verifica se já existe um chat_id na sessão
        if session_id in chat_sessions:
            chat_id = chat_sessions[session_id]
        else:
            chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            chat_sessions[session_id] = chat_id

        return {"message": "Chat iniciado", "chat_id": chat_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
