import streamlit as st
from style.ui import Visual
from services.api.db.auth import load_cookies
from services.api.courses import get_enrollment_date, enroll, learner_list, lecture_list, upload_lecture_media
from streamlit_extras.switch_page_button import switch_page
st.set_page_config(
    page_title="Preview",
    page_icon="✍️",
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
            