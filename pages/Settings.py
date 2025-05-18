import streamlit as st
st.set_page_config(
    page_title="Setting",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from style.ui import Visual
from services.api.settings import info, security, appearance
from services.api.db.auth import load_cookies
import toml
import os


load_cookies()
Visual.initial()

if not st.session_state.view:
    st.session_state.view = "info"

def show_settings():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.title("Settings")
        if st.button("Personal Information"):
            st.session_state.view = "info"
        if st.button("Security"):
            st.session_state.view = "security"
        if st.button("Appearance"):
            st.session_state.view = "appearance"    
        
    with col2:
        if st.session_state.view == "info":
            info()
        if st.session_state.view == "security":
            security()
        if st.session_state.view == "appearance":
            appearance()

show_settings()