import streamlit as st
from style.ui import Visual
from services.api.db.auth import load_cookies
from services.api.courses import connect_db

# --- PAGE SETUP ---
st.set_page_config(
    page_title="About Us – The Learning House",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_cookies()
Visual.initial()

# --- GLOBAL CSS FOR FONT SIZE ---
st.markdown(
    """
    <style>
      /* Increase font size for body text and list items */
      .css-1d391kg p, .css-1d391kg li, .markdown-text-container p, .markdown-text-container li {
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# --- KEY METRICS ---
conn = connect_db()
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM Courses")
total_courses = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT LearnerID) FROM Enrollments")
total_learners = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM Instructors")
total_instructors = cur.fetchone()[0]
cur.close()
conn.close()

# --- HEADER & INTRO ---
st.title("About The Learning House")
st.markdown(
    """
    Welcome to **The Learning House**, the home of **Learning Connect** —
    a comprehensive marketplace uniting passionate learners with expert instructors across all domains.
    """,
    unsafe_allow_html=True
)

# --- METRICS ROW ---
m1, m2, m3 = st.columns(3)
m1.metric("📚 Courses", total_courses)
m2.metric("👩‍🎓 Learners", total_learners)
m3.metric("👩‍🏫 Instructors", total_instructors)
st.markdown("---")

# --- PROBLEM STATEMENT ---
st.header("Problem Statement")
st.markdown(
    """
    **Learners** today crave diverse, high-quality content spanning from **soft skills** (e.g., communication, personal branding) to **academic subjects** (e.g., mathematics, chemistry, programming).  
    Yet existing platforms fall short:
    - **YouTube**: lacks structured curricula, clear learning paths, and interactive support.  
    - **Traditional e-learning sites**: often restrict content to specific grades or fields (e.g., high school).  
    - **Instructors** struggle** to publish, monetize, and reach eager audiences due to opaque onboarding, inconsistent formats, and unclear revenue sharing.
    """,
    unsafe_allow_html=True
)

# --- OUR SOLUTION ---
st.header("Our Solution: The Learning House")
st.markdown(
    """
    **The Learning House** is a unified **education marketplace** designed to be:
    1. **Easy to learn**: Micro-learning videos, clear skill tracks, badges & certificates, and free to access
    2. **Easy to teach**: One-click course builder, standardized templates, transparent analytics & payouts
    3. **Unlimited content**: From personal development to advanced technical subjects
    4. **Community-driven**: Live Q&A, livestreaming, mentorship, and workshops
    """,
    unsafe_allow_html=True
)

# --- KEY FEATURES ---
st.header("Key Features")
st.markdown(
    """
    | User Type   | Features                                                              |
    |-------------|-----------------------------------------------------------------------|
    | **Learners**    | • Personalized dashboard: progress, skill badges<br>• AI-powered course recommender<br>• Interactive Q&A, quizzes, hands-on projects<br>• Gamification: leaderboards & rewards                    |
    | **Instructors** | • One-click course creation: video, slides, quizzes, live-stream<br>• Detailed analytics: engagement, completion rates<br>• Seamless marketplace integration & promotional tools<br>• Flexible monetization: subscriptions, one-time payments, crowdfunding  |
    """,
    unsafe_allow_html=True
)

# --- COMPETITIVE ADVANTAGE ---
st.header("Competitive Advantage")
st.markdown(
    """
    - **Structured Learning**: Combined modules, assessments, and certificates — not just passive video content.
    - **Open Platform**: Anyone from life coaches to data scientists can share expertise.
    - **Smart Technology**: AI-driven subtitles, summarization, and personalized paths.
    - **Community & Support**: Mentor matching, peer reviews, instructor workshops.
    """,
    unsafe_allow_html=True
)

# --- ROADMAP & VISION ---
st.header("Roadmap & Vision")
st.markdown(
    """
    **Phase 1 (MVP)**:
    - Core marketplace: course listing, enrollment, secure payments<br>
    - Foundational UX for web & mobile

    **Phase 2**:
    - AI-driven recommendations & auto-transcripts
    - Advanced analytics & community forums

    **Phase 3**:
    - B2B white-label offerings for organizations & schools
    - Multi-language expansion targeting APAC and global markets

    **Long-term Vision**: Transform Learning Connect into the world’s most **learner-centric**, **community-driven**, and **innovation-led** educational ecosystem.
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# --- TEAM SECTION ---
st.header("Meet Our Specialists")
cols = st.columns(4)
team = [
    ("Doan Quoc Bao",       "Backend Developer"),
    ("Ly Thanh Long",       "Frontend Developer"),
    ("Tran Anh Tuan",       "Data Engineer"),
    ("Ha Quang Minh",       "UI/UX Designer"),
]

image_paths = [
    "D:/Minh/Tài liệu học tập (DSEB)/Kì 4/Database Management Systems/Final Project/dbms_online_learning/logo/ava1.webp",
    "D:/Minh/Tài liệu học tập (DSEB)/Kì 4/Database Management Systems/Final Project/dbms_online_learning/logo/ava2.webp",
    "D:/Minh/Tài liệu học tập (DSEB)/Kì 4/Database Management Systems/Final Project/dbms_online_learning/logo/ava3.webp",
    "D:/Minh/Tài liệu học tập (DSEB)/Kì 4/Database Management Systems/Final Project/dbms_online_learning/logo/ava4.webp",
]


for (name, role), img_path, col in zip(team, image_paths, cols):
    with col:
        col.image(img_path, width=200)
        st.markdown(f"**{name}**")
        st.markdown(f"*{role}*")

st.markdown("---")

# --- CONTACT & FOOTER ---
st.header("Get In Touch")
st.markdown(
    """
    📧 Email: [support@learninghouse.com](mailto:support@learninghouse.com)  
    🌐 Website: [www.learninghouse.com](https://www.learninghouse.com)  
    📞 Phone: +84 888 888 888
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="text-align:center; color:gray; font-size:0.8rem;">
    © 2025 The Learning House. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)