import os
import streamlit as st
import json
from style.ui import Visual
from services.api.db.auth import load_cookies
from services.api.courses import (
  get_enrollment_date, 
  enroll, 
  connect_db,
  get_total_learners,
  get_lectures,
  get_course_description,
  learner_list, 
  lecture_list, 
  upload_lecture_media)
from streamlit_extras.switch_page_button import switch_page
from urllib.parse import urlencode

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Course Preview",
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_cookies()
Visual.initial()


if st.session_state.role == "Learner":
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

if st.session_state.role == "Instructor":
    course_info = st.query_params.to_dict()
    st.title(course_info["course_name"])
    st.write("Course Overview")
    if "view" not in st.session_state:
        st.session_state.view = "learner_list"
    st.markdown("""
    <style>
    /* Make selectbox look like button */
    div[data-baseweb="select"] {
        background-color: #f63366; /* Same as Streamlit button pink */
        color: white;
        border: 0.5px solid #f63366;
        border-radius: 0.5rem;
        padding: 0.25rem;
        box-shadow: none;
        transition: background-color 0.2s ease-in-out;
    }

    div[data-baseweb="select"]:hover {
        background-color: #e0315c; /* darker pink on hover */
    }

    div[data-baseweb="select"] * {
        color: white !important; /* text color */
    }

    /* Remove focus outline */
    div[data-baseweb="select"]:focus {
        outline: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Learners"):
            st.session_state.view = "learner_list"
        if st.button("Lectures"):
            st.session_state.view = "lecture_management"
        # if st.button("Assignment"):
        #     st.session_state.view = "assignment"                
        # if st.button("Chat"):
        #     st.session_state.view = "about"
    with col2:
        if "learner_list" not in st.session_state:
            st.session_state.learner_list = learner_list(course_info["course_id"])
        if "lecture_list" not in st.session_state:
            st.session_state.lecture_list = lecture_list(course_info["course_id"])
        if st.session_state.view == "learner_list":
            st.data_editor(st.session_state.learner_list, hide_index = True)
        elif st.session_state.view == "lecture_management":
            st.write("Select a lecture")
            options = [None] + list(st.session_state.lecture_list["Lecture Title"])
            cols = st.columns([10, 2])
            selected_lecture = cols[0].selectbox(label="lecture", options=options, label_visibility="collapsed")
            if selected_lecture:
                row = st.session_state.lecture_list[st.session_state.lecture_list["Lecture Title"] == selected_lecture].iloc[0]
                with st.form("hehe"):
                    st.write("Title")
                    new_title = st.text_input(label="title", value=row["Lecture Title"], label_visibility="collapsed")
                    
                    st.write("Content")
                    new_content = st.text_input(label="content", value=row["Content"], label_visibility="collapsed")
                    st.write("Media")
                    media = st.file_uploader(label="video", type=["mp4", "docx", "pdf", "pptx"], label_visibility="collapsed")
                    #st.write("Quiz")
                    #st.file_uploader(label="quiz", type=["docx", "pdf"], label_visibility="collapsed")
                    if st.form_submit_button("Submit"):
                        if media and ".mp4" in media.name:
                            upload_lecture_media(row["CourseID"], row["LectureID"], media)
                            

            if cols[1].button("Add"):
                pass
            
# --- QUERY PARAMS ---
params = st.query_params

def _first(val, default=""):
    if isinstance(val, list):
        return val[0] if val else default
    return val or default

course_id_raw   = _first(params.get("course_id"), "0")
course_name     = _first(params.get("course_name"))
instructor_name = _first(params.get("instructor_name"))
course_image    = _first(params.get("image_url"), "")

try:
    course_id = int(course_id_raw)
except ValueError:
    course_id = 0

# --- BULK DATA FETCH ---
conn = connect_db()
cur = conn.cursor()

# 1. Ratings
cur.execute(
    "SELECT COUNT(*), COALESCE(AVG(Rating),0) FROM CourseStatuses WHERE CourseID=%s",
    (course_id,)
)
review_count, avg_rating = cur.fetchone()

# 2. Course metadata
cur.execute(
    "SELECT Skills, Difficulty, JSON_UNQUOTE(JSON_EXTRACT(Skills, '$[0]')) "
    "FROM Courses WHERE CourseID=%s",
    (course_id,)
)
row = cur.fetchone() or (None, "", "")
skills_json, difficulty, primary_skill = row

# 3. Series and total hours
cur.execute(
    "SELECT COUNT(*), COALESCE(SUM(EstimatedDuration),0) "
    "FROM Courses WHERE JSON_UNQUOTE(JSON_EXTRACT(Skills, '$[0]')) = %s",
    (primary_skill,)
)
series_count, total_hours = cur.fetchone()

cur.close()
conn.close()

# Parse skills list
try:
    skills = json.loads(skills_json) if skills_json else []
except json.JSONDecodeError:
    skills = []

# Other computed fields
total_learners = get_total_learners(course_id)
duration_months = max(1, round(total_hours / 40))

# --- HEADER ---
cols = st.columns([1, 6, 1])
with cols[0]:
    logo_path = os.path.join("logo", "logo_course.webp")
    if os.path.isfile(logo_path):
        try:
            st.image(logo_path, width=120)
        except Exception:
            st.text("No image available")
    else:
        st.text("No image available")
with cols[1]:
    st.markdown(f"## {course_name}")
    st.markdown(f"**Instructor:** {instructor_name}")
    st.markdown(f"⭐ {avg_rating:.1f} **|** {total_learners} enrolled")
with cols[2]:
    if not get_enrollment_date(course_id):
        if st.button("Enroll Now"):
            enroll(course_id)
            st.experimental_rerun()
    else:
        if st.button("Go To Course"):
            redirect = "/Course_Content?" + urlencode({"course_id": course_id})
            st.experimental_set_query_params(redirect=redirect)
st.divider()

# --- SUMMARY BOX ---
sum_cols = st.columns([2, 1, 1, 1, 1])
with sum_cols[0]:
    st.markdown(f"**{series_count} course series**")
    st.markdown(f"Get in-depth knowledge of {primary_skill}")
with sum_cols[1]:
    st.markdown(f"**{avg_rating:.1f} ★**")
    st.markdown(f"({review_count} reviews)")
with sum_cols[2]:
    st.markdown(f"**{difficulty} level**")
    st.markdown("Recommended experience")
with sum_cols[3]:
    st.markdown(f"**{duration_months} months**")
    st.markdown("at 10 hours a week")
with sum_cols[4]:
    st.markdown("**Flexible schedule**")
    st.markdown("Learn at your own pace")
st.divider()

# --- DESCRIPTION ---
course_desc = get_course_description(course_id)
if course_desc:
    st.markdown("## Description")
    st.write(course_desc)
    st.divider()

# --- SKILLS YOU'LL GAIN ---
if skills:
    st.markdown("## Skills you'll gain")
    for skill in skills:
        st.markdown(
            f"<span style='display:inline-block; background-color:#eef4ff;"
            f" color:#174ea6; padding:4px 12px; border-radius:12px;"
            f" margin:2px 4px; font-size:0.9em;'>{skill}</span>",
            unsafe_allow_html=True,
        )
    st.divider()

# --- LECTURES ---
lectures = get_lectures(course_id)
st.markdown(f"## Lectures — {len(lectures)} lecture{'s' if len(lectures)>1 else ''}")
for lec in lectures:
    link = "/Lecture_Preview?" + urlencode({"lecture_id": lec['id']})
    st.markdown(f"- [{lec['title']}]({link})")

