import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from style.CSSHandle import load_css

class SideBar:
    @classmethod
    def show(cls):
        load_css("style/style.css")
        with st.sidebar:
            # Logo for web


            # Learner Navigation
            if st.session_state.login == "Learner":
                if st.button("Dashboard"):
                    switch_page("Learner Dashboard")
                if st.button("Courses"):
                    switch_page("Learner Courses") 
                if st.button("Notebook"):
                    switch_page("Learner Notebook")
                if st.button("Timer"):
                    switch_page("Learner Timer")
            # Instructor
            if st.session_state.login == "Instructor":
                if st.button("Dashboard"):
                    switch_page("Instructor Dashboard")
                if st.button("Courses"):
                    switch_page("Instructor Courses") 
            
            if st.button("Settings"):
                switch_page("Settings")
            if st.button("Feedback"):
                switch_page("Feedback")
            
