import streamlit as st
from style.ui import Visual
from services.api.notebook import get_notebooks, notebook_list, create, edit
st.set_page_config(
    page_title="Notebooks",
    page_icon="📔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

Visual.initial()

st.session_state.setdefault("note", "list")

def create_form():
    with st.form("new notebook"):
        st.write("Notebook Name")
        name = st.text_input(label="name", label_visibility="collapsed")
        
        if st.form_submit_button("OK"):
            create(notebook_name=name)
            st.session_state.note = "list"
            st.rerun()

def view_note():
    st.markdown(f"<div style='font-size: small; font-style: italic;'>Created: {st.session_state.note_date_created}, Course: {st.session_state.note_course}, Lecture: {st.session_state.note_lecture}</div>", unsafe_allow_html=True)
    st.header(st.session_state.note_title)
    st.markdown(st.session_state.note_content)
    
    
def show_notebook_page():
    st.title("Notebooks")
    st.markdown("One place for all knowledge! [See the cheatsheet.](https://www.markdownguide.org/cheat-sheet/)", unsafe_allow_html=True)
    df = get_notebooks()

    col1, col2, col3, col4 = st.columns([2, 2, 14, 2])
    
    if st.session_state.note == "list":
        notebook_list(df)
        if col4.button("Create", type="primary"):
            st.session_state.note = "create"
            st.rerun()
    
    if st.session_state.note == "edit":
        st.write("Notebook Title")
        new_title = st.text_input(label = "new_title", value = st.session_state.note_title, label_visibility="collapsed")
        new_content = st.text_area(label = "new_content", height = 400, value = st.session_state.note_content, label_visibility="collapsed")
        if col1.button("Cancel"):
            st.session_state.note = "view"
            st.rerun()
        if col4.button("Save", type="primary"):
            edit(new_title, new_content, st.session_state.id)
            st.session_state.note = "view"
            st.rerun()


    if st.session_state.note == "create":
        create_form()
    
    if st.session_state.note == "view":
        view_note()
        if col1.button("Back"):
            st.session_state.note = "list"
            st.rerun()
        if col4.button("Edit", type="primary"):
            st.session_state.note = "edit"
            st.rerun()
       
        
    
    

show_notebook_page()