from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings  # Ajustado para Pydantic v2
from dotenv import load_dotenv
import os


# Obter a chave da API
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Iniciando a API
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://chat.escoladepos.inf.ufg.br", "https://escola-de-pos-ufg.onrender.com", "http://localhost:3000"],  # Permitir todas as origens (use origens específicas em produção)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)