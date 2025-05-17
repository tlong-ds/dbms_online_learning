import streamlit as st
from services.api.db.auth import load_cookies
from urllib.parse import urlencode
import toml
import os
from dotenv import load_dotenv
import pymysql
import pandas as pd
from datetime import datetime

load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))

def connect_db():
    if "id" not in st.session_state:
        load_cookies()
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT
    )

import pandas as pd
import streamlit as st
from services.api.courses import connect_db

def get_courses():
    conn   = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.CourseID,
                c.CourseName,
                i.InstructorID,
                i.InstructorName,
                avg(e.Rating)      AS avg_rating,
                COUNT(e.CourseID)  AS EnrolledCount
            FROM courses c
            LEFT JOIN instructors i ON c.InstructorID = i.InstructorID
            LEFT JOIN enrollments  e ON c.CourseID     = e.CourseID
            GROUP BY 
                c.CourseID,
                c.CourseName,
                i.InstructorID,
                i.InstructorName;
        """)
        rows = cursor.fetchall()
        columns = [
            "CourseID",
            "Course Name",
            "Instructor ID",
            "Instructor Name",
            "Average Rating",
            "EnrolledCount",
        ]
        df = pd.DataFrame(rows, columns=columns)
        return df.fillna({"Average Rating": 0.0})
    finally:
        cursor.close()
        conn.close()

def get_course_description(course_id: int) -> str:
    conn  = connect_db()
    cur   = conn.cursor()
    cur.execute(
        "SELECT Descriptions FROM Courses WHERE CourseID = %s",
        (course_id,)
    )
    desc = cur.fetchone()
    cur.close()
    conn.close()
    return desc[0] if desc and desc[0] else ""


def get_enrollment_date(course_id, learner_id=st.session_state.id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                EnrollmentDate
            FROM enrollments
            WHERE LearnerID=%s AND CourseID=%s;
        """, (learner_id, course_id))
        data = cursor.fetchone()
        return data[0] if data else None
    except Exception as e:
        st.error(str(e))

def enroll(course_id, learner_id=st.session_state.id, enroll_date=datetime.today()):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
    "CALL sp_EnrollLearner(%s, %s, %s)",
    (learner_id, course_id, enroll_date)
)
        conn.commit()
        st.success("Successfully enrolled")
        st.rerun()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error when enrolling: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()
        
def courses_card(df):
    cols = st.columns(4)
    for i in range(4):
        params = {
            "course_id": df.loc[i, "CourseID"],
            "course_name": df.loc[i, "Course Name"],
            "instructor_id": df.loc[i, "Instructor ID"],
            "instructor_name": df.loc[i, "Instructor Name"],
            "average_rating": df.loc[i, 'Average Rating'] if 'Average Rating' in df.columns and not pd.isna(df.loc[i, 'Average Rating']) else 0,
        }

        href = f"./Course_Preview?{urlencode(params)}"
        cols[i].markdown(f"""
        <div class="card-container">
            <a href={href} class="card">
                <img src="https://i.imgur.com/O3GVLty.jpeg" alt="Course Image">
                <div class="card-body">
                    <div class="card-university">{params["instructor_name"]}</div>
                    <div class="card-title">{params["course_name"]}</div>
                    <div class="card-footer" style="text-align: right;">{round(params["average_rating"],1)} ⭐️</div>
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
def courses_list(df):
    view = df.fillna({"Average Rating": 0.0})
    view["Course Link"] = view.apply(
        lambda row: f"./Course_Preview?"
                    f"course_id={row['CourseID']}&"
                    f"course_name={row['Course Name']}&"
                    f"instructor_id={row['Instructor ID']}&"
                    f"instructor_name={row['Instructor Name']}&"
                    f"average_rating={row['Average Rating']}", axis=1)

    view = view[["Course Link", "Instructor Name", "Average Rating"]]

    st.data_editor(
        view,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Course Link": st.column_config.LinkColumn(
                label="Course Name",
                help="Click to view course details",
                display_text=r"course_name=([^&]+)"
            )
        },
        disabled=["widgets"]
    )

def get_courses_overview():
    """
    Lấy danh sách khóa học + giảng viên + số người đăng kí + rating TB.
    Trả về DataFrame có cột 'Total Learners'.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                c.CourseID,
                c.CourseName,
                i.InstructorID,
                i.InstructorName,
                IFNULL(enr.TotalLearners, 0) AS total_learners,
                IFNULL(AVG(e.Rating), 0)    AS avg_rating
            FROM  Courses            AS c
            LEFT JOIN Instructors    AS i   ON i.InstructorID = c.InstructorID
            LEFT JOIN Enrollments    AS e   ON e.CourseID = c.CourseID

            /* Đếm người đăng kí */
            LEFT JOIN (
                SELECT  CourseID,
                        COUNT(*) AS TotalLearners
                FROM    Enrollments
                GROUP BY CourseID
            ) AS enr ON enr.CourseID = c.CourseID
        """)
        data = cursor.fetchall()
        cols = ["CourseID", "Course Name",
                "Instructor ID", "Instructor Name",
                "Total Learners", "Average Rating"]
        df = pd.DataFrame(data, columns=cols)
        return df.fillna({"Average Rating": 0.0, "Total Learners": 0})
    except Exception as e:
        st.error(f"Error fetching courses: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()

def get_total_learners(course_id: int) -> int:
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM Enrollments WHERE CourseID = %s",
        (course_id,)
    )
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

def get_lectures(course_id: int):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT LectureID, Title
        FROM Lectures
        WHERE CourseID = %s
        ORDER BY CreatedAt
    """, (course_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": r[0], "title": r[1]} for r in rows]