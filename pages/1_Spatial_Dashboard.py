import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Indonesia Microclimate Network",
    page_icon="🗺️",
    layout="wide"
)

# --- LOAD DATA ---
@st.cache_data
def load_site_metadata():
    """Load site metadata from CSV"""
    try:
        df = pd.read_csv('metadata_site_ikro.csv')
        
        # Clean and convert data types
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df['id_site'] = pd.to_numeric(df['id_site'], errors='coerce')
        df['th_pengadaan'] = pd.to_numeric(df['th_pengadaan'], errors='coerce')
        
        # Remove rows with invalid coordinates
        df = df.dropna(subset=['latitude', 'longitude'])
        
        return df
        
    except Exception as e:
        st.error(f"Error loading site metadata: {str(e)}")
        return None

def create_indonesia_map(df, selected_site_id=50001):
    """Create interactive map of Indonesia with all microclimate sites"""
    
    # Center map on Indonesia
    center_lat = -2.5
    center_lon = 129.0
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=4.2,
        tiles='OpenStreetMap'
    )
    
    # Add different tile layers
    folium.TileLayer(
        tiles='CartoDB positron',
        attr='© OpenStreetMap contributors © CARTO'
    ).add_to(m)
    
    # Add markers for each site
    for idx, site in df.iterrows():
        # Determine marker color and size
        if int(site['id_site']) == selected_site_id:
            color = 'red'
            icon = 'star'
            size = 15
        else:
            color = 'blue'
            icon = 'info-sign'
            size = 10
        
        # Create popup content
        popup_content = f"""
        <div style="width: 300px;">
            <h4>{site['nama_site']}</h4>
            <hr>
            <b>Site ID:</b> {site['id_site']}<br>
            <b>Province:</b> {site['provinsi']}<br>
            <b>District:</b> {site['kabupaten']}<br>
            <b>Coordinates:</b> {site['latitude']:.3f}, {site['longitude']:.3f}<br>
            <b>Installation Year:</b> {site['th_pengadaan'] if pd.notna(site['th_pengadaan']) else 'N/A'}<br>
            <b>Equipment:</b> {site['merk'] if pd.notna(site['merk']) else 'N/A'}<br>
            <b>Address:</b> {site['alamat'] if pd.notna(site['alamat']) else 'N/A'}
        </div>
        """
        
        # Add marker
        folium.Marker(
            location=[site['latitude'], site['longitude']],
            popup=folium.Popup(popup_content, max_width=350),
            tooltip=f"{site['nama_site']} (ID: {site['id_site']})",
            icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def create_province_distribution_chart(df):
    """Create bar chart showing site distribution by province"""
    province_counts = df['provinsi'].value_counts()
    
    fig = px.bar(
        x=province_counts.values,
        y=province_counts.index,
        orientation='h',
        title="Microclimate Sites Distribution by Province",
        labels={'x': 'Number of Sites', 'y': 'Province'},
        color=province_counts.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def create_installation_timeline_chart(df):
    """Create timeline chart showing site installations over years"""
    df_clean = df.dropna(subset=['th_pengadaan'])
    year_counts = df_clean['th_pengadaan'].value_counts().sort_index()
    
    fig = px.bar(
        x=year_counts.index,
        y=year_counts.values,
        title="Microclimate Sites Installation Timeline",
        labels={'x': 'Installation Year', 'y': 'Number of Sites'},
        color=year_counts.values,
        color_continuous_scale='blues'
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Year",
        yaxis_title="Number of Sites Installed"
    )
    
    return fig

def create_equipment_distribution_chart(df):
    """Create pie chart showing equipment brand distribution"""
    df_clean = df.dropna(subset=['merk'])
    brand_counts = df_clean['merk'].value_counts()
    
    fig = px.pie(
        values=brand_counts.values,
        names=brand_counts.index,
        title="Equipment Brand Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(height=400)
    
    return fig

def main():
    st.title("🗺️ Indonesia Microclimate Network")
    st.markdown("---")
    
    # Load site metadata
    df = load_site_metadata()
    
    if df is None:
        st.error("Failed to load site metadata.")
        return
    
    # Sidebar for site selection only
    st.sidebar.header("🔍 Site Selection")
    
    # Site selection
    site_options = df[['id_site', 'nama_site']].copy()
    site_options['id_site_str'] = site_options['id_site'].astype(str)
    site_options['display'] = site_options['id_site_str'] + ' - ' + site_options['nama_site']

    # Find default index for site 50001
    default_index = 0
    try:
        # Get the position in the dataframe, not the pandas index
        mask = site_options['id_site'] == 50001
        if mask.any():
            default_index = mask.idxmax()  # Get the first True index
            # Convert pandas index to list position
            default_index = site_options.index.get_loc(default_index)
        else:
            default_index = 0
    except (IndexError, KeyError):
        # If site 50001 not found, use first site
        default_index = 0

    selected_site_display = st.sidebar.selectbox(
        "Select Site for Detailed Analysis:",
        options=site_options['display'].tolist(),
        index=int(default_index)  # Ensure it's a regular Python int
    )

    # Extract selected site ID right after selectbox
    selected_site_id = int(selected_site_display.split(' - ')[0])
    
    # No more province or equipment filters
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Interactive Map", "📊 Statistics", "📋 Site Directory", "🎯 Selected Site"])
    
    with tab1:
        st.subheader("🌍 Indonesia Microclimate Sites Map")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sites", len(df))
        with col2:
            st.metric("Provinces Covered", df['provinsi'].nunique())
        with col3:
            st.metric("Active Since", int(df['th_pengadaan'].min()) if df['th_pengadaan'].notna().any() else "N/A")
        
        # Create and display map
        map_obj = create_indonesia_map(df, selected_site_id)
        map_data = st_folium(map_obj, width=1200, height=600)
        
        # Map legend
        st.markdown("""
        **Map Legend:**
        - 🔴 **Red Star**: Currently selected site for detailed analysis
        - 🔵 **Blue Markers**: Other microclimate monitoring sites
        - Click on markers for detailed site information
        """)
    
    with tab2:
        st.subheader("📈 Network Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_province_distribution_chart(df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_equipment_distribution_chart(df), use_container_width=True)
        
        st.plotly_chart(create_installation_timeline_chart(df), use_container_width=True)
        
        # Summary statistics
        st.subheader("📊 Network Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **Geographic Coverage:**
            - **Northernmost:** {df['latitude'].max():.3f}°
            - **Southernmost:** {df['latitude'].min():.3f}°
            - **Easternmost:** {df['longitude'].max():.3f}°
            - **Westernmost:** {df['longitude'].min():.3f}°
            """)
        
        with col2:
            st.info(f"""
            **Administrative Coverage:**
            - **Provinces:** {df['provinsi'].nunique()}
            - **Districts:** {df['kabupaten'].nunique()}
            - **Sub-districts:** {df['kecamatan'].nunique()}
            """)
        
        with col3:
            equipment_info = df['merk'].value_counts()
            equipment_text = "\n".join([f"- **{brand}:** {count}" for brand, count in equipment_info.head(5).items()])
            st.info(f"""
            **Equipment Brands:**
            {equipment_text}
            """)
    
    with tab3:
        st.subheader("📋 Complete Site Directory")
        
        # Search functionality
        search_term = st.text_input("🔍 Search sites by name or location:")
        
        if search_term:
            search_df = df[
                df['nama_site'].str.contains(search_term, case=False, na=False) |
                df['provinsi'].str.contains(search_term, case=False, na=False) |
                df['kabupaten'].str.contains(search_term, case=False, na=False)
            ]
        else:
            search_df = df
        
        # Display sites table
        display_columns = ['id_site', 'nama_site', 'provinsi', 'kabupaten', 'latitude', 'longitude', 'th_pengadaan', 'merk']
        st.dataframe(
            search_df[display_columns].sort_values('id_site'),
            use_container_width=True,
            column_config={
                'id_site': 'Site ID',
                'nama_site': 'Site Name',
                'provinsi': 'Province',
                'kabupaten': 'District',
                'latitude': st.column_config.NumberColumn('Latitude', format="%.3f"),
                'longitude': st.column_config.NumberColumn('Longitude', format="%.3f"),
                'th_pengadaan': 'Installation Year',
                'merk': 'Equipment Brand'
            }
        )
        
        # Export functionality
        if st.button("📥 Download Site Data"):
            csv = search_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"microclimate_sites_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with tab4:
        st.subheader(f"🎯 Selected Site Details")
        
        # Get selected site details
        selected_site = df[df['id_site'] == selected_site_id].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            ### 📍 {selected_site['nama_site']}
            
            **Basic Information:**
            - **Site ID:** {selected_site['id_site']}
            - **Site Type:** {selected_site['id_jenis'] if pd.notna(selected_site['id_jenis']) else 'N/A'}
            - **Installation Year:** {int(selected_site['th_pengadaan']) if pd.notna(selected_site['th_pengadaan']) else 'N/A'}
            - **Equipment:** {selected_site['merk'] if pd.notna(selected_site['merk']) else 'N/A'} {selected_site['tipe'] if pd.notna(selected_site['tipe']) else ''}
            
            **Location:**
            - **Province:** {selected_site['provinsi']}
            - **District:** {selected_site['kabupaten']}
            - **Sub-district:** {selected_site['kecamatan']}
            - **Village:** {selected_site['desa'] if pd.notna(selected_site['desa']) else 'N/A'}
            """)
        
        with col2:
            st.markdown(f"""
            ### 🌍 Geographic Details
            
            **Coordinates:**
            - **Latitude:** {selected_site['latitude']:.6f}°
            - **Longitude:** {selected_site['longitude']:.6f}°
            - **Elevation:** {selected_site['elevasi'] if pd.notna(selected_site['elevasi']) else 'N/A'} m
            
            **Administrative:**
            - **Regional Office:** {selected_site['kanwil'] if pd.notna(selected_site['kanwil']) else 'N/A'}
            - **Postal Code:** {selected_site['pos'] if pd.notna(selected_site['pos']) else 'N/A'}
            - **Procurement:** {selected_site['pengadaan'] if pd.notna(selected_site['pengadaan']) else 'N/A'}
            
            **Address:**
            {selected_site['alamat'] if pd.notna(selected_site['alamat']) else 'Address not available'}
            """)
        
        # Link to detailed analysis
        st.markdown("---")
        st.info(f"""
        💡 **Ready to analyze data from {selected_site['nama_site']}?**
        
        If you have microclimate data for this site, you can use the main dashboard to visualize and analyze the measurements.
        The current dashboard is configured for Site ID {selected_site_id}.
        """)

main()