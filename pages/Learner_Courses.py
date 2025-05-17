import re
import math
import streamlit as st
from urllib.parse import urlencode
from style.ui import Visual
from services.api.courses import get_courses, courses_list, connect_db
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

# ════════════════  DỮ LIỆU  ════════════════
df_raw = get_courses()  # DataFrame có cột CourseID, Course Name, Instructor..., EnrolledCount

# Bulk-fetch rating info cho tất cả course
course_ids = [int(row['CourseID']) for _, row in df_raw.iterrows() if row.get('CourseID')]
rating_map: dict[int, tuple[int, float]] = {}
if course_ids:
    conn = connect_db()
    cur = conn.cursor()
    # Tạo chuỗi tham số %s cho IN
    placeholders = ','.join(['%s'] * len(course_ids))
    query = (
        f"SELECT CourseID, COUNT(*), COALESCE(AVG(Rating),0) "
        f"FROM Enrollments WHERE CourseID IN ({placeholders}) GROUP BY CourseID"
    )
    cur.execute(query, tuple(course_ids))
    for cid, rev_cnt, avg_rat in cur.fetchall():
        rating_map[int(cid)] = (rev_cnt, avg_rat)
    cur.close()
    conn.close()

# ════════════════  HÀM TIỆN ÍCH  ════════════════
def make_key(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")

# ══════════════════  CÀI ĐẶT  ══════════════════
ROWS_PER_CLICK    = 5
CARDS_PER_ROW_MAP = {"xl": 4, "lg": 6, "md": 8}
VIEW_LABEL2KEY    = {"Extra large icons":"xl", "Large icons":"lg", "Medium icons":"md", "List":"list"}
VIEW_KEY2LABEL    = {v:k for k,v in VIEW_LABEL2KEY.items()}

# --- thêm hằng số default ---
DEFAULT_VIEW_KEY = "md"

SORT_OPTIONS = {
    "Name (A → Z)": ("Course Name", True),
    "Name (Z → A)": ("Course Name", False),
    "Rating (High → Low)": ("dummy", False),  # dummy, sort after
    "Rating (Low → High)": ("dummy", True),
    "Date modified (Newest)": ("Date modified", False),
    "Date modified (Oldest)": ("Date modified", True),
}
KEY2LABEL_SORT   = {make_key(k):k for k in SORT_OPTIONS}
DEFAULT_SORT_KEY = make_key("Name (A → Z)")

# Session state
st.session_state.setdefault("view", DEFAULT_VIEW_KEY)
st.session_state.setdefault("rows", 1)
st.session_state.setdefault("sort_key", DEFAULT_SORT_KEY)

# Sắp xếp DataFrame, hỗ trợ sort theo rating từ rating_map
def sort_df(df: pd.DataFrame) -> pd.DataFrame:
    label = KEY2LABEL_SORT.get(st.session_state.sort_key, "Name (A → Z)")
    col, asc = SORT_OPTIONS[label]
    if "Rating" in label:
        df['__avg_rating'] = df['CourseID'].apply(lambda cid: rating_map.get(int(cid), (0,0.0))[1])
        sorted_df = df.sort_values('__avg_rating', ascending=asc, kind='mergesort')
        return sorted_df.drop(columns='__avg_rating')
    if col in df.columns:
        return df.sort_values(col, ascending=asc, kind="mergesort")
    return df

def render_cards(df_subset: pd.DataFrame, cards_per_row: int):
    for start in range(0, len(df_subset), cards_per_row):
        cols = st.columns(cards_per_row)
        slice_df = df_subset.iloc[start:start + cards_per_row]
        for col, (_, row) in zip(cols, slice_df.iterrows()):
            href = "./Course_Preview?" + urlencode({
                "course_id":       row["CourseID"],
                "course_name":     row["Course Name"],
                "instructor_id":   row["Instructor ID"],
                "instructor_name": row["Instructor Name"],
                "average_rating":  round(row["Average Rating"] or 0, 1),
            })
            col.markdown(
f"""
<div class="card-container">
    <a href={href} class="card">
        <img src="https://i.imgur.com/O3GVLty.jpeg" alt="Course Image">
        <div class="card-body">
            <div style="font-size:0.8rem;color:#777">{row['Instructor Name']}</div>
            <div style="font-weight:600">{row['Course Name']}</div>
            <div style="text-align:right">{round(row['Average Rating'] or 0,1)} ⭐️</div>
        </div>
    </a>
</div>
""",
                unsafe_allow_html=True,
            )
        for col, (_, row) in zip(cols, df_subset.iloc[start:start+cards_per_row].iterrows()):
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
            html = f"""
<a href="{href}"
   style="text-decoration:none;
          display:block;
          border:1px solid #eee;
          border-radius:8px;
          overflow:hidden;
          margin-bottom:1rem;
          background-color: #f2f2f2;">
  <div style="padding:0.5rem;">
    <div style="font-size:1.4rem;
                font-weight:600;
                margin:0;">
      {row['Course Name']}
    </div>
    <div style="font-size:0.9rem;
                color: #888888;      /* màu xám cho Instructor */
                margin:0.25rem 0;">
      {row['Instructor Name']}
    </div>
    <div style="display:flex;
                justify-content:space-between;
                align-items:center;
                font-size:0.9rem;">
      <span>{row['EnrolledCount']} enrolled</span>
      <span>{avg_rat:.1f} ⭐️</span>
    </div>
  </div>
</a>
"""
            col.markdown(html, unsafe_allow_html=True)

# Main
def show_courses():
    st.title("Courses")
    cards_per_row = CARDS_PER_ROW_MAP.get(st.session_state.view, CARDS_PER_ROW_MAP[DEFAULT_VIEW_KEY])
    # tạo một list weight có cards_per_row-2 phần tử bỏ trống, rồi 2 phần tử cho sort/view
    weights = [1] * (cards_per_row - 2) + [2, 2]
    header_cols = st.columns(weights, gap="small")

    # --- phần Sort bỏ nguyên ---
    with header_cols[-2]:
        sort_labels   = list(SORT_OPTIONS.keys())
        current_label = KEY2LABEL_SORT[st.session_state.sort_key]
        new_label     = st.selectbox("Sort by", sort_labels, index=sort_labels.index(current_label))
        new_key       = make_key(new_label)
        if new_key != st.session_state.sort_key:
            st.session_state.sort_key = new_key
            st.rerun()

    # --- phần View đã sửa ---
    with header_cols[-1]:
        view_labels = list(VIEW_LABEL2KEY.keys())
        # lấy nhãn hiện tại, nếu không có thì về nhãn mặc định
        cur_view_label = VIEW_KEY2LABEL.get(
            st.session_state.view,
            VIEW_KEY2LABEL[DEFAULT_VIEW_KEY]
        )
        # tìm index an toàn
        default_idx = view_labels.index(cur_view_label) if cur_view_label in view_labels else 0
        new_view = st.selectbox("View", view_labels, index=default_idx)
        key_view = VIEW_LABEL2KEY[new_view]
        if key_view != st.session_state.view:
            st.session_state.view = key_view
            st.session_state.rows = 1
            st.rerun()

    df = sort_df(df_raw)
    if st.session_state.view == "list":
        courses_list(df)
        return

    limit = st.session_state.rows * CARDS_PER_ROW_MAP.get(st.session_state.view,8)
    render_cards(df.head(limit), CARDS_PER_ROW_MAP.get(st.session_state.view,8))
    if limit < len(df):
        if st.button("Expand"):
            st.session_state.rows += ROWS_PER_CLICK
            st.rerun()

show_courses()