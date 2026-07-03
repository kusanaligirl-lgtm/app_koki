import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sqlite3
from ultralytics import YOLO

# Konfigurasi halaman utama (diubah ke centered agar lebih optimal di mobile)
st.set_page_config(
    page_title="Rekomendasi Resep Bahan Makanan",
    page_icon="🍲",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk tampilan Neobrutalism (Stark borders, high contrast, flat shadows)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;700;900&display=swap');

    /* Mengubah background aplikasi */
    [data-testid="stAppViewContainer"] {
        background-color: #FFFDF5; /* Cream background */
        color: #000000;
        font-family: 'Lexend', 'Inter', sans-serif;
    }
    
    /* Global Typography Styling */
    h1, h2, h3, h4, h5, h6, p, span, label {
        font-family: 'Lexend', sans-serif !important;
        color: #000000 !important;
    }
    
    h1, h2, h3 {
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: -1px;
    }

    /* File Uploader Custom Styling */
    [data-testid="stFileUploader"] {
        background-color: #FDE047; /* Bright yellow */
        border: 4px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 6px 6px 0px 0px #000000;
        padding: 1.5rem !important;
    }
    
    [data-testid="stFileUploader"] label {
        font-weight: 900 !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        border: 3px dashed #000000 !important;
        background-color: #ffffff !important;
        border-radius: 0px !important;
    }

    /* Image Styling */
    img {
        border: 4px solid #000000 !important;
        box-shadow: 6px 6px 0px 0px #000000 !important;
        border-radius: 0px !important;
    }

    /* Notification Box / Info Box */
    div[data-testid="stNotification"] {
        background-color: #38BDF8 !important; /* Bright cyan */
        border: 3px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px 0px #000000;
        color: #000000 !important;
    }
    
    div[data-testid="stNotification"] p {
        font-weight: 700 !important;
        color: #000000 !important;
    }
    
    /* Judul Utama */
    .main-title {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        color: #000000;
        background-color: #A855F7; /* Purple */
        border: 4px solid #000000;
        border-radius: 0px;
        box-shadow: 8px 8px 0px 0px #000000;
        padding: 1rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        font-family: 'Lexend', sans-serif;
    }
    
    .main-subtitle {
        font-size: 1.15rem;
        font-weight: 700;
        text-align: center;
        color: #000000;
        background-color: #F43F5E; /* Vibrant rose */
        border: 3px solid #000000;
        border-radius: 0px;
        box-shadow: 5px 5px 0px 0px #000000;
        padding: 0.75rem;
        margin-bottom: 3rem;
        text-transform: uppercase;
    }

    /* Kartu Resep Custom */
    .recipe-card-success {
        background-color: #86EFAC; /* Pastel green */
        border: 4px solid #000000;
        border-radius: 0px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 6px 6px 0px 0px #000000;
        color: #000000;
    }

    .recipe-card-warning {
        background-color: #FDA4AF; /* Pastel rose */
        border: 4px solid #000000;
        border-radius: 0px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 6px 6px 0px 0px #000000;
        color: #000000;
    }
    
    .recipe-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: #000000;
        border-bottom: 3px solid #000000;
        padding-bottom: 0.5rem;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
    }
    
    .recipe-steps {
        font-size: 1rem;
        font-weight: 600;
        color: #000000;
        line-height: 1.6;
        white-space: pre-line;
    }

    /* Responsive Styling untuk Layar HP (Mobile) */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.2rem !important;
            box-shadow: 5px 5px 0px 0px #000000;
            padding: 0.75rem !important;
            margin-bottom: 1rem;
        }
        
        .main-subtitle {
            font-size: 0.95rem !important;
            box-shadow: 3px 3px 0px 0px #000000;
            padding: 0.5rem !important;
            margin-bottom: 2rem;
        }
        
        .recipe-title {
            font-size: 1.25rem !important;
        }
        
        .recipe-steps {
            font-size: 0.9rem !important;
        }
        
        /* Kurangi padding luar kontainer pada layar kecil */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Tampilkan Header Utama
st.markdown('<div class="main-title">🍲 Koki AI: Resep Saku</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Solusi anti-bingung masak dari sisa bahan makanan terbatas</div>', unsafe_allow_html=True)

# Memuat model YOLO secara aman & di-cache agar performa cepat
@st.cache_resource
def load_model():
    return YOLO('best.pt')

try:
    model = load_model()
except Exception as e:
    st.error(f"Gagal memuat model YOLO 'best.pt'. Pastikan file model tersebut berada di folder project. Detail error: {e}")
    st.stop()

# Fungsi pencarian resep dari database
def cari_resep(bahan_terdeteksi):
    try:
        conn = sqlite3.connect('resep.db')
        cursor = conn.cursor()
        
        # Ambil seluruh resep dan bahannya
        cursor.execute("""
            SELECT r.id, r.nama, r.langkah, GROUP_CONCAT(b.nama, ',') as bahan_list
            FROM resep r
            JOIN resep_bahan rb ON r.id = rb.resep_id
            JOIN bahan b ON b.id = rb.bahan_id
            GROUP BY r.id
        """)
        rows = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Gagal mengakses database resep.db: {e}")
        return [], []

    set_terdeteksi = set(bahan_terdeteksi)
    bisa_dimasak = []
    kurang_bahan = []

    for r_id, nama, langkah, bahan_list in rows:
        req_bahan = set(bahan_list.split(','))
        missing = req_bahan - set_terdeteksi
        
        if len(missing) == 0:
            bisa_dimasak.append((nama, langkah))
        elif len(missing) <= 2:  # Kurang maksimal 2 bahan
            kurang_bahan.append((nama, langkah, list(missing)))
            
    return bisa_dimasak, kurang_bahan

# Fungsi pemrosesan gambar & deteksi YOLO
def deteksi_bahan(img_pil):
    # Ubah gambar PIL ke numpy array
    img_np = np.array(img_pil)
    # Konversi format RGB (PIL) ke BGR (OpenCV)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    # Deteksi dengan YOLO (menggunakan imgsz=320 untuk kecepatan pemrosesan)
    results = model(img_bgr, conf=0.45, imgsz=320, verbose=False)
    
    # Ambil kelas bahan unik yang terdeteksi
    detected_classes = []
    if len(results) > 0 and results[0].boxes is not None:
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            if label not in detected_classes:
                detected_classes.append(label)
                
    # Dapatkan gambar beranotasi (bounding box)
    annotated_img = results[0].plot()
    # Konversi kembali BGR ke RGB untuk Streamlit
    annotated_img_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
    
    return annotated_img_rgb, detected_classes

# Layout pembantu untuk menampilkan hasil
def tampilkan_hasil(detected_list, annotated_image):
    st.write("---")
    
    col_img, col_rec = st.columns([1, 1.2])
    
    with col_img:
        st.subheader("🔍 Hasil Deteksi Objek")
        st.image(annotated_image, caption="Hasil Deteksi Bahan Makanan", use_container_width=True)
        
    with col_rec:
        st.subheader("🛒 Bahan Terdeteksi")
        if detected_list:
            # Tampilkan tag/badge bahan ala Neobrutalism
            badges_html = " ".join([f'<span style="background-color: #38BDF8; color: #000000; border: 3px solid #000000; box-shadow: 3px 3px 0px 0px #000000; padding: 6px 14px; font-weight: 900; margin-right: 12px; margin-bottom: 12px; font-size: 0.95rem; display: inline-block; text-transform: uppercase;">{b}</span>' for b in detected_list])
            st.markdown(f'<div style="margin-bottom: 2rem;">{badges_html}</div>', unsafe_allow_html=True)
            
            bisa, kurang = cari_resep(detected_list)
            
            st.markdown("### 🍳 Menu Masak Instan (Bahan Lengkap)")
            if bisa:
                for nama, langkah in bisa:
                    st.markdown(f"""
                    <div class="recipe-card-success">
                        <div class="recipe-title">🟢 {nama}</div>
                        <div class="recipe-steps">{langkah}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Bahan-bahanmu belum lengkap untuk membuat menu utama. Coba tambahkan bahan lain.")
                
            st.markdown("### 💡 Menu Alternatif (Kurang 1-2 Bahan)")
            if kurang:
                for nama, langkah, missing in kurang:
                    missing_str = ", ".join(missing)
                    st.markdown(f"""
                    <div class="recipe-card-warning">
                        <div class="recipe-title">🟠 {nama} <span style="font-size: 0.9rem; color: #500f1c; font-weight: 800;">(Butuh beli: {missing_str})</span></div>
                        <div class="recipe-steps">{langkah}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Tidak ada resep alternatif yang mendekati bahan sisa kamu.")
        else:
            st.warning("Belum ada bahan makanan yang dikenali AI. Pastikan bahan terlihat jelas di foto.")

# --- INTERFACE UNGGAH FOTO ---
uploaded_file = st.file_uploader(
    "Tarik & lepas atau pilih foto bahan makanan dari galerimu", 
    type=["jpg", "jpeg", "png"],
    key="file_uploader"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    with st.spinner("Menganalisis foto dengan YOLO..."):
        annotated_img, detected = deteksi_bahan(image)
    tampilkan_hasil(detected, annotated_img)
