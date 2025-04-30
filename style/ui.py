import streamlit as st
from style.CSSHandle import load_css
from streamlit_extras.switch_page_button import switch_page
import os
import toml



class Visual:
    FOLDER = "style"
    THEME = toml.load(".streamlit/config.toml")["theme"]["base"] 
    LOGO = THEME + "_logo.webp" if THEME else None
    CSS = "style.css"
    
    @classmethod
    def custom_sidebar(cls):
        with st.sidebar:
            # Logo for web
            if cls.LOGO:
                st.image(os.path.join(cls.FOLDER, cls.LOGO))
            # Learner Navigation
            if st.session_state.login == True and st.session_state.role == "Learner":
                if st.button("Dashboard"):
                    switch_page("Learner Dashboard")
                if st.button("Courses"):
                    switch_page("Learner Courses") 
                if st.button("Notebook"):
                    switch_page("Learner Notebook")
                if st.button("Timer"):
                    switch_page("Learner Timer")
            # Instructor
            if st.session_state.login == True and st.session_state.role == "Instructor":
                if st.button("Dashboard"):
                    switch_page("Instructor Dashboard")
                if st.button("Courses"):
                    switch_page("Instructor Courses") 
            st.divider()
            if st.button("Settings"):
                switch_page("Settings")
            if st.button("Feedback"):
                switch_page("Feedback")
            st.divider()
            if st.session_state.login == True:
                if st.button("Log out"):
                    pass
    
    @classmethod
    def initial(cls):
        load_css(os.path.join(cls.FOLDER, cls.CSS))
        cls.custom_sidebar()

    