import streamlit as st
#from services.api.db.auth import load_cookies
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
        #load_cookies()
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT
    )
def get_lecture_data(lecture_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Lấy đúng các cột cần thiết, đặt LectureID đúng chính tả
        cursor.execute(
            """
               SELECT
                    l.LectureID,      
                    l.Title,
                    l.Description,
                    l.Content,
                    l.CourseID, 
                    c.CourseName   
                FROM Lectures l
                LEFT JOIN Courses c ON c.CourseID = l.CourseID 
                WHERE l.LectureID = %s
            """,
            (lecture_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        # row = (LectureID, Title, Description, Content, CourseID)
        _, title, description, content, course_id, course_name = row
        return {
            'Title': title,
            'Description': description,
            'Content': content,
            'CourseID': course_id,
            'CourseName': course_name
        }
    except Exception as e:
        st.error(f"Error fetching lecture data: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def lecture_list(course_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT
            l.LectureID,
            l.CourseID, 
            c.CourseName,          
            l.Title,
            l.Description,
            l.Content
        from Lectures l
        LEFT JOIN Courses c ON c.CourseID = l.CourseID 
        WHERE l.CourseID = %s
        """, (course_id))
        data = cursor.fetchall()
        columns = ["LectureID", "CourseID", "Course Name", "Lecture Title", "Description", "Content"] 
        df = pd.DataFrame(data, columns = columns)
        return df
    except Exception as e:
        st.error(f"Error fetching lecture: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()
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

from services.api.chatbot.retrieval import sync_lectures_to_qdrant
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
        sync_lectures_to_qdrant()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding lecture: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


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
    
def get_quiz(lecture_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT q.QuizID, q.Title, q.Description
            FROM Quizzes q
            JOIN Lectures l ON q.LectureID = l.LectureID
            WHERE l.LectureID = %s
        """, (lecture_id,))
        quiz = cursor.fetchone()
        if quiz:
            quiz_id, title, description = quiz
            cursor.execute("""
                SELECT q.QuestionID, q.QuestionText, o.OptionText, o.IsCorrect
                FROM Questions q
                JOIN Options o ON q.QuestionID = o.QuestionID
                WHERE q.QuizID = %s
            """, (quiz_id,))
            questions = {}
            for question_id, question_text, option_text, is_correct in cursor.fetchall():
                if question_id not in questions:
                    questions[question_id] = {
                        "question": question_text,
                        "options": [],
                        "correct": []
                    }
                questions[question_id]["options"].append(option_text)
                if is_correct:
                    questions[question_id]["correct"].append(option_text)
            return {
                "title": title,
                "description": description,
                "questions": questions
            }
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching quiz: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def update_score(learner_id, course_id, lecture_id, score):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """CALL sp_update_lecture_result(%s, %s, %s, %s)""",
            (learner_id, course_id, lecture_id, score))
        conn.commit()
        st.success("Score updated successfully!")
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating score: {e}")
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

