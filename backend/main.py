from config import app
import chat  # Para carregar as configurações e variáveis globais
from endpoints.new_chat import router as new_chat_router
from endpoints.end_chat import router as end_chat_router
from endpoints.chat import router as chat_router

# Registrando os routers dos endpoints
app.include_router(new_chat_router)
app.include_router(end_chat_router)
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
