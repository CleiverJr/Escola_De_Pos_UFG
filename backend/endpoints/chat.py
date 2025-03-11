from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Importando dependências necessárias
from chat import chain
from utils.chat_utils import chat_sessions, save_chat_to_json
from langchain_google_genai import ChatGoogleGenerativeAI

router = APIRouter()

# Definindo formato da requisição
class Message(BaseModel):
    query: str
    chat_id: str  # Agora o chat_id será enviado pelo frontend

@router.post("/api/chat")
async def chat(message: Message):
    try:
        if message.chat_id not in chat_sessions.values():
            return {"reply": "Sessão expirada. Por favor, inicie um novo chat."}
        
        response = chain.invoke(
            {"input": message.query},
            config={"configurable": {"session_id": message.chat_id}}
        )

        answer_text = response.get("answer", "Desculpe, não consegui gerar uma resposta.")
        save_chat_to_json(message.chat_id, [{"sender": "user", "text": message.query}, {"sender": "bot", "text": answer_text}])
        return {"reply": answer_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))