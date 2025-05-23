import openai
import pandas as pd
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import streamlit as st

# Configurar a API da OpenAI
openai_api_key = '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'
openai.api_key = openai_api_key

# Carregar o arquivo CSV
df = pd.read_csv('Content.csv')

# Criar embeddings para o conteúdo do CSV
embeddings = OpenAIEmbeddings()
textos = df['Pergunta'].tolist()
vetor_store = FAISS.from_texts(textos, embeddings)

# Buscar informações baseadas em similaridade
def buscar_informacao_similar(pergunta):
    resultados = vetor_store.similarity_search(pergunta)
    if resultados:
        # Encontrar a resposta correspondente no DataFrame
        similar_pergunta = resultados[0].page_content
        resposta = df[df['Pergunta'] == similar_pergunta].iloc[0]['Resposta']
        return resposta
    return None

# Criar um template de prompt
def criar_prompt(pergunta, resposta_local):
    contexto = """
    Você é um assistente inteligente que responde perguntas baseadas em um arquivo CSV local. O arquivo contém informações detalhadas sobre coisas que um asistente gosta ou tem. 
    Sua tarefa é fornecer respostas precisas e úteis com base nas informações contidas no arquivo. 
    Se a resposta não estiver no arquivo, você deve informar que a informação não está disponível.
    """
    prompt = f"{contexto}\n\nPergunta: {pergunta}\nResposta encontrada no CSV: {resposta_local}\nReformule a resposta de forma natural e contextual:"
    return prompt

# Integrar com a API da OpenAI para respostas
def responder_com_openai(pergunta):
    resposta_local = buscar_informacao_similar(pergunta)
    if resposta_local:
        prompt = criar_prompt(pergunta, resposta_local)
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente inteligente que responde perguntas baseadas em um arquivo CSV local."},
                {"role": "user", "content": prompt}
            ]
        )
        resposta_texto = resposta['choices'][0]['message']['content'].strip()
        
        # Verificar se a pergunta contém uma negação
        if "não" in pergunta.lower() or "né" in pergunta.lower():
            resposta_texto = resposta_texto.replace("Sim", "Não")
        
        return resposta_texto
    else:
        prompt = criar_prompt(pergunta, "Desculpe, não encontrei uma resposta no arquivo CSV.")
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente inteligente que responde perguntas baseadas em um arquivo CSV local."},
                {"role": "user", "content": prompt}
            ]
        )
        return resposta['choices'][0]['message']['content'].strip()

# Criar a interface gráfica com Streamlit
st.title("Assistente Inteligente")
st.write("Faça uma pergunta baseada no conteúdo do arquivo CSV.")

pergunta = st.text_input("Pergunta:")
if st.button("Enviar"):
    resposta = responder_com_openai(pergunta)
    st.write("Resposta:", resposta)
