import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import base64
import imghdr
import os
from dotenv import load_dotenv
from streamlit_pdf_viewer import pdf_viewer

# Carregar .env
load_dotenv()

# Configuração da página
st.set_page_config(page_title="Assistente de Dress Code", layout="wide")

# Banner com largura total do container
st.image("banner.jpg", use_container_width=False)

# Sidebar de navegação

st.sidebar.image("Logo.png", use_container_width=True)

st.sidebar.title("📌 Navegação")
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
        st.image(uploaded_file, caption="Imagem enviada", height=100)

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
      - Primeira versão funcional do Assistente de Dress Code  
      - Análise de texto e imagem com IA  
      - Visualização de documentos internos (PDF)
      - 📷 Análise de imagens com IA
      - ✏️ Interpretação de descrições escritas
      - 📄 Visualização de documentos internos
      - 🔐 Regras de dress code personalizadas (via arquivo `regras_dresscode.txt`)
    ""    
     
        - **v1.1 (planejado)**  
          - Melhor exibição de PDFs  
          - Página de créditos  
          - Otimizações de UX
    """)
