from langchain.chains import RetrievalQA
from retriever import retriever
from rich.panel import Panel
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from rich.console import Console
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
import json


# Obter a chave da API
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Iniciando a API
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens (use origens específicas em produção)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)

# Definindo formato da requisição
class Message(BaseModel):
    query: str

def llm():


    console = Console()

    #Startando modelo
    llm = ChatGroq(
        api_key = GROQ_API_KEY,
        model="llama3-8b-8192",
        temperature=0.4,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    #Prompt tamplate (evitar alucinações)
    prompt_template = """
    Você é um assistente virtual especializado na Escola de Pós-Graduação da UFG e na UFG. Responda a cada PERGUNTA de forma clara, objetiva e educada, usando apenas as informações do CONTEXTO.  

### Instruções:  
1. **Seja direto**: Dê respostas curtas e informativas, evitando detalhes desnecessários.  
2. **Mantenha o foco**: Se a pergunta não for sobre a Escola de Pós-Graduação da UFG ou a UFG, responda de forma educada e direcione o usuário para temas nos quais você pode ajudar.  
3. **Erros de digitação**: Se a pergunta não fizer sentido, sugira que o usuário reformule.  
4. **Interações curtas**:  
   - Se o usuário cumprimentar, cumprimente e pergunte como pode ajudar.  
   - Se fizer um elogio, agradeça de forma breve e simpática.  
   - Se se despedir, retribua de forma curta.  

### Exemplo de respostas curtas:  
- **Pergunta:** "O que é a UFG?"  
  **Resposta:** "A UFG é a Universidade Federal de Goiás, uma instituição pública de ensino superior que oferece cursos de graduação e pós-graduação."  
- **Pergunta:** "O que é a Escola de Pós-Graduação da UFG?"  
  **Resposta:** "É um setor da UFG que coordena cursos de especialização, MBAs e residências. Oferece diversas opções para aprimoramento profissional."  
- **Pergunta irrelevante:** "Quem descobriu o Brasil?"  
  **Resposta:** "Posso te ajudar com dúvidas sobre a Escola de Pós-Graduação da UFG. Alguma pergunta sobre isso?"  

Agora, aqui está a pergunta do usuário:  
PERGUNTA: `{question}`  
CONTEXTO: `{context}
    """

    # Obs: aqui, estamos deixando claro que o prompt vai mudar de acordo com o contexto e com a pergunta.
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}

    #integrando LLM com retriver
    chain = RetrievalQA.from_chain_type(llm=llm,
                                chain_type="stuff",
                                retriever=retriever(),
                                input_key="query",
                                return_source_documents=True,
                                chain_type_kwargs=chain_type_kwargs)
    return chain 

chain = llm()


# Criar pasta para armazenar os chats, se não existir
CHAT_DIR = "chats"
os.makedirs(CHAT_DIR, exist_ok=True)

def save_chat_to_json(chat_id, messages):
    """Salva o histórico do chat em um arquivo JSON."""
    filename = os.path.join(CHAT_DIR, f"chat_{chat_id}.json")
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)
        
@app.post("/api/chat")
async def chat(message: Message):
    try: 
        chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")  # Identificador único para o chat
        response = chain.invoke({"query": message.query})

        # Criar estrutura do histórico do chat
        chat_history = [
            {"sender": "user", "text": message.query, "time": datetime.now().strftime("%H:%M:%S")},
            {"sender": "bot", "text": response["result"], "time": datetime.now().strftime("%H:%M:%S")},
        ]

        # Salvar no arquivo JSON
        save_chat_to_json(chat_id, chat_history)

        return {"reply": response["result"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))