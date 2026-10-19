import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser 
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
import os


## page config

st.set_page_config(page_title="Langchain Chat bot", page_icon="😎")

##title 
st.title("Langchain Chatbot with Gemini")
st.markdown("XYZ")


with st.sidebar:
    st.header("Settings")

    ##API KEY
    api_key =st.text_input("Gemini API KEY", type="password", help="Get Free API key at google gemini")

    model_name = st.selectbox(
        "Model",
        ["Gemini Flash"],
    )
    if st.button("Clear Chat"):
        st.session_state = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []


## initialize llm
@st.cache_resource
def get_chain(api_key,model_name):
    if not api_key:
        return None

    ##initialize model 
    llm=ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model="gemini-flash-latest",   # not "Gemini Flash" — needs the real model id
                temperature=0.7,
                streaming=True
            )
    #create prompt 
    prompt=ChatPromptTemplate.from_messages([
        ("system","You are Ravi Kishan. Answer question like he does."),
        ("user", "{question}")
    ])

    ## create chain
    chain=prompt| llm| StrOutputParser()
    return chain

## get chain

chain=get_chain(api_key,model_name)

if not chain: 
    st.warning("Please Enter Your API KEY to start chatting")
    st.markdown("[Get your api key here](google.com)")
else:
    ##display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    ##chat input
    if question:= st.chat_input("Ask Me Anything"):
        ## add user message to session state
        st.session_state.messages.append({"role":"user", "content":question})
        with st.chat_message("user"):
            st.write(question)

        ## generate response
        with st.chat_message("assistant"):
            message_placeholder=st.empty()
            full_response=""

            try: 
                #stream response from gemini
                for chunk in chain.stream({"question": question}):
                    full_response+=chunk
                    message_placeholder.markdown(full_response + "| ")

                message_placeholder.markdown(full_response)
                #add to history
                st.session_state.messages.append({"role":"assistant","content":full_response})

            except Exception as e: 
                st.error(f"Error: {str(e)}")

            