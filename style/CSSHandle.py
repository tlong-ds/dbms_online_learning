import streamlit as st

def load_css(css: str):
    with open(css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)