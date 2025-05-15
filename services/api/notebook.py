import streamlit as st
from services.api.db.auth import load_cookies
# import markdown2
import pandas as pd
from datetime import datetime
import pymysql
from dotenv import load_dotenv
import os


load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))

st.session_state.setdefault("note_title", None)
st.session_state.setdefault("note_date_created", None)
st.session_state.setdefault("note_course_id", None)
st.session_state.setdefault("note_course", None)
st.session_state.setdefault("note_lecture_id", None)
st.session_state.setdefault("note_lecture", None)
st.session_state.setdefault("note_content", None)

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

def get_notebooks(learner_id=st.session_state.id):
    conn = connect_db()
    cursor = conn.cursor()
    if not st.session_state.id:
        raise ValueError("You must sign in to continue!")
    try:
        cursor.execute("""
            SELECT
                n.NotebookID,
                n.CreatedDate,
                n.NotebookName,
                c.CourseID,
                c.CourseName,
                l.LectureID,
                l.Title,
                n.Content
            FROM Notebooks n
            LEFT JOIN Courses c ON n.CourseID = c.CourseID
            LEFT JOIN Lectures l ON n.LectureID = l.LectureID
            WHERE n.LearnerID = %s;
        """, (learner_id))
        data = cursor.fetchall()
        columns = ["Notebook ID", "Date Created", "Notebook Title", "CourseID", "Course", "LectureID", "Lecture", "Content"] 
        return pd.DataFrame(data, columns = columns)
    except Exception as e:
        st.error(f"Error fetching notebooks: {str(e)}")
        return pd.DataFrame() 
    finally:
        cursor.close()
        conn.close()



def notebook_list(df):
    try:
        view = df[["Date Created", "Notebook Title", "Course", "Lecture"]]
        view["View"] = False  # Ensure consistent initial state
        # Set checkbox based on session
        if "selected_index" not in st.session_state:
            st.session_state.selected_index = None
        view["View"] = view.index == st.session_state.selected_index

        edited_view = st.data_editor(
            view,
            use_container_width=True,
            column_config={
                "View": st.column_config.CheckboxColumn(
                    "View", help="Select to open notebook", default=False
                )
            },
            disabled=["widgets"],
            hide_index=True
        )
        # Find checked row(s)
        selected_rows = edited_view[edited_view["View"]].index.tolist()
        if len(selected_rows) > 1:
            raise ValueError("You only see 1 notebook at one time.")
        elif len(selected_rows) == 1:
            idx = selected_rows[0]
            st.session_state.note_title = df.loc[idx, 'Notebook Title']
            st.session_state.note_date_created = df.loc[idx, 'Date Created']
            st.session_state.note_course_id = df.loc[idx, 'CourseID']
            st.session_state.note_course = df.loc[idx, 'Course']
            st.session_state.note_lecture_id = df.loc[idx, 'LectureID']
            st.session_state.note_lecture = df.loc[idx, 'Lecture']
            st.session_state.note_content = df.loc[idx, 'Content']
            st.session_state.note = "view"
            st.rerun()
    except Exception as e:
        st.error(str(e))

def create(notebook_name, learner_id=st.session_state.id, course_id = None, lecture_id = None):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Notebooks (LearnerID, NotebookName, CreatedDate, CourseID, LectureID) VALUES (%s, %s, %s, %s, %s)", (learner_id, notebook_name, datetime.now(), course_id, lecture_id))
        conn.commit()
        st.success("Successfully Create Notebook!")
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error inserting notebook: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def edit(notebook_name, content, learner_id, old_notebook_name = st.session_state.note_title):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Notebooks SET NotebookName=%s, Content=%s WHERE NotebookName = %s AND LearnerID = %s;", (notebook_name, content, old_notebook_name, learner_id))
        conn.commit()

        st.success("Edit notebook successfully!")
        st.session_state.note_title = notebook_name
        st.session_state.note_content = content
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error editing notebook: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

