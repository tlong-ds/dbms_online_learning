import streamlit as st
from style.ui import Visual
from services.api.dashboard import show_dashboard_learner
from services.api.db.auth import load_cookies
st.set_page_config(
    page_title="Learner Statistics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_cookies()
Visual.initial()

if st.session_state.role == "Learner":
    show_dashboard_learner()