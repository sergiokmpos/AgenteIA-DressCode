
        
import openai
import pandas as pd
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import streamlit as st
import os

# --- Configuração e Carregamento ---
# Configurar a API da OpenAI
# ATENÇÃO: Expor a chave da API diretamente no código é uma falha de segurança grave.
# Considere usar variáveis de ambiente ou um arquivo de configuração seguro.
# Exemplo: openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_api_key = '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'
openai.api_key = openai_api_key

# Carregar o arquivo CSV
try:
    df = pd.read_csv('Content.csv')
except FileNotFoundError:
    st.error("Erro: Arquivo 'Content.csv' não encontrado.")
    st.stop()  # Para a execução do script se o arquivo não for encontrado

# --- Processamento de Embeddings e Busca ---
# Criar embeddings para o conteúdo do CSV
# Adiciona um try-except para lidar com possíveis erros na criação de embeddings
try:
    embeddings = OpenAIEmbeddings()
    textos = df['Pergunta'].tolist()
    vetor_store = FAISS.from_texts(textos, embeddings)
except Exception as e:
    st.error(f"Erro ao criar embeddings ou vetor store: {e}")
    st.stop()

# Buscar informações baseadas em similaridade
def buscar_informacao_similar(pergunta):
    try:
        # Aumentar o número de resultados retornados para melhorar a precisão
        resultados = vetor_store.similarity_search(pergunta, k=5)  # k=5 busca os 5 mais similares
        if resultados:
            # Iterar sobre os resultados para encontrar a melhor correspondência no DataFrame
            for resultado in resultados:
                similar_pergunta = resultado.page_content
                resposta = df[df['Pergunta'] == similar_pergunta].iloc[0]['Resposta']
                if resposta:
                    return resposta
        return None
    except Exception as e:
        st.error(f"Erro na busca de similaridade: {e}")
        return None

# --- Geração de Resposta com OpenAI ---
# Criar um template de prompt
def criar_prompt(pergunta, resposta_local):
    # Contexto aprimorado para guiar a IA
    contexto = """
    Você é um assistente inteligente e amigável que responde perguntas baseadas estritamente nas informações fornecidas de um arquivo CSV local. O arquivo contém pares de Pergunta e Resposta sobre um tópico específico.
    Sua tarefa é:
    1. Analisar a 'Resposta encontrada no CSV'.
    2. Reformular essa resposta de forma natural, clara e contextual para responder à 'Pergunta' do usuário.
    3. Se a 'Resposta encontrada no CSV' indicar que a informação não foi encontrada (ex: "Desculpe, não sei nada sobre este tema."), você deve responder educadamente que a informação não está disponível no seu conhecimento atual (baseado no CSV).
    4. Mantenha a resposta concisa e direta.
    """
    # Inclui a resposta local encontrada para que a IA a reformule
    prompt = f"{contexto}\n\nPergunta do Usuário: {pergunta}\nInformação encontrada no CSV: {resposta_local}\n\nCom base na 'Informação encontrada no CSV', reformule a resposta para o usuário:"
    return prompt

# Integrar com a API da OpenAI para respostas
def responder_com_openai(pergunta):
    resposta_local = buscar_informacao_similar(pergunta)
    # Define a resposta local a ser usada no prompt
    if resposta_local is None:
        info_para_prompt = "Desculpe, não encontrei informações sobre este tema no meu conhecimento."
    else:
        info_para_prompt = resposta_local
    prompt = criar_prompt(pergunta, info_para_prompt)
    try:
        resposta_openai = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente inteligente que responde perguntas baseadas em um arquivo CSV local."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7  # Controla a criatividade da resposta (0.0 a 1.0)
        )
        resposta_texto = resposta_openai['choices'][0]['message']['content'].strip()
        return resposta_texto
    except Exception as e:
        st.error(f"Erro ao chamar a API da OpenAI: {e}")
        return "Desculpe, ocorreu um erro ao tentar gerar a resposta."

# --- Feedback ---
# Função para salvar perguntas, respostas e feedback em um arquivo CSV
def salvar_feedback(pergunta, resposta, feedback):
    try:
        if not os.path.exists('feedback.csv'):
            feedback_df = pd.DataFrame(columns=['Pergunta', 'Resposta', 'Feedback'])
        else:
            feedback_df = pd.read_csv('feedback.csv')
        novo_feedback = pd.DataFrame({'Pergunta': [pergunta], 'Resposta': [resposta], 'Feedback': [feedback]})
        feedback_df = pd.concat([feedback_df, novo_feedback], ignore_index=True)
        feedback_df.to_csv('feedback.csv', index=False)
        st.success("Feedback salvo com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar feedback: {e}")

# --- Interface Streamlit ---
st.title("Assistente Inteligente")
st.write("O Assistente sobre o assunto que você treinou.")

# Inicializar o estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = True

# Mostrar o histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Lógica de Input e Resposta ---
if st.session_state.feedback_given:
    user_input = st.chat_input("Digite sua pergunta aqui...", key="user_input_active")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.spinner("Pensando..."):
            resposta = responder_com_openai(user_input)
            st.session_state.messages.append({"role": "assistant", "content": resposta})
            with st.chat_message("assistant"):
                st.markdown(resposta)
            st.session_state.feedback_given = False
            st.rerun()

# --- Lógica de Feedback ---
if not st.session_state.feedback_given and len(st.session_state.messages) > 0:
    st.write("Por favor, forneça seu feedback sobre a última resposta:")
    col1, col2 = st.columns(2)
    ultima_pergunta = st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else "N/A"
    ultima_resposta = st.session_state.messages[-1]["content"] if len(st.session_state.messages) >= 1 else "N/A"
    with col1:
        if st.button("👍 Bom", key="feedback_bom"):
            salvar_feedback(ultima_pergunta, ultima_resposta, "Bom")
            st.session_state.feedback_given = True
            st.rerun()
    with col2:
        if st.button("👎 Ruim", key="feedback_ruim"):
            salvar_feedback(ultima_pergunta, ultima_resposta, "Ruim")
            st.session_state.feedback_given = True
            st.rerun()
