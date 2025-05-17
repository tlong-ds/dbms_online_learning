import streamlit as st
from style.ui import Visual
import toml
import os
from dotenv import load_dotenv
import pymysql
import pandas as pd
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
    # fetch learner
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

    # top metrics
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

    st.title("Learning Statistics")
    st.markdown(f"Hello **{learner_name}**—here’s your progress overview.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Courses Enrolled", enrolled)
    c2.metric("Courses Completed", completed)
    c3.metric("Completion Rate", rate)
    c4.metric("Lectures Passed", passed)

    # load data
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

    # raw data
    # with st.expander("View raw quiz data"):
    #     st.dataframe(df)


