import re
import streamlit as st
from urllib.parse import urlencode
from style.ui import Visual
from services.api.courses import lecture_list
from services.api.lecture_display import get_lecture_data
from services.api.db.auth import load_cookies
import pandas as pd

load_cookies()
params = st.query_params
st.session_state.lecture_id = params.get("lecture_id")
title, description, content, course_id = get_lecture_data(st.session_state.lecture_id)

course_content = lecture_list(course_id)