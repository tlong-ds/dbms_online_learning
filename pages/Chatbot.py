import streamlit as st
from style.ui import Visual
from services.api.db.auth import load_cookies
import toml
import os
from services.api.chatbot.core import get_chat_response

st.set_page_config(
    page_title="Chat bot",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_cookies()
Visual.initial()

st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 2em;
        font-weight: bold;
    }
    </style>
    <h1 class="title">Chatbot</h1>
    """,
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Nhập tin nhắn của bạn...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Gọi chatbot để lấy phản hồi
    response = get_chat_response(user_input)

    # Hiển thị phản hồi của chatbot
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)


