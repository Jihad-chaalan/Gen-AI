import streamlit as st
import PyPDF2
import docx


page = st.navigation(
    [
        st.Page("pages/load.py", title="Add",icon="➕"),
        st.Page("pages/Chatbot/chatbot.py", title="Add",icon="➕")
    ],
      position="top",
)

page.run()

