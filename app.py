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
    layout="wide"
)

# --- KONEKSI DATABASE ---
# Koneksi GSheets dengan penanganan error yang stabil
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Mencoba membaca data dari Sheet1
        df = conn.read(worksheet="Sheet1", ttl="0")
        # Jika sheet kosong atau tidak valid, kembalikan struktur default
        if df is None or df.empty:
            return pd.DataFrame(columns=[
                "Tanggal", "Tanggal_SPT", "Nama", "NIP", "Jabatan", 
                "OPD", "No_HP", "Bidang", "Maksud", "Kesan_Pesan", "ID"
            ])
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "Tanggal", "Tanggal_SPT", "Nama", "NIP", "Jabatan", 
            "OPD", "No_HP", "Bidang", "Maksud", "Kesan_Pesan", "ID"
        ])

data_existing = load_data()

# --- CSS CUSTOM UNTUK TAMPILAN PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header-box {
        background: linear-gradient(135deg, #004a99 0%, #0072ff 100%);
        padding: 30px; border-radius: 15px; color: white;
        text-align: center; margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    div[data-testid="stForm"] {
        background-color: white !important; padding: 25px !important;
        border-radius: 12px !important; border: 1px solid #e2e8f0 !important;
    }
    .stButton>button {
        background-color: #004a99; color: white; border-radius: 8px;
        font-weight: bold; width: 100%; height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a8/Logo_Kota_Pariaman.png", width=70)
    st.title("BAPPEDA")
    st.write("Kota Pariaman")
    st.divider()
    menu = st.radio("Navigasi Menu:", ["🏠 Beranda", "📊 Statistik", "📋 Daftar Tamu"])
    st.divider()
    st.caption("v2.1 - Sistem Buku Tamu Digital")

# --- LOGIKA HALAMAN ---

if menu == "🏠 Beranda":
    st.markdown('<div class="header-box"><h1>BUKU TAMU DIGITAL</h1><p>BAPPEDA KOTA PARIAMAN</p></div>', unsafe_allow_html=True)
    st.info("📍 Verifikasi Lokasi Aktif: Pastikan Anda berada di lingkungan kantor BAPPEDA.")

    with st.form("guest_form", clear_on_submit=True):
        st.subheader("📝 Formulir Kunjungan")
        c1, c2 = st.columns(2)
        with c1:
            tgl_kunjungan = st.date_input("Tanggal Kunjungan", datetime.date.today())
            nama = st.text_input("Nama Lengkap*")
            nip = st.text_input("NIP (Isi '-' jika tidak ada)")
            jabatan = st.text_input("Jabatan")
            opd = st.text_input("OPD / Instansi*")
        with c2:
            tgl_spt = st.date_input("Tanggal SPT", datetime.date.today())
            no_hp = st.text_input("Nomor WhatsApp*")
            bidang = st.selectbox("Bidang Tujuan*", [
                "Sekretariat", 
                "Bidang Litbang & Evlap", 
                "Bidang Pemerintahan dan Sosial Budaya", 
                "Bidang Ekonomi", 
                "Bidang Sarana dan Prasarana Wilayah"
            ])
            maksud = st.text_area("Maksud Kunjungan")
            kesan = st.text_area("Kesan & Pesan")

        st.write("---")
        
        # Fitur Kamera
        st.write("📸 **Verifikasi Wajah**")
        foto = st.camera_input("Ambil foto untuk arsip digital")
        
        # Fitur Tanda Tangan
        st.write("✍️ **Tanda Tangan Digital**")
        canvas_result = st_canvas(
            stroke_width=2,
            stroke_color="#000000",
            background_color="#ffffff",
            height=150,
            width=500, # Lebar otomatis menyesuaikan di HP
            drawing_mode="freedraw",
            key="canvas_beranda",
        )

        st.write("")
        submitted = st.form_submit_button("KIRIM DATA KUNJUNGAN")
        
        if submitted:
            if not nama or not no_hp or not opd:
                st.error("Waduh Del, ada data bintang (*) yang belum diisi!")
            else:
                # Menyiapkan baris data baru
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
                    "Kesan_Pesan": kesan,
                    "ID": datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                }])
                
                try:
                    # Gabungkan data lama dan baru kemudian update GSheets
                    updated_df = pd.concat([data_existing, new_row], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=updated_df)
                    st.success(f"Mantap Del! Data {nama} sudah berhasil terkirim ke Spreadsheet.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Aduh, gagal simpan Del. Coba cek koneksi atau akses GSheets. Error: {e}")

elif menu == "📊 Statistik":
    st.title("📊 Statistik Pengunjung")
    if not data_existing.empty:
        st.metric("Total Tamu Terdaftar", len(data_existing))
        st.write("---")
        # Grafik Bar berdasarkan Bidang
        df_stats = data_existing['Bidang'].value_counts().reset_index()
        fig = px.bar(df_stats, x='Bidang', y='count', title="Jumlah Tamu per Bidang Tujuan", color='Bidang')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Data masih kosong, belum ada statistik yang bisa ditampilkan.")

elif menu == "📋 Daftar Tamu":
    st.title("📋 Riwayat Daftar Tamu")
    if not data_existing.empty:
        # Menampilkan tabel data (tanpa kolom ID biar rapi)
        st.dataframe(data_existing, use_container_width=True)
        
        st.write("---")
        st.subheader("🗑️ Menu Admin: Hapus Data")
        target_id = st.selectbox("Pilih ID Tamu yang ingin dihapus:", ["-- Pilih ID --"] + data_existing['ID'].tolist())
        
        if st.button("Hapus Data Terpilih"):
            if target_id != "-- Pilih ID --":
                df_filtered = data_existing[data_existing['ID'] != target_id]
                try:
                    conn.update(worksheet="Sheet1", data=df_filtered)
                    st.success("Data berhasil dihapus dari sistem.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menghapus data: {e}")
            else:
                st.warning("Pilih dulu ID yang mau dihapus ya Del.")
    else:
        st.info("Belum ada riwayat kunjungan tamu.")
