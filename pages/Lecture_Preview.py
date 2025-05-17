import re
import streamlit as st
from urllib.parse import urlencode
from style.ui import Visual
from services.api.courses import get_courses, courses_list, get_total_learners
from services.api.db.auth import load_cookies
import pandas as pd

