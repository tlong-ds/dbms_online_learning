import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_js_eval import get_cookie
from style.ui import Visual
from services.api.db.auth import load_from_cookies
Visual.initial()


def main():
    print(load_from_cookies())
      
    if not st.session_state.login:
        switch_page("Authentification")
    else:
        switch_page("Courses")

if __name__ == "__main__":
    main()
