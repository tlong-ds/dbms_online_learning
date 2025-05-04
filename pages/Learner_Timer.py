import streamlit as st
from style.ui import Visual
import time
import os

st.set_page_config(
    page_title="Timer",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

Visual.initial()
if "timer_state" not in st.session_state:
    st.session_state.timer_state = None
if "timer_name" not in st.session_state:
    st.session_state.timer_name = "Default Timer"
if "sound" not in st.session_state:
    st.session_state.sound = "None"
def countdown():
    load_music()
    st.markdown(f"<div style='text-align: center;'>{st.session_state.timer_name}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; font-style: italic;'>Now Playing: {st.session_state.sound} ♫</div>", unsafe_allow_html=True)
    total_time = st.session_state.min * 60 + st.session_state.sec
    countdown_placeholder = st.empty()
    while total_time >= 0:
        mins, secs = divmod(total_time, 60)
        countdown_placeholder.markdown(
            f"<h1 style='text-align: center; font-size: 129px;'>{mins:02d}:{secs:02d}</h1>",
            unsafe_allow_html=True
        )
        time.sleep(1)
        total_time -= 1

    return True
        

def load_music():
    FOLDER = "assets"
    if st.session_state.sound != "None":
        SOUND_PATH = st.session_state.sound.lower() + ".mp3"
        with open(os.path.join(FOLDER, SOUND_PATH), "rb") as sound_file:
            sound_bytes = sound_file.read()
            st.audio(sound_bytes, format="audio/mp3", autoplay=True)

def timer_init():
    m, s = st.columns(2)
    with m:
        st.markdown("<div style='text-align:center;'>min</div>", unsafe_allow_html=True)
        min_input = st.text_input(label="minutes", label_visibility="collapsed", max_chars=3, value = "000")
        if min_input:
            try:
                st.session_state.min = int(min_input)
                if st.session_state.min > 180:
                    raise ValueError("Minutes must be no more than 180!")
            except Exception as e:
                st.error(str(e))
    with s:
        st.markdown("<div style='text-align:center;'>sec</div>", unsafe_allow_html=True)
        sec_input = st.text_input(label="seconds", label_visibility="collapsed", max_chars=2, value = "00")
        if sec_input:
            try:
                st.session_state.sec = int(sec_input)
                if st.session_state.sec >= 60:
                    raise ValueError("Seconds must be less than 60!")
            except Exception as e:
                st.error(str(e))
    st.text_input(label="timer_name", value="Timer", label_visibility="collapsed", key = "timer_name")
    sound_options = ['None','Classic', 'Edm', 'Healing', 'Lofi', 'Piano']
    st.selectbox(label="Sound", options = sound_options, label_visibility="collapsed", key = "sound", index=sound_options.index(st.session_state.sound))
def show_timer():
    st.header("Timer")
    st.markdown("<div style='font-size: 17px;'>The best timer for ultra-focusing!</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.timer_state:
            timer_init()
            if st.button("OK") and isinstance(st.session_state.min, int) and isinstance(st.session_state.sec, int):
                st.session_state.timer_state = "Run"
                st.rerun()
        if st.session_state.timer_state == "Run":
            st.session_state.timer_state = "In Progress"
            countdown()
            st.rerun()
        elif st.session_state.timer_state == "In Progress":
            st.markdown(
                "<h1 style='text-align: center; font-size: 70px;'>TIME UP!</h1>",
                unsafe_allow_html=True
            )
            st.write("Congrat on your effective learning session!")
            st.write("Click 'Done' to return.")
            if st.button("Done"):
                st.session_state.min = 0
                st.session_state.sec = 0
                st.session_state.timer_name = "Default Timer"
                st.session_state.sound = "None"
                st.session_state.timer_state = None
                st.rerun()
show_timer()

