import streamlit as st
from style.ui import Visual
import toml
import os
from dotenv import load_dotenv
import pymysql
from services.api.db.auth import update_password, update_user_info


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
            st.success(f"Change mode successfully!")
            st.rerun()
    except Exception as e:
        st.error(f"Failed to change mode: {str(e)}")

# Setting for Personal Information
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
        update_password(st.session_state.username,
                        cp, 
                        st.session_state.role, 
                        npw, 
                        cf)


