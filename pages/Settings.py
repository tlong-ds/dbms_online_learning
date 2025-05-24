import streamlit as st
st.set_page_config(
    page_title="Setting",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
#from services.api.db.auth import load_cookies
#load_cookies()
from streamlit_extras.switch_page_button import switch_page
if "login" not in st.session_state:
    switch_page("Authentification")
from style.ui import Visual
from services.api.settings import info, security, appearance

Visual.initial()

if "setting_view" not in st.session_state:
    st.session_state.setting_view = "info"

def show_settings():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.title("Settings")
        if st.button("Personal Information"):
            st.session_state.setting_view = "info"
        if st.button("Security"):
            st.session_state.setting_view = "security"
        if st.button("Appearance"):
            st.session_state.setting_view = "appearance"    
        
    with col2:
        if st.session_state.setting_view == "info":
            info()
        if st.session_state.setting_view == "security":
            security()
        if st.session_state.setting_view == "appearance":
            appearance()

show_settings()