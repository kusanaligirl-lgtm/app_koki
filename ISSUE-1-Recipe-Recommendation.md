# Issue: AI-Powered Recipe Recommendation (YOLO + SQL)

## 📌 Deskripsi Singkat
Kebingungan anak kos atau ibu rumah tangga saat melihat sisa bahan makanan yang terbatas dan tidak tahu mau masak apa adalah masalah sehari-hari. Proyek ini bertujuan untuk membangun aplikasi yang memecahkan masalah tersebut dengan bantuan Computer Vision (YOLO) dan Database (SQL).

## 🎯 Alur Kerja (Workflow)
1. **Input Pengguna:** Pengguna mengarahkan kamera HP (misalnya menggunakan versi web atau IP Webcam) ke meja yang berisi bahan-bahan sisa (contoh: telur, tomat, bawang, mi instan) atau mengunggah (upload) foto.
2. **Deteksi Objek (YOLO):** Model YOLO akan memproses gambar tersebut, mendeteksi, dan mencatat bahan-bahan makanan apa saja yang ada di layar.
3. **Pencocokan Database (SQL):** Setelah objek dikenali (misalnya `telur` dan `bawang`), program Python akan mengambil daftar bahan tersebut dan menjalankan *query* SQL untuk mencari irisan data di *database* resep.
4. **Output/Rekomendasi:** Program mengembalikan output resep yang paling cocok, misalnya **"Telur Ceplok Bawang"**, beserta panduan langkah-langkah memasaknya yang ditampilkan di layar.

---

## 🛠️ Tugas & Langkah Implementasi (Untuk Junior Programmer / AI)

### Tahap 1: Persiapan Database (SQLite)
Karena proyek ini berbasis Python, disarankan menggunakan **SQLite** agar ringan dan tidak perlu menginstal server terpisah.
- [ ] Buat file *database* (misal: `resep.db`).
- [ ] Buat tabel `bahan_makanan` (id, nama_bahan).
- [ ] Buat tabel `resep` (id, nama_resep, cara_memasak).
- [ ] Buat tabel relasi `detail_resep` (resep_id, bahan_id).
- [ ] Isi *database* dengan beberapa data *dummy* (contoh resep: Telur Dadar, Telur Ceplok Bawang, Mi Rebus Spesial, dll).

### Tahap 2: Integrasi Deteksi YOLO ke Python List
- [ ] Modifikasi file `app.py` yang sudah ada. 
- [ ] Saat YOLO mendeteksi objek (dari *bounding box*), ambil label *class* objek tersebut (misal: "egg", "onion") dan terjemahkan/simpan ke dalam sebuah `List` (array) di Python (contoh: `['telur', 'bawang']`).
- [ ] Hindari duplikasi dalam *list* (jika ada dua telur, cukup catat "telur" satu kali).

### Tahap 3: Query SQL Dinamis
- [ ] Buat fungsi Python untuk menerima daftar bahan (misal: `['telur', 'bawang']`).
- [ ] Tulis *query* SQL (contoh menggunakan `JOIN` dan `GROUP BY` dengan klausa `HAVING`) untuk mencari resep yang bahan-bahannya *sebagian besar* atau *seluruhnya* cocok dengan daftar bahan yang terdeteksi.
- [ ] Ambil `nama_resep` dan `cara_memasak` dari hasil *query*.

### Tahap 4: Antarmuka Pengguna (UI)
- **Versi Desktop (OpenCV):**
  - [ ] Tambahkan fungsi untuk menampilkan teks resep dan langkah memasak menggunakan `cv2.putText` di layar kamera, atau *print* hasilnya ke terminal.
- **Versi Web (Opsional & Peningkatan):**
  - [ ] Gunakan **Flask** atau **Streamlit** (sangat disarankan untuk *prototyping* cepat) agar pengguna bisa mengakses kamera HP lewat *browser* atau fitur *upload* foto.
  - [ ] Tampilkan hasil deteksi gambar (dengan *bounding box*) dan teks resep yang rapi di halaman web.

---

## 💡 Catatan Tambahan
- Pastikan *class names* (label) pada model `best.pt` YOLO kamu benar-benar sinkron dengan `nama_bahan` yang ada di database SQL. Jika YOLO mendeteksi `"egg"`, maka di database harus ada mekanisme *mapping* (penerjemahan) ke `"telur"`.
- Untuk mencegah query berjalan berkali-kali setiap detik (karena FPS kamera jalan terus), buatlah sistem *delay* atau mekanisme *"Tekan tombol Spasi untuk mencari resep dari frame saat ini"*.
