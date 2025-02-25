from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from retriever import retriever
from rich.console import Console
from pydantic import BaseModel

from config import GEMINI_API_KEY

retriever = retriever()

# Definindo formato da requisição
class Message(BaseModel):
    query: str

def llm():
    #Console
    console = Console()

    #Startando modelo
    llm = ChatGoogleGenerativeAI(
        api_key = GEMINI_API_KEY,
        model="gemini-1.5-flash",
        temperature=0.4,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
   
    #Reformular a pergunta do usuário para que seja independente do histórico de bate-papo
    contextualize_q_system_prompt = (
    "Dado um histórico de bate-papo e a pergunta mais recente do usuário"
    "que pode fazer referência ao contexto no histórico de bate-papo,"
    "formule uma pergunta independente que possa ser entendida sem o histórico de bate-papo."
    "NÃO responda à pergunta, apenas reformule-a se necessário e devolva-a como está."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    #chain
    system_prompt = (
        "Você é um assistente virtual especializado na Escola de Pós-Graduação da UFG e na UFG."
        "Responda a cada PERGUNTA de forma clara, objetiva e educada, usando apenas as informações do CONTEXTO." 

    "Instruções"  
    "1.Seja direto: Dê respostas curtas e informativas, evitando detalhes desnecessários."  
    "2.Mantenha o foco: Se a pergunta não for sobre a Escola de Pós-Graduação da UFG ou a UFG, responda de forma educada e direcione o usuário para temas nos quais você pode ajudar."
    "3.Erros de digitação**: Se a pergunta não fizer sentido, sugira que o usuário reformule." 
    "4.Interações curtas: Seja breve e educado. Não faça perguntas ao usuário, a menos que seja necessário."
    "5.Respostas educadas: Sempre seja educado e profissional, mesmo se o usuário não for."
    "6. Não responda fora do contexto: Responda apenas com base nas informações fornecidas no contexto."
    "PERGUNTA: {input}"
    "CONTEXTO: `{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)   

    
    #histórico de mensagens
    store = {}

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]
    
    #chain com histórico de mensagens
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    
    return conversational_rag_chain 

chain = llm()