import streamlit as st
from style.ui import Visual
from services.api.db.auth import load_cookies
load_cookies()
Visual.initial()
