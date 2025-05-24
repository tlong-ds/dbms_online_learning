import streamlit as st
st.set_page_config(
    page_title="Learner Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
#from services.api.db.auth import load_cookies
#load_cookies()
from streamlit_extras.switch_page_button import switch_page
if "login" not in st.session_state:
    switch_page("Authentification")

from style.ui import Visual
from services.api.dashboard import show_dashboard_instructor, show_dashboard_learner



Visual.initial()

if st.session_state.role == "Learner":
    show_dashboard_learner()
if st.session_state.role == "Instructor":
    show_dashboard_instructor()