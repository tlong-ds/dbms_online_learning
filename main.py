import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from style.ui import Visual
Visual.initial()

def main():
    if not st.session_state.login:
        switch_page("Authentification")
    else:
        switch_page("Courses")

if __name__ == "__main__":
    main()
