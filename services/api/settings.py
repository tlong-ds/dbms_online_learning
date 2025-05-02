import streamlit as st
from style.ui import Visual
import toml
import os
from dotenv import load_dotenv
import pymysql
from .db.auth import verify_user, hash_password

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
# Settings for Appearance
def appearance():
    with st.form("appearance"):
        themes = ['Dark', 'Light']
        st.markdown("<h4>Select your appearance</h4>", unsafe_allow_html=True)
        st.selectbox("select theme", themes, label_visibility="collapsed", index = themes.index(Visual.THEME.title()), key="selected")
        st.form_submit_button("Apply", on_click=save_mode)

def save_mode():
    try:
        selected_mode = st.session_state.selected.lower()
        if selected_mode != Visual.THEME.title():
            Visual.THEME = selected_mode
            Visual.CONFIG["theme"]["base"] = selected_mode
            with open('.streamlit/config.toml', 'w') as f:
                toml.dump(Visual.CONFIG, f)
            st.rerun()
            st.success(f"Change mode successfully!")
    except Exception as e:
        st.error(f"Failed to change mode: {str(e)}")


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

# Setting for Appearance
def info():
    st.header("Account Settings")
    with st.form("info_form"):
        name = st.text_input(
            "Full name", 
            value=st.session_state.name, 
            key="info_name"
        )
        email = st.text_input(
            "Email address", 
            value=st.session_state.email, 
            key="info_email"
        )

        if st.session_state.role == "Learner":
            extra_label = "Phone number"
            extra_value = st.text_input(
                extra_label, 
                value=st.session_state.phone, 
                key="info_extra"
            )
        elif st.session_state.role == "Instructor":
            extra_label = "Expertise"
            extra_value = st.text_input(
                extra_label, 
                value=st.session_state.expertise, 
                key="info_extra"
            )
        submitted = st.form_submit_button("Save")

    if submitted:
        update_user_info(
            username=st.session_state.username,
            role=st.session_state.role,
            name=name,
            email=email,
            extra=extra_value
        )
        st.success("Profile updated successfully!")

    

# Setting for Security
def security():
    st.header("Change Password")

    with st.form("pwd_form"):
        cp = st.text_input("Current Password", type="password", key="current_password")
        npw = st.text_input("New Password",     type="password", key="new_password")
        cf = st.text_input("Confirm New Password", type="password", key="confirm_password")
        submitted = st.form_submit_button("Change Password")

    if submitted:
        if verify_user(st.session_state.username, cp, st.session_state.role):
            if npw == cf:
                conn = connect_db()
                cursor = conn.cursor()
                if st.session_state.role == "Learner":
                    cursor.execute(
                        "UPDATE Learners SET Password = %s WHERE AccountName = %s",
                        (hash_password(npw), st.session_state.username)
                    )
                else:
                    cursor.execute(
                        "UPDATE Instructors SET Password = %s WHERE AccountName = %s",
                        (hash_password(npw), st.session_state.username)
                    )
                conn.commit()
                conn.close()
                st.success("Password changed successfully")
            else:
                st.error("New password and confirm password do not match.")
        else:
            st.error("Current password is incorrect.")


# Setting for About
def about():
    pass




    

