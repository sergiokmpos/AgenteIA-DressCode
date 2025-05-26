import openai
import pandas as pd
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import streamlit as st
import os

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
    

# Função para salvar perguntas, respostas e feedback em um arquivo CSV
def salvar_feedback(pergunta, resposta, feedback):
    if not os.path.exists('feedback.csv'):
        feedback_df = pd.DataFrame(columns=['Pergunta', 'Resposta', 'Feedback'])
    else:
        feedback_df = pd.read_csv('feedback.csv')
    
    novo_feedback = pd.DataFrame({'Pergunta': [pergunta], 'Resposta': [resposta], 'Feedback': [feedback]})
    feedback_df = pd.concat([feedback_df, novo_feedback], ignore_index=True)
    feedback_df.to_csv('feedback.csv', index=False)

    

# Criar a interface gráfica com Streamlit
st.title("Assistente Inteligente")
st.write("Faça uma pergunta baseada no conteúdo do arquivo CSV.")

# Inicializar o estado da sessão para armazenar mensagens e feedback
if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = True

# Mostrar o histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de entrada para o usuário
if st.session_state.feedback_given:
    user_input = st.chat_input("Você:", key="user_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Adiciona um container para a resposta do modelo
        resposta = responder_com_openai(user_input)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
        
        with st.chat_message("assistant"):
            st.markdown(resposta)
        
        st.session_state.feedback_given = False

# Botões de feedback
if not st.session_state.feedback_given:
    st.write("Por favor, forneça seu feedback sobre a resposta:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Bom", key="feedback_bom"):
            salvar_feedback(st.session_state.messages[-2]["content"], st.session_state.messages[-1]["content"], "Bom")
            st.session_state.feedback_given = True
    with col2:
        if st.button("Ruim", key="feedback_ruim"):
            salvar_feedback(st.session_state.messages[-2]["content"], st.session_state.messages[-1]["content"], "Ruim")
            st.session_state.feedback_given = True
