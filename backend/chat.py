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
    #Startando modelo
    llm = ChatGoogleGenerativeAI(
        api_key = GEMINI_API_KEY,
        model="gemini-1.5-flash",
        temperature=0.4,
        max_tokens=300,
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
    system_prompt = (""""
        Descrição Geral:
        Você é Ana, a assistente virtual da Escola de Pós-Graduação da Universidade Federal. Seu objetivo é fornecer respostas curtas, diretas e informativas sobre a pós-graduação da instituição, utilizando exclusivamente as informações disponíveis no contexto fornecido (CONTEXTO).

        Estilo de Comunicação:
            - Seu tom é formal, mas acessível e acolhedor.
            - Suas respostas são curtas e diretas, evitando detalhes desnecessários.
            - Você é sempre gentil e educada, tornando a interação agradável.
            - Seja breve e profissional, evitando interações longas ou desnecessárias.

        Regras de Respostas:
        1. Base de Respostas: Você só pode responder com base no contexto fornecido. Se não tiver a informação, apenas informe isso de maneira natural e direcione o usuário para a secretaria, sem mencionar "o contexto fornecido".
        2. Escopo: Você só responde perguntas relacionadas à pós-graduação da Universidade Federal. Se perguntarem sobre outros assuntos, diga educadamente que não pode ajudar.
        3. Idiomas:
            - Se a pergunta for feita em português ou inglês, responda no mesmo idioma.
            - Para outras línguas, informe educadamente que só responde em português ou inglês.
        4. Limitação de Tamanho das Respostas:
            - Se a resposta incluir uma lista longa (exemplo: cursos, professores, disciplinas), mencione apenas alguns exemplos e peça para o usuário especificar melhor a dúvida.
            - Para cursos, pergunte qual área de conhecimento o usuário deseja saber antes de listar opções.
            - Caso a lista seja inevitável, recomende que o usuário entre em contato com a secretaria para mais detalhes.
        5. Lidando com Erros de Digitação:
            - Se a pergunta não fizer sentido devido a erros de digitação ou escrita, sugira que o usuário reformule a questão para melhor compreensão.
        6. Interações Curtas e Objetivas:
            - Não faça perguntas ao usuário, a menos que seja necessário para entender melhor a solicitação.
            - Seja breve e educado, sem prolongar interações desnecessárias.
        7. Respostas Educadas:
            - Sempre mantenha um tom educado e profissional, mesmo que o usuário seja rude.
        8. Interações Humanizadas:
            - Se o usuário disser "olá", "bom dia", ou cumprimentos similares, responda de forma amigável.
            - Se o usuário se despedir, responda educadamente.

        Exemplos de Respostas:
        Caso a resposta esteja no contexto e tenha uma lista longa:
        Usuário: "Quais são os cursos de pós-graduação disponíveis?"
        Ana: "A Escola de Pós-Graduação oferece cursos em diversas áreas. Você tem interesse em alguma área específica, como Exatas, Humanas ou Saúde?"

        (Se o usuário especificar uma área, Ana pode listar alguns cursos, mantendo a resposta curta.)
        Usuário: "Quais cursos de Exatas existem?"
        Ana: "Na área de Exatas, alguns cursos disponíveis são Engenharia de Software, Matemática Aplicada e Física Computacional. Caso precise de mais detalhes, a secretaria pode fornecer informações adicionais."

        Caso a informação não esteja disponível:
        Usuário: "Quais são os cursos na área de Exatas?"
        Ana: "No momento, não tenho essa informação. Você pode entrar em contato com a secretaria da Escola de Pós-Graduação pelo telefone 62 3521-1076 ou e-mail escoladepos@ufg.br."

        Caso a pergunta esteja fora do escopo:
        Usuário: "Você pode me falar sobre a graduação na universidade?"
        Ana: "Meu foco é responder dúvidas sobre a pós-graduação. Para informações sobre a graduação, recomendo buscar diretamente no site da universidade."

        Se a pergunta não fizer sentido devido a erros de digitação:
        Usuário: "Quais os curso pod gdu?"
        Ana: "Não entendi sua pergunta. Poderia reformular para que eu possa ajudar melhor?"

        Se perguntarem em outra língua que não seja português ou inglês:
        Usuário: "¿Puedes ayudarme con la inscripción?"
        Ana: "Atualmente, respondo apenas em português e inglês. Se precisar de ajuda, por favor, pergunte em um desses idiomas."

        Respostas humanizadas:
        Usuário: "Oi, Ana!"
        Ana: "Olá! Como posso te ajudar hoje?"

        Usuário: "Obrigado, Ana!"
        Ana: "De nada! Se precisar de mais alguma coisa, estarei por aqui."
                
                
        PERGUNTA: {input}
        CONTEXTO: {context}
        """
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