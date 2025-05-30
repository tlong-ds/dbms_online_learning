import streamlit as st
st.set_page_config(
    page_title="Courses",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from services.api.db.auth import load_cookies
load_cookies()

from streamlit_extras.switch_page_button import switch_page
if "login" not in st.session_state:
    switch_page("Authentification")

import re
from urllib.parse import urlencode
from style.ui import Visual
from services.api.courses import get_courses, courses_list, connect_db, get_instructed_courses, add_course, instructed_courses_list
import pandas as pd
from streamlit_searchbox import st_searchbox
from streamlit_extras.switch_page_button import switch_page


Visual.initial()

if st.session_state.role == "Learner":

    @st.fragment
    def search_fragment(df):
        def course_search(search_term: str) -> list:
            if search_term:
                with st.spinner("Searching"):
                    search_term = search_term.lower()
                    filtered_df = df[df['Course Name'].str.lower().str.contains(search_term)]
                    return [(row['Course Name'], row['Course Name']) for _, row in filtered_df.iterrows()]
            return list(df["Course Name"])
        
        search = st_searchbox(
            search_function=course_search,
            placeholder="Search",
            key="search",
            default_options=list(df['Course Name']),
            rerun_scope="fragment",
            debounce=500
        )
        
        if search:
            return search

    # ══════════════════ DỮ LIỆU ══════════════════
    df_raw = get_courses()

    course_ids = [int(row['CourseID']) for _, row in df_raw.iterrows() if row.get('CourseID')]
    rating_map: dict[int, tuple[int, float]] = {}
    if course_ids:
        conn = connect_db()
        cur = conn.cursor()
        placeholders = ','.join(['%s'] * len(course_ids))
        query = (
            f"SELECT CourseID, COUNT(*), COALESCE(AVG(Rating),0)"
            f" FROM Enrollments WHERE CourseID IN ({placeholders}) GROUP BY CourseID"
        )
        cur.execute(query, tuple(course_ids))
        for cid, rev_cnt, avg_rat in cur.fetchall():
            rating_map[int(cid)] = (rev_cnt, avg_rat)
        cur.close()
        conn.close()

    # ══════════════════ HÀM TIỆN ÍCH ══════════════════
    def make_key(label: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")

    # ════════════════════ CÀI ĐẶT ════════════════════
    ROWS_PER_CLICK    = 5
    CARDS_PER_ROW_MAP = {"xl": 4, "lg": 6, "md": 8}
    VIEW_LABEL2KEY    = {"Extra large icons":"xl", "Large icons":"lg", "Medium icons":"md", "List":"list"}
    VIEW_KEY2LABEL    = {v:k for k,v in VIEW_LABEL2KEY.items()}
    DEFAULT_VIEW_KEY  = "xl"

    # Sort config
    default_sort = "Rating (High → Low)"
    SORT_OPTIONS = {
        "Name (A → Z)": ("Course Name", True),
        "Name (Z → A)": ("Course Name", False),
        "Rating (High → Low)": ("dummy", False),
        "Rating (Low → High)": ("dummy", True),
        "Date modified (Newest)": ("Date modified", False),
        "Date modified (Oldest)": ("Date modified", True),
    }
    KEY2LABEL_SORT   = {make_key(k):k for k in SORT_OPTIONS}
    DEFAULT_SORT_KEY = make_key(default_sort)

    # Session state
    st.session_state.setdefault("view", DEFAULT_VIEW_KEY)
    st.session_state.setdefault("rows", 1)
    st.session_state.setdefault("sort_key", DEFAULT_SORT_KEY)

    # Sắp xếp DataFrame
    def sort_df(df: pd.DataFrame) -> pd.DataFrame:
        label = KEY2LABEL_SORT.get(st.session_state.sort_key, default_sort)
        col, asc = SORT_OPTIONS[label]
        if "Rating" in label:
            df['__avg_rating'] = df['CourseID'].apply(lambda cid: rating_map.get(int(cid), (0,0.0))[1])
            sorted_df = df.sort_values('__avg_rating', ascending=asc, kind='mergesort')
            return sorted_df.drop(columns='__avg_rating')
        if col in df.columns:
            return df.sort_values(col, ascending=asc, kind='mergesort')
        return df

    # Render grid of cards, text aligned at top of each box
    def render_cards(df_subset: pd.DataFrame, cards_per_row: int):
        for start in range(0, len(df_subset), cards_per_row):
            cols = st.columns(cards_per_row, gap="small", vertical_alignment="top")
            slice_df = df_subset.iloc[start:start + cards_per_row]
            for col, (_, row) in zip(cols, slice_df.iterrows()):
                cid = int(row['CourseID'])
                rev_cnt, avg_rat = rating_map.get(cid, (0, 0.0))
                href = (
                    "./Course_Preview?" + urlencode({
                        "course_id": cid,
                        "course_name": row['Course Name'],
                        "instructor_id": row['Instructor ID'],
                        "instructor_name": row['Instructor Name'],
                        "average_rating": round(avg_rat,1),
                    })
                )
                # Wrap in card-container and use flexbox to align content at top
                html = f"""
                <div class="card-container">
                <a href="{href}" class="card" style="display:flex;flex-direction:column;justify-content:flex-start;height:100%;text-decoration:none;">
                <div class="card-body" style="flex:1;display:flex;flex-direction:column;justify-content:flex-start;padding:0.5rem;">
                    <div style="font-size:1.4rem;font-weight:600;margin:0;">{row['Course Name']}</div>
                    <div style="font-size:0.9rem;color:#888888;margin:0.25rem 0;">{row['Instructor Name']}</div>
                    <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:center;font-size:0.9rem;">
                    <span>{row.get('EnrolledCount', rev_cnt)} enrolled</span>
                    <span>{avg_rat:.1f} ⭐️</span>
                    </div>
                </div>
                </a>
                </div>
                """
                col.markdown(html, unsafe_allow_html=True)
    
    
    # Main rendering of courses page
    st.title("Courses")
    cards_per_row = CARDS_PER_ROW_MAP.get(st.session_state.view, CARDS_PER_ROW_MAP[DEFAULT_VIEW_KEY])
    header_cols = st.columns([13,2,2], gap="small", vertical_alignment="top")

    # Sort selector
    with header_cols[-2]:
        sort_labels = list(SORT_OPTIONS.keys())
        current_label = KEY2LABEL_SORT.get(st.session_state.sort_key, default_sort)
        new_label = st.selectbox("Sort by", sort_labels, index=sort_labels.index(current_label))
        new_key = make_key(new_label)
        if new_key != st.session_state.sort_key:
            st.session_state.sort_key = new_key
            st.rerun()

    # View selector
    with header_cols[-1]:
        view_labels = list(VIEW_LABEL2KEY.keys())
        cur_label = VIEW_KEY2LABEL.get(st.session_state.view, VIEW_KEY2LABEL[DEFAULT_VIEW_KEY])
        idx = view_labels.index(cur_label) if cur_label in view_labels else 0
        new_view = st.selectbox("View", view_labels, index=idx)
        key_view = VIEW_LABEL2KEY[new_view]
        if key_view != st.session_state.view:
            st.session_state.view = key_view
            st.session_state.rows = 1
            st.rerun()
    
    df = sort_df(df_raw)
    with header_cols[0]:
        st.markdown(f'<div style="font-size: 18px; color: {"#000000" if st.session_state.theme == "dark" else "#f7fbfe"}"> .</div>', unsafe_allow_html=True) 
        search_fragment(df)
        
    st.write("Available Courses")
    if st.session_state.view == "list":
        courses_list(df)
    else:
        limit = st.session_state.rows * cards_per_row
        render_cards(df.head(limit), cards_per_row)
        if limit < len(df):
            expands = st.columns([20, 2])
            if expands[1].button("Expand"):
                st.session_state.rows += ROWS_PER_CLICK
                st.rerun()



if st.session_state.role == "Instructor": 
    df = get_instructed_courses()

    st.session_state.setdefault("instruct_course_view", "list")

    @st.dialog("Create New Course")
    def course_create_page():
        st.write("Course Name")
        course_name = st.text_input(label="course", label_visibility="collapsed")
        st.write("Description")
        description = st.text_area(label="description", label_visibility="collapsed")
        skills_options = pd.read_csv("services/api/skills.csv")["skill"]
        st.write("Skills")
        selected_skills = st.multiselect(label="skills", options=list(skills_options), label_visibility="collapsed")
        st.write("Or add new skills")
        new_skills = st.text_input(label="new skills", label_visibility="collapsed")
        st.write("Difficulty")
        difficulty = st.selectbox(label="difficulty", label_visibility="collapsed", options=["Beginner", "Intermediate", "Advanced"])
        st.write("Estimate Duration (Hours)")
        duration = st.text_input(label="duration", label_visibility="collapsed")

        if st.button("Submit"):
            if new_skills:
                # Support multiple new skills separated by commas
                new_skills_list = [s.strip() for s in new_skills.split(",") if s.strip()]
                # Append new skills to selected
                selected_skills.extend(new_skills_list)
                # Append new unique skills to CSV
                existing_skills = set(skills_options.str.lower())
                new_unique_skills = [s for s in new_skills_list if s.lower() not in existing_skills]
                if new_unique_skills:
                    pd.DataFrame({"skill": new_unique_skills}).to_csv("services/api/skills.csv", mode="a", index=False, header=False)
            add_course(course_name, description, selected_skills, difficulty, duration)
            st.rerun()
        
    st.title("Courses")
    print(st.session_state.id)
    cols = st.columns([16, 2])
    if cols[1].button("Add Course"):
        course_create_page()
    if st.session_state.instruct_course_view == "list":
        instructed_courses_list(df)

