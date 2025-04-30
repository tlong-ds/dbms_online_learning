import streamlit as st
#from streamlit_extras.switch_page_button import switch_page
#from style.sidebar import SideBar
from pages.Authentification import show_auth_ui
# st.session_state["login"] = "Learner"
# SideBar.show()

def main():
    if "login" not in st.session_state:
        st.session_state["login"] = None
    show_auth_ui()
    

if __name__ == "__main__":
    main()

    