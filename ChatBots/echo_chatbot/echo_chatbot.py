#practicing to build chatbot without AI as a first step to adding API
#this chatbot just repeat the input of the user
import streamlit as st

st.set_page_config(page_title = "Echo Chatbot bulding" , layout="wide")
st.title("Basic Echo ChatBot 🤖")


if "messages" not in st.session_state:
    st.session_state.messages = []


def add_message():
    msg = st.session_state.input_msg
    if msg.strip() != "":
        #Adding user message
        st.session_state.messages.append({
            "role": "user",
            "content": msg
        })

        st.session_state.messages.append({
            "role": "AI",
            "content": f"Echo🔊: {msg}"
        })
    st.session_state.input_msg= ""


#Input for the user
st.text_input("Type a message:", key="input_msg", on_change=add_message)

#Display the chat

for m in st.session_state.messages:
    if m["role"] == "user":
        st.write(f"😎 **You**: {m['content']} ")
    else:
        st.write(f"🤖**AI**: {m['content']}")