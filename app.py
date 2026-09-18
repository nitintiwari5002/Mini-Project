import streamlit as st

# Page Configuration
Home = st.Page("pages/home.py", title="Home")
Features = st.Page("pages/features.py", title="Features")
About = st.Page("pages/about_us.py", title="About")
Resume = st.Page("pages/resume.py", title="Resume")

pg = st.navigation([Home, Features, About, Resume], position="hidden")

# 🚀 Run Navigation
pg.run()
