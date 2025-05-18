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
def get_lecture_data(lecture_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Lấy đúng các cột cần thiết, đặt LectureID đúng chính tả
        cursor.execute(
            "SELECT LectureID, Title, Description, Content, CourseID "
            "FROM Lectures WHERE LectureID = %s",
            (lecture_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        # row = (LectureID, Title, Description, Content, CourseID)
        _, title, description, content, course_id = row
        return {
            'Title': title,
            'Description': description,
            'Content': content,
            'CourseID': course_id
        }
    except Exception as e:
        st.error(f"Error fetching lecture data: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
