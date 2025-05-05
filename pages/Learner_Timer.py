import streamlit as st
from style.ui import Visual
from services.api.timer import learn_countdown, break_countdown, timer_init

st.set_page_config(
    page_title="Focus Timer",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

Visual.initial()
st.session_state.setdefault("timer_state", None)
st.session_state.setdefault("timer_name", "Default Timer")
st.session_state.setdefault("sound", "None")
st.session_state.setdefault("preset", "None")
st.session_state.setdefault("min", 0)
st.session_state.setdefault("sec", 0)
st.session_state.setdefault("break_time", 0)
st.session_state.setdefault("session", 1)

def show_timer():
    st.title("Focus Timer")
    st.markdown("<div style='font-size: 17px;'>The best timer for ultra-focusing!</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.timer_state:
            timer_init()
            if st.button("OK"):
                st.session_state.timer_state = "Run"
                st.rerun()
        if st.session_state.timer_state == "Run":
            st.session_state.timer_state = "In Progress"
            learn_countdown()
            st.rerun()
        elif st.session_state.timer_state == "In Progress":
            st.markdown(
                "<h1 style='text-align: center; font-size: 70px;'>TIME UP!</h1>",
                unsafe_allow_html=True
            )
            st.write("Congrat on your effective learning session!")
            st.write("Click 'Finish' to stop.")
            st.write(f"Click 'Break' to have a {st.session_state.break_time}-min break.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Finish"):
                    st.session_state.timer_state = None
                    st.rerun()
            with c2:
                if st.button("Break"):
                    st.session_state.session += 1
                    st.session_state.timer_state = "Break"
                    st.rerun()
        elif st.session_state.timer_state == "Break":
            st.session_state.timer_state = "Break In Progress"
            break_countdown()
            st.rerun()
        elif st.session_state.timer_state == "Break In Progress":
            st.markdown(
                "<h1 style='text-align: center; font-size: 70px;'>TIME UP!</h1>",
                unsafe_allow_html=True
            )
            st.write("Your break is over!")
            st.write("Click 'Continue' to return.")
            if st.button("OK"):
                st.session_state.timer_state = "Run"
                st.rerun()

show_timer()

