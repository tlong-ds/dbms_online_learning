import pymysql
import os
from dotenv import load_dotenv
import bcrypt
import streamlit as st

load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))

def connect_db():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT
    )

# --- password hashing ---

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8') 

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# --- user sign up ---
def register_user(account_name: str,
                  password: str,
                  role: str,
                  name: str,
                  email: str,
                  phone: str = None,
                  expertise: str = None) -> bool:

    cfg = {
        "Learner":    ("Learners",    "LearnerName",    "PhoneNumber", phone),
        "Instructor": ("Instructors", "InstructorName", "Expertise",    expertise),
    }
    table, name_col, extra_col, extra_val = cfg[role]

    cols = [name_col, "Email", "AccountName", "Password"]
    vals = [name, email, account_name, hash_password(password)]
    if extra_val:
        cols.append(extra_col)
        vals.append(extra_val)

    conn = connect_db()
    cursor = conn.cursor()
    try:
        # 1) email and account name check
        cursor.execute(
            f"SELECT 1 FROM `{table}` WHERE AccountName=%s OR Email=%s LIMIT 1",
            (account_name, email)
        )
        if cursor.fetchone():
            return False

        # 2) insert new user
        cols_str       = ", ".join(f"`{c}`" for c in cols)
        placeholders   = ", ".join(["%s"] * len(cols))
        insert_sql     = f"INSERT INTO `{table}` ({cols_str}) VALUES ({placeholders})"
        cursor.execute(insert_sql, vals)
        conn.commit()
        return True

    except pymysql.Error:
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def verify_user(username, password, role):
    conn = connect_db()
    cursor = conn.cursor()
    if role == "Learner":
        cursor.execute("SELECT Password FROM Learners WHERE AccountName = %s", (username,))
        data = cursor.fetchone()
        conn.close()
        if data and check_password(password, data[0]):
            return True
        return False
    elif role == "Instructor":
        cursor.execute("SELECT Password FROM Instructors WHERE AccountName = %s", (username,))
        data = cursor.fetchone()
        conn.close()
        if data and check_password(password, data[0]):
            return True
        return False
    
def get_user_info(username, role):
    conn = connect_db()
    cursor = conn.cursor()
    if role == "Learner":
        cursor.execute("SELECT LearnerID, LearnerName, Email, PhoneNumber FROM Learners WHERE AccountName = %s", (username,))
        data = cursor.fetchone()
        
        st.session_state.username = username
        st.session_state.role = role
        st.session_state.id = data[0]
        st.session_state.name = data[1]
        st.session_state.email = data[2]
        st.session_state.phone = data[3]
        conn.close()
    elif role == "Instructor":
        cursor.execute("SELECT InstructorID, InstructorName, Email, Expertise FROM Instructors WHERE AccountName = %s", (username,))
        data = cursor.fetchone()
        st.session_state.username = username
        st.session_state.role = role
        st.session_state.id = data[0]
        st.session_state.name = data[1]
        st.session_state.email = data[2]
        st.session_state.expertise = data[3]
        conn.close()

def update_user_info(username, role, name, email, extra):
    conn = connect_db()
    cursor = conn.cursor()
    if role == "Learner":
        cursor.execute("""
            UPDATE Learners SET LearnerName = %s, Email = %s, PhoneNumber = %s WHERE AccountName = %s
        """, (name, email, extra, username))
        st.session_state.name = name
        st.session_state.email = email
        st.session_state.phone = extra
    elif role == "Instructor":
        cursor.execute("""
            UPDATE Instructors SET InstructorName = %s, Email = %s, Expertise = %s WHERE AccountName = %s
        """, (name, email, extra, username))
        st.session_state.name = name
        st.session_state.email = email
        st.session_state.phone = extra
    conn.commit()
    conn.close()
    
def update_password(username, old_password, role, new_password, confirmed_new_password):
    if verify_user(username, old_password, role):
        if new_password == confirmed_new_password:
            conn = connect_db()
            cursor = conn.cursor()
            if role == "Learner":
                cursor.execute(
                    "UPDATE Learners SET Password = %s WHERE AccountName = %s",
                    (hash_password(new_password), username)
                )
            else:
                cursor.execute(
                    "UPDATE Instructors SET Password = %s WHERE AccountName = %s",
                    (hash_password(new_password), username)
                )
            conn.commit()
            conn.close()
            st.success("Password changed successfully")
        else:
            st.error("New password and confirm password do not match.")
    else:
        st.error("Current password is incorrect.")