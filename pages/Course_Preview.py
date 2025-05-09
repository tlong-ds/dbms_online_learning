import streamlit as st
from style.ui import Visual
from services.api.db.auth import load_cookies
from services.api.courses import get_enrollment_date, enroll

st.set_page_config(
    page_title="Preview",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_cookies()
Visual.initial()

course_info = st.query_params.to_dict()

# Course Title
st.title(course_info["course_name"])
# Course Instructor
st.markdown(f'<div style="font-size: large;">Instructor: <b>{course_info["instructor_name"]}</b></div>', unsafe_allow_html=True)
# Course Average Rating & No. of students
st.markdown(f'<div style=""> <b>{round(float(course_info.get("average_rating", 0)), 1)}</b> ⭐️ | <b>{10}</b> already enrolled </div>', unsafe_allow_html=True)
enroll_date = get_enrollment_date(course_info["course_id"])
if enroll_date:
    st.markdown(f'<div style="font-style: italic;"> Enrolled on {enroll_date}</div>', unsafe_allow_html=True)
cols = st.columns([3, 20])

if enroll_date:
    cols[0].button("Go To Course")
else:
    if cols[0].button("Enroll Now"):
        enroll(int(course_info["course_id"]))