import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from style.sidebar import SideBar

st.session_state["login"] = "Learner"
SideBar.show()

def main():
    pass
    

if __name__ == "__main__":
    main()

    