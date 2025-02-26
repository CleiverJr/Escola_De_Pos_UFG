from config import app
import chat  # Para carregar as configurações e variáveis globais
from endpoints.new_chat import router as new_chat_router
from endpoints.end_chat import router as end_chat_router
from endpoints.chat import router as chat_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from fastapi import Request, HTTPException

# Configurando o Limiter antes dos routers
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Registrando os routers dos endpoints
app.include_router(new_chat_router)
app.include_router(end_chat_router)
app.include_router(chat_router)

@app.get("/api/secure-endpoint")
@limiter.limit("10/minute")  
async def secure_endpoint(request: Request):
    print("Acesso seguro")
    return {"message": "Acesso seguro"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
