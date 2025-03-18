
import streamlit as st
import time
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder

chat_model = ChatGoogleGenerativeAI(api_key="AIzaSyC1B3zDW4G19olwgTz368YgS-ZARqzsEFE", model="gemini-2.0-flash-exp")
output_parser = StrOutputParser()

chat_template = ChatPromptTemplate(
    [
        SystemMessage("""you act as an data science instructor. so you should answer only data science related questions.
#   if anyone ask you other questions rather then data science then simply tell them to ask data science related question."""), 
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("""{Que}""")
    ]
)


with st.sidebar:
    st.title("Data Science Tutor App")
    with st.spinner("Loading..."):
        time.sleep(1)
    st.success("Done!")

st.title(":tophat: Data Science Tutor")

memory_buffer = {"history": []}

def load_history():
    try:
        with open("history.json", "r") as file:
            data = json.load(file)
            history = []
            for message in data["history"]:
                if message["type"] == "HumanMessage":
                    history.append(HumanMessage(content=message["content"]))
                elif message["type"] == "AIMessage":
                    history.append(AIMessage(content=message["content"]))
            return {"history": history}
    except (FileNotFoundError, json.JSONDecodeError):
        return {"history": []}

def save_history(history):
    with open("history.json", "w") as file:
        data = {"history": []}
        for message in history["history"]:
            if isinstance(message, HumanMessage):
                data["history"].append({"type": "HumanMessage", "content": message.content})
            elif isinstance(message, AIMessage):
                data["history"].append({"type": "AIMessage", "content": message.content})
        json.dump(data, file, indent=4)

memory_buffer = load_history()

def get_history_from_buffer(human_input):
    return memory_buffer["history"]

def my_fragment(source):
    qu = {"Que": source}
    response = chain.invoke(qu)
    
    memory_buffer["history"].append(HumanMessage(content=qu["Que"]))
    memory_buffer["history"].append(AIMessage(content=response))
    
    save_history(memory_buffer)

    return memory_buffer["history"]

runnable_get_history_from_buffer = RunnableLambda(get_history_from_buffer)

chain = RunnablePassthrough.assign(chat_history=runnable_get_history_from_buffer) | chat_template | chat_model | output_parser

conversation_container = st.container()


st.markdown(
    """
    <style>
        .stTextArea textarea {
            position: fixed;
            bottom: 80px;
            width: 50%;
            background-color: #f0f0f0;
        }
        .stButton button {
            position: fixed;
            bottom: 10px;
        }
        #history-container {
            max-height: 70vh;
            overflow-y: auto;
        }
    </style>
    """, unsafe_allow_html=True
)

input_container = st.container()
with input_container:
    source = st.text_area(label="Enter your data science question", placeholder="Enter Your Data Science Question...")

if st.button("Generate", type="primary"):
    if source:
        my_fragment(source)
        
        source = ""
        
        st.subheader("Your Chat")
        for message in memory_buffer["history"]:
            if isinstance(message, HumanMessage):
                st.write(f"**:speech_balloon:**: {message.content}")
            elif isinstance(message, AIMessage):
                st.write(f"**:point_right:**: {message.content}")

st.markdown(
    """
    <script>
        const chatHistory = document.querySelector('#history-container');
        chatHistory.scrollTop = chatHistory.scrollHeight;
    </script>
    """, unsafe_allow_html=True
)
