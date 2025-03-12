import os
import json
from datetime import datetime
from pydantic import BaseModel

# Criar pasta para armazenar os chats, se não existir
CHAT_DIR = "chats"
os.makedirs(CHAT_DIR, exist_ok=True)

# Dicionário para armazenar sessões de chat
chat_sessions = {}

class Message(BaseModel):
    query: str
    chat_id: str  # Agora o chat_id será enviado pelo frontend

def save_chat_to_json(chat_id, messages):
    """Salva o histórico do chat em um arquivo JSON."""
    filename = os.path.join(CHAT_DIR, f"chat_{chat_id}.json")

    # Se o arquivo já existe, carrega o conteúdo anterior
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_messages = json.load(f)
    else:
        existing_messages = []

    # Adiciona as novas mensagens ao histórico
    existing_messages.extend(messages)

    # Salva o histórico atualizado
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_messages, f, indent=4, ensure_ascii=False)

def get_current_chat_id():
    """Obtém o chat_id atual ou cria um novo."""
    session_id = "abc123"  # Aqui pode ser um identificador real do usuário
    if session_id not in chat_sessions:
        chat_sessions[session_id] = datetime.now().strftime("%Y%m%d_%H%M%S")
    return chat_sessions[session_id]
    