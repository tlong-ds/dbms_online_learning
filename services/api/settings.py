import streamlit as st
from style.ui import Visual
import toml

# Settings for Appearance
def appearance():
    with st.form("appearance"):
        themes = ['Dark', 'Light']
        st.markdown("<h4>Select your appearance</h4>", unsafe_allow_html=True)
        st.selectbox("select theme", themes, label_visibility="collapsed", index = themes.index(Visual.THEME.title()), key="selected")
        st.form_submit_button("Apply", on_click=save_mode)

def save_mode():
    try:
        selected_mode = st.session_state.selected.lower()
        if selected_mode != Visual.THEME.title():
            Visual.THEME = selected_mode
            Visual.CONFIG["theme"]["base"] = selected_mode
            with open('.streamlit/config.toml', 'w') as f:
                toml.dump(Visual.CONFIG, f)
            st.rerun()
            st.success(f"Change mode successfully!")
    except Exception as e:
        st.error(f"Failed to change mode: {str(e)}")

# Setting for Appearance
def info():
    pass

# Setting for Security
def security():
    pass

# Setting for About
def about():
    pass