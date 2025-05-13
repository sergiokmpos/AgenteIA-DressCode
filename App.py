import streamlit as st
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain. chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv
from longchain_community.document_loaders import CSVLoader

load_dotenv()

loader = CSVLoader(file_path="Content.csv")
documents = loader.load()

embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(documents, embeddings)


def retrieve(query):
    similar_response = db.similarity_search(query, k=3)
    return [doc.page_content for doc in similar_response]

                   
