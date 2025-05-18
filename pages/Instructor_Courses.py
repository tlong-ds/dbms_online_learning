import streamlit as st
from style.ui import Visual
from services.api.db.auth import load_cookies
from services.api.courses import get_instructed_courses, instructed_courses_list, add_course
import pandas as pd

# st.set_page_config(
#     page_title="Courses",
#     page_icon="✍️",
#     layout="wide",
#     initial_sidebar_state="collapsed",
# )

load_cookies()
Visual.initial()
df = get_instructed_courses()

st.session_state.setdefault("instruct_course_view", "list")

@st.dialog("Create New Course")
def course_create_page():
    st.write("Course Name")
    course_name = st.text_input(label="course", label_visibility="collapsed")
    st.write("Description")
    description = st.text_area(label="description", label_visibility="collapsed")
    skills_options = pd.read_csv("services/api/skills.csv")["skill"]
    st.write("Skills")
    selected_skills = st.multiselect(label="skills", options=list(skills_options), label_visibility="collapsed")
    st.write("Or add new skills")
    new_skills = st.text_input(label="new skills", label_visibility="collapsed")
    st.write("Difficulty")
    difficulty = st.selectbox(label="difficulty", label_visibility="collapsed", options=["Beginner", "Intermediate", "Advanced"])
    st.write("Estimate Duration (Hours)")
    duration = st.text_input(label="duration", label_visibility="collapsed")

    if st.button("Submit"):
        if new_skills:
            # Support multiple new skills separated by commas
            new_skills_list = [s.strip() for s in new_skills.split(",") if s.strip()]
            # Append new skills to selected
            selected_skills.extend(new_skills_list)
            # Append new unique skills to CSV
            existing_skills = set(skills_options.str.lower())
            new_unique_skills = [s for s in new_skills_list if s.lower() not in existing_skills]
            if new_unique_skills:
                pd.DataFrame({"skill": new_unique_skills}).to_csv("services/api/skills.csv", mode="a", index=False, header=False)
        add_course(course_name, description, selected_skills, difficulty, duration)
    
def show_instructor_courses():
    st.title("Courses")
    cols = st.columns([16, 2])
    if cols[1].button("Add Course"):
        course_create_page()
    if st.session_state.instruct_course_view == "list":
        instructed_courses_list(df)
    
    
    

show_instructor_courses()