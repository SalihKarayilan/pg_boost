import streamlit as st
from dotenv import load_dotenv

from ui.login import render_login
from ui.dashboard import render_dashboard

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="pg_boost", page_icon="🐘", layout="wide")

# Render views
render_login()
render_dashboard()
