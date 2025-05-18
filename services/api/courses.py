import streamlit as st
from services.api.db.auth import load_cookies
import json
import os
from dotenv import load_dotenv
import pymysql
import pandas as pd
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))

AWS_ACCESS_KEY=os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
REGION=os.getenv("REGION_NAME")
s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
    )

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


# ═══════════════ FUNCTIONS FOR LEARNERS ════════════════

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


def courses_list(df, selected_col = ["Instructor Name", "Average Rating"]):
    view = df.fillna({"Average Rating": 0.0})
    view["Course Link"] = view.apply(
        lambda row: f"./Course_Preview?"
                    f"course_id={row['CourseID']}&"
                    f"course_name={row['Course Name']}&"
                    f"instructor_id={row['Instructor ID']}&"
                    f"instructor_name={row['Instructor Name']}&"
                    f"average_rating={row['Average Rating']}", axis=1)

    selected_col.insert(0, "Course Link")
    view = view[selected_col]

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

# ═══════════════ FUNCTIONS FOR INSTRUCTORS ════════════════
def get_instructed_courses(instructor_id=st.session_state.id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT 
            c.CourseID,
            c.CourseName, 
            enr.avg_rating,
            COALESCE(enr.TotalLearners, 0) AS TotalLearners
        FROM Courses c
        LEFT JOIN Instructors i ON c.InstructorID = i.InstructorID
        LEFT JOIN (
            SELECT  
                CourseID,
                COALESCE(AVG(Rating), 0) AS avg_rating,
                COUNT(*) AS TotalLearners
            FROM Enrollments
            GROUP BY CourseID
        ) AS enr ON enr.CourseID = c.CourseID
        WHERE c.InstructorID = %s
        GROUP BY CourseID;
        """, (instructor_id))
        data = cursor.fetchall()
        columns = ["CourseID", "Course Name", "Total Learners", "Average Rating"] 
        df = pd.DataFrame(data, columns = columns)
        return df.fillna({"Average Rating": 0.0})
    except Exception as e:
        st.error(f"Error fetching courses: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()

def instructed_courses_list(df):
    view = df.fillna({"Average Rating": 0.0})
    view["Course Link"] = view.apply(
        lambda row: f"./Course_Preview?"
                    f"course_id={row['CourseID']}&"
                    f"course_name={row['Course Name']}&",
        axis = 1
    )
    view = view[["Course Link", "Total Learners", "Average Rating"]]
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
        disabled=["widgets", "Course Link"]
    )

def learner_list(course_id, instructor_id = st.session_state.id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT 
            enr.LearnerID,
            l.LearnerName,
            enr.EnrollmentDate
        FROM Enrollments enr 
        LEFT JOIN Learners l ON enr.LearnerID = l.LearnerID
        LEFT JOIN Courses c ON enr.CourseID = c.CourseID
        WHERE enr.CourseID = %s AND c.InstructorID = %s
        """, (course_id, instructor_id))
        data = cursor.fetchall()
        columns = ["LearnerID", "Learner Name", "EnrollmentDate"] 
        df = pd.DataFrame(data, columns = columns)
        return df
    except Exception as e:
        st.error(f"Error fetching learners: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()


def add_course(course_name, description, skills, difficulty, duration, instructor_id = st.session_state.id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Courses (CourseName, Descriptions, Skills, Difficulty, EstimatedDuration, InstructorID) VALUES (%s,%s,%s,%s,%s,%s)",
            (course_name, description, json.dumps(skills), difficulty, duration, instructor_id)
        )
        conn.commit()
        st.success(f"Successfully adding course: {course_name}!")
        return True
    except Exception as e:
        st.error(f"Error adding course: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def lecture_list(course_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT
            LectureID,
            CourseID,            
            Title,
            Description,
            Content
        from Lectures 
        WHERE CourseID = %s
        """, (course_id))
        data = cursor.fetchall()
        columns = ["LectureID", "CourseID", "Lecture Title", "Description", "Content"] 
        df = pd.DataFrame(data, columns = columns)
        return df
    except Exception as e:
        st.error(f"Error fetching lecture: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()

def add_lecture(course_id, title, description, content):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Lectures (CourseID, Title, Description, Content) VALUES (%s, %s, %s, %s)",
            (course_id, title, description, content)
        )
        conn.commit()
        st.success(f"Lecture '{title}' added successfully!")
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding lecture: {e}")
        return False
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
        SELECT LectureID, Title, Description as description
        FROM Lectures
        WHERE CourseID = %s
        ORDER BY CreatedAt
    """, (course_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2]} for r in rows]

def get_lecture_id(course_id: int, lecture_title: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT LectureID
        FROM Lectures
        WHERE CourseID = %s AND Title = %s
    """, (course_id,lecture_title))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0]

def get_user_courses(user_id=st.session_state.id):
    """
    Trả về danh sách courses mà user hiện tại đã enroll,
    mỗi phần tử dạng {"id": int, "name": str}.
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.CourseID, c.Name
        FROM Courses c
        JOIN Enrollments e ON e.CourseID = c.CourseID
        WHERE e.UserID = %s
        ORDER BY c.Name
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]

def create_quiz(lecture_id, title, description, questions):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Quizzes (LectureID, Title, Description) VALUES (%s, %s, %s)",
            (lecture_id, title, description)
        )
        conn.commit()
        st.success(f"Quiz '{title}' created successfully!")
        cursor.execute(
            "SELECT LAST_INSERT_ID()"
        )
        quiz_id = cursor.fetchone()[0]
        for question in questions:
            cursor.execute(
                "INSERT INTO Questions (QuizID, QuestionText) VALUES (%s, %s)",
                (quiz_id, question['question'])
            )
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            question_id = cursor.fetchone()[0]
            answers = question['answers']
            for i in range(4):
                cursor.execute("""
                    INSERT INTO Options (QuestionID, OptionText, IsCorrect)
                    VALUES (%s, %s, %s)
                """, (question_id, answers[f"Option {i + 1}"], answers[f"Correct"] == f"Option {i + 1}"))
            conn.commit()
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error creating quiz: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def upload_video(course_id, lecture_id, media_file, bucket_name="tlhmaterials"):
    media_path = f"videos/cid{course_id}/lid{lecture_id}/vid_lecture.mp4"
    with st.spinner("Uploading to S3..."):
        upload_video_to_s3(media_file, bucket_name, media_path)
    url = get_video_stream_url(bucket_name, media_path)
    st.success("Upload successful!")
    st.write("Preview uploaded video!")
    st.video(url)

def upload_text(course_id, lecture_id, media_file, bucket_name="tlhmaterials"):
    media_path = f"videos/cid{course_id}/lid{lecture_id}/{media_file.name}"
    with st.spinner("Uploading to S3..."):
        upload_video_to_s3(media_file, bucket_name, media_path)
    url = get_video_stream_url(bucket_name, media_path)
    st.success("Upload successful!")

# ═══════════════ BOTO3 FUNCTIONALITIES ════════════════
def file_exists(bucket_name, s3_key):
    try:
        s3.head_object(Bucket=bucket_name, Key=s3_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == '404':
            return False
        else:
            raise
def get_video_stream_url(bucket_name, s3_key, region=REGION):
    return f"https://{bucket_name}.s3-{region}.amazonaws.com/{s3_key}"

def upload_video_to_s3(uploaded_file, bucket_name, s3_key):
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=uploaded_file.read(),
        ContentType="video/mp4",        # allows browser streaming
        ACL="public-read",              # public access if needed
        ContentDisposition="inline"     # forces browser to render instead of download
    )


