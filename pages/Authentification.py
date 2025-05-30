import streamlit as st
st.set_page_config(
    page_title="Login",
    page_icon="👤",
    layout="centered",
    initial_sidebar_state="collapsed",
)
from style.ui import Visual
import os
from services.api.db.auth import register_user, verify_user, get_user_info
from streamlit_extras.switch_page_button import switch_page
import re



Visual.initial()

def show_auth():
    top_cols = st.columns([12,4,12])
    with top_cols[1]:
        st.image(f"./style/{st.session_state.theme}_logo.webp", use_column_width=True)
    # --- Header ---
    st.markdown('<div class="auth-title">The Learning House</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">The Best Learning Platform for Learners and Instructors!</div>', unsafe_allow_html=True)

    # --- role & action ---
    st.write("Select your role.")
    role   = st.selectbox(label = "Who are you?", options = ["Learner", "Instructor"], index = 0, label_visibility="collapsed")
    action = st.radio(label = "action", options = ["Login", "Sign Up"], label_visibility="collapsed", horizontal=True)

    # --- center the form ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("auth_form", clear_on_submit=True):
            if action == "Login":
                username = st.text_input("Username", key="f_user", placeholder="Enter username")
                password = st.text_input("Password", type="password", key="f_pass", placeholder="Enter password")
                ok = st.form_submit_button("Login")
                if ok:
                    if verify_user(username, password, role):
                        st.success(f"Welcome back, {username}!")
                        st.session_state.login = True
                        get_user_info(username, role)
                        switch_page(f"Courses")
                        
                    else:
                        st.error("Wrong username or password.")

            else:  # Sign Up
                st.subheader("Create Account")

                full_name = st.text_input("Full Name", placeholder="Enter your full name")
                username  = st.text_input("Username", key="f_new_user", placeholder="Choose a username")
                email     = st.text_input("Email", key="f_email", placeholder="Enter your email")
                password  = st.text_input("Password", type="password", key="f_new_pass", placeholder="Choose a password")
                confirm   = st.text_input("Confirm Password", type="password", key="f_new_pass_confirm", placeholder="Confirm password")

                if role == "Learner":
                    phone = st.text_input("Phone Number", key="f_phone", placeholder="Enter your phone number")
                else:
                    expertise = st.text_input("Expertise", key="f_expertise", placeholder="Enter your expertise area")

                ok = st.form_submit_button("Sign Up")
                if ok:
                    required_fields = [full_name, username, email, password, confirm]
                    if role == "Learner":
                        required_fields.append(phone)
                    else:
                        required_fields.append(expertise)

                    if not all(required_fields):
                        st.warning("Please fill in all required fields.")
                    elif len(password) < 8:
                        st.warning("Password must be at least 8 characters long.")
                    elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                        st.warning("Please enter a valid email address (e.g., example@gmail.com).")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    elif role == "Learner" and len(phone) < 9:
                        st.error("Invalid phone number")
                    else:
                        success = register_user(
                            account_name=username,
                            password=password,
                            role=role,
                            name=full_name,
                            email=email,
                            phone=phone if role == "Learner" else "",
                            expertise=expertise if role == "Instructor" else ""
                        )
                        if success:
                            st.success("Account created! You can now log in.")
                        else:
                            st.warning("Registration failed: username/email may already exist.")



    st.markdown("---")
    st.markdown(
    """
    <div style="text-align:center; color:gray; font-size:0.8rem;">
    © 2025 The Learning House. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
    )

show_auth()
