import cv2
import sqlite3
from ultralytics import YOLO

# 1. Load model yang sudah kamu latih
model = YOLO('best.pt')

# 2. Buka koneksi ke webcam menggunakan IP Webcam atau Kamera Lokal
# GANTI ke 1 atau 2 jika menggunakan DroidCam/Iriun, atau masukkan URL IP Webcam
cap = cv2.VideoCapture(0)

# Cek apakah kamera berhasil dibuka
if not cap.isOpened():
    print("Error: Tidak bisa membuka webcam.")
    exit()

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

print("Mulai deteksi...")
print("=============================================================")
print("Tekan tombol 'SPASI' pada jendela webcam untuk mencari resep.")
print("Tekan tombol 'q' untuk keluar.")
print("=============================================================")

while True:
    # 3. Ambil setiap frame dari webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Gagal menerima frame.")
        break
        
    # 4. YOLO memproses frame (imgsz diperkecil jadi 320 agar lebih ringan dan FPS naik)
    results = model(frame, conf=0.5, imgsz=320, verbose=False)
    
    # Ekstrak bahan makanan unik yang terdeteksi di frame saat ini
    detected_now = []
    if len(results) > 0 and results[0].boxes is not None:
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            if label not in detected_now:
                detected_now.append(label)

    # 5. Gambarkan kotak (bounding box) dan label di atas frame asli
    annotated_frame = results[0].plot()
    
    # Tampilkan teks petunjuk di layar webcam
    cv2.putText(annotated_frame, "Tekan 'SPASI' untuk cari resep", (15, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(annotated_frame, f"Terdeteksi: {', '.join(detected_now)}", (15, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # 6. Tampilkan frame ke layar
    cv2.imshow("Pemindai Bahan Makanan", annotated_frame)
    
    # 7. Logika tombol keluar (q) atau pencarian resep (Spasi)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord(' '):  # Tombol Spasi ditekan
        print("\n=== MENCARI REKOMENDASI RESEP ===")
        print(f"Bahan terdeteksi: {', '.join(detected_now) if detected_now else 'Tidak ada'}\n")
        
        bisa, kurang = cari_resep(detected_now)
        
        if bisa:
            print("🍳 RESEP YANG BISA LANGSUNG DIMASAK:")
            for nama, langkah in bisa:
                print(f"\n👉 {nama}")
                print(langkah)
        else:
            print("❌ Tidak ada resep yang semua bahannya lengkap.")
            
        if kurang:
            print("\n💡 RESEP HAMPIR JADI (Kurang 1-2 bahan):")
            for nama, langkah, missing in kurang:
                print(f"\n👉 {nama} (Bahan kurang: {', '.join(missing)})")
                print(langkah)
        print("\n=================================\n")
        
# Bersihkan memori setelah selesai
cap.release()
cv2.destroyAllWindows()