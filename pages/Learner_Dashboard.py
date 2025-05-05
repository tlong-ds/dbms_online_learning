import streamlit as st
from style.ui import Visual
from services.api.dashboard import show_dashboard_learner

st.set_page_config(
    page_title="Learner Statistics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

Visual.initial()

if st.session_state.role == "Learner":
    show_dashboard_learner()