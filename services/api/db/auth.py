import pymysql
import os
from dotenv import load_dotenv
import bcrypt
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
import streamlit.components.v1 as components
import streamlit_js_eval as js_eval

import requests
cookies = EncryptedCookieManager(prefix="auth_", password=os.getenv("COOKIE_SECRET", "default_secret_key"))
if not cookies.ready():
    st.stop()

load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))

FASTAPI_URL = "http://0.0.0.0:8000"

def connect_db():
    try:
        return pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT
        )
    except pymysql.err.OperationalError as e:
        return None

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
    if conn is None:
        return False
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
    if conn is None:
        return False
    cursor = conn.cursor()
    if role == "Learner":
        cursor.execute("SELECT Password FROM Learners WHERE AccountName = %s", (username,))
        data = cursor.fetchone()
        conn.close()
        if data and check_password(password, data[0]):
            cookies["username"] = username
            cookies["role"] = role
            cookies.save()

    elif role == "Instructor":
        cursor.execute("SELECT Password FROM Instructors WHERE AccountName = %s", (username,))
        data = cursor.fetchone()
        conn.close()
        if data and check_password(password, data[0]):
            cookies["username"] = username
            cookies["role"] = role
            cookies.save()
    
    
    if "username" in st.session_state and "role" in st.session_state:
        components.html(f"""
            <script>
                fetch("http://localhost:8000/set_cookie?username={st.session_state.username}&role={st.session_state.role}", {{
                    method: "GET",
                    credentials: "include"
                }}).then(() => {{
                    window.location.reload();
                }});
            </script>
        """, height=0)
        return True
    else:
        st.error("Invalid login credentials/")
        return False
    
def load_cookies():
    if "username" not in st.session_state and cookies.get("username"):
        username = cookies.get("username")
        role = cookies.get("role")
        get_user_info(username, role)
        st.session_state.login = True
        st.rerun()

        
    
def get_user_info(username, role):
    conn = connect_db()
    if conn is None:
        return False
    cursor = conn.cursor()
    if role == "Learner":
        cursor.execute("SELECT LearnerID, LearnerName, Email, PhoneNumber FROM Learners WHERE AccountName = %s", (username,))
        data = cursor.fetchone()
        st.session_state.id = data[0]
        st.session_state.name = data[1]
        st.session_state.email = data[2]
        st.session_state.phone = data[3]
        st.session_state.username = username
        st.session_state.role = role
        conn.close()

    elif role == "Instructor":
        cursor.execute("SELECT InstructorID, InstructorName, Email, Expertise FROM Instructors WHERE AccountName = %s", (username,))
        data = cursor.fetchone()
        st.session_state.id = data[0]
        st.session_state.name = data[1]
        st.session_state.email = data[2]
        st.session_state.expertise = data[3]
        st.session_state.username = username
        st.session_state.role = role
        conn.close()

def update_user_info(username, role, name, email, extra):
    conn = connect_db()
    if conn is None:
        return False
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
            if conn is None:
                return False
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

def logout_user():
    cookies["username"] = ""
    cookies["role"] = ""
    cookies.save()
    st.session_state.clear()

def load_from_cookies():
    # Inject JS to extract cookie and place it in DOM
    components.html("""
        <script>
            function getCookie(name) {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }
            
            // Get the auth_token cookie
            const token = getCookie('auth_token');
            console.log('Auth token from cookie:', token);
            
            // Store it in a div for Streamlit to access
            const tokenEl = window.parent.document.getElementById("token-display");
            if (tokenEl) {
                tokenEl.innerText = token || "No token found in cookies";
            }
            
            // Also attempt the whoami request to see server response
            fetch("http://0.0.0.0:8000/whoami", {
                method: "GET",
                credentials: "include",
                headers: {
                    "Accept": "application/json"
                }
            })
            .then(res => {
                console.log('Response status:', res.status);
                if (!res.ok) {
                    throw new Error(`HTTP error! Status: ${res.status}`);
                }
                return res.json();
            });
        </script>
        <div id="debug-info"></div>
    """, height=0)
    # Try reading from the hidden div (may require rerun)
    token = st.empty()
    token_html = st.markdown("<div id='token-holder'></div>", unsafe_allow_html=True)
    token_val = st.query_params.get("token", None)
    print(token_val)

    if not token_val and "browser_token" not in st.session_state:
        st.warning("Waiting for browser to sync auth token...")
        return False

    token_val = st.session_state.get("browser_token", token_val)

    try:
        r = requests.get(f"{FASTAPI_URL}/whoami", cookies={"auth_token": token_val})
        if r.status_code == 200:
            data = r.json()
            if isinstance(data.get("user_info"), dict):
                info = data["user_info"]
                st.session_state.username = info["username"]
                st.session_state.role = info["role"]
                st.session_state.login = True
                get_user_info(info["username"], info["role"])
                return True
    except Exception as e:
        st.error(f"Failed to verify token: {e}")

    st.session_state.login = False
    return False
