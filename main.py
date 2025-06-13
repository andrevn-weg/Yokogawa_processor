from pathlib import Path
import sys
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from datetime import datetime
from PIL import Image
from utils.css_loader import load_css

# Page configuration
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add project root directory to PATH
project_root = Path(__file__).parent
sys.path.append(str(project_root))
# Load centralized CSS
css_path = os.path.join(project_root, "static", "css", "material_styles.css")
load_css(css_path)



pages = {
    "Data Processing": [
        st.Page("pages/Process_gtd_Files.py", title='GTD File Processing', icon="📊"),
    ]
}

pg = st.navigation(pages, expanded=True)
pg.run()