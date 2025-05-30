import streamlit as st
import time
import os

def learn_countdown():
    load_music()
    st.markdown(f"<div style='text-align: center;'>{st.session_state.timer_name} -- Session {st.session_state.session}</div>", unsafe_allow_html=True)
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

def break_countdown():  
    st.markdown(f"<div style='text-align: center;'>{st.session_state.timer_name}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; font-style: italic;'>Break Time!</div>", unsafe_allow_html=True)
    total_time = st.session_state.break_time * 60
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
    st.session_state.session = 1
    m, s = st.columns(2)
    with m:
        st.markdown("<div style='text-align:center;'>min</div>", unsafe_allow_html=True)
        min_input = st.text_input(label="minutes", label_visibility="collapsed", max_chars=3, value = str(st.session_state.min))
        if min_input:
            try:
                st.session_state.min = int(min_input)
                if st.session_state.min > 180:
                    raise ValueError("Minutes must be no more than 180!")
            except Exception as e:
                st.error(str(e))
    with s:
        st.markdown("<div style='text-align:center;'>sec</div>", unsafe_allow_html=True)
        sec_input = st.text_input(label="seconds", label_visibility="collapsed", max_chars=2, value = str(st.session_state.sec))
        if sec_input:
            try:
                st.session_state.sec = int(sec_input)
                if st.session_state.sec >= 60:
                    raise ValueError("Seconds must be less than 60!")
            except Exception as e:
                st.error(str(e))

    st.write("Break time (min)")
    break_input = st.text_input(label="break", max_chars = 3, value = str(st.session_state.break_time), label_visibility="collapsed")
    if break_input:
        try:
            st.session_state.break_time = int(break_input)
            #if st.session_state.break_time >= st.session_state.min and st.session_state.break_time > 0:
            #   raise ValueError("Break Time must be less than Minutes!")
        except Exception as e:
            st.error(str(e))

    st.write("Timer Name")
    timer_name = st.text_input(label="timer_name", value = st.session_state.timer_name, label_visibility="collapsed")
    if timer_name:
        st.session_state.timer_name = timer_name
    st.write("Focus Music")
    sound_options = ['None','Classic', 'Edm', 'Healing', 'Lofi', 'Piano']
    sound = st.selectbox(label="Sound", options = sound_options, label_visibility="collapsed", index=sound_options.index(st.session_state.sound))
    if sound:
        st.session_state.sound = sound
    st.write("Presets")
    presets = ['None', '25/5', '50/10', '75/15']
    selected_preset = st.selectbox(label="preset", label_visibility="collapsed", options=presets, index = presets.index(st.session_state.preset))
    if selected_preset != st.session_state.preset:
        if selected_preset == "25/5":
            st.session_state.min = 25
            st.session_state.sec = 0
            st.session_state.preset = selected_preset
            st.rerun()
        elif selected_preset == "50/10":
            st.session_state.min = 50
            st.session_state.sec = 0
            st.session_state.preset = selected_preset
            st.rerun()
        elif selected_preset == "75/15":
            st.session_state.min = 75
            st.session_state.sec = 0
            st.session_state.preset = selected_preset
            st.rerun()