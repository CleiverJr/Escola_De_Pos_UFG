#Importando bibliotecas
from langchain_google_genai import ChatGoogleGenerativeAI
from rich import print
from rich.panel import Panel
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Obter a chave da API
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def retriever():
        #importando o banco de dados
        loader = CSVLoader(file_path='concatenated_perguntas_respostas_combined.csv', source_column="PERGUNTAS", encoding="ISO-8859-1")
        # Armazenar os dados do loader na variável data
        data = loader.load()

        #Embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key = GEMINI_API_KEY)

        #Vector database
        vectordb = FAISS.from_documents(documents=data,
                                        embedding=embeddings)

        #Criando Retriever:
        retriever = vectordb.as_retriever(score_threshold = 0.7)

        return retriever