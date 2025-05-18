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
        cursor.execute("SELECT * FROM Lectures WHERE LectureiD = %s", (lecture_id,))
        lecture_data = conn.fetchone()[0]
        return {'Title': lecture_data[1], 'Description': lecture_data[2], 'Content': lecture_data[3], 'CourseID': lecture_data[4]}
    except Exception as e:
        st.error(f"Error fetching lecture data: {e}")
        return None
    finally:
        cursor.close()
        conn.close()