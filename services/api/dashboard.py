import streamlit as st
from style.ui import Visual
import toml
import os
from dotenv import load_dotenv
import pymysql
import pandas as pd
import altair as alt
from services.api.courses import courses_list
import altair as alt

load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))

def connect_db():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT
    )

def make_period_df(series, freq_label):
    dfp = series.reset_index().rename(columns={'index':'Date', series.name:series.name})
    if freq_label == 'Weekly':
        dfp['Period'] = (
            dfp['Date'].dt.strftime('%d/%m')
            + '–'
            + (dfp['Date'] + pd.Timedelta(days=6)).dt.strftime('%d/%m')
        )
    elif freq_label == 'Monthly':
        dfp['Period'] = dfp['Date'].dt.strftime('%b %Y')
    else:  # Daily
        dfp['Period'] = dfp['Date'].dt.strftime('%d/%m')
    return dfp

def show_dashboard_learner():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT LearnerID, LearnerName FROM Learners WHERE AccountName = %s",
        (st.session_state.username,)
    )

    row = cursor.fetchone()
    if not row:
        st.error("Learner not found.")
        return
    learner_id, learner_name = row

    cursor.execute("SELECT COUNT(*) FROM Enrollments WHERE LearnerID = %s", (learner_id,))
    enrolled = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM Enrollments WHERE LearnerID = %s AND Percentage = 100",
        (learner_id,)
    )
    
    completed = cursor.fetchone()[0]
    rate = f"{completed/enrolled*100:.1f}%" if enrolled else "0%"
    cursor.execute(
        "SELECT COUNT(*) FROM LectureResults WHERE LearnerID = %s AND State = 'Passed'",
        (learner_id,)
    )
    passed = cursor.fetchone()[0]
    conn.close()

    st.title("Learning Dashboard")
    st.markdown(f"Hello **{learner_name}** - here's your progress overview.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Courses Enrolled", enrolled)
    c2.metric("Courses Completed", completed)
    c3.metric("Completion Rate", rate)
    c4.metric("Lectures Passed", passed)

    if not st.session_state.view:
        st.session_state.view = 'Statistics'

    col = st.columns([1,1,12])
    with col[0]:
        if st.button("Statistics"):
            st.session_state.view = 'Statistics'
    with col[1]:
        if st.button("Enrolled course"):
            st.session_state.view = 'Enrolled course'

    # --- view: Statistics ---
    if st.session_state.view == 'Statistics':
        conn = connect_db()
        df = pd.read_sql(
            """
            SELECT Date, Score
            FROM LectureResults
            WHERE LearnerID = %s AND State = 'Passed'
            """,
            conn,
            params=(learner_id,),
            parse_dates=["Date"]
        )
        conn.close()

        if df.empty:
            st.info("You haven't passed any lecture quizzes yet.")
            return

        df = df.set_index("Date").sort_index()
        span_days = (df.index.max() - df.index.min()).days

        # freq options
        opts = ["Daily"]
        if span_days >= 7:  opts.append("Weekly")
        if span_days >= 30: opts.append("Monthly")

        freq_params = {
            "Daily":   ("D",      "left"),
            "Weekly":  ("W-MON",  "left"),
            "Monthly": ("MS",     "left")
        }
        freq_label = st.radio("Aggregation Frequency", opts, horizontal=True)
        freq, label_side = freq_params[freq_label]

        # full index
        full_idx = pd.date_range(df.index.min(), df.index.max(), freq=freq)

        # compute series
        lec_counts = (
            df.resample(freq, label=label_side)
              .size()
              .reindex(full_idx, fill_value=0)
              .rename("Lectures Passed")
        )
        avg_scores = (
            df["Score"]
              .resample(freq, label=label_side)
              .mean()
              .reindex(full_idx, fill_value=0)
              .rename("Average Score")
        )

        # chart in tabs
        tab1, tab2 = st.tabs(["Lectures Passed", "Average Score"])
        with tab1:
            df_counts = make_period_df(lec_counts, freq_label)
            chart1 = (
                alt.Chart(df_counts)
                   .mark_bar()
                   .encode(
                       x=alt.X('Period:N',
                               title=freq_label,
                               axis=alt.Axis(labelAngle=0, labelAlign='center')),
                       y=alt.Y('Lectures Passed:Q', title='Lectures Passed'),
                       tooltip=['Period', 'Lectures Passed']
                   )
                   .properties(height=300)
            )
            st.altair_chart(chart1, use_container_width=True)

        with tab2:
            df_avg = make_period_df(avg_scores, freq_label)
            chart2 = (
                alt.Chart(df_avg)
                   .mark_line(point=True)
                   .encode(
                       x=alt.X('Period:N',
                               title=freq_label,
                               axis=alt.Axis(labelAngle=0, labelAlign='center')),
                       y=alt.Y('Average Score:Q', title='Average Score'),
                       tooltip=['Period', 'Average Score']
                   )
                   .properties(height=300)
            )
            st.altair_chart(chart2, use_container_width=True)

    # --- view: Enrolled course ---
    elif st.session_state.view == 'Enrolled course':
        conn = connect_db()
        df_enrolled = pd.read_sql(
            """
            SELECT
                c.CourseID           AS CourseID,
                c.CourseName         AS "Course Name",
                i.InstructorID       AS "Instructor ID",
                i.InstructorName     AS "Instructor Name",
                AVG(e.Rating)        AS "Average Rating",
                e.Percentage         AS Percentage
            FROM Enrollments e
            JOIN Courses    c ON e.CourseID     = c.CourseID
            JOIN Instructors i ON c.InstructorID = i.InstructorID
            WHERE e.LearnerID = %s
            GROUP BY
                c.CourseID,
                c.CourseName,
                i.InstructorID,
                i.InstructorName,
                e.Percentage
            ORDER BY c.CourseName
            """,
            conn,
            params=(learner_id,)
        )
        conn.close()

        if df_enrolled.empty:
            st.info("You are not enrolled in any courses yet.")
        else:
            courses_list(df_enrolled, ["Instructor Name", "Percentage"])
            #st.dataframe(df_enrolled, use_container_width=True, hide_index=True)

    # raw data
    # with st.expander("View raw quiz data"):
    #     st.dataframe(df)







def show_dashboard_instructor():
    # 1. Fetch instructor ID and name
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT InstructorID, InstructorName FROM Instructors WHERE AccountName = %s",
        (st.session_state.username,)
    )
    row = cursor.fetchone()
    if not row:
        st.error("Instructor not found.")
        conn.close()
        return
    instructor_id, instructor_name = row
    conn.close()

    # 2. Calculate key metrics
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM Courses WHERE InstructorID = %s",
        (instructor_id,)
    )
    total_courses = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM Lectures l JOIN Courses c ON l.CourseID = c.CourseID WHERE c.InstructorID = %s",
        (instructor_id,)
    )
    total_lectures = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(DISTINCT e.LearnerID) FROM Enrollments e JOIN Courses c ON e.CourseID = c.CourseID WHERE c.InstructorID = %s",
        (instructor_id,)
    )
    total_learners = cursor.fetchone()[0]

    cursor.execute(
        "SELECT AVG(AverageRating) FROM Courses WHERE InstructorID = %s",
        (instructor_id,)
    )
    avg_rating = cursor.fetchone()[0] or 0.0
    conn.close()

    # 3. Display header and metrics
    st.title("Instructor Dashboard")
    st.markdown(f"Hello **{instructor_name}** - here’s your progress overview.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Courses", total_courses)
    c2.metric("Total Lectures", total_lectures)
    c3.metric("Total Learners", total_learners)
    c4.metric("Avg. Rating", f"{avg_rating:.1f}")
    st.markdown("---")

    # 4. View selector buttons
    if 'instr_view' not in st.session_state:
        st.session_state.instr_view = 'Courses Overview'

    col = st.columns([2,2,13])
    with col[0]:
        if st.button("Courses Overview"):
            st.session_state.instr_view = 'Courses Overview'
    with col[1]:
        if st.button("Enrollment Trends"):
            st.session_state.instr_view = 'Enrollment Trends'

    st.markdown(
    """""",
    unsafe_allow_html=True)

    # 5. Courses Overview
    if st.session_state.instr_view == 'Courses Overview':
        conn = connect_db()
        df = pd.read_sql(
            """
            SELECT
              c.CourseID            AS CourseID,
              c.CourseName          AS "Course Name",
              i.InstructorID        AS "Instructor ID",
              i.InstructorName      AS "Instructor Name",
              c.Difficulty          AS Difficulty,
              c.EstimatedDuration   AS "Duration (h)",
              c.AverageRating       AS "Average Rating",
              COUNT(e.LearnerID)    AS "Enrolled Learners"
            FROM Courses c
            JOIN Instructors i 
              ON c.InstructorID = i.InstructorID
            LEFT JOIN Enrollments e 
              ON c.CourseID = e.CourseID
            WHERE c.InstructorID = %s
            GROUP BY
              c.CourseID, c.CourseName,
              i.InstructorID, i.InstructorName,
              c.Difficulty, c.EstimatedDuration,
              c.AverageRating
            ORDER BY c.CourseName
            """,
            conn,
            params=(instructor_id,)
        )
        conn.close()

        if df.empty:
            st.info("You have no courses yet.")
        else:
            cols = ["Difficulty", "Duration (h)", "Average Rating", "Enrolled Learners"]
            courses_list(df, cols)

    # 6. Enrollment Trends
    else:
        conn = connect_db()
        df_courses = pd.read_sql(
            "SELECT CourseID, CourseName FROM Courses WHERE InstructorID = %s ORDER BY CourseName",
            conn,
            params=(instructor_id,)
        )
        conn.close()

        if df_courses.empty:
            st.info("You have no courses to show trends for.")
            return

        sel = st.selectbox(
            "Choose a course to view the number of registrations over time.", 
            df_courses["CourseID"],
            format_func=lambda x: df_courses.set_index("CourseID").loc[x, "CourseName"]
        )

        # Load enrollment dates
        conn = connect_db()
        df_enroll = pd.read_sql(
            "SELECT EnrollmentDate AS Date FROM Enrollments WHERE CourseID = %s",
            conn,
            params=(sel,),
            parse_dates=["Date"]
        )
        conn.close()

        if df_enroll.empty:
            st.info("Chưa có người đăng ký cho khóa này.")
        else:
            df_enroll = df_enroll.set_index("Date").sort_index()
            span_days = (df_enroll.index.max() - df_enroll.index.min()).days

            # Frequency options
            opts = ["Daily"]
            if span_days >= 7:  opts.append("Weekly")
            if span_days >= 30: opts.append("Monthly")

            freq_params = {
                "Daily":   ("D",      "left"),
                "Weekly":  ("W-MON",  "left"),
                "Monthly": ("MS",     "left")
            }
            freq_label = st.radio("Aggregation Frequency", opts, horizontal=True)
            freq, label_side = freq_params[freq_label]

            # Full date index
            full_idx = pd.date_range(df_enroll.index.min(), df_enroll.index.max(), freq=freq)

            # Compute series
            new_counts = (
                df_enroll.resample(freq, label=label_side)
                         .size()
                         .reindex(full_idx, fill_value=0)
                         .rename("New Enrollments")
            )
            cum_counts = new_counts.cumsum().rename("Cummulative Enrollments")

            # Charts in tabs
            tab1, tab2 = st.tabs(["New Enrollments", "Cummulative Enrollments"])
            with tab1:
                df_new = make_period_df(new_counts, freq_label)
                chart1 = (
                    alt.Chart(df_new)
                       .mark_bar()
                       .encode(
                           x=alt.X('Period:N',
                                   title=freq_label,
                                   axis=alt.Axis(labelAngle=0, labelAlign='center')),
                           y=alt.Y('New Enrollments:Q', title='New Enrollments'),
                           tooltip=['Period', 'New Enrollments']
                       )
                       .properties(height=300)
                )
                st.altair_chart(chart1, use_container_width=True)

            with tab2:
                df_cum = make_period_df(cum_counts, freq_label)
                chart2 = (
                    alt.Chart(df_cum)
                       .mark_line(point=True)
                       .encode(
                           x=alt.X('Period:N',
                                   title=freq_label,
                                   axis=alt.Axis(labelAngle=0, labelAlign='center')),
                           y=alt.Y('Cumulative Enrollments:Q', title='Cumulative Enrollments'),
                           tooltip=['Period', 'Cumulative Enrollments']
                       )
                       .properties(height=300)
                )
                st.altair_chart(chart2, use_container_width=True)