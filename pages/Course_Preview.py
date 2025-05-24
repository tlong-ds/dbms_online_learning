import streamlit as st
# --- PAGE SETUP ---
st.set_page_config(
    page_title="Course Preview",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
#from services.api.db.auth import load_cookies
#load_cookies()
from streamlit_extras.switch_page_button import switch_page
if "login" not in st.session_state:
    switch_page("Authentification")

import json
import os
from style.ui import Visual
from services.api.courses import (
  get_enrollment_date, 
  enroll, 
  connect_db,
  get_total_learners,
  get_course_description,
  learner_list
)
from services.api.lectures import (
    get_lectures,
    get_lecture_id,
    file_exists,
    lecture_list, 
    add_lecture,
    upload_video,
    create_quiz
)
from streamlit_extras.switch_page_button import switch_page
from urllib.parse import urlencode


Visual.initial()

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
    "SELECT COUNT(*), COALESCE(AVG(Rating),0) FROM Enrollments WHERE CourseID=%s",
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
    """
    SELECT 
      COUNT(*) AS series_count,
      COALESCE(SUM(EstimatedDuration), 0) AS total_hours
    FROM Courses
    WHERE JSON_UNQUOTE(JSON_EXTRACT(Skills, '$[0]')) = %s
    """,
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
duration_week = max(1, round(total_hours / 20))

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

st.divider()

# --- SUMMARY BOX ---
lectures = get_lectures(course_id)
lecture_count = len(lectures)

sum_cols = st.columns([2, 1, 1, 1, 1])
with sum_cols[0]:
    st.markdown(f"**{lecture_count} lecture{'s' if lecture_count>1 else ''} series**")
    st.markdown(f"Get in-depth knowledge of {primary_skill}")
with sum_cols[1]:
    st.markdown(f"**{avg_rating:.1f} ★**")
    st.markdown(f"({review_count} reviews)")
with sum_cols[2]:
    st.markdown(f"**{difficulty} level**")
    st.markdown("Recommended experience")
with sum_cols[3]:
    st.markdown(f"**{duration_week} weeks**")
    st.markdown("at 10 hours a week")
with sum_cols[4]:
    st.markdown("**Flexible schedule**")
    st.markdown("Learn at your own pace")
st.divider()


if st.session_state.role == "Learner":
    # --- ENROLLMENTS ---
    if not get_enrollment_date(course_id):
        if cols[2].button("Enroll Now"):
            enroll(course_id)
            st.rerun()
    else:
        temp_lecture = get_lectures(course_id=course_id)
        if cols[2].button("Go To Course"):
            st.session_state.lecture_id = temp_lecture[0]["id"]
            switch_page("Lecture_Preview")
   
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
    enrolled_date = get_enrollment_date(course_id=course_id)
    if enrolled_date:
        for lec in lectures:
            link = "/Lecture_Preview?" + urlencode({"lecture_id": lec['id']})
            st.markdown(f"[{lec['title']}]({link})")
            if lec.get("description"):
                st.markdown(f"  - {lec['description']}")
        st.divider()

    else:
        for lec in lectures:
            st.markdown(lec['title'])
            if lec.get("description"):
                st.markdown(f"  - {lec['description']}")
        st.divider()


    

@st.dialog("Create New Lecture")
def create_lecture_dialog(course_id=course_id):
    st.write("Title")
    title = st.text_input(label="title", label_visibility="collapsed")
    st.write("Description")
    description = st.text_input(label="description", label_visibility="collapsed")
    st.write("Video Material")
    video = st.file_uploader(label="video", type=["mp4"], label_visibility="collapsed")
    st.write("Content")
    content = st.text_area(label="content", label_visibility="collapsed")
    st.write("Quiz")
    st.write("Quiz Title")
    quiz_title = st.text_input(label="qtitle", label_visibility="collapsed")
    st.write("Quiz Description")
    quiz_description = st.text_input(label="qdescription", label_visibility="collapsed")
    st.write("Number of question")
    num_questions = st.select_slider(label="number", label_visibility="collapsed", options=range(1,11))
    questions = []
    
    valid = True
    error_msg = ""

    for i in range(num_questions):
        st.write(f"Question {i + 1}")
        question = st.text_input(label=f"question{i}", label_visibility="collapsed")
        if not question.strip():
            valid = False
            error_msg = f"Question {i + 1} is missing."

        answers = {}
        for j in range(4):
            st.write(f"Option {j + 1}")
            answer = st.text_input(label=f"q{i}a{j}", label_visibility="collapsed")
            if not answer.strip():
                valid = False
                error_msg = f"Option {j + 1} for question {i + 1} is missing."
            answers[f"Option {j + 1}"] = answer

        st.write(f"Correct Answer of question {i + 1}")
        correct_answer = st.selectbox(label=f"correct{i}", options=["Option 1", "Option 2", "Option 3", "Option 4"], label_visibility="collapsed")
        if not correct_answer:
            valid = False
            error_msg = f"Correct answer for question {i + 1} is not selected."
        else:
            answers["Correct"] = correct_answer
        questions.append({"question": question, "answers": answers})

    if st.button("Submit"):
        add_lecture(course_id, title, description, content)
        lecture_id = get_lecture_id(course_id, title)
        if video is not None:
            upload_video(course_id, lecture_id, video)
        print(questions)
        create_quiz(lecture_id, quiz_title, quiz_description, questions)



if st.session_state.role == "Instructor":
    st.write("Lecture Preview")
    # maybe switch to api
    if "learner_list" not in st.session_state:
        st.session_state.learner_list = learner_list(course_id)
    if "lecture_list" not in st.session_state:
        st.session_state.lecture_list = lecture_list(course_id)
    if "lec_view" not in st.session_state:
        st.session_state.lec_view = "learner_list"
    if "lec_idx" not in st.session_state:
        st.session_state.lec_idx = -1
    if "lecture_id" not in st.session_state:
        st.session_state.lecture_id = -1
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Learners"):
            st.session_state.lec_view = "learner_list"
        for i in range(len(st.session_state.lecture_list.index)):
            if st.button(f"Lecture {i + 1}"):
                st.session_state.lec_view = "lecture_view"
                st.session_state.lec_idx = i
                st.session_state.lecture_id = st.session_state.lecture_list.loc[i, "LectureID"]

        if st.button("Add Lecture"):
           create_lecture_dialog()
    with col2:
        if st.session_state.lec_view == "learner_list":
            st.data_editor(st.session_state.learner_list, hide_index = True)
        if st.session_state.lec_view == "lecture_view":
            row = st.session_state.lecture_list[st.session_state.lecture_list["LectureID"] == st.session_state.lecture_id].iloc[0]
            st.write(f"Title: {row["Lecture Title"]}")
            st.write(f"Description: {row["Description"]}")
            video_path = f"videos/cid{course_id}/lid{st.session_state.lecture_id}/vid_lecture.mp4"
            if file_exists("tlhmaterials", video_path):
                st.video(f"https://tlhmaterials.s3-ap-southeast-1.amazonaws.com/" + video_path)
            st.markdown(row["Content"], unsafe_allow_html=True)
