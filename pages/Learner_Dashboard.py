import streamlit as st
from style.ui import Visual
from services.api.dashboard import show_dashboard_learner

Visual.initial()

if st.session_state.role == "Learner":
    show_dashboard_learner()