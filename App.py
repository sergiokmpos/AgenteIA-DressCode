import streamlit as st
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()

# Carregar o arquivo CSV
df = pd.read_csv("Content.csv")

def retrieve(query):
    # Realizar busca simples nas perguntas
    similar_response = df[df['Pergunta'].str.contains(query, case=False, na=False)]
    return similar_response['Resposta'].tolist()

llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")

template = """
Você é um assistente especializado em requisitos de qualidade.
Você tem acesso a um banco de dados com perguntas e respostas sobre processos e requisitos de qualidade.
As perguntas podem variar, incluindo "pode ou não pode", "o que é", "como deve ser", "quando deve ser" e "por que", entre outras.
Use essas informações para fornecer respostas precisas e úteis.

Aqui está um exemplo de pergunta e resposta do banco de dados:
Pergunta: {message}
Resposta: {best_pratice}

Com base nas informações fornecidas, escreva a melhor resposta que eu deveria enviar para a pessoa que está com dúvida sobre o processo ou requisito de qualidade.
"""

prompt = PromptTemplate(
    input_variables=["message", "best_pratice"],
    template=template,
)

chain = LLMChain(llm=llm, prompt=prompt)

def generate_response(message):
    similar_response = retrieve(message)
    if similar_response:
        best_pratice = similar_response[0]
        response = chain.run(message=message, best_pratice=best_pratice)
        return response
    else:
        return "Desculpe, não encontrei uma resposta adequada no banco de dados."

def main():
    st.set_page_config(page_title="Assistente", page_icon=":guardsman:", layout="wide")
    st.title("Assistente")
    st.header("Faça sua pergunta sobre requisitos:")
    message = st.text_input("Digite sua pergunta:")

    if message:
        st.write("Buscando informações relevantes...")
        
        result = generate_response(message)

        st.info(result)

if __name__ == "__main__":
    main()
