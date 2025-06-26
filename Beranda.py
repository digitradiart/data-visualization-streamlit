import streamlit as st
import subprocess
import sys

# Page configuration
st.set_page_config(
    page_title="Indonesia Microclimate Network",
    page_icon="🌡️",
    layout="wide"
)

def main():
    # Header
    st.title("🌡️ Indonesia Microclimate Monitoring System")
    st.markdown("---")
    
    st.markdown("""
    ## Welcome to the Indonesia Microclimate Network
    
    Choose your dashboard to explore the microclimate monitoring data:
    """)
    
    # Dashboard selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 **Data Analysis Dashboard**
        
        Analyze detailed microclimate measurements:
        - Multi-height data (4m, 7m, 10m)
        - Temperature, humidity, wind analysis
        - Time series visualizations
        - Statistical comparisons
        """)
        
        if st.button("📊 Open Data Analysis Dashboard", use_container_width=True, type="primary"):
            st.info("🚀 **Starting Data Analysis Dashboard...**")
            st.code("streamlit run dashboard.py", language="bash")
            st.markdown("**Or run:** `python run_dashboard.py`")
    
    with col2:
        st.markdown("""
        ### 🗺️ **Spatial Network Dashboard**
        
        Explore the monitoring network across Indonesia:
        - Interactive map of all sites
        - Site metadata and locations
        - Network coverage statistics
        - Equipment distribution
        """)
        
        if st.button("🗺️ Open Spatial Dashboard", use_container_width=True, type="primary"):
            st.info("🚀 **Starting Spatial Dashboard...**")
            st.code("streamlit run spatial_dashboard.py", language="bash")
            st.markdown("**Or run:** `python run_spatial_dashboard.py`")
    
    st.markdown("---")
    
    # Quick info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🗺️ Total Sites", "27", help="Monitoring stations across Indonesia")
    
    with col2:
        st.metric("📊 Parameters", "4", help="Temperature, Humidity, Wind Speed, Wind Direction")
    
    with col3:
        st.metric("🏗️ Heights", "3", help="4m, 7m, and 10m measurements")
    
    st.markdown("---")
    
    # Instructions
    st.subheader("📋 How to Use")
    
    st.markdown("""
    1. **Choose a dashboard** using the buttons above
    2. **Follow the instructions** to open the selected dashboard
    3. **Each dashboard runs independently** in a separate Streamlit session
    
    **Note:** You can also run the dashboards directly from command line:
    - `streamlit run dashboard.py` - for data analysis
    - `streamlit run spatial_dashboard.py` - for spatial overview
    """)

if __name__ == "__main__":
    main()
