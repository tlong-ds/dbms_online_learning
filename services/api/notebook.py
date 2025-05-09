import streamlit as st
import markdown2
from services.api.db.auth import connect_db
from datetime import datetime
import mysql.connector

def create_notebook(notebook_name, learnerid):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Notebooks (LearnerID, NotebookName, CreatedDate) VALUES (%s, %s, %s)", (learnerid, notebook_name, datetime.now()))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error inserting notebook: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def edit_notebook(old_notebook_name, content, learnerid, notebook_name = None):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        if not notebook_name:
            notebook_name = old_notebook_name
        cursor.execute("UPDATE Notebooks SET NotebookName=%s, Content=%s WHERE NotebookName = %s AND LearnerID = %s;", (notebook_name, content, old_notebook_name, learnerid))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error editing notebook: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

