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

#st.sidebar.title("🤖 - Paginas")
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


    # Entradas
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
                    ]))
                else:
                    st.warning("⚠️ Tipo de imagem não suportado.")
                    st.stop()

            messages.append(HumanMessage(content="Com base nas regras e/ou imagem, diga se a roupa pode, deve ou não deve ser usada, explicando o motivo."))

            with st.spinner("🔍 Analisando..."):
                try:
                    response = llm.invoke(messages)
                    st.success("✅ Análise concluída!")
                    st.subheader("Resposta do Assistente:")
                    st.write(response.content)
                except Exception as e:
                    st.error(f"❌ Erro ao consultar o modelo: {e}")

# Página: Visualizador de PDF
elif pagina == "📄 Dress Code":
    st.title("📄 Dress Code Fábrica")

    pdf_path = "Orientações Dress Code Fábrica YBL.pdf"

    if not os.path.exists(pdf_path):
        st.error("❌ O arquivo PDF 'Orientações Dress Code Fábrica YBL.pdf' não foi encontrado no projeto.")
    else:
        # Upload necessário para usar Google Viewer
        # Ou você deve hospedar o PDF em um link público (ex: Google Drive compartilhado ou Dropbox público)

        st.info("Baixe abaixo o Dress code completo original:")

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            label="📥 Baixar PDF do Dress Code",
            data=pdf_bytes,
            file_name="Dress_Code_Fabrica_YBL.pdf",
            mime="application/pdf"
        )

# Página: Créditos & Histórico de Versões
elif pagina == "ℹ️ Créditos & Versões":
    st.title("ℹ️ Créditos & Histórico de Versões")
    
    st.subheader("👨‍💻 Créditos")
    st.write("""
    **Desenvolvedor:** Sergio Paiva de Campos  
    **Contato:** sergio.campos@br.yazaki.com  
    """)

    st.subheader("📜 Histórico de Versões")

    
    st.write("""
      - **v1.0 (2025-06-06)**   
         - Interpretação de descrições escritas e imagens com IA
         - Download de documento base
        - Regras de dress code personalizadas
                     
      - **v2.0 (planejado)**  
        - Função upload de imagens por camera  
         - gerar log com input e output  
        - Otimizações de UX
        
      - **v3.0 (planejado)**  
         - Função de feed-back do usuário
         - Otimizações de UX
    """)

st.markdown(
    """
    <hr>
    <div style="text-align:center; font-size: 0.9em; color: #888;">
        All for one. One for All ·  
        <a href="mailto:sergio.campos@br.yazaki.com" style="text-decoration: none; color: #888;">Contato</a> ·  
        <a href="https://github.com/sergiokmpos" target="_blank" style="text-decoration: none; color: #888;">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)