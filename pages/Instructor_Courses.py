import streamlit as st
from style.ui import Visual
from services.api.db.auth import load_cookies
from services.api.courses import get_instructed_courses, instructed_courses_list

st.set_page_config(
    page_title="Courses",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_cookies()
Visual.initial()
df = get_instructed_courses()
def show_instructor_courses():
    st.title("Courses")
    cols = st.columns([16, 2])
    if cols[1].button("Add Course"):
        pass
    instructed_courses_list(df)

show_instructor_courses()