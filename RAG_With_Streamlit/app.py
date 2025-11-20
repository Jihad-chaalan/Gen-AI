import streamlit as st


# page = st.navigation(
#     [
#         st.Page("pages/load.py", title="Add",icon="➕"),
#         st.Page("pages/Chatbot/chatbot.py", title="Add",icon="➕")
#     ],
#       position="top",
# )

# page.run()

# [file name]: app.py (updated)
# [file content begin]


page = st.navigation(
    [
        st.Page("pages/load.py", title="Add Documents", icon="➕"),
        st.Page("pages/db_management.py", title="Manage Database", icon="🗃️"),
        st.Page("pages/Chatbot/chatbot.py", title="Chatbot", icon="🤖")
    ],
    position="top",
)

page.run()
# [file content end]
