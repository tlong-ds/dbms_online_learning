import streamlit as st
from urllib.parse import urlencode
from style.ui import Visual
from services.api.courses import get_courses, courses_list, courses_card
from services.api.db.auth import load_cookies
import pandas as pd

st.set_page_config(
    page_title="Courses",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_cookies()
Visual.initial()

df = get_courses()
st.session_state.setdefault("course", "cards")
def show_courses_page():
    st.title("Courses")
    if st.session_state.course == "cards":
        courses_card(df)
        cols = st.columns([2, 16])
        if cols[0].button("Expand as List"):
            st.session_state.course = "list"
            st.rerun()
    if st.session_state.course == "list":
        courses_list(df)
        cols = st.columns([2, 16])
        if cols[0].button("Minimize"):
            st.session_state.course = "cards"
            st.rerun()

show_courses_page()