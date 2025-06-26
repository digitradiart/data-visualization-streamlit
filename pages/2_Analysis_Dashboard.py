import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Microclimate Analysis Dashboard",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .height-section {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .height-4m { border-left-color: #ff7f0e; }
    .height-7m { border-left-color: #2ca02c; }
    .height-10m { border-left-color: #d62728; }
    
    .stMetric {
        background-color: white;
        padding: 0.5rem;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


def load_microclimate_data():
    """Upload and analyze microclimate CSV file"""
    uploaded_file = st.file_uploader("📁 Upload Microclimate CSV File", type="csv")

    if uploaded_file is not None:
        try:
            # Load CSV
            df = pd.read_csv(uploaded_file)

            # Try parsing date_time column
            df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce', infer_datetime_format=True)

            # Drop rows with missing datetime
            df = df.dropna(subset=['date_time'])

            # Convert all other columns (except id_logger/date_time) to numeric
            numeric_columns = [col for col in df.columns if col not in ['id_logger', 'date_time']]
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Sort and reset index
            df = df.sort_values('date_time').reset_index(drop=True)

            # Display analysis summary in the sidebar or main area
            st.success("✅ Data loaded successfully!")
            st.markdown(f"**📊 Shape:** {df.shape}")
            st.markdown(f"**📅 Date Range:** {df['date_time'].min()} to {df['date_time'].max()}")
            st.markdown(f"**📋 Columns:** {', '.join(df.columns)}")

            return df

        except Exception as e:
            st.error(f"❌ Failed to process file: {str(e)}")
            return None
    else:
        st.info("📂 Please upload a CSV file to begin.")
        return None


def create_temperature_comparison_chart(df):
    """Create temperature comparison chart for all heights"""
    fig = go.Figure()
    
    heights = ['4', '7', '10']
    colors = ['#ff7f0e', '#2ca02c', '#d62728']
    
    for i, height in enumerate(heights):
        # Add average temperature line
        fig.add_trace(go.Scatter(
            x=df['date_time'],
            y=df[f'tt{height}_avg'],
            mode='lines',
            name=f'{height}m (Avg)',
            line=dict(color=colors[i], width=2)
        ))
        
        # Add min-max range
        fig.add_trace(go.Scatter(
            x=df['date_time'],
            y=df[f'tt{height}_max'],
            mode='lines',
            line=dict(color=colors[i], width=0),
            showlegend=False,
            hovertemplate=f'{height}m Max: %{{y:.1f}}°C<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date_time'],
            y=df[f'tt{height}_min'],
            mode='lines',
            fill='tonexty',
            fillcolor=f'rgba({int(colors[i][1:3], 16)}, {int(colors[i][3:5], 16)}, {int(colors[i][5:7], 16)}, 0.2)',
            line=dict(color=colors[i], width=0),
            name=f'{height}m (Range)',
            hovertemplate=f'{height}m Min: %{{y:.1f}}°C<extra></extra>'
        ))
    
    fig.update_layout(
        title="Temperature Comparison by Height (°C)",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_humidity_comparison_chart(df):
    """Create humidity comparison chart for all heights"""
    fig = go.Figure()
    
    heights = ['4', '7', '10']
    colors = ['#ff7f0e', '#2ca02c', '#d62728']
    
    for i, height in enumerate(heights):
        fig.add_trace(go.Scatter(
            x=df['date_time'],
            y=df[f'rh{height}_avg'],
            mode='lines',
            name=f'{height}m (Avg)',
            line=dict(color=colors[i], width=2)
        ))
        
        # Add min-max range
        fig.add_trace(go.Scatter(
            x=df['date_time'],
            y=df[f'rh{height}_max'],
            mode='lines',
            line=dict(color=colors[i], width=0),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date_time'],
            y=df[f'rh{height}_min'],
            mode='lines',
            fill='tonexty',
            fillcolor=f'rgba({int(colors[i][1:3], 16)}, {int(colors[i][3:5], 16)}, {int(colors[i][5:7], 16)}, 0.2)',
            line=dict(color=colors[i], width=0),
            name=f'{height}m (Range)'
        ))
    
    fig.update_layout(
        title="Humidity Comparison by Height (%)",
        xaxis_title="Time",
        yaxis_title="Relative Humidity (%)",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_wind_speed_comparison_chart(df):
    """Create wind speed comparison chart for all heights"""
    fig = go.Figure()
    
    heights = ['4', '7', '10']
    colors = ['#ff7f0e', '#2ca02c', '#d62728']
    
    for i, height in enumerate(heights):
        fig.add_trace(go.Scatter(
            x=df['date_time'],
            y=df[f'ws{height}_avg'],
            mode='lines',
            name=f'{height}m (Avg)',
            line=dict(color=colors[i], width=2)
        ))
        
        # Add max wind speed
        fig.add_trace(go.Scatter(
            x=df['date_time'],
            y=df[f'ws{height}_max'],
            mode='lines',
            name=f'{height}m (Max)',
            line=dict(color=colors[i], width=1, dash='dot')
        ))
    
    fig.update_layout(
        title="Wind Speed Comparison by Height (m/s)",
        xaxis_title="Time",
        yaxis_title="Wind Speed (m/s)",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_wind_direction_chart(df, height):
    """Create wind direction scatter plot for specific height"""
    fig = go.Figure()
    
    colors = {'4': '#ff7f0e', '7': '#2ca02c', '10': '#d62728'}
    
    fig.add_trace(go.Scatter(
        x=df['date_time'],
        y=df[f'wd{height}_avg'],
        mode='markers',
        name=f'{height}m Wind Direction',
        marker=dict(color=colors[height], size=4)
    ))
    
    # Add reference lines for cardinal directions
    fig.add_hline(y=360, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=270, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=180, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=90, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title=f"Wind Direction at {height}m Height (°)",
        xaxis_title="Time",
        yaxis_title="Wind Direction (°)",
        height=300,
        showlegend=False,
        yaxis=dict(range=[0, 360])
    )
    
    return fig

def create_vertical_profile_chart(df, parameter, param_name, unit):
    """Create vertical profile chart showing parameter variation with height"""
    latest = df.iloc[-1]
    
    heights = [4, 7, 10]
    min_vals = [latest[f'{parameter}{h}_min'] for h in heights]
    avg_vals = [latest[f'{parameter}{h}_avg'] for h in heights]
    max_vals = [latest[f'{parameter}{h}_max'] for h in heights]
    
    fig = go.Figure()
    
    # Add min, avg, max lines
    fig.add_trace(go.Scatter(
        x=min_vals, y=heights,
        mode='lines+markers',
        name='Minimum',
        line=dict(color='blue', dash='dash'),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=avg_vals, y=heights,
        mode='lines+markers',
        name='Average',
        line=dict(color='red', width=3),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=max_vals, y=heights,
        mode='lines+markers',
        name='Maximum',
        line=dict(color='green', dash='dash'),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f"Vertical Profile - {param_name}",
        xaxis_title=f"{param_name} ({unit})",
        yaxis_title="Height (m)",
        height=400,
        yaxis=dict(tickvals=[4, 7, 10])
    )
    
    return fig

def main():
    # Load data
    df = load_microclimate_data()
    
    if df is None:
        st.error("Failed to load microclimate data. Please check the file.")
        return
    
    # Get latest readings
    latest = df.iloc[-1]
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🌡️ Microclimate Analysis Dashboard</h1>
        <p>📊 Multi-Height Weather Station Data Analysis</p>
        <p style="text-align: right; margin: 0;">
            Last Update: {latest['date_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>
            Logger ID: {latest['id_logger']} | Data Points: {len(df)} | Interval: 10 minutes
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Current readings by height
    st.subheader("📊 Current Readings by Height")
    
    heights = ['4', '7', '10']
    height_colors = ['height-4m', 'height-7m', 'height-10m']
    
    for i, height in enumerate(heights):
        st.markdown(f'<div class="height-section {height_colors[i]}">', unsafe_allow_html=True)
        st.markdown(f"### 🏗️ {height}m Height")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            temp_now = latest[f'tt{height}_now']
            temp_avg = latest[f'tt{height}_avg']
            temp_range = f"{latest[f'tt{height}_min']:.1f} - {latest[f'tt{height}_max']:.1f}"
            st.metric(
                "Temperature", 
                f"{temp_now:.1f}°C",
                delta=f"{temp_now - temp_avg:.1f}°C from avg",
                help=f"Range: {temp_range}°C"
            )
        
        with col2:
            rh_now = latest[f'rh{height}_now']
            rh_avg = latest[f'rh{height}_avg']
            rh_range = f"{latest[f'rh{height}_min']:.1f} - {latest[f'rh{height}_max']:.1f}"
            st.metric(
                "Humidity", 
                f"{rh_now:.1f}%",
                delta=f"{rh_now - rh_avg:.1f}% from avg",
                help=f"Range: {rh_range}%"
            )
        
        with col3:
            ws_now = latest[f'ws{height}_now']
            ws_avg = latest[f'ws{height}_avg']
            ws_max = latest[f'ws{height}_max']
            st.metric(
                "Wind Speed", 
                f"{ws_now:.2f} m/s",
                delta=f"{ws_now - ws_avg:.2f} m/s from avg",
                help=f"Max: {ws_max:.2f} m/s"
            )
        
        with col4:
            wd_now = latest[f'wd{height}_now']
            # Convert to cardinal direction
            directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            cardinal = directions[int((wd_now + 22.5) // 45) % 8]
            st.metric(
                "Wind Direction", 
                f"{cardinal}",
                help=f"{wd_now:.1f}°"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Time series comparisons
    st.subheader("📈 Time Series Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Temperature", "💧 Humidity", "💨 Wind Speed", "🧭 Wind Direction"])
    
    with tab1:
        st.plotly_chart(create_temperature_comparison_chart(df), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_vertical_profile_chart(df, 'tt', 'Temperature', '°C'), use_container_width=True)
        with col2:
            # Temperature statistics table
            st.subheader("Temperature Statistics")
            temp_stats = []
            for height in heights:
                temp_stats.append({
                    'Height': f'{height}m',
                    'Current': f"{latest[f'tt{height}_now']:.1f}°C",
                    'Average': f"{latest[f'tt{height}_avg']:.1f}°C",
                    'Min': f"{latest[f'tt{height}_min']:.1f}°C",
                    'Max': f"{latest[f'tt{height}_max']:.1f}°C"
                })
            st.dataframe(pd.DataFrame(temp_stats), use_container_width=True)
    
    with tab2:
        st.plotly_chart(create_humidity_comparison_chart(df), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_vertical_profile_chart(df, 'rh', 'Humidity', '%'), use_container_width=True)
        with col2:
            # Humidity statistics table
            st.subheader("Humidity Statistics")
            rh_stats = []
            for height in heights:
                rh_stats.append({
                    'Height': f'{height}m',
                    'Current': f"{latest[f'rh{height}_now']:.1f}%",
                    'Average': f"{latest[f'rh{height}_avg']:.1f}%",
                    'Min': f"{latest[f'rh{height}_min']:.1f}%",
                    'Max': f"{latest[f'rh{height}_max']:.1f}%"
                })
            st.dataframe(pd.DataFrame(rh_stats), use_container_width=True)
    
    with tab3:
        st.plotly_chart(create_wind_speed_comparison_chart(df), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_vertical_profile_chart(df, 'ws', 'Wind Speed', 'm/s'), use_container_width=True)
        with col2:
            # Wind speed statistics table
            st.subheader("Wind Speed Statistics")
            ws_stats = []
            for height in heights:
                ws_stats.append({
                    'Height': f'{height}m',
                    'Current': f"{latest[f'ws{height}_now']:.2f} m/s",
                    'Average': f"{latest[f'ws{height}_avg']:.2f} m/s",
                    'Min': f"{latest[f'ws{height}_min']:.2f} m/s",
                    'Max': f"{latest[f'ws{height}_max']:.2f} m/s",
                    'Sum': f"{latest[f'sum_ws{height}']:.1f}"
                })
            st.dataframe(pd.DataFrame(ws_stats), use_container_width=True)
    
    with tab4:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.plotly_chart(create_wind_direction_chart(df, '4'), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_wind_direction_chart(df, '7'), use_container_width=True)
        
        with col3:
            st.plotly_chart(create_wind_direction_chart(df, '10'), use_container_width=True)
    
    # Data summary
    st.markdown("---")
    st.subheader("📋 Data Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Dataset Information:**
        - 📅 **Date Range:** {df['date_time'].min().strftime('%Y-%m-%d %H:%M')} to {df['date_time'].max().strftime('%Y-%m-%d %H:%M')}
        - 📊 **Total Records:** {len(df):,}
        - ⏱️ **Data Interval:** 10 minutes
        - 🏗️ **Heights Monitored:** 4m, 7m, 10m
        - 📈 **Parameters:** Temperature, Humidity, Wind Speed, Wind Direction
        """)
    
    with col2:
        # Recent data preview
        st.subheader("Recent Data (Last 5 records)")
        recent_data = df[['date_time', 'tt4_now', 'rh4_now', 'ws4_avg', 'tt7_now', 'rh7_now', 'ws7_avg', 'tt10_now', 'rh10_now', 'ws10_avg']].tail()
        st.dataframe(recent_data, use_container_width=True)
    
    # Export options
    st.markdown("---")
    st.subheader("💾 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Current Data as CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"microclimate_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Summary Statistics"):
            summary_stats = []
            for height in heights:
                for param in ['tt', 'rh', 'ws']:
                    summary_stats.append({
                        'Height': f'{height}m',
                        'Parameter': param,
                        'Current': latest[f'{param}{height}_now'],
                        'Average': latest[f'{param}{height}_avg'],
                        'Min': latest[f'{param}{height}_min'],
                        'Max': latest[f'{param}{height}_max']
                    })
            
            summary_df = pd.DataFrame(summary_stats)
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="Download Summary CSV",
                data=csv,
                file_name=f"microclimate_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

main()