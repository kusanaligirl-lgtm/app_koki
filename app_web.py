import os
import sqlite3
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)

# Konfigurasi Upload Folder
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maksimal file 16MB

# Buat folder uploads jika belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load model YOLOv8 secara global sekali saja
try:
    model = YOLO('best.pt')
except Exception as e:
    print(f"Error: Gagal memuat model YOLO 'best.pt'. Error: {e}")
    model = None

def cari_resep(bahan_terdeteksi):
    """
    Mencari resep dari database resep.db berdasarkan bahan yang terdeteksi.
    Mengembalikan daftar resep yang bisa langsung dimasak dan resep yang kurang bahan.
    """
    try:
        conn = sqlite3.connect('resep.db')
        cursor = conn.cursor()
        
        # Ambil semua data resep beserta daftar bahannya
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
        print(f"Error Database: {e}")
        return [], []

    set_terdeteksi = set(bahan_terdeteksi)
    bisa_dimasak = []
    kurang_bahan = []

    for r_id, nama, langkah, bahan_list in rows:
        req_bahan = set(bahan_list.split(','))
        missing = req_bahan - set_terdeteksi
        
        if len(missing) == 0:
            bisa_dimasak.append((nama, langkah))
        elif len(missing) <= 2:  # Toleransi kurang maksimal 2 bahan
            kurang_bahan.append((nama, langkah, list(missing)))
            
    return bisa_dimasak, kurang_bahan

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Cek apakah file gambar diunggah
        if 'image' not in request.files:
            return render_template('index.html', error_msg="Tidak ada bagian file di form.", results_ready=False)
        
        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', error_msg="Tidak ada file foto yang dipilih.", results_ready=False)
        
        if file and model is not None:
            # Simpan file asli
            filename = secure_filename(file.filename)
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(original_path)
            
            # Membaca gambar menggunakan OpenCV
            image = cv2.imread(original_path)
            if image is None:
                return render_template('index.html', error_msg="Gagal membaca format gambar. Pastikan file berupa foto (JPG/PNG).", results_ready=False)
            
            # Jalankan deteksi YOLO (menggunakan imgsz=320 agar pemrosesan cepat)
            results = model(image, conf=0.45, imgsz=320, verbose=False)
            
            # Ekstrak bahan makanan unik yang terdeteksi
            detected_ingredients = []
            if len(results) > 0 and results[0].boxes is not None:
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    if label not in detected_ingredients:
                        detected_ingredients.append(label)
            
            # Gambar hasil deteksi (bounding box)
            annotated_image = results[0].plot()
            annotated_filename = 'annotated_' + filename
            annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
            cv2.imwrite(annotated_path, annotated_image)
            
            # Cari rekomendasi resep di database
            resep_bisa, resep_kurang = cari_resep(detected_ingredients)
            
            return render_template(
                'index.html', 
                results_ready=True,
                annotated_filename=annotated_filename,
                detected_ingredients=detected_ingredients,
                resep_bisa=resep_bisa,
                resep_kurang=resep_kurang
            )
        elif model is None:
            return render_template('index.html', error_msg="Model YOLO gagal dimuat di server.", results_ready=False)
            
    return render_template('index.html', results_ready=False)

if __name__ == '__main__':
    print("Server Flask berjalan di http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
