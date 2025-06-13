import streamlit as st
import os

def load_css(css_file_path):
    """
    Load CSS file and inject it into Streamlit
    
    Parameters:
        css_file_path (str): Path to the CSS file
    """
    if os.path.exists(css_file_path):
        with open(css_file_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        print(f"CSS file not found: {css_file_path}")
