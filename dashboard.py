import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA UI/UX
# ==========================================
st.set_page_config(
    page_title="Dashboard Monitoring Pelatihan PPSDM LH 2026",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Palet Warna Korporat LHK (Forest Emerald & Digital Teal)
LHK_COLORS = {
    "primary": "#064e3b",      # Emerald 950
    "secondary": "#059669",    # Emerald 600
    "accent": "#0d9488",       # Teal 600
    "light_teal": "#ccfbf1",   # Teal 100
    "background": "#f8fafc",   # Slate 50
    "text_dark": "#0f172a",    # Slate 900
    "neutral_light": "#ffffff" # White
}

# Custom CSS untuk mempercantik tampilan Card KPI dan Elemen UI
st.markdown(f"""
    <style>
    .reportview-container {{
        background-color: {LHK_COLORS['background']};
    }}
    .kpi-card {{
        background-color: {LHK_COLORS['neutral_light']};
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-left: 5px solid {LHK_COLORS['secondary']};
        margin-bottom: 15px;
    }}
    .kpi-title {{
        color: #64748b;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .kpi-value {{
        color: {LHK_COLORS['text_dark']};
        font-size: 28px;
        font-weight: 800;
        line-height: 1.2;
        margin-top: 5px;
    }}
    .kpi-subtitle {{
        color: {LHK_COLORS['secondary']};
        font-size: 11px;
        font-weight: 600;
        margin-top: 5px;
    }}
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. FUNGSI PEMROSESAN & PEMBERSIHAN DATA (EDA)
# ==========================================
@st.cache_data
def load_and_clean_data(file_source):
    # Membaca data CSV
    df = pd.read_excel(file_source)
    
    # UI/UX Clean: Menghapus spasi gaib di awal/akhir nama kolom
    df.columns = df.columns.str.strip()
    
    # Pembersihan Data Kategorikal (Typo Sanitization)
    if 'Metode' in df.columns:
        df['Metode'] = df['Metode'].str.strip().replace('Offiline/Klasikal', 'Offline/Klasikal')
        df['Metode'] = df['Metode'].replace('Klasikal', 'Offline/Klasikal')
    
    # Pengurutan Bulan Pelaksanaan secara Logis Kronologis
    urutan_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                    "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    if 'Bulan pelaksanaan' in df.columns:
        df['Bulan pelaksanaan'] = pd.Categorical(df['Bulan pelaksanaan'].str.strip(), categories=urutan_bulan, ordered=True)
        
    return df


# ==========================================
# 3. SIDEBAR PANEL INTERAKTIF & FILE INTAKE
# ==========================================
with st.sidebar:
    st.image("Logo.png")
    st.markdown(f"<h2 style='color:{LHK_COLORS['primary']}; margin-top:0;'>PPSDM LH</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Input File Data
    uploaded_file = st.file_uploader("Unggah File Database Peserta", type=["excel"])
    
    # Fallback to local file if no file uploaded
    data_file = None
    if uploaded_file is not None:
        data_file = uploaded_file
    else:
        try:
            # Mencoba membaca file bawaan jika ada di direktori kerja
            data_file = "Data Peserta Pelatihan 2026.xlsx"
            df_test = pd.read_excel(data_file)
            st.info("💡 Menggunakan file default sistem.")
        except:
            st.warning("Silakan unggah file CSV Anda untuk mengaktifkan visualisasi.")
            st.stop()

# Memuat data ke aplikasi
df_master = load_and_clean_data(data_file)

# ==========================================
# 4. KONTROL FILTER (SLICER GLOBAL)
# ==========================================
with st.sidebar:
    st.markdown(f"<h3 style='color:{LHK_COLORS['primary']}; font-size:16px;'>Slicer Data Global</h3>", unsafe_allow_html=True)
    
    # Filter 1: Bulan Pelaksanaan
    list_bulan = ["Semua Bulan"] + sorted([b for b in df_master['Bulan pelaksanaan'].dropna().unique()])
    filter_bulan = st.selectbox("Pilih Bulan Pelaksanaan", list_bulan)
    
    # Filter 2: Eselon I
    list_eselon = ["Semua Eselon I"] + sorted([str(e) for e in df_master['Eselon I (Singkatan)'].dropna().unique()])
    filter_eselon = st.selectbox("Pilih Unit Kerja Eselon I", list_eselon)
    
    # Filter 3: Metode Pelaksanaan
    list_metode = ["Semua Metode"] + sorted([m for m in df_master['Metode'].dropna().unique()])
    filter_metode = st.selectbox("Pilih Metode Pelaksanaan", list_metode)
    
    # Filter 4: Kategori Jabatan
    list_kat_jab = ["Semua Kategori"] + sorted([k for k in df_master['Kategori Jabatan'].dropna().unique()])
    filter_kat_jab = st.selectbox("Pilih Kategori Jabatan", list_kat_jab)

    # Search Bar untuk Query Teks Global
    search_query = st.text_input("🔍 Pencarian Nama / NIP / Judul", "").strip()

    st.markdown("---")
    st.caption("Dashboard BI Pemantauan Pelatihan Lingkup Kementerian Lingkungan Hidup v2026.1")

# Aplikasi Filter ke Dataset Master
df_filtered = df_master.copy()

if filter_bulan != "Semua Bulan":
    df_filtered = df_filtered[df_filtered['Bulan pelaksanaan'] == filter_bulan]
if filter_eselon != "Semua Eselon I":
    df_filtered = df_filtered[df_filtered['Eselon I (Singkatan)'] == filter_eselon]
if filter_metode != "Semua Metode":
    df_filtered = df_filtered[df_filtered['Metode'] == filter_metode]
if filter_kat_jab != "Semua Kategori":
    df_filtered = df_filtered[df_filtered['Kategori Jabatan'] == filter_kat_jab]
if search_query:
    df_filtered = df_filtered[
        df_filtered['Nama'].str.contains(search_query, case=False, na=False) |
        df_filtered['NIP'].astype(str).str.contains(search_query, na=False) |
        df_filtered['Nama Pelatihan'].str.contains(search_query, case=False, na=False)
    ]

# ==========================================
# 5. HEADER UTAMA DASHBOARD
# ==========================================
st.markdown(f"""
    <div style='background-gradient: to right, {LHK_COLORS['primary']}, {LHK_COLORS['accent']}; padding:20px; border-radius:16px; margin-bottom:25px; color:white; background-color:{LHK_COLORS['primary']}'>
        <h1 style='margin:0; font-size:28px; font-weight:800;'>🌲 MONITORING PELATIHAN PPSDM LH 2026</h1>
        <p style='margin:5px 0 0 0; font-size:14px; opacity:0.85;'>Pusat Komando Analisis Kompetensi dan Distribusi Pelatihan Lingkup Kementerian Lingkungan Hidup</p>
    </div>
""", unsafe_allow_html=True)


# ==========================================
# 6. PENYUSUNAN ROW 1: KARTU METRIK UTAMA (KPI CARDS)
# ==========================================
total_peserta = len(df_filtered)
ragam_materi = df_filtered['Nama Pelatihan'].nunique() if total_peserta > 0 else 0
sertifikat_terbit = df_filtered['Nomor Sertifikat'].dropna().str.strip().astype(bool).sum() if total_peserta > 0 else 0
rasio_kelulusan = round((sertifikat_terbit / total_peserta) * 100) if total_peserta > 0 else 0

total_daring = len(df_filtered[df_filtered['Metode'].str.contains('Daring|Online', case=False, na=False)])
rasio_daring = round((total_daring / total_peserta) * 100) if total_peserta > 0 else 0

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">👥 Total Peserta</div>
            <div class="kpi-value">{total_peserta:,} <span style='font-size:14px; font-weight:500;'>Orang</span></div>
            <div class="kpi-subtitle">Aktif dalam lingkup filter</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {LHK_COLORS['accent']};">
            <div class="kpi-title">📚 Ragam Pelatihan</div>
            <div class="kpi-value">{ragam_materi} <span style='font-size:14px; font-weight:500;'>Topik</span></div>
            <div class="kpi-subtitle">Variasi modul kompetensi</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #f59e0b;">
            <div class="kpi-title">📜 Sertifikat Terbit</div>
            <div class="kpi-value">{sertifikat_terbit:,} <span style='font-size:14px; font-weight:500;'>Sertifikat</span></div>
            <div class="kpi-subtitle">Tingkat kelulusan formal: {rasio_kelulusan}%</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #4f46e5;">
            <div class="kpi-title">💻 Rasio Daring</div>
            <div class="kpi-value">{rasio_daring}%</div>
            <div class="kpi-subtitle">Offline / Klasikal: {100 - rasio_daring}%</div>
        </div>
    """, unsafe_allow_html=True)


# Handle Kondisi Jika Hasil Filter Kosong
if total_peserta == 0:
    st.warning("⚠️ Tidak ada data peserta yang memenuhi kombinasi kriteria filter saat ini. Sila ubah opsi saringan Anda.")
else:
    # ==========================================
    # 7. PENYUSUNAN ROW 2: TREN & PROFIL (LINE & DONUTS)
    # ==========================================
    chart_col1, chart_col2 = st.columns([2, 1])

    with chart_col1:
        st.markdown("<h4 style='font-size:15px; font-weight:700; color:#334155; margin-bottom:10px;'>LINE CHART: TREN KEPESERTAAN BULANAN (2026)</h4>", unsafe_allow_html=True)
        # Agregasi data tren bulanan
        df_tren = df_filtered.groupby('Bulan pelaksanaan', as_index=False).size().rename(columns={'size': 'Jumlah Peserta'})
        
        fig_line = px.line(
            df_tren, 
            x='Bulan pelaksanaan', 
            y='Jumlah Peserta',
            markers=True,
            text='Jumlah Peserta',
            color_discrete_sequence=[LHK_COLORS['secondary']]
        )
        fig_line.update_traces(textposition="top center", line=dict(width=3.5))
        fig_line.update_layout(
            template="plotly_white",
            margin=dict(l=20, r=20, t=10, b=20),
            height=280,
            xaxis_title=None,
            yaxis_title="Volume Partisipasi"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with chart_col2:
        st.markdown("<h4 style='font-size:15px; font-weight:700; color:#334155; margin-bottom:10px;'>KOMPOSISI DEMOGRAFI & GENDER</h4>", unsafe_allow_html=True)
        
        df_gender = df_filtered.groupby('Jenis Kelamin', as_index=False).size()
        fig_donut = px.pie(
            df_gender, 
            names='Jenis Kelamin', 
            values='size', 
            hole=0.6,
            color_discrete_sequence=[LHK_COLORS['accent'], '#fda4af']
        )
        fig_donut.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_donut, use_container_width=True)


    # ==========================================
    # 8. PENYUSUNAN ROW 3: TOP PELATIHAN & DISTRIBUSI UNIT (BARS)
    # ==========================================
    bar_col1, bar_col2 = st.columns(2)

    with bar_col1:
        st.markdown("<h4 style='font-size:15px; font-weight:700; color:#334155; margin-bottom:10px;'>TOP 10 TOPID PELATIHAN DENGAN PESERTA TERBANYAK</h4>", unsafe_allow_html=True)
        # Agregasi Top Pelatihan
        df_top_pel = df_filtered.groupby('Nama Pelatihan', as_index=False).size().sort_values(by='size', ascending=True).tail(10)
        
        fig_bar_pel = px.bar(
            df_top_pel,
            x='size',
            y='Nama Pelatihan',
            orientation='h',
            color_discrete_sequence=[LHK_COLORS['accent']],
            text_auto=True
        )
        fig_bar_pel.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            xaxis_title="Jumlah Peserta",
            yaxis_title=None
        )
        # UI/UX Tip: Nama Pelatihan panjang di sumbu Y akan terpotong jika tidak diberi margin lebar otomatis
        st.plotly_chart(fig_bar_pel, use_container_width=True)

    with bar_col2:
        st.markdown("<h4 style='font-size:15px; font-weight:700; color:#334155; margin-bottom:10px;'>DISTRIBUSI PESERTA PER UNIT ESELON I & METODE</h4>", unsafe_allow_html=True)
        # Agregasi Stacked Bar
        df_eselon_metode = df_filtered.groupby(['Eselon I (Singkatan)', 'Metode'], as_index=False).size()
        
        fig_eselon = px.bar(
            df_eselon_metode,
            x='Eselon I (Singkatan)',
            y='size',
            color='Metode',
            barmode='stack',
            color_discrete_sequence=['#4f46e5', LHK_COLORS['secondary']],
            text_auto=True
        )
        fig_eselon.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            xaxis_title=None,
            yaxis_title="Jumlah Peserta",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_eselon, use_container_width=True)


    # ==========================================
    # 9. ROW 4: TABEL DETAIL (DATA GRANULAR DRILL-DOWN)
    # ==========================================
    st.markdown("---")
    st.markdown("<h3 style='font-size:18px; font-weight:800; color:#0f172a;'>📋 DETAIL GRANULAR DATA OPERASIONAL</h3>", unsafe_allow_html=True)
    
    # Kolom pilihan yang penting ditampilkan di tabel agar tidak terlalu padat
    view_columns = ['Nama', 'NIP', 'Jenis Kelamin', 'Eselon I (Singkatan)', 'Unit Kerja Eselon II', 
                    'Nama Pelatihan', 'Metode', 'Bulan pelaksanaan', 'Nomor Sertifikat']
    
    # Render tabel dengan gaya interaktif khas Streamlit yang mendukung sorting dan filter lokal
    st.dataframe(
        df_filtered[view_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Nama": st.column_config.TextColumn("Nama Lengkap", width="medium"),
            "NIP": st.column_config.TextColumn("NIP Pegawai", width="medium"),
            "Eselon I (Singkatan)": st.column_config.TextColumn("Eselon I", width="small"),
            "Nama Pelatihan": st.column_config.TextColumn("Judul Kursus/Bimtek", width="large"),
            "Nomor Sertifikat": st.column_config.TextColumn("No. Sijil Resmi", help="Jika kosong, status kelulusan belum terbit.")
        }
    )

st.markdown("""
<div style='text-align: center; color: #94a3b8; font-size: 11px; margin-top: 40px;'>
    Hak Cipta © 2026 Pusat Pengembangan SDM Lingkungan Hidup (PPSDM LH). Dikembangkan untuk Kebutuhan BI Eksekutif.
</div>
""", unsafe_allow_html=True)