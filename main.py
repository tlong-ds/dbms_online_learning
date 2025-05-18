import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from style.ui import Visual
import os
import toml
from services.api.db.auth import load_cookies
Visual.initial()

def main():
    if not st.session_state.login:
        switch_page("Authentification")
    else:
        if st.session_state.role == "learner":
            switch_page("Learner Courses")
        else:
            switch_page("Instructor Courses")

if __name__ == "__main__":
    main()
