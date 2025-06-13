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
project_root = Path(__file__).parent.parent
css_path = os.path.join(project_root, "static", "css", "material_styles.css")
load_css(css_path)

# Note: Page configuration is handled in main.py to avoid conflicts

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
    All processing is done in memory for better security and performance.</p>
    <details>
            <summary style="cursor: pointer; background-color: rgb(30, 136, 229); color: white; padding: 4px 10px; border-radius: 15px; font-size: 0.9em; margin-right: 10px;">
            Features: (click to expand)
            </summary>
            <div style="margin-top: 15px; margin-bottom: 5px;"><strong>Features:</strong></div>
        <ul style="margin-top: 0px; padding-left: 20px;">
            <li>Upload one or multiple GTD files</li>
            <li>Automatic data processing in memory</li>
            <li>Export to Excel and JSON formats</li>
            <li>Interactive data visualization</li>
            <li>View detected channels and metadata</li>
            <li>Multi-user support without conflicts</li>
        </ul>
    </details>
</div>
""", unsafe_allow_html=True)

# 

# Function to process GTD files (using session state instead of file system)
def process_gtd_files(uploaded_files):
    """Process GTD files and store results in session state to avoid conflicts between users"""
    print("Processing GTD files...")
    # Create a GTD processor
    processor = GTDProcessor()
    
    # If there are no files, return None
    if not uploaded_files:
        return None
      # Process uploaded files directly from memory
    for uploaded_file in uploaded_files:
        temp_filepath = None
        try:
            # Create temporary file in memory with proper context management
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.gtd') as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_filepath = temp_file.name
            
            # Process the temporary file
            processor.process_file(temp_filepath)
            st.success(f"File {uploaded_file.name} processed successfully.")
            
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {str(e)}")
        finally:
            # Clean up temporary file with error handling
            if temp_filepath and os.path.exists(temp_filepath):
                try:
                    os.unlink(temp_filepath)
                except PermissionError:
                    # If file is still locked, try again after a brief delay
                    import time
                    time.sleep(0.1)
                    try:
                        os.unlink(temp_filepath)
                    except:
                        pass  # If still can't delete, continue
    
    return processor

# Function to generate results in memory (no file system storage)
def generate_results_in_memory(processor, base_filename):
    """Generate Excel and JSON data in memory without saving to file system"""
    if not processor:
        return None, None
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
    
    try:
        # Create Excel in memory using BytesIO
        from io import BytesIO
        
        excel_filename = f"{base_filename}_{timestamp}.xlsx"
        
        # Create temporary file with proper context management
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xlsx') as temp_excel:
            temp_path = temp_excel.name
        
        try:
            # Export to temporary file
            processor.export_to_excel(temp_path)
            
            # Read Excel data to memory
            with open(temp_path, 'rb') as f:
                excel_data = f.read()
                
        finally:
            # Ensure cleanup even if error occurs
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except PermissionError:
                    # If file is still locked, try again after a brief delay
                    import time
                    time.sleep(0.1)
                    try:
                        os.unlink(temp_path)
                    except:
                        pass  # If still can't delete, continue
        
        # Create JSON in memory
        json_filename = f"{base_filename}_{timestamp}.json"
        json_data = {
            "metadata": processor.metadata,
            "channels": {}
        }
        
        # Add each channel to the JSON
        for channel_id, channel in processor.channels.items():
            json_data["channels"][str(channel_id)] = channel.to_json()
        
        json_string = json.dumps(json_data, indent=4)
        json_bytes = json_string.encode('utf-8')
        
        return (excel_data, excel_filename), (json_bytes, json_filename)
        
    except Exception as e:
        st.error(f"Error generating results: {str(e)}")
        return None, None

# Function to create channel data for download (in memory)
def generate_channel_data(processor):
    """Generate channel data in JSON format for download"""
    if not processor:
        return None, None
    
    # Create a dictionary with channel information
    channels_data = {
        "metadata": processor.metadata,
        "channels": {}
    }
    
    # Add each channel to the dictionary
    for channel_id, channel in processor.channels.items():
        channels_data["channels"][str(channel_id)] = channel.to_json()
    
    # Convert to JSON string
    json_string = json.dumps(channels_data, indent=4)
    json_bytes = json_string.encode('utf-8')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
    filename = f"channels_{timestamp}.json"
    
    return json_bytes, filename

# Function to load data from memory for visualization
def load_data_for_visualization(processor):
    """Load processed data directly from processor object for visualization"""
    if not processor or not processor.channels:
        return None
    
    # Create DataFrame from processor data
    df_data = {}
    
    # Get the channel with most samples to use as base for timestamps
    max_samples = 0
    base_channel = None
    for channel in processor.channels.values():
        if len(channel.timestamps) > max_samples:
            max_samples = len(channel.timestamps)
            base_channel = channel
    
    if base_channel is None:
        return None
    
    # Add timestamp column
    df_data['Timestamp'] = base_channel.timestamps
    
    # Add data from all channels
    for channel_id, channel in processor.channels.items():
        if len(channel.timestamps) == max_samples:  # Only use channels with same number of samples
            df_data[f"Ch{channel_id}_Min_{channel.unit}"] = channel.samples_min
            df_data[f"Ch{channel_id}_Max_{channel.unit}"] = channel.samples_max
    
    return pd.DataFrame(df_data)

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
if st.button("Process Files", use_container_width=True):
    # Process the files
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
                        
                        # Generate results in memory
                        excel_result, json_result = generate_results_in_memory(processor, base_filename)
                        if excel_result and json_result:
                            st.session_state["excel_data"] = excel_result
                            st.session_state["json_data"] = json_result
                            st.markdown("""
                            <div class="success-box">
                                <p style="color: #155724; margin: 0;">
                                    <strong>✅ Success:</strong> Files processed successfully!
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error("Error generating processed files.")
                    else:
                        st.error("No channels were found in the processed files. Please check if the files are valid GTD files.")
                        
            except Exception as e:
                st.error(f"Error processing files: {str(e)}")
                st.info("Please check if the uploaded files are valid GTD files from Yokogawa equipment.")

if st.session_state.get("processor_files"):
    processor = st.session_state["processor_files"]
    # Get data from session state
    excel_data = st.session_state.get("excel_data")
    json_data = st.session_state.get("json_data")
    # If results were generated successfully
    if excel_data and json_data:
        st.success(f"Files processed successfully!")
        # Create download buttons
        c1, c2, c3 = st.columns(3)
        # Excel download
        with c1:
            st.download_button(
                label="📊 Export - Excel",
                data=excel_data[0],
                file_name=excel_data[1],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        # JSON download
        with c2:
            st.download_button(
                label="📄 Export - JSON",
                data=json_data[0],
                file_name=json_data[1],
                mime="application/json",
                use_container_width=True
            )
        # Channel data download (if option is checked)
        if save_to_database:
            with c3:
                channel_data, channel_filename = generate_channel_data(processor)
                if channel_data:
                    st.download_button(
                        label="🗂️ Export - Channels",
                        data=channel_data,
                        file_name=channel_filename,
                        mime="application/json",
                        use_container_width=True
                    )        # Display channel information
        st.markdown("""
                            <div class="ghfm-info-card slide-in">
                                <h4 class="ghfm-info-title">📋 Processed Channels</h4>
                            </div>
                        """, unsafe_allow_html=True)
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
          # Display metadata        if processor.metadata:
            st.markdown("""
                            <div class="ghfm-info-card slide-in">
                                <h4 class="ghfm-info-title">📄 Metadata</h4>
                            </div>
                        """, unsafe_allow_html=True)
            st.json(processor.metadata)          # Data visualization section
        st.markdown("""
                            <div class="ghfm-info-card slide-in">
                                <h4 class="ghfm-info-title">📊 Data Visualization</h4>
                            </div>
                        """, unsafe_allow_html=True)
        # Load data directly from processor
        df = load_data_for_visualization(processor)
        if df is not None and isinstance(df, pd.DataFrame):# Display the first rows of the DataFrame
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
                        st.markdown("""
                            <div class="ghfm-info-card slide-in">
                                <h4 class="ghfm-info-title">📊 Advanced Chart Visualization </h4>
                            </div>
                        """, unsafe_allow_html=True)
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
                    try:                        # Simplified Data Chart for All Columns
                        st.markdown("""
                            <div class="ghfm-info-card slide-in">
                                <h4 class="ghfm-info-title">📊 Complete Dataset Visualization</h4>
                            </div>
                        """, unsafe_allow_html=True)
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
