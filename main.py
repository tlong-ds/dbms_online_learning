import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from style.ui import Visual
import os
import toml

st.session_state["login"] = True
st.session_state["name"] = "Ly Thanh Long"
st.session_state["role"] = "Learner"


Visual.initial()


def main():
    pass
    

if __name__ == "__main__":
    main()

    