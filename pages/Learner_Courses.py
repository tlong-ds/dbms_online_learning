import re
import streamlit as st
from urllib.parse import urlencode
from style.ui import Visual
from services.api.courses import get_courses, courses_list, get_total_learners
from services.api.db.auth import load_cookies
import pandas as pd

# ══════════════════  CẤU HÌNH TRANG  ══════════════════
st.set_page_config(
    page_title="Courses",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_cookies()
Visual.initial()
df_raw = get_courses()                # có cột “Average Rating”

# ════════════════  HÀM TIỆN ÍCH  ════════════════
def make_key(label: str) -> str:
    """Chuẩn-hoá nhãn menu thành khoá: chữ thường, a-z0-9, gạch dưới."""
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")

# ════════════════  THÔNG SỐ & TRẠNG THÁI  ════════════════
ROWS_PER_CLICK    = 5
CARDS_PER_ROW_MAP = {"xl": 4, "lg": 6, "md": 8}

VIEW_LABEL2KEY = {
    "Extra large icons": "xl",
    "Large icons":       "lg",
    "Medium icons":      "md",
    "List":              "list",
}
VIEW_KEY2LABEL = {v: k for k, v in VIEW_LABEL2KEY.items()}

# ➜➜➜  ĐÃ BỔ SUNG 2 TUỲ CHỌN SẮP XẾP THEO RATING
SORT_OPTIONS = {
    "Name (A → Z)"                 : ("Course Name",   True),
    "Name (Z → A)"                 : ("Course Name",   False),

    "Rating (High → Low)"          : ("Average Rating", False),
    "Rating (Low → High)"          : ("Average Rating", True),

    "Date modified (Newest)"       : ("Date modified", False),
    "Date modified (Oldest)"       : ("Date modified", True),
}
KEY2LABEL_SORT   = {make_key(k): k for k in SORT_OPTIONS}
DEFAULT_SORT_KEY = make_key("Name (A → Z)")

# ─── session_state ───
st.session_state.setdefault("view",     "md")
st.session_state.setdefault("rows",     1)
st.session_state.setdefault("sort_key", DEFAULT_SORT_KEY)

# ════════════════  XỬ LÝ SORT  ════════════════
def sort_df(df: pd.DataFrame) -> pd.DataFrame:
    label = KEY2LABEL_SORT.get(st.session_state.sort_key, "Name (A → Z)")
    col, asc = SORT_OPTIONS[label]
    if col in df.columns:
        return df.sort_values(col, ascending=asc, kind="mergesort")
    return df

# ════════════════  RENDER CARDS  ════════════════
def render_cards(df_subset: pd.DataFrame, cards_per_row: int):
    for start in range(0, len(df_subset), cards_per_row):
        cols     = st.columns(cards_per_row)
        slice_df = df_subset.iloc[start : start + cards_per_row]

        for col, (_, row) in zip(cols, slice_df.iterrows()):
            href = "./Course_Preview?" + urlencode({
                "course_id":       row["CourseID"],
                "course_name":     row["Course Name"],
                "instructor_id":   row["Instructor ID"],
                "instructor_name": row["Instructor Name"],
                "average_rating":  round(row["Average Rating"] or 0, 1),
            })

            # 1 lần gọi markdown, 1 cặp <a>…</a> duy nhất
            html = f"""
<a href="{href}" style="text-decoration:none; display:block; border:1px solid #eee; border-radius:8px; overflow:hidden;">
  <div style="padding:0.5rem;">
    <div style="font-size:1.4rem; font-weight:600; margin:0;">
      {row['Course Name']}
    </div>
    <div style="font-size:0.9rem; color:#555; margin:0.25rem 0;">
      {row['Instructor Name']}
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.9rem;">
      <span>{row['EnrolledCount']} enrolled</span>
      <span>{round(row['Average Rating'] or 0,1)} ⭐️</span>
    </div>
  </div>
</a>
"""
            col.markdown(html, unsafe_allow_html=True)

# ════════════════  TRANG CHÍNH  ════════════════
def show_courses():
    st.title("Courses")

    cards_per_row = CARDS_PER_ROW_MAP.get(st.session_state.view, 8)
    header_cols   = st.columns(cards_per_row)

    # SORT menu
    with header_cols[-2]:
        st.markdown(
            """
            <style>
            div[data-testid="stSelectbox-sort_menu"]{width:fit-content!important;margin-left:auto}
            div[data-testid="stSelectbox-sort_menu"] label{display:none}
            </style>
            """,
            unsafe_allow_html=True,
        )
        sort_labels = list(SORT_OPTIONS.keys())
        current_sort_label = KEY2LABEL_SORT[st.session_state.sort_key]
        new_sort_label = st.selectbox(
            "", sort_labels,
            index=sort_labels.index(current_sort_label),
            key="sort_menu",
            label_visibility="collapsed",
        )
        new_key = make_key(new_sort_label)
        if new_key != st.session_state.sort_key:
            st.session_state.sort_key = new_key
            st.rerun()

    # VIEW menu
    with header_cols[-1]:
        st.markdown(
            """
            <style>
            div[data-testid="stSelectbox-view_menu"]{width:fit-content!important;margin-left:auto}
            div[data-testid="stSelectbox-view_menu"] label{display:none}
            </style>
            """,
            unsafe_allow_html=True,
        )
        view_labels = list(VIEW_LABEL2KEY.keys())
        current_view_label = VIEW_KEY2LABEL[st.session_state.view]
        new_view_label = st.selectbox(
            "", view_labels,
            index=view_labels.index(current_view_label),
            key="view_menu",
            label_visibility="collapsed",
        )
        new_view_key = VIEW_LABEL2KEY[new_view_label]
        if new_view_key != st.session_state.view:
            st.session_state.view = new_view_key
            st.session_state.rows = 1
            st.rerun()

    # dữ liệu sau sort
    df = sort_df(df_raw)

    if st.session_state.view == "list":
        courses_list(df)
        return

    limit = st.session_state.rows * cards_per_row
    render_cards(df.head(limit), cards_per_row)

    # Expand
    if limit < len(df):
        expand_cols = st.columns(cards_per_row)
        with expand_cols[-1]:
            st.markdown(
                """
                <style>
                div[data-testid="baseButton-expand_btn"] button{
                    width:fit-content!important;margin-left:auto;padding:0.25rem 0.75rem}
                </style>
                """, unsafe_allow_html=True,
            )
            if st.button("Expand", key="expand_btn"):
                st.session_state.rows += ROWS_PER_CLICK
                st.rerun()

# Run page
show_courses()