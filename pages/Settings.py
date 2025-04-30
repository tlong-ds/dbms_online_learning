import streamlit as st
from style.ui import Visual

st.set_page_config(
    page_title="Setting",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

Visual.initial()


def show_settings():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.header("Settings")
        if st.button("Personal Information"):
            pass
        if st.button("Security"):
            pass
        if st.button("Dark Mode"):
            pass
        if st.button("About Us"):
            pass


show_settings()