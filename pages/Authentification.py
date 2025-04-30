import streamlit as st
import mysql.connector
import hashlib
import os
from dotenv import load_dotenv
from style.sidebar import SideBar


load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))

def connect_db():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT
    )

# --- password hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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

    except mysql.connector.Error:
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
        if data and data[0] == hash_password(password):
            return True
        return False
    elif role == "Instructor":
        cursor.execute("SELECT Password FROM Instructors WHERE AccountName = %s", (username,))
        data = cursor.fetchone()
        conn.close()
        if data and data[0] == hash_password(password):
            return True
        return False

def show_auth_ui():
    SideBar.show()
   # --- Custom CSS (Dark theme + Radio pill) ---
    st.markdown("""
    <style>
    /* Background chung */
    .block-container {
        background-color: #121212;
        color: #E0E0E0;
    }
    /* Tiêu đề */
    .auth-title {
        text-align: center;
        color: #BB86FC;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
    .auth-sub {
        text-align: center;
        color: #B0B0B0;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    /* Form */
    .stForm {
        background: #1F1B24;
        padding: 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.5);
    }
    /* Input text */
    .stTextInput>div>div>input {
        background: #2C2C2C;
        color: #E0E0E0;
    }
    /* Button */
    .stButton>button {
        background-color: #03DAC6 !important;
        color: #000 !important;
        font-size: 1rem;
        height: 2.5rem;
    }
    /* Divider */
    .stMarkdown hr {
        border-color: #333333;
    }

    /* === Custom Radio as Pill Toggle === */
    div[role="radiogroup"] {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        justify-content: center;
    }
    div[role="radio"] {
        padding: 0.5rem 1rem;
        border: 1px solid #444444;
        border-radius: 1rem;
        background-color: #2C2C2C;
        color: #E0E0E0;
        cursor: pointer;
        transition: background-color 0.2s, border-color 0.2s;
    }
    div[role="radio"][aria-checked="true"] {
        background-color: #BB86FC;
        border-color: #BB86FC;
        color: #121212;
    }
    div[role="radio"]:hover {
        background-color: #3A3A3A;
    }
    div[role="radio"]:focus {
        outline: none;
        box-shadow: 0 0 0 2px rgba(187,134,252,0.5);
    }
    div[role="radio"] input[type="radio"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)



    # --- Header ---
    st.markdown('<div class="auth-title">Online Learning</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Secure Login & Registration</div>', unsafe_allow_html=True)

    # --- role & action ---
    role   = st.selectbox("Who are you?", ["Learner", "Instructor"])
    action = st.radio("", ["Login", "Sign Up"], horizontal=True)

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
                        st.session_state.login = role
                    else:
                        st.error("Wrong username or password.")

            else:  # Sign Up
                st.subheader("Create Account")
                
                full_name = st.text_input("Full Name", placeholder="Enter your full name")
                username  = st.text_input("Username", key="f_new_user", placeholder="Choose a username")
                email     = st.text_input("Email", key="f_email", placeholder="Enter your email")
                password  = st.text_input("Password", type="password", key="f_new_pass", placeholder="Choose a password")
                confirm   = st.text_input("Confirm Password", type="password", key="f_new_pass_confirm", placeholder="Confirm password")
                # different info of roles
                if role == "Learner":
                    phone = st.text_input("Phone Number", key="f_phone", placeholder="Enter your phone number")
                else:  # Instructor
                    expertise = st.text_input("Expertise", key="f_expertise", placeholder="Enter your expertise area")
                ok = st.form_submit_button("Sign Up")
                if ok:
                    if not all([full_name, username, email, password, confirm, phone if role == "Learner" else expertise]):
                        st.warning("Please fill in all required fields.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
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
    st.caption("© Tuấn đẹp trai nhất thế giới")


