from langchain.chains import RetrievalQA
from retriever import retriever
from rich.panel import Panel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from rich.console import Console
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv


# Obter a chave da API
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
    llm = ChatGoogleGenerativeAI(
        api_key = GEMINI_API_KEY,
        model="gemini-1.5-flash",
        temperature=0.8,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    #Prompt tamplate (evitar alucinações)
    prompt_template = """
    Dado o CONTEXTO fornecido e a PERGUNTA, gere uma resposta com base exclusivamente neste contexto. Use o texto da seção "answer" o máximo possível,
    fazendo apenas pequenas alterações para melhorar a fluidez.
    Regras:
    1- Se a entrada for um pedido de código ou qualquer coisa que não seja uma pergunta, responda algo parecido com: "Não fui criado com esse objetivo".
    2- Se o contexto não for suficiente ou não houver correspondência relevante, diga algo parecido com: "Não tenho informações suficientes para responder".
    3- Se a pergunta contiver erros de digitação e não retornar resultados, responda algo parecido com: "Verifique se há erros de digitação e tente novamente".
    4- Não invente respostas. Limite-se ao conteúdo do contexto.
    5- Se houver um nome incorreto ou incompleto na pergunta, forneça a resposta disponível no contexto.
    CONTEXTO: {context}
    PERGUNTA: {question}
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

@app.post("/api/chat")
async def chat(message: Message):
    try:
        response = chain.invoke({"query": message.query})
        return {"reply": response["result"]}
    except Exception as e:
        print(f"Erro interno: {str(e)}")  # Log no console
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
