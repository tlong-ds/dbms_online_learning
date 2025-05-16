import streamlit as st
from style.ui import Visual
from services.api.db.auth import load_cookies
from services.api.courses import get_enrollment_date, enroll, connect_db, get_total_learners, get_lectures, get_course_description
from urllib.parse import urlencode

st.set_page_config(
    page_title="Course Preview",
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_cookies()
Visual.initial()

# --- LẤY THÔNG TIN KHÓA HỌC TỪ URL PARAMS ---
params = st.query_params

course_id       = int(params.get("course_id", "0"))
course_name     = params.get("course_name", "")
instructor_name = params.get("instructor_name", "")
average_rating  = float(params.get("average_rating", "0.0"))
total_learners = get_total_learners(course_id)
course_image    = params.get("image_url", "https://via.placeholder.com/150")
course_desc     = params.get("description", "")


# --- HEADER ---
cols = st.columns([1, 6, 3])
with cols[0]:
    st.image("D:/Minh/Tài liệu học tập (DSEB)/Kì 4/Database Management Systems/Final Project/dbms_online_learning/logo/logo_course.webp", width=120)
with cols[1]:
    st.markdown(f"### {course_name}")
    st.markdown(f"**Instructor:** {instructor_name}")
    st.markdown(f"⭐ {average_rating:.1f}   **|**  Number of enrollment: {total_learners}")
with cols[2]:
    # Kiểm tra xem user đã enroll chưa
    if not get_enrollment_date(course_id):
        # Chưa enroll → hiển thị nút Enroll Now
        if st.button("Enroll Now"):
            enroll(course_id)
            st.experimental_rerun()
    else:
        # Đã enroll → hiển thị nút Go To Course
        if st.button("Go To Course"):
            target = "/Course_Content?" + urlencode({"course_id": course_id})
            st.experimental_set_query_params(redirect=target)


st.divider()

# --- DESCRIPTION ---
# nếu bạn đã truyền description qua URL param hoặc fetch từ DB
course_id       = int(params.get("course_id", "0"))
course_desc     = get_course_description(course_id)

if course_desc:
    st.markdown("## Description")
    st.write(course_desc)
    st.divider()

# --- LẤY DANH SÁCH LECTURES TỪ DB ---
lectures = get_lectures(course_id)

# --- HIỂN THỊ LECTURES ---
st.markdown(f"## Lectures — {len(lectures)} lecture{'s' if len(lectures)>1 else ''}")
for lec in lectures:
    link = "/Lecture_Preview?" + urlencode({"lecture_id": lec["id"]})
    st.markdown(f"- [{lec['title']}]({link})")