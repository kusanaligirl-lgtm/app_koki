import sqlite3

def init():
    conn = sqlite3.connect('resep.db')
    cursor = conn.cursor()

    # Hapus tabel jika sudah ada agar bisa di-run ulang (idempotent)
    cursor.execute("DROP TABLE IF EXISTS resep_bahan")
    cursor.execute("DROP TABLE IF EXISTS resep")
    cursor.execute("DROP TABLE IF EXISTS bahan")

    # Buat tabel bahan
    cursor.execute("""
    CREATE TABLE bahan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT UNIQUE
    )
    """)

    # Buat tabel resep
    cursor.execute("""
    CREATE TABLE resep (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT UNIQUE,
        langkah TEXT
    )
    """)

    # Buat tabel detail/relasi resep_bahan
    cursor.execute("""
    CREATE TABLE resep_bahan (
        resep_id INTEGER,
        bahan_id INTEGER,
        FOREIGN KEY(resep_id) REFERENCES resep(id),
        FOREIGN KEY(bahan_id) REFERENCES bahan(id),
        PRIMARY KEY(resep_id, bahan_id)
    )
    """)

    # Data bahan makanan dari model YOLO
    classes = [
        'bawang merah', 'bawang putih', 'bumbu nasi goreng', 'garam', 'gula', 
        'kopi', 'margarin', 'mie gelas', 'mie goreng', 'mie goreng hype', 
        'royco', 'susu kental manis', 'telur'
    ]
    for c in classes:
        cursor.execute("INSERT INTO bahan (nama) VALUES (?)", (c,))

    # Data resep masakan dummy
    recipes = [
        {
            "nama": "Telur Ceplok Bawang",
            "langkah": "1. Iris tipis bawang merah dan bawang putih.\n2. Panaskan margarin di wajan.\n3. Tumis irisan bawang hingga wangi.\n4. Masukkan telur, beri sedikit garam/royco.\n5. Goreng hingga matang dan sajikan hangat-hangat.",
            "bahan": ["telur", "bawang merah", "bawang putih", "margarin", "garam"]
        },
        {
            "nama": "Nasi Goreng Instan",
            "langkah": "1. Panaskan margarin di wajan.\n2. Tumis bawang merah dan bawang putih yang sudah diiris.\n3. Masukkan telur, aduk orak-arik.\n4. Masukkan nasi dingin dan bumbu nasi goreng.\n5. Aduk hingga merata, tambahkan royco secukupnya, lalu sajikan.",
            "bahan": ["margarin", "bawang merah", "bawang putih", "telur", "bumbu nasi goreng"]
        },
        {
            "nama": "Kopi Susu Manis",
            "langkah": "1. Masukkan kopi dan gula secukupnya ke dalam cangkir.\n2. Seduh dengan air panas, aduk rata.\n3. Tambahkan susu kental manis sesuai selera, aduk kembali sampai menyatu.",
            "bahan": ["kopi", "gula", "susu kental manis"]
        },
        {
            "nama": "Mie Goreng Telur Spesial",
            "langkah": "1. Rebus mie goreng hingga matang, tiriskan dan campur dengan bumbunya.\n2. Panaskan margarin di wajan terpisah.\n3. Masukkan bawang merah dan bawang putih, tumis sebentar.\n4. Masukkan telur lalu orak-arik atau buat telur ceplok.\n5. Campurkan mie goreng dengan telur, taburi sedikit royco jika suka.",
            "bahan": ["mie goreng", "telur", "margarin", "bawang merah", "bawang putih"]
        },
        {
            "nama": "Mie Gelas Praktis",
            "langkah": "1. Masukkan mie gelas beserta seluruh bumbunya ke dalam gelas/mangkok.\n2. Seduh dengan air panas mendidih secukupnya.\n3. Tutup rapat dan tunggu selama 2-3 menit.\n4. Aduk hingga rata dan siap dinikmati selagi hangat.",
            "bahan": ["mie gelas"]
        }
    ]

    # Masukkan data resep ke database
    for r in recipes:
        cursor.execute("INSERT INTO resep (nama, langkah) VALUES (?, ?)", (r["nama"], r["langkah"]))
        resep_id = cursor.lastrowid
        for b in r["bahan"]:
            cursor.execute("SELECT id FROM bahan WHERE nama = ?", (b,))
            bahan_row = cursor.fetchone()
            if bahan_row:
                bahan_id = bahan_row[0]
                cursor.execute("INSERT OR IGNORE INTO resep_bahan (resep_id, bahan_id) VALUES (?, ?)", (resep_id, bahan_id))

    conn.commit()
    conn.close()
    print("Database resep.db berhasil dibuat dan diisi dengan data awal!")

if __name__ == '__main__':
    init()
