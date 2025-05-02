import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from style.ui import Visual
import os
import toml

Visual.initial()

def main():
    switch_page("Authentification")

if __name__ == "__main__":
    main()

    