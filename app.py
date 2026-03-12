import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
import plotly.express as px
from fpdf import FPDF
import base64

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Buku Tamu Digital - BAPPEDA Kota Pariaman",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #004a99; color: white; font-weight: bold; }
    .header-box { background: linear-gradient(90deg, #004a99 0%, #0072ff 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #eee; }
    .footer-text { text-align: center; color: #888; font-size: 12px; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- INTEGRASI DATABASE (Google Sheets) ---
# Menggunakan st.connection untuk membaca dan menulis ke spreadsheet
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(worksheet="Sheet1", ttl="0")
    except:
        return pd.DataFrame(columns=[
            "Tanggal", "Tanggal_SPT", "Nama", "NIP", "Jabatan", 
            "OPD", "No_HP", "Bidang", "Maksud", "Kesan_Pesan"
        ])

data_existing = load_data()

# --- SIDEBAR ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/a8/Logo_Kota_Pariaman.png", width=80)
st.sidebar.title("NAVIGASI")

menu = st.sidebar.radio(
    "Pilih Menu:",
    ["🏠 Beranda", "📊 Statistik", "📋 Daftar Tamu", "📂 Laporan"],
    index=0
)

# --- HALAMAN UTAMA ---
if menu == "🏠 Beranda":
    st.markdown('<div class="header-box"><h1>SELAMAT DATANG</h1><p>Buku Tamu Digital BAPPEDA Kota Pariaman</p></div>', unsafe_allow_html=True)
    
    # Simulasi Radius Lokasi
    st.warning("📍 Verifikasi Lokasi: Pastikan GPS Anda aktif dan berada di kawasan BAPPEDA.")
    
    with st.form("guest_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tgl_kunjungan = st.date_input("Tanggal Kunjungan", datetime.date.today())
            nama = st.text_input("Nama Lengkap*")
            nip = st.text_input("NIP")
            jabatan = st.text_input("Jabatan")
            opd = st.text_input("OPD / Instansi")
            
        with col2:
            tgl_spt = st.date_input("Tanggal SPT")
            no_hp = st.text_input("Nomor HP")
            bidang = st.selectbox("Bidang Tujuan", [
                "Sekretariat", 
                "Bidang Litbang & Evlap", 
                "Bidang Pemerintahan dan Sosial Budaya", 
                "Bidang Ekonomi", 
                "Bidang Sarana dan Prasarana Wilayah"
            ])
            maksud = st.text_area("Maksud dan Tujuan Kunjungan")
            kesan = st.text_area("Kesan dan Pesan")

        st.write("---")
        st.subheader("📸 Dokumentasi & Tanda Tangan")
        
        t1, t2 = st.tabs(["Kamera/Upload", "Tanda Tangan Digital"])
        with t1:
            foto = st.camera_input("Ambil Foto")
        with t2:
            canvas_result = st_canvas(
                stroke_width=2, stroke_color="#000", background_color="#fff",
                height=150, width=300, drawing_mode="freedraw", key="canvas"
            )

        submitted = st.form_submit_button("SIMPAN DATA")
        
        if submitted:
            if not nama or not bidang:
                st.error("Nama dan Bidang Tujuan wajib diisi!")
            else:
                new_row = pd.DataFrame([{
                    "Tanggal": str(tgl_kunjungan),
                    "Tanggal_SPT": str(tgl_spt),
                    "Nama": nama,
                    "NIP": nip,
                    "Jabatan": jabatan,
                    "OPD": opd,
                    "No_HP": no_hp,
                    "Bidang": bidang,
                    "Maksud": maksud,
                    "Kesan_Pesan": kesan
                }])
                
                # Menggabungkan data lama dan baru
                updated_df = pd.concat([data_existing, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("Data berhasil disimpan ke Spreadsheet!")
                st.balloons()

# --- HALAMAN STATISTIK ---
elif menu == "📊 Statistik":
    st.header("📊 Statistik Pengunjung")
    
    total_tamu = len(data_existing)
    tamu_hari_ini = len(data_existing[data_existing['Tanggal'] == str(datetime.date.today())])
    
    c1, c2 = st.columns(2)
    c1.metric("Total Pengunjung", total_tamu)
    c2.metric("Pengunjung Hari Ini", tamu_hari_ini)
    
    if not data_existing.empty:
        df_counts = data_existing['Bidang'].value_counts().reset_index()
        fig = px.pie(df_counts, values='count', names='Bidang', title='Distribusi Tamu per Bidang')
        st.plotly_chart(fig, use_container_width=True)

# --- HALAMAN DAFTAR TAMU ---
elif menu == "📋 Daftar Tamu":
    st.header("📋 Riwayat Buku Tamu")
    
    search = st.text_input("Cari Nama...")
    filtered_data = data_existing
    if search:
        filtered_data = data_existing[data_existing['Nama'].str.contains(search, case=False)]
    
    st.dataframe(filtered_data, use_container_width=True)
    
    if st.button("Download CSV"):
        csv = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button("Klik untuk Download", csv, "buku_tamu.csv", "text/csv")

# --- HALAMAN LAPORAN ---
elif menu == "📂 Laporan":
    st.header("📂 Laporan Periodik")
    opsi = st.selectbox("Jenis Laporan", ["Harian", "Bulanan", "Tahunan"])
    st.info(f"Menyiapkan pratinjau laporan {opsi}...")
    st.button("Export ke PDF")

st.markdown('<div class="footer-text">© 2025 BAPPEDA KOTA PARIAMAN</div>', unsafe_allow_html=True)
