import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
import plotly.express as px
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Buku Tamu Digital - BAPPEDA Kota Pariaman",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM UNTUK UI PREMIUM ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Custom Header Gradasi */
    .header-container {
        background: linear-gradient(135deg, #004a99 0%, #0072ff 100%);
        padding: 45px;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 10px 25px rgba(0, 74, 153, 0.2);
    }
    
    /* Styling Card Form */
    div[data-testid="stForm"] {
        background-color: white !important;
        padding: 40px !important;
        border-radius: 20px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }
    
    /* Tombol Utama */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: linear-gradient(90deg, #004a99 0%, #0056b3 100%);
        color: white;
        font-weight: 600;
        border: none;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 74, 153, 0.3);
        color: white;
    }
    
    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #004a99;
        font-family: 'Inter', sans-serif;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #94a3b8;
        font-size: 13px;
        margin-top: 60px;
        padding: 20px;
        border-top: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KONEKSI DATABASE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Load data tanpa cache agar perubahan (seperti hapus) langsung terlihat
        return conn.read(worksheet="Sheet1", ttl="0")
    except Exception:
        # Jika sheet masih kosong, buat kolom header
        return pd.DataFrame(columns=[
            "ID", "Tanggal", "Tanggal_SPT", "Nama", "NIP", "Jabatan", 
            "OPD", "No_HP", "Bidang", "Maksud", "Kesan_Pesan"
        ])

data_existing = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a8/Logo_Kota_Pariaman.png", width=100)
    st.markdown("<h2 style='text-align: center; color: #004a99;'>MENU UTAMA</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio(
        "Pilih Halaman:",
        ["🏠 Beranda", "📊 Statistik", "📋 Daftar Tamu", "📂 Laporan"],
        label_visibility="collapsed"
    )
    st.write("---")
    st.caption("v2.0 - UI Premium Edition")

# --- LOGIK HALAMAN ---

if menu == "🏠 Beranda":
    st.markdown("""
        <div class="header-container">
            <h1 style='margin:0; font-size: 2.5em;'>BUKU TAMU DIGITAL</h1>
            <p style='margin:10px 0 0 0; opacity:0.9; font-weight: 300; letter-spacing: 1px;'>BAPPEDA KOTA PARIAMAN</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("📍 **Lokasi Terverifikasi:** Anda berada dalam area layanan publik BAPPEDA.")

    with st.form("guest_form", clear_on_submit=True):
        st.subheader("📑 Formulir Kedatangan")
        
        col1, col2 = st.columns(2)
        with col1:
            tgl_kunjungan = st.date_input("Tanggal Kunjungan", datetime.date.today())
            nama = st.text_input("Nama Lengkap*", placeholder="Masukkan nama Anda...")
            nip = st.text_input("NIP", placeholder="Isi '-' jika tidak ada")
            jabatan = st.text_input("Jabatan", placeholder="Contoh: Analis Kebijakan")
            opd = st.text_input("OPD / Instansi*", placeholder="Contoh: Bappeda Provinsi")
            
        with col2:
            tgl_spt = st.date_input("Tanggal SPT")
            no_hp = st.text_input("Nomor WhatsApp*", placeholder="08xxxxxxxxxx")
            bidang = st.selectbox("Bidang Tujuan*", [
                "Sekretariat", 
                "Bidang Litbang & Evlap", 
                "Bidang Pemerintahan dan Sosial Budaya", 
                "Bidang Ekonomi", 
                "Bidang Sarana dan Prasarana Wilayah"
            ])
            maksud = st.text_area("Maksud Kunjungan", height=100)
            kesan = st.text_area("Kesan dan Pesan", height=100)

        st.markdown("### ✍️ Tanda Tangan Digital")
        st.caption("Gunakan mouse atau jari Anda pada area di bawah:")
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#ffffff",
            height=150,
            width=500,
            drawing_mode="freedraw",
            key="canvas",
        )

        st.write("")
        submitted = st.form_submit_button("SIMPAN DATA KUNJUNGAN")
        
        if submitted:
            if not nama or not no_hp or not opd:
                st.error("Mohon lengkapi data bertanda bintang (*)!")
            else:
                # Generate Unique ID
                unique_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                
                new_data = pd.DataFrame([{
                    "ID": unique_id,
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
                
                try:
                    # Gabungkan dan simpan
                    updated_df = pd.concat([data_existing, new_data], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=updated_df)
                    st.success(f"Selamat {nama}, data Anda berhasil tersimpan!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan data. Pastikan Google Sheet Anda diatur sebagai 'Editor'. Detail: {e}")

elif menu == "📊 Statistik":
    st.subheader("📊 Statistik Pengunjung")
    if not data_existing.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Tamu", len(data_existing))
        
        today_str = str(datetime.date.today())
        tamu_hari_ini = len(data_existing[data_existing['Tanggal'] == today_str])
        c2.metric("Tamu Hari Ini", tamu_hari_ini)
        c3.metric("Status Server", "Online ✅")
        
        st.write("---")
        df_bidang = data_existing['Bidang'].value_counts().reset_index()
        fig = px.pie(df_bidang, values='count', names='Bidang', title='Tujuan Bidang Terfavorit',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Belum ada data masuk.")

elif menu == "📋 Daftar Tamu":
    st.subheader("📋 Riwayat Daftar Tamu")
    
    if not data_existing.empty:
        # Filter Pencarian
        search = st.text_input("🔍 Cari berdasarkan Nama atau OPD", "")
        
        df_display = data_existing.copy()
        if search:
            df_display = df_display[
                df_display['Nama'].str.contains(search, case=False, na=False) |
                df_display['OPD'].str.contains(search, case=False, na=False)
            ]
        
        # Tampilan Tabel (Sembunyikan ID agar rapi di mata user)
        st.dataframe(df_display.drop(columns=['ID']) if 'ID' in df_display.columns else df_display, use_container_width=True)
        
        # --- FITUR HAPUS (KHUSUS ADMIN) ---
        st.write("---")
        st.markdown("### 🗑️ Menu Penghapusan (Admin)")
        
        if 'ID' in data_existing.columns:
            # Buat pilihan list: "Nama - (ID)"
            options_to_delete = data_existing['Nama'] + " [" + data_existing['ID'] + "]"
            target = st.selectbox("Pilih tamu yang ingin dihapus datanya:", ["-- Pilih Tamu --"] + options_to_delete.tolist())
            
            if st.button("Hapus Data Terpilih", type="secondary"):
                if target != "-- Pilih Tamu --":
                    # Ambil ID dari dalam kurung siku
                    id_to_del = target.split("[")[-1].replace("]", "")
                    
                    # Filter data yang BUKAN ID tersebut
                    data_after_delete = data_existing[data_existing['ID'] != id_to_del]
                    
                    try:
                        conn.update(worksheet="Sheet1", data=data_after_delete)
                        st.success(f"Data {target} Berhasil Dihapus!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menghapus: {e}")
                else:
                    st.warning("Pilih nama tamu terlebih dahulu!")
        else:
            st.info("Fitur hapus otomatis akan aktif untuk data baru yang memiliki ID.")
    else:
        st.info("Belum ada data tamu.")

elif menu == "📂 Laporan":
    st.subheader("📂 Download Laporan")
    st.info("Data dapat diunduh dalam format CSV untuk dibuka di Excel.")
    if not data_existing.empty:
        csv = data_existing.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data Tamu (CSV/Excel)",
            data=csv,
            file_name=f'laporan_bappeda_{datetime.date.today()}.csv',
            mime='text/csv',
        )
    else:
        st.warning("Data kosong, tidak ada yang bisa diunduh.")

st.markdown('<div class="footer-text">© 2025 BAPPEDA KOTA PARIAMAN<br>Sistem Informasi Manajemen Tamu Digital</div>', unsafe_allow_html=True)
