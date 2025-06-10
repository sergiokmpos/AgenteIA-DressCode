# Assistente de Dress Code

## Prova de Conceito para uso de Agentes de IA

### POC – Agente IA Dresscode YAZAKI

---

## Conceito do Projeto

O projeto visa desenvolver um agente de IA que simplifique a escolha de vestimentas de acordo com o dress code, eliminando a necessidade de consultar manuais extensos. Utilizando tecnologias de Processamento de Linguagem Natural (NLP) e Machine Learning, o agente fornecerá recomendações personalizadas com base nas preferências do usuário e no dress code especificado, podendo ajustar-se continuamente com base no feedback recebido.

---

## Situação Problema

1. A necessidade de simplificar a escolha de vestimentas conforme dress code.
2. Eliminar a consulta a manuais extensos.

---

## Tecnologia Utilizada

Um Agente de IA é como um ajudante inteligente que vive dentro de computadores e celulares. Ele usa a engenharia de alguma IA (API) e uma base de conhecimento local e específica para ajudar com tarefas, como encontrar informações, responder dúvidas ou até contar histórias.

---

## Fluxo de Desenvolvimento

- Sprint
- Criar código de programação
- Organizar e estruturar o dress code
- Criar o banco de dados com dress code
- Integrar app e banco de dados
- Revisar e testar

---

## Como Funciona?

### Interface Web

- Input por texto ou imagem
- Retorno escrito, similar a resposta humana

---

## Vantagens e Desvantagens

### Vantagens

- Simplificação na escolha de vestimentas
- Recomendações personalizadas
- Ajuste contínuo baseado no feedback

### Desvantagens

- Dependência da qualidade das regras fornecidas
- Necessidade de manutenção contínua

---

## Capturas de Tela

### Página Inicial
!Página Inicial

### Assistente de Dress Code
![Assistnte de Dress Code

### Dress Code Fábrica
![Dress Code Fábrica](images/dresscode_fabrica
```python
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import base64
import imghdr
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Configuração da página
st.set_page_config(page_title="Assistente de Dress Code", layout="wide")

# Banner com largura total do container
st.image("banner.jpg", use_container_width=False)

# Sidebar de navegação
st.sidebar.image("Logo.png", use_container_width=True)
pagina = st.sidebar.radio(
    "Ir para:",
    [
        "🏠 Home",
        "🧥 Assistente de Dress Code",
        "📄 Dress Code",
        "ℹ️ Créditos & Versões"
    ]
)
st.sidebar.image("capa.png", use_container_width=False)

# Obter chave da API
openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("openai_key", None)
if not openai_key:
    st.error("❌ Chave da API OpenAI não foi encontrada. Configure via .env ou st.secrets.")
    st.stop()

# Carregar regras do dress code
with open("regras_dresscode.txt", "r", encoding="utf-8") as f:
    regras = f.read()

# Criar LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.2, openai_api_key=openai_key)

# Página: HOME
if pagina == "🏠 Home":
    st.title("Bem-vindo ao Assistente de Dress Code 👗")
    st.write("""
    Este aplicativo ajuda você a verificar se uma roupa está adequada conforme regras específicas de vestimenta (dress code).
    
    ---
    
    ### Como usar:
    - Vá até a aba **Assistente de Dress Code**
    - Envie uma imagem ou escreva sua dúvida
    - A IA irá analisar com base nas regras fornecidas
    """)

# Página: Assistente de Dress Code
elif pagina == "🧥 Assistente de Dress Code":
    st.title("👔 Assistente de Dress Code")
    st.write("Descreva sua dúvida ou envie uma imagem para análise:")
    user_text_input = st.text_area("Sua pergunta ou descrição da roupa:")
    uploaded_file = st.file_uploader("Envie uma imagem (JPEG ou PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Imagem enviada", width=100)
    if st.button("Consultar"):
        if not user_text_input and not uploaded_file:
            st.error("⚠️ Informe uma descrição ou envie uma imagem.")
        else:
            messages = [
                SystemMessage(
                    content=f"Você é um assistente especializado em dress code. Use as regras a seguir para responder:\n{regras}"
                )
            ]
            if user_text_input:
                messages.append(HumanMessage(content=f"Pergunta: {user_text_input}"))
            if uploaded_file:
                bytes_data = uploaded_file.getvalue()
                img_type = imghdr.what(None, h=bytes_data)
                if img_type in ["jpeg", "png"]:
                    base64_image = base64.b64encode(bytes_data).decode("utf-8")
                    messages.append(HumanMessage(content=[
                        {"type": "image_url", "image_url": {"url": f"data:image/{img_type};base64,{base64_image}"}}
                   
