import streamlit as st
import pandas as pd
import plotly.express as px

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(layout="wide", page_title="Pratinjau Data CSV",)

# --- Judul dan Deskripsi Dashboard ---
st.title('📊 Dashboard Visualisasi Data CSV Interaktif')
st.markdown("""
    Unggah file CSV Anda di sini untuk memvisualisasikan data dengan mudah.
    Anda dapat melihat pratinjau data, memfilter berdasarkan kolom kategorikal, 
    dan membuat berbagai jenis plot interaktif.
    
    **Cara menggunakan:**
    1. Klik 'Telusuri file' di bawah untuk mengunggah file CSV Anda.
    2. Setelah file diunggah, Anda akan melihat pratinjau data.
    3. Gunakan filter di bawah untuk memilih subset data.
    4. Pilih kolom untuk visualisasi yang berbeda.
""")

# --- Bagian Unggah File CSV ---
st.header("1. Unggah File CSV Anda")
uploaded_file = st.file_uploader("Pilih file CSV Anda", type="csv")

df = None # Inisialisasi dataframe di luar blok if

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File CSV berhasil diunggah dan dibaca!")
        
        # --- Bagian Pratinjau Data ---
        st.header("2. Pratinjau Data")
        st.write(f"Baris: {df.shape[0]}, Kolom: {df.shape[1]}")
        st.dataframe(df.head())

        # --- Bagian Informasi Kolom ---
        st.header("3. Informasi Kolom")
        st.write("Tipe Data Setiap Kolom:")
        st.dataframe(df.dtypes.rename('Tipe Data'))

        # --- Bagian Filter Data Interaktif ---
        st.header("4. Filter Data (Opsional)")
        
        # Mendeteksi kolom kategorikal (object atau category)
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        filtered_df = df.copy() # Salin dataframe untuk filtering

        if categorical_cols:
            st.subheader("Filter Berdasarkan Kolom Kategorikal")
            # Membuat dua kolom untuk selectbox dan multiselect agar lebih rapi
            col_filter_select, col_filter_multi = st.columns([1, 2])
            
            with col_filter_select:
                selected_filter_col = st.selectbox(
                    "Pilih Kolom untuk Filter:", 
                    ['-- Pilih Kolom --'] + categorical_cols,
                    key="filter_col_selector"
                )

            if selected_filter_col != '-- Pilih Kolom --':
                unique_values = df[selected_filter_col].unique().tolist()
                with col_filter_multi:
                    selected_values_for_filter = st.multiselect(
                        f"Pilih nilai dari '{selected_filter_col}':", 
                        unique_values, 
                        default=unique_values, # Defaultnya semua nilai terpilih
                        key="filter_value_selector"
                    )
                
                if selected_values_for_filter:
                    filtered_df = df[df[selected_filter_col].isin(selected_values_for_filter)]
                    st.subheader("Pratinjau Data Setelah Filter:")
                    st.dataframe(filtered_df.head())
                    st.write(f"Data setelah filter: {filtered_df.shape[0]} baris.")
                else:
                    st.info("Tidak ada nilai yang dipilih untuk filter, menampilkan semua data.")
            else:
                st.info("Pilih kolom kategorikal untuk mengaktifkan filter.")
        else:
            st.warning("Tidak ada kolom kategorikal yang terdeteksi untuk filter.")

        # --- Bagian Visualisasi Data ---
        st.header("5. Visualisasi Data")

        # Mendeteksi kolom numerik
        numeric_cols = filtered_df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        if not numeric_cols and not categorical_cols:
            st.error("Tidak ada kolom numerik atau kategorikal yang terdeteksi untuk visualisasi.")
        else:
            st.subheader("Pilih Jenis Visualisasi:")
            plot_type = st.selectbox(
                "Pilih jenis plot yang ingin Anda buat:",
                ['Histogram', 'Scatter Plot', 'Bar Chart', 'Line Plot', 'Pie Chart'],
                key="plot_type_selector"
            )

            # --- Histogram ---
            if plot_type == 'Histogram' and numeric_cols:
                st.subheader("Histogram Distribusi")
                hist_col = st.selectbox("Pilih Kolom Numerik untuk Histogram:", numeric_cols, key="hist_col")
                if hist_col:
                    fig_hist = px.histogram(filtered_df, x=hist_col, 
                                            title=f"Distribusi {hist_col}",
                                            template="plotly_white")
                    st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.warning("Pilih kolom numerik untuk membuat histogram.")
            elif plot_type == 'Histogram':
                st.warning("Tidak ada kolom numerik yang tersedia untuk Histogram.")

            # --- Scatter Plot ---
            if plot_type == 'Scatter Plot' and len(numeric_cols) >= 2:
                st.subheader("Scatter Plot (Hubungan Antar Kolom Numerik)")
                col_x, col_y = st.columns(2)
                with col_x:
                    scatter_x = st.selectbox("Pilih Kolom X:", numeric_cols, key="scatter_x")
                with col_y:
                    scatter_y = st.selectbox("Pilih Kolom Y:", [col for col in numeric_cols if col != scatter_x], key="scatter_y")
                
                if scatter_x and scatter_y:
                    color_by = st.selectbox("Warna Berdasarkan (Opsional):", ['Tidak Ada'] + categorical_cols, key="scatter_color_by")
                    if color_by != 'Tidak Ada':
                        fig_scatter = px.scatter(filtered_df, x=scatter_x, y=scatter_y, 
                                                 color=color_by, 
                                                 title=f"Scatter Plot {scatter_x} vs {scatter_y} (Warna Berdasarkan {color_by})",
                                                 template="plotly_white")
                    else:
                        fig_scatter = px.scatter(filtered_df, x=scatter_x, y=scatter_y, 
                                                 title=f"Scatter Plot {scatter_x} vs {scatter_y}",
                                                 template="plotly_white")
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.warning("Pilih setidaknya dua kolom numerik untuk Scatter Plot.")
            elif plot_type == 'Scatter Plot':
                st.warning("Membutuhkan setidaknya dua kolom numerik untuk Scatter Plot.")

            # --- Bar Chart ---
            if plot_type == 'Bar Chart' and categorical_cols and numeric_cols:
                st.subheader("Bar Chart (Agregasi Data)")
                col_cat, col_val = st.columns(2)
                with col_cat:
                    bar_category = st.selectbox("Pilih Kolom Kategorikal (X-axis):", categorical_cols, key="bar_category")
                with col_val:
                    bar_value = st.selectbox("Pilih Kolom Numerik (Y-axis):", numeric_cols, key="bar_value")
                
                if bar_category and bar_value:
                    # Agregasi data (contoh: sum). Bisa diubah ke mean, count, dll.
                    grouped_df = filtered_df.groupby(bar_category)[bar_value].sum().reset_index()
                    fig_bar = px.bar(grouped_df, x=bar_category, y=bar_value, 
                                     title=f"Total {bar_value} per {bar_category}",
                                     template="plotly_white")
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.warning("Pilih kolom kategorikal dan numerik untuk Bar Chart.")
            elif plot_type == 'Bar Chart':
                st.warning("Membutuhkan kolom kategorikal dan numerik untuk Bar Chart.")

            # --- Line Plot ---
            if plot_type == 'Line Plot' and numeric_cols:
                st.subheader("Line Plot (Tren Data)")
                if len(numeric_cols) >= 1:
                    line_x = st.selectbox("Pilih Kolom X (misal: Waktu/Indeks):", df.columns.tolist(), key="line_x")
                    line_y = st.selectbox("Pilih Kolom Y (Nilai Tren):", numeric_cols, key="line_y")
                    
                    if line_x and line_y:
                        # Coba konversi kolom X ke datetime jika memungkinkan
                        try:
                            filtered_df['__temp_line_x'] = pd.to_datetime(filtered_df[line_x])
                            # Urutkan berdasarkan waktu jika kolom x adalah waktu
                            filtered_df_sorted = filtered_df.sort_values(by='__temp_line_x')
                            x_col_for_plot = '__temp_line_x'
                        except Exception:
                            # Jika bukan datetime, gunakan apa adanya
                            filtered_df_sorted = filtered_df
                            x_col_for_plot = line_x
                        
                        fig_line = px.line(filtered_df_sorted, x=x_col_for_plot, y=line_y, 
                                           title=f"Tren {line_y} berdasarkan {line_x}",
                                           template="plotly_white")
                        st.plotly_chart(fig_line, use_container_width=True)
                        if '__temp_line_x' in filtered_df.columns:
                            filtered_df.drop(columns=['__temp_line_x'], inplace=True) # Hapus kolom temporer
                    else:
                        st.warning("Pilih kolom X dan Y untuk Line Plot.")
                else:
                    st.warning("Membutuhkan kolom numerik untuk Line Plot.")
            elif plot_type == 'Line Plot':
                st.warning("Tidak ada kolom numerik yang tersedia untuk Line Plot.")

            # --- Pie Chart ---
            if plot_type == 'Pie Chart' and categorical_cols and numeric_cols:
                st.subheader("Pie Chart (Proporsi Kategori)")
                pie_names = st.selectbox("Pilih Kolom Kategorikal (Nama Bagian Pie):", categorical_cols, key="pie_names")
                pie_values = st.selectbox("Pilih Kolom Numerik (Ukuran Bagian Pie):", numeric_cols, key="pie_values")
                
                if pie_names and pie_values:
                    # Agregasi data untuk pie chart
                    pie_df = filtered_df.groupby(pie_names)[pie_values].sum().reset_index()
                    fig_pie = px.pie(pie_df, values=pie_values, names=pie_names, 
                                     title=f"Proporsi {pie_values} per {pie_names}",
                                     template="plotly_white")
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.warning("Pilih kolom kategorikal dan numerik untuk Pie Chart.")
            elif plot_type == 'Pie Chart':
                st.warning("Membutuhkan kolom kategorikal dan numerik untuk Pie Chart.")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {e}")
        st.info("Pastikan file yang diunggah adalah CSV yang valid dan tidak kosong.")
else:
    st.info("Silakan unggah file CSV Anda di atas untuk memulai visualisasi.")

# --- Bagian Sidebar ---
st.sidebar.header("Tentang Dashboard Ini")
st.sidebar.info("""
    Dashboard ini dibuat dengan ❤️ menggunakan:
    - **Python**
    - **Streamlit** (untuk kerangka aplikasi web)
    - **Pandas** (untuk manipulasi data)
    - **Plotly Express** (untuk visualisasi interaktif)
    
    Anda dapat memodifikasi kode ini untuk menambahkan lebih banyak fitur atau jenis visualisasi.
""")
st.sidebar.markdown("---")
# Menambahkan link source code
st.sidebar.markdown(
    "**Lihat Source Code:** [GitHub Repo Anda](https://github.com/URL_GITHUB_REPO_ANDA/)"
)