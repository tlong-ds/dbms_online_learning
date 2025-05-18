import re
import streamlit as st
from style.ui import Visual
from services.api.db.auth import load_cookies
from services.api.courses import lecture_list, file_exists
from services.api.lecture_display import get_lecture_data

# --- SETUP ---
st.set_page_config(
    page_title="Lecture & Assignment",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_cookies()
Visual.initial()

# --- READ QUERY PARAMS ---
params = st.experimental_get_query_params()
if "course_id" in params:
    course_id = int(params.get("course_id")[0])
    init_lecture_id = None
elif "lecture_id" in params:
    init_lecture_id = int(params.get("lecture_id")[0])
    lec_detail = get_lecture_data(init_lecture_id)
    if lec_detail:
        course_id = lec_detail.get("CourseID", 0)
    else:
        st.error("Lecture không tồn tại.")
        st.stop()
else:
    course_id = 0
    init_lecture_id = None

# --- FETCH LECTURES FOR THIS COURSE ---
lectures_df = lecture_list(course_id)
n_lec = len(lectures_df)
if n_lec == 0:
    st.error("Không tìm thấy bài giảng cho khóa này.")
    st.stop()

# --- INITIALIZE SESSION STATE ---
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "lecture"
if "lec_idx" not in st.session_state:
    if init_lecture_id is not None:
        matches = lectures_df[lectures_df["LectureID"] == init_lecture_id].index
        st.session_state.lec_idx = int(matches[0]) if len(matches) else 0
    else:
        st.session_state.lec_idx = 0

# --- LAYOUT: NAV + CONTENT ---
col1, col2, col3 = st.columns([1.5, 0.5, 9])

with col1:
    st.title("Navigation")
    st.subheader("Lectures")
    for i, row in lectures_df.iterrows():
        if st.button(f"Lecture {i+1}", key=f"lec_{i}"):
            st.session_state.view_mode = "lecture"
            st.session_state.lec_idx = i
    st.markdown("---")
    st.subheader("Assignments")
    for i, row in lectures_df.iterrows():
        if st.button(f"Assignment {i+1}", key=f"ass_{i}"):
            st.session_state.view_mode = "assignment"
            st.session_state.lec_idx = i

with col3:
    if st.session_state.view_mode == "lecture":
        lec_row = lectures_df.iloc[st.session_state.lec_idx]
        lec_id = lec_row["LectureID"]
        lecture = get_lecture_data(lec_id)
        if lecture:
            st.markdown(f"# {lecture['Title']}")
            st.write(lecture['Description'])
            # Video
            video_path = f"videos/cid{course_id}/lid{lec_id}/vid_lecture.mp4"
            if file_exists("tlhmaterials", video_path):
                url = f"https://tlhmaterials.s3-ap-southeast-1.amazonaws.com/{video_path}"
                st.video(url)
            
            st.markdown("---")
            st.markdown(f"## Content")
            st.markdown(lecture["Content"], unsafe_allow_html=True)
        else:
            st.error("Unable to load lecture content.")
    else:
        st.header("Assignment")
        st.write("Chưa có nội dung assignment cho mục này.")