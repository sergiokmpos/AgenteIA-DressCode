import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import base64 # Para codificar a imagem em base64
import io # Para manipular a imagem como bytes

# Certifique-se de ter suas chaves de API configuradas como variáveis de ambiente ou passe diretamente
# from dotenv import load_dotenv
# load_dotenv()

# Carregue as regras de dress code de um arquivo local (por exemplo, "regras_dresscode.txt")
try:
    with open("regras_dresscode.txt", "r", encoding="utf-8") as file:
        regras = file.read()
except FileNotFoundError:
    st.error("O arquivo 'regras_dresscode.txt' não foi encontrado. Por favor, crie-o na mesma pasta do script.")
    st.stop() # Interrompe a execução se o arquivo não for encontrado

# Configure o modelo multimodal da OpenAI (GPT-4o ou gpt-4-vision-preview)
# É importante ter a chave de API da OpenAI configurada.
# Você pode definir como variável de ambiente (OPENAI_API_KEY) ou passar diretamente:
llm = ChatOpenAI(model="gpt-4o", temperature=0.2, openai_api_key='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') # Substitua 'SUA_CHAVE_API_OPENAI' pela sua chave real

# Interface com Streamlit
st.title("Assistente de Dress Code")
st.write("Digite sua dúvida e/ou faça upload de uma imagem para análise do dress code:")

user_text_input = st.text_area("Sua pergunta ou descrição da roupa:")
uploaded_file = st.file_uploader("Faça upload de uma imagem (opcional)", type=["jpg", "jpeg", "png"])

# Linha de código para exibir a imagem em tamanho pequeno-médio
if uploaded_file:
    st.image(uploaded_file, caption="Imagem Carregada para Análise", width=150) # Define a largura 

if st.button("Consultar"):
    if not user_text_input and not uploaded_file:
        st.error("Por favor, insira uma pergunta ou faça upload de uma imagem.")
    else:
        messages_content = []

        # Adiciona as regras de dress code como parte da mensagem inicial do sistema
        messages_content.append({"type": "text", "text": f"Você atua como um assistente especializado em regras de dress code. Utilize as seguintes regras para responder à pergunta:\n{regras}"})

        # Adiciona a pergunta do usuário
        if user_text_input:
            messages_content.append({"type": "text", "text": f"Pergunta: {user_text_input}"})

        # Adiciona a imagem, se houver
        if uploaded_file:
            # Lendo a imagem como bytes e codificando para base64
            bytes_data = uploaded_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            messages_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})

        # Adiciona a instrução final para o modelo
        messages_content.append({"type": "text", "text": "Com base nas regras e/ou na imagem, responda se a roupa pode ser usada, deve ser usada ou não deve ser usada, detalhando os motivos."})

        with st.spinner("Analisando..."):
            try:
                # Cria a mensagem HumanMessage com o conteúdo combinado (texto e/ou imagem)
                response = llm.invoke(
                    [
                        HumanMessage(
                            content=messages_content
                        )
                    ]
                )
                st.subheader("Resposta do Assistente:")
                st.write(response.content)
            except Exception as e:
                st.error(f"Ocorreu um erro ao consultar o modelo: {e}. Verifique sua chave de API e se o modelo 'gpt-4o' está disponível para sua conta.")