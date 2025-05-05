import streamlit as st
from style.ui import Visual
from services.api.settings import info, security, appearance, about
import toml
import os

st.set_page_config(
    page_title="Setting",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

Visual.initial()

if "view" not in st.session_state:
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
        if st.button("About Us"):
            st.session_state.view = "about"
        
    with col2:
        if st.session_state.view == "info":
            info()
        if st.session_state.view == "security":
            security()
        if st.session_state.view == "appearance":
            appearance()
        if st.session_state.view == "about":
            about() 

show_settings()