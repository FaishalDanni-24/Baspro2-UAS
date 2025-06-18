# Import library untuk program
import sqlite3
import os
import platform


# Koneksi ke database (akan membuat file jika belum ada)
conn = sqlite3.connect("restoran.db")
cursor = conn.cursor()

# Tabel menu
cursor.execute("""
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    harga REAL NOT NULL,
    kategori TEXT
)
""")

# Tabel pesanan
cursor.execute("""
CREATE TABLE IF NOT EXISTS pesanan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    jumlah INTEGER,
    total REAL
)
""")

# Tabel detail pesanan
cursor.execute("""
CREATE TABLE IF NOT EXISTS detail_pesanan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pesanan_id INTEGER,
    menu_id INTEGER,
    jumlah INTEGER,
    FOREIGN KEY(pesanan_id) REFERENCES pesanan(id),
    FOREIGN KEY(menu_id) REFERENCES menu(id)
)
""")


# Fungsi untuk clear screen terminal
def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# Fungsi untuk mengecek table kosong
def menuEmpty():
    cursor.execute("SELECT COUNT(*) FROM menu")
    row = cursor.fetchone()
    jumlah_data = row[0] if row else 0

    if jumlah_data > 0:
        return False
    else:
        return True

# Menampilkan menu yang ada
def displayMenu():
    cursor.execute("SELECT * FROM menu")
    hasil = cursor.fetchall()
    if not hasil:
        print("Belum ada menu yang tersedia.\n")
        return
    print(f"{'ID':<4} {'Nama Menu':<25} {'Harga':<10} {'Kategori'}")
    print("-"*50)
    for id, nama, harga, kategori in hasil:
        print(f"{id:<4} {nama:<25} Rp{harga:<10.0f} {kategori}")
    print("")

# Menampilkan detail pesanan
def displayPesanan():
    cursor.execute("SELECT * FROM pesanan")
    hasil = cursor.fetchall()
    if not hasil:
        print("Belum ada pesanan.\n")
    else:
        for id, waktu, jumlah, total in hasil:
            print(f"\nPesanan #{id} | {waktu}")
            print(f"Jumlah item: {jumlah} | Total: Rp{total:.0f}")
            print("Rincian:")
            cursor.execute("""
                SELECT menu.nama, detail_pesanan.jumlah 
                FROM detail_pesanan
                JOIN menu ON menu.id = detail_pesanan.menu_id 
                WHERE pesanan_id=?
            """, (id,))
            detail = cursor.fetchall()
            for nama, jml in detail:
                print(f"  - {nama} x{jml}")
            print("-"*30)

# Fungsi untuk menu admin (mengubah menu, melihat riwayat)
def adminMenu():
    choice = ""
    while(choice != "6"):
        clear_screen()
        print("="*50)
        print("\t\tMENU ADMIN")
        print("1. Tambah Menu")
        print("2. Update Menu")
        print("3. Hapus Menu")
        print("4. Tampilkan Riwayat Pesanan")
        print("5. Hapus/Batal Pesanan")
        print("6. Kembali ke Menu Utama")
        print("="*50)
        choice = input("Pilihan anda : ")

        if(choice == "1"):
            displayMenu()
            nama_baru = input("Masukkan nama menu baru: ")
            try:
                harga_baru = float(input("Masukkan harga menu baru (Rp.): "))
            except ValueError:
                print("Harga tidak valid. Masukkan angka.")
                input("Pencet key apa pun untuk kembali ke menu utama...")
                continue
            kategori_baru = input("Masukkan kategori menu baru (Makanan/Minuman): ").capitalize()
            while kategori_baru != "Makanan" and kategori_baru != "Minuman":
                kategori_baru = input("Masukkan kategori menu baru (Makanan/Minuman): ").capitalize()
            cursor.execute("INSERT INTO menu (nama, harga, kategori) VALUES (?, ?, ?)", (nama_baru, harga_baru, kategori_baru))
            conn.commit()
            print("Menu baru berhasil ditambahkan.")
            input("Pencet key apa pun untuk kembali ke menu admin...")

        elif(choice == "2"):
            displayMenu()
            id_edit = input("Masukkan ID menu yang akan diubah: ")
            cursor.execute("SELECT * FROM menu WHERE id=?", (id_edit,))
            if cursor.fetchone() is None:
                print("ID menu tidak ditemukan.")
                input("Pencet key apa pun untuk kembali ke menu admin...")
                continue
            nama = input("Nama baru: ")
            try:
                harga = float(input("Masukkan harga menu baru (Rp.): "))
            except ValueError:
                print("Harga tidak valid. Masukkan angka.")
                input("Pencet key apa pun untuk kembali ke menu admin...")
                continue
            kategori = input("Kategori baru: ")
            cursor.execute("UPDATE menu SET nama=?, harga=?, kategori=? WHERE id=?", (nama, harga, kategori, id_edit))
            conn.commit()
            print("Menu berhasil diupdate!\n")
            input("Pencet key apa pun untuk kembali ke menu admin...")
            
        elif(choice == "3"):
            displayMenu()
            id_hapus = input("Masukkan ID menu yang akan dihapus: ")
            cursor.execute("SELECT * FROM menu WHERE id=?", (id_hapus,))
            if cursor.fetchone() is None:
                print("ID menu tidak ditemukan.")
                input("Pencet key apa pun untuk kembali ke menu admin...")
                continue
            
            if input("Apakah anda yakin ingin menghapus? (Y/N): ").lower() == "y":
                cursor.execute("DELETE FROM menu WHERE id=?", (id_hapus,))
                conn.commit()
                print("Menu berhasil dihapus!\n")
                input("Pencet key apa pun untuk kembali ke menu admin...")
            else:
                continue
            
        elif(choice == "4"):
            displayPesanan()
            input("Pencet key apa pun untuk kembali ke menu admin...")
        
        elif(choice == "5"):
            displayPesanan()
            try:
                id_pesanan = int(input("Masukkan ID pesanan yang ingin dihapus: "))
                cursor.execute("SELECT * FROM pesanan WHERE id=?", (id_pesanan,))
                if cursor.fetchone() is None:
                    print("ID pesanan tidak ditemukan.")
                else:
                    if input("Apakah anda yakin ingin menghapus? (Y/N): ").lower() == "y":
                        cursor.execute("DELETE FROM detail_pesanan WHERE pesanan_id=?", (id_pesanan,))
                        cursor.execute("DELETE FROM pesanan WHERE id=?", (id_pesanan,))
                        conn.commit()
                        print("Pesanan berhasil dihapus.")
                    else:
                        print("Penghapusan dibatalkan.")
            except ValueError:
                print("Input tidak valid.")
            input("Pencet key apa pun untuk kembali ke menu utama...")

# Fungsi untuk menu tamu
def guestMenu():
    while True:
        clear_screen()
        if (menuEmpty()):
            print("Data Masih Kosong!\n")
            input("Pencet key apa pun untuk kembali ke menu utama...")
            return
        else:
            continue_order = ""
            pesanan = []
            while(continue_order != "n"):
                print("="*50)
                print("\t\tMENU PEMESANAN")
                displayMenu()
                print("="*50)
                try:
                    input_id_menu = int(input("Masukkan id menu yang anda pilih: "))
                    cursor.execute("SELECT harga FROM menu WHERE id=?", (input_id_menu,))
                    row = cursor.fetchone()
                    if row is None:
                        print("ID menu tidak ditemukan. Coba lagi.")
                        input("Pencet key apa pun untuk lanjut...")
                        continue

                    input_jumlah = int(input("Masukkan jumlah pesanan: "))
                    pesanan.append((input_id_menu, input_jumlah))

                except ValueError:
                    print("Input tidak valid. Harus berupa angka.")
                    input("Pencet key apa pun untuk kembali ke menu utama...")
                    continue

                continue_order = input("Mau menambah pesanan? (Y untuk lanjut pesan, N untuk selesai): ").lower()

            # Hitung total
            total = 0
            for id_menu, jumlah in pesanan:
                cursor.execute("SELECT harga FROM menu WHERE id=?", (id_menu,))
                row = cursor.fetchone()
                if row is None:
                    print("ID menu tidak ditemukan. Coba lagi.")
                    continue
                harga = row[0]
                total += harga * jumlah

            if not pesanan:
                print("Tidak ada pesanan yang dimasukkan.")
                input("Pencet key apa pun untuk kembali...")
                return
            
            # Simpan ke tabel pesanan
            cursor.execute("INSERT INTO pesanan (jumlah, total) VALUES (?, ?)", (sum(j[1] for j in pesanan), total))
            pesanan_id = cursor.lastrowid

            # Simpan ke tabel detail_pesanan
            for id_menu, jumlah in pesanan:
                cursor.execute("INSERT INTO detail_pesanan (pesanan_id, menu_id, jumlah) VALUES (?, ?, ?)",
                            (pesanan_id, id_menu, jumlah))
            conn.commit()

            # Cetak struk
            print("\n", "="*30)
            print("\tSTRUK PESANAN")
            print("ID Pesanan:", pesanan_id)
            cursor.execute("SELECT waktu FROM pesanan WHERE id=?", (pesanan_id,))
            row = cursor.fetchone()
            waktu = row[0] if row else "Tidak diketahui"
            print("Waktu:", waktu)
            print("-"*30)
            for id_menu, jumlah in pesanan:
                cursor.execute("SELECT nama, harga FROM menu WHERE id=?", (id_menu,))
                result = cursor.fetchone()
                if result:
                    nama, harga = result
                    print(f"{nama} x{jumlah} = Rp{harga * jumlah:.0f}")
            print("-"*30)
            print(f"TOTAL = Rp{total:.0f}")
            print("Jika Anda ingin membatalkan pesanan, tolong hubungi admin/staf restoran")
            print("="*30)

            input("Pencet key apa pun untuk kembali ke menu utama...")
        
        keluar = input("Apakah Anda ingin keluar dari menu tamu? (y/n): ").lower()
        if keluar == "y":
            break
 
# Fungsi utama (Menu Self-service)
def main():
    choice = ""
    while(choice != "3"):
        clear_screen()
        print("="*50)
        print("\t\tPROGRAM SELF SERVICE RESTORAN")
        print("1. Menu Admin")
        print("2. Menu Tamu")
        print("3. Keluar")
        print("="*50)
        choice = input("Pilihan anda : ")

        if(choice == "1"):
            adminMenu()
        elif(choice == "2"):
            guestMenu()

    quit()


# Menjalankan fungsi main
if __name__ == "__main__":
    main()
    # Menutup koneksi ke database
    conn.close()