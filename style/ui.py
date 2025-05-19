import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.switch_page_button import switch_page
import os
import toml
from services.api.db.auth import logout_user


class Visual:
    CONFIG = toml.load(".streamlit/config.toml")
    FOLDER = "style"
    THEME = CONFIG["theme"]["base"] 
    CSS = "style.css"
    
    @staticmethod
    def load_css(css: str):
        with open(css) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    @classmethod
    def custom_sidebar(cls, css = None):
        if not css:
            cls.initial()
        if "login" not in st.session_state:
            st.session_state.login = False
        components.html("""
        <script>
            const theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
            const input = window.parent.document.querySelector('input[data-baseweb="input"]');
            if (input) {
                input.value = theme;
                input.dispatchEvent(new Event("input", { bubbles: true }));
            }
        </script>
        """, height=0)
        st.session_state.theme = cls.THEME
        with st.sidebar:
            # Logo for web
            logo_path = os.path.join(cls.FOLDER, f"{st.session_state.theme}_logo.webp")
            if os.path.exists(logo_path):  # This loads by default using config.toml
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(logo_path, use_column_width="always", output_format="PNG")
                with col2:
                    st.markdown(f'<div style="font-size: 20px; font-weight: bold; line-height: 1;">The</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size: 20px; font-weight: bold; line-height: 1;">Learning House</div>', unsafe_allow_html=True)


            if st.session_state.login:
                # User Information
                st.markdown(f'<div style="font-size: 20px; font-weight: bold;">Welcome, {st.session_state.name}!</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 18px; ">Role: {st.session_state.role}</div>', unsafe_allow_html=True)
                st.divider()
                if st.button("Courses"):
                        switch_page("Courses") 
                if st.button("Dashboard"):
                    switch_page("Dashboard")
                # Learner Navigation
                if st.session_state.role == "Learner":
                    if st.button("Notebook"):
                        switch_page("Notebook")
                    if st.button("Focus Timer"):
                        switch_page("Timer")
                    if st.button("EduMate"):
                        switch_page("Chatbot")
                st.divider()
                if st.button("Settings"):
                    switch_page("Settings")
                if st.button("About Us"):
                    switch_page("About")
                st.divider()
                
                if st.button("Log out"):
                    logout_user()
                    switch_page("main")
            else:
                st.markdown('<div style="text-align: center;">Please login to continue!</div>', unsafe_allow_html=True)
    
    @classmethod
    def initial(cls):
        if cls.CSS:
            cls.load_css(os.path.join(cls.FOLDER, cls.CSS))
        cls.custom_sidebar(cls.CSS)

    