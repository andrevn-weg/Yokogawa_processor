import streamlit as st
import os
import sys
import pandas as pd
import tempfile
import json
import numpy as np
from datetime import datetime
from PIL import Image
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# Adds the project root directory to PATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Imports the necessary classes
from models.gtd_processor import GTDProcessor
from models.Channel import Channel

# Import CSS loader
from utils.css_loader import load_css

# Load centralized CSS (commented out as static folder doesn't exist)
# project_root = Path(__file__).parent.parent
# css_path = os.path.join(project_root, "static", "css", "material_styles.css")
# load_css(css_path)

# Page configuration
# st.set_page_config(
#     page_title="GTD File Processor",
#     initial_sidebar_state="expanded",
#     page_icon="📊",
#     layout="wide"
# )

# CSS para estilização geral
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(to right, #4e73df, #224abe);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        color: white;
        text-align: center;
    }
    .feature-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .section-header {
        background-color: #e6f7ff;
        padding: 10px 15px;
        border-radius: 5px;
        border-left: 5px solid #1890ff;
        margin-top: 20px;
        margin-bottom: 15px;
        font-size: 1.2em;
        font-weight: 500;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #17a2b8;
        margin-bottom: 15px;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        margin-bottom: 15px;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
        margin-bottom: 15px;
    }
    div.stButton > button {
        background-color: #4e73df;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: 500;
        border: none;
        transition: background-color 0.3s;
    }
    div.stButton > button:hover {
        background-color: #2e59d9;
    }
    div.stDownloadButton > button {
        background-color: #1e7e34;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: 500;
        border: none;
        transition: background-color 0.3s;
    }
    div.stDownloadButton > button:hover {
        background-color: #218838;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
# st.sidebar.title("📊 GTD File Processor")
st.markdown("""
<div class="page-main-header">
    <h1 style="font-size: 2.3em; margin-bottom: 0px;">
        <span style="margin-right: 10px;">📂</span> GTD File Processor
    </h1>
    <p>
        Convert, analyze and visualize GTD file data
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-container">
    <p>This application allows you to process one or more GTD files and convert them to Excel and JSON formats.
    The processed files will be saved in the project's <code>temp_data</code> folder.</p>
    <details>
            <summary style="cursor: pointer; background-color: rgb(30, 136, 229); color: white; padding: 4px 10px; border-radius: 15px; font-size: 0.9em; margin-right: 10px;">
            Features: (click to expand)
            </summary>
            <div style="margin-top: 15px; margin-bottom: 5px;"><strong>Features:</strong></div>
        <ul style="margin-top: 0px; padding-left: 20px;">
            <li>Upload one or multiple GTD files</li>
            <li>Automatic data processing</li>
            <li>Export to Excel and JSON</li>
            <li>View detected channels and metadata</li>
        </ul>
    </details>
</div>
""", unsafe_allow_html=True)

# 

# Function to process GTD files
def process_gtd_files(uploaded_files):
    print("Processing GTD files...")
    print(uploaded_files)
    # Create a GTD processor
    processor = GTDProcessor()
    
    # If there are no files, return None
    if not uploaded_files:
        return None
    
    # Process uploaded files
    else:
        temp_filepaths = []
        
        # Save files in the temporary directory
        for uploaded_file in uploaded_files:
            # Create the complete path for the temporary file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            temp_dir = os.path.join(base_dir, "temp_data")
            
            # Create directory if it doesn't exist
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            temp_filepath = os.path.join(temp_dir, uploaded_file.name)
            
            # Save the file temporarily
            with open(temp_filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Add the path to the list
            temp_filepaths.append(temp_filepath)
        
        # Process the temporary files
        for filepath in temp_filepaths:
            try:
                processor.process_file(filepath)
                st.success(f"File {os.path.basename(filepath)} processed successfully.")
            except Exception as e:
                st.error(f"Error processing file {os.path.basename(filepath)}: {str(e)}")
    
    return processor

# Function to save results
def save_results(processor, base_filename):
    if not processor:
        return None, None
    
    # Base directory of the project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Directory to save the processed files
    output_dir = os.path.join(base_dir, "temp_data")
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
    
    # Define complete paths for the output files
    excel_filepath = os.path.join(output_dir, f"{base_filename}_{timestamp}.xlsx")
    json_filepath = os.path.join(output_dir, f"{base_filename}_{timestamp}.json")
      # Export to Excel and JSON
    try:
        processor.export_to_excel(excel_filepath)
        processor.export_to_json(json_filepath)
        
        # Return the paths of generated files
        return excel_filepath, json_filepath
    except Exception as e:
        st.error(f"Error exporting results: {str(e)}")
        return None, None

# Function to save channels to channel.json file
def save_channels_to_database(processor):
    if not processor:
        return None
    
    # Base directory of the project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Database directory
    database_dir = os.path.join(base_dir, "database")
    
    # Create the database directory if it doesn't exist
    if not os.path.exists(database_dir):
        os.makedirs(database_dir)
    
    # Path to channel.json file
    channel_json_path = os.path.join(database_dir, "channel.json")
    
    # Create a dictionary with channel information
    channels_data = {
        "metadata": processor.metadata,
        "channels": {}
    }
      # Add each channel to the dictionary
    for channel_id, channel in processor.channels.items():
        channels_data["channels"][str(channel_id)] = channel.to_json()
    
    # Save the dictionary as JSON
    try:
        with open(channel_json_path, 'w', encoding='utf-8') as f:
            json.dump(channels_data, f, indent=4)
        
        return channel_json_path
    except Exception as e:
        st.error(f"Error saving channels to database: {str(e)}")
        return None

# Load a CSV/Excel file for visualization
def load_file_for_visualization(filepath):
    try:
        if filepath.endswith('.xlsx'):
            return pd.read_excel(filepath)
        elif filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading file for visualization: {str(e)}")
        return None
    return None

# Sidebar for settings
col1, col2 = st.columns([1, 3], vertical_alignment="top", border=True)
with col1:
    st.markdown("""
        <div style='background-color: #e6f2ff; padding: 10px; border-radius: 5px; border-left: 5px solid #0066cc; margin-bottom: 15px;'>
            <h3 style='color: #0066cc; margin: 0;'>⚙️ Settings</h3>
        </div>
    """, unsafe_allow_html=True)      # Base name for output files
    base_filename = st.text_input("📄 **Base filename for output files**", value="GTD_Processed_Data")
    
    # Option to save channels to database
    save_to_database = st.checkbox("💾 **Save channels to database**", value=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    


# Interface principal
with st.container():
    with col2:        # Upload files with styled header
        st.markdown("""
        <div style='background-color: #e6f2ff; padding: 10px; border-radius: 5px; border-left: 5px solid #0066cc; margin-bottom: 15px;'>
            <h3 style='color: #0066cc;; margin: 0;'>📤 Upload GTD Files</h3>
        </div>
        """, unsafe_allow_html=True)

        uploaded_files = st.file_uploader("Select one or more GTD files", 
                                         type=["gtd", "GTD"], 
                                         label_visibility='hidden',
                                         accept_multiple_files=True)

        

    # Botão para processar os arquivos
    
    if st.button("Process Files", use_container_width=True):          # Process the files
        if not uploaded_files:
            st.markdown("""
            <div class="warning-box">
                <p style="color: #856404; margin: 0;">
                    <strong>⚠️ Attention:</strong> Please select at least one GTD file to process.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Processing files..."):
                try:
                    # Process the files
                    processor = process_gtd_files(uploaded_files)
                    
                    # If processing was successful
                    if processor and processor.channels:
                        st.session_state["processor_files"] = processor
                        excel_path, json_path = save_results(processor, base_filename)
                        if excel_path and json_path:
                            st.session_state["excel_path"] = excel_path
                            st.session_state["json_path"] = json_path
                            st.markdown("""
                            <div class="success-box">
                                <p style="color: #155724; margin: 0;">
                                    <strong>✅ Success:</strong> Files processed successfully!
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error("Error saving processed files.")
                    else:
                        st.error("No channels were found in the processed files. Please check if the files are valid GTD files.")
                        
                except Exception as e:
                    st.error(f"Error processing files: {str(e)}")
                    st.info("Please check if the uploaded files are valid GTD files from Yokogawa equipment.")

    if st.session_state.get("processor_files"):
        processor = st.session_state["processor_files"]
        # Display processor information
        # st.write("Processor:", processor)
        # Save the results
        # excel_path, json_path = save_results(processor, base_filename)
        excel_path = st.session_state.get("excel_path")
        json_path = st.session_state.get("json_path")
        # If results were saved successfully
        if excel_path and json_path:
            st.success(f"Files processed successfully!")
              # Create links for downloading files
            excel_filename = os.path.basename(excel_path)
            json_filename = os.path.basename(json_path)
            c1, c2 = st.columns(2)
            # Read files to create download links
            with c1:
                try:
                    with open(excel_path, 'rb') as excel_file:
                        st.download_button(
                            label="Export - Excel",
                            data=excel_file,
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error reading Excel file: {str(e)}")
            with c2:
                try:
                    with open(json_path, 'rb') as json_file:
                        st.download_button(
                            label="Export - JSON",
                            data=json_file,
                            file_name=json_filename,
                            mime="application/json",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error reading JSON file: {str(e)}")          # If the option to save to database is checked
            if save_to_database:
                channel_json_path = save_channels_to_database(processor)
                if channel_json_path:
                    st.success(f"Channels saved to database: {os.path.basename(channel_json_path)}")
        
        # Display channel information
        st.header("Processed Channels")
        if processor.channels:
            # Create a DataFrame to display channel information
            channel_info = []
            for channel_id, channel in processor.channels.items():
                # Ensure channel ID is converted to string to avoid type issues
                channel_info.append({
                    'Channel ID': str(channel.channel_id),  # Explicitly convert to string
                    'Unit': channel.unit,
                    'Samples': len(channel.timestamps),
                    'First Sample': channel.timestamps[0] if channel.timestamps else None,
                    'Last Sample': channel.timestamps[-1] if channel.timestamps else None
                })
            # Create DataFrame outside the loop to avoid recreating it on each iteration
            channel_df = pd.DataFrame(channel_info)
            st.dataframe(channel_df)
        else:
            st.warning("No channels were found in the processed files.")
          # Display metadata
        if processor.metadata:
            st.header("Metadata")
            st.json(processor.metadata)
        
        # If Excel files were generated, offer visualization
        if excel_path:
            st.header("Data Visualization")
            
            # Load the Excel file
            df = load_file_for_visualization(excel_path)
            if df is not None and isinstance(df, pd.DataFrame):                # Display the first rows of the DataFrame
                st.subheader("First rows of data")
                st.dataframe(df.head())
                # If there are many columns, offer a selection
                if len(df.columns) > 5:
                    selected_columns = st.multiselect(
                        "Select columns to visualize",
                        options=df.columns.tolist(),
                        default=df.columns.tolist()[9:17]
                    )
                    
                    if selected_columns:
                        st.dataframe(df[selected_columns])
                        
                        # Enhanced Chart Visualization Section
                        st.header("📊 Advanced Chart Visualization")
                        
                        # Prepare data for plotting
                        plot_columns = selected_columns.copy()
                        if 'Timestamp' not in plot_columns and 'Timestamp' in df.columns:
                            plot_columns = ['Timestamp'] + plot_columns
                        
                        # Enhanced data filtering with scaling options
                        filtered_plot_columns = []
                        scaling_info = {}
                        
                        for col in plot_columns:
                            if col == 'Timestamp':
                                filtered_plot_columns.append(col)
                                continue
                            
                            # Check column statistics
                            col_data = df[col].dropna()
                            if len(col_data) == 0:
                                st.warning(f"Column '{col}' has no valid data, excluding from chart")
                                continue
                                
                            col_max = col_data.max()
                            col_min = col_data.min()
                            col_range = col_max - col_min
                            col_mean = col_data.mean()
                            col_std = col_data.std()
                            
                            # # Smart scaling detection
                            # if abs(col_max) > 1e6 or abs(col_min) > 1e6:
                            #     scaling_info[col] = {
                            #         'scale_factor': 1e6,
                            #         'scale_name': 'Million',
                            #         'original_unit': 'Original'
                            #     }
                            #     st.info(f"Column '{col}' scaled by 1M for better visualization")
                            # elif abs(col_max) > 1e3 or abs(col_min) > 1e3:
                            #     scaling_info[col] = {
                            #         'scale_factor': 1e3,
                            #         'scale_name': 'Thousand',
                            #         'original_unit': 'Original'
                            #     }
                            #     st.info(f"Column '{col}' scaled by 1K for better visualization")
                            # else:
                            #     scaling_info[col] = {
                            #         'scale_factor': 1,
                            #         'scale_name': '',
                            #         'original_unit': 'Original'
                            #     }
                            # st.write(f"Column '{col}': Max={col_max:.3f}, Min={col_min:.3f}, Mean={col_mean:.3f}, Std Dev={col_std:.3f}, type={df[col].dtype}")
                            if col_max > 3000 or col_min < -200:
                                st.info(f"Column '{col}' has extreme values and excluding it from chart for better visualization")
                                continue
                            filtered_plot_columns.append(col)
                        
                        plot_columns = filtered_plot_columns
                        
                        if 'Timestamp' in plot_columns and len(plot_columns) > 1:
                            # Create the plot DataFrame with scaling
                            plot_df = df[plot_columns].copy()
                            
                            # # Apply scaling
                            # for col in plot_columns:
                            #     if col != 'Timestamp' and col in scaling_info:
                            #         plot_df[col] = plot_df[col] / scaling_info[col]['scale_factor']                            # Chart customization options
                            with st.expander("🎛️ Chart Options", expanded=True):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    chart_type = st.segmented_control(
                                        "Chart Type",
                                        ["Line Chart", "Scatter Plot"],
                                        default="Line Chart"
                                    )
                                    
                                with col2:
                                    # Data sampling options
                                    df_len = len(df)
                                    max_points = df_len
                                    
                                
                                # Set default values for removed options
                                resample_method = "Every Nth Point"
                                chart_height = 600
                                color_scheme = "Default"
                                show_grid = True
                                show_statistics = False
                            
                            # Apply data sampling if needed
                            if max_points < len(plot_df):
                                n_rows = len(plot_df)
                                
                                if resample_method == "Every Nth Point":
                                    sample_every = max(1, n_rows // max_points)
                                    plot_df_sampled = plot_df.iloc[::sample_every].copy()
                                else:
                                    sample_every = max(1, n_rows // max_points)
                                    
                                    if resample_method == "Average":
                                        plot_df_sampled = plot_df.groupby(plot_df.index // sample_every).mean().reset_index(drop=True)
                                    elif resample_method == "Minimum":
                                        plot_df_sampled = plot_df.groupby(plot_df.index // sample_every).min().reset_index(drop=True)
                                    else:  # Maximum
                                        plot_df_sampled = plot_df.groupby(plot_df.index // sample_every).max().reset_index(drop=True)
                                    
                                    # Restore Timestamp column for grouped data
                                    if 'Timestamp' in plot_df.columns:
                                        timestamps_grouped = df['Timestamp'].groupby(df.index // sample_every)
                                        if resample_method == "Average":
                                            plot_df_sampled['Timestamp'] = timestamps_grouped.first().values
                                        elif resample_method == "Minimum":
                                            plot_df_sampled['Timestamp'] = timestamps_grouped.first().values
                                        else:
                                            plot_df_sampled['Timestamp'] = timestamps_grouped.last().values
                            else:
                                plot_df_sampled = plot_df.copy()
                            
                            # Create the interactive chart using Plotly
                            try:
                                # Define color palette
                                color_palettes = {
                                    "Default": px.colors.qualitative.Plotly,
                                    "Viridis": px.colors.sequential.Viridis,
                                    "Plasma": px.colors.sequential.Plasma,
                                    "Set3": px.colors.qualitative.Set3,
                                    "Dark24": px.colors.qualitative.Dark24
                                }
                                
                                colors = color_palettes.get(color_scheme, px.colors.qualitative.Plotly)
                                
                                # Create the main chart
                                fig = go.Figure()
                                
                                data_columns = [col for col in plot_columns if col != 'Timestamp']
                                
                                for i, col in enumerate(data_columns):
                                    color = colors[i % len(colors)]
                                      # Prepare hover text with scaling info
                                    hover_text = f"<b>{col}</b><br>"
                                    if col in scaling_info and scaling_info[col]['scale_factor'] != 1:
                                        hover_text += f"Scaled Value: %{{y:.3f}} ({scaling_info[col]['scale_name']})<br>"
                                        hover_text += f"Original Value: %{{customdata:.3f}}<br>"
                                        customdata = plot_df_sampled[col] * scaling_info[col]['scale_factor']
                                    else:
                                        hover_text += f"Value: %{{y:.3f}}<br>"
                                        customdata = None
                                    
                                    hover_text += f"Time: %{{x}}<br>"
                                    
                                    if chart_type == "Line Chart":
                                        fig.add_trace(go.Scatter(
                                            x=plot_df_sampled['Timestamp'],
                                            y=plot_df_sampled[col],
                                            mode='lines',
                                            name=col,
                                            line=dict(color=color, width=2),
                                            customdata=customdata,
                                            hovertemplate=hover_text + "<extra></extra>"
                                        ))
                                    
                                    elif chart_type == "Scatter Plot":
                                        fig.add_trace(go.Scatter(
                                            x=plot_df_sampled['Timestamp'],
                                            y=plot_df_sampled[col],
                                            mode='markers',
                                            name=col,
                                            marker=dict(color=color, size=4, opacity=0.7),
                                            customdata=customdata,
                                            hovertemplate=hover_text + "<extra></extra>" ))
                                  # Update layout
                                fig.update_layout(
                                    title="GTD Data Visualization",
                                    xaxis_title="Timestamp",
                                    yaxis_title="Values",
                                    height=chart_height,
                                    showlegend=True
                                )
                                
                                # Display the chart
                                st.plotly_chart(fig, use_container_width=True)

                                # Export options
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("📥 Export Chart as HTML",use_container_width=True):
                                        html_str = fig.to_html(include_plotlyjs='cdn')
                                        st.download_button(
                                            label="Download HTML",
                                            data=html_str,
                                            file_name=f"gtd_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                            mime="text/html",
                                            use_container_width=True
                                        )
                                
                                
                                
                            except Exception as e:
                                st.error(f"Error creating interactive chart: {str(e)}")
                                st.info("Falling back to Streamlit line chart...")
                                  # Fallback to Streamlit chart
                                try:
                                    chart_data = plot_df_sampled.set_index('Timestamp')
                                    st.line_chart(chart_data, height=chart_height)
                                except Exception as fallback_error:
                                    st.error(f"Chart creation failed: {str(fallback_error)}")
                        else:
                            st.warning("Please ensure 'Timestamp' column is included and at least one data column is selected for visualization.")
                else:
                    st.dataframe(df)
                    try:
                        # Simplified Data Chart for All Columns
                        st.header("📊 Complete Dataset Visualization")

                        if 'Timestamp' in df.columns:
                            # Filter to use only numeric columns
                            numeric_cols = df.select_dtypes(include=['float64', 'int64', 'float32', 'int32']).columns.tolist()
                            if 'Timestamp' in numeric_cols:
                                numeric_cols.remove('Timestamp')

                            if numeric_cols:
                                # Simple chart options
                                with st.expander("🎛️ Chart Options", expanded=True):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        all_chart_type = st.selectbox(
                                            "Chart Type",
                                            ["Line Chart", "Scatter Plot"],
                                            index=0
                                        )

                                    with col2:
                                        # Simplified column selection
                                        num_cols_len = len(numeric_cols)
                                        
                                        max_cols_display = num_cols_len
                                        

                                # Select columns to display
                                display_cols = numeric_cols[:max_cols_display]

                                # Create simple chart
                                try:
                                    plot_data = df[['Timestamp'] + display_cols].copy()

                                    # Create Plotly figure
                                    fig_all = go.Figure()

                                    colors = px.colors.qualitative.Set3

                                    for i, col in enumerate(display_cols):
                                        if all_chart_type == "Line Chart":
                                            fig_all.add_trace(go.Scatter(
                                                x=plot_data['Timestamp'],
                                                y=plot_data[col],
                                                mode='lines',
                                                name=col,
                                                line=dict(color=colors[i % len(colors)], width=1.5),
                                                hovertemplate=f"<b>{col}</b><br>Value: %{{y:.3f}}<br>Time: %{{x}}<br><extra></extra>"
                                            ))
                                        else:  # Scatter Plot
                                            fig_all.add_trace(go.Scatter(
                                                x=plot_data['Timestamp'],
                                                y=plot_data[col],
                                                mode='markers',
                                                name=col,
                                                marker=dict(color=colors[i % len(colors)], size=3, opacity=0.7),
                                                hovertemplate=f"<b>{col}</b><br>Value: %{{y:.3f}}<br>Time: %{{x}}<br><extra></extra>"
                                            ))

                                    fig_all.update_layout(
                                        title="Complete Dataset Overview",
                                        xaxis_title="Timestamp",
                                        yaxis_title="Values",
                                        height=600,
                                        showlegend=True
                                    )

                                    st.plotly_chart(fig_all, use_container_width=True)

                                except Exception as e:
                                    st.error(f"Error creating chart: {str(e)}")
                                    # Fallback to streamlit chart
                                    try:
                                        st.line_chart(df.set_index('Timestamp')[display_cols], height=600)
                                    except Exception as fallback_error:
                                        st.error(f"Fallback chart creation failed: {str(fallback_error)}")

                            else:
                                st.warning("No numeric columns were found to plot in the chart.")
                        else:
                            st.warning("'Timestamp' column not found in the data.")
                    except:
                        pass

# Footer
st.markdown("---")
