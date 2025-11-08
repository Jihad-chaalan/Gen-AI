import streamlit as st
from google import genai
import os
from dotenv import load_dotenv


 # Load the .env file 
load_dotenv("../../.env")

#get the Key
key = os.getenv("Gemini_API_KEY")



#this is code from google studio(where i get the key)
client = genai.Client(api_key = key)

# response = client.models.generate_content(
#     model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)

if "messages" not in st.session_state:
    st.session_state.messages = []

def generate_response():
    user_msg = st.session_state.user_msg    
    response = client.models.generate_content(
    model="gemini-2.5-flash", contents=user_msg
    )
    st.session_state.messages.append({
        "role":"user",
        "content": {user_msg}
    })
    if response:
        st.session_state.messages.append({
        "role":"AI",
        "content": {response.text}
        })
    else:
        st.session_state.messages.append({
        "role":"AI",
        "content": "There is an error, Please Try Again later"
        })
    st.session_state.user_msg = ""



#####ChatBot Page####
st.title("ChatBot using Gemini API🤖")
st.text_input("Please enter your message", key="user_msg", on_change=generate_response)

for m in  st.session_state.messages:
    if m['role'] == "user":
        st.write(f"🙎 ***You:*** '{m['content']}")
    else:
        st.write(f"🤖 ***AI:*** '{m['content']}")
