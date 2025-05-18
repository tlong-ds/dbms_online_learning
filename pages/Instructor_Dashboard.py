import streamlit as st
st.set_page_config(
    page_title="Learner Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from style.ui import Visual
from services.api.dashboard import show_dashboard_instructor
from services.api.db.auth import load_cookies

load_cookies()
Visual.initial()

if st.session_state.role == "Instructor":
    show_dashboard_instructor()