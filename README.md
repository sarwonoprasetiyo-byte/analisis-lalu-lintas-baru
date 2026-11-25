[README.md](https://github.com/user-attachments/files/35421780/README.md)
# Traffic Analysis Dashboard – PJBL Teknik Sipil

Aplikasi Streamlit untuk pencatatan dan analisis deskriptif survei lalu lintas.

## Menjalankan (Windows / PowerShell atau terminal VS Code)

1. Ekstrak ZIP dan buka folder hasil ekstrak di VS Code.
2. Jalankan `python -m pip install -r requirements.txt`.
3. Jalankan `python -m streamlit run app.py`.
4. Buka alamat Local URL yang muncul pada terminal (biasanya http://localhost:8501).

## Penggunaan

- Isi identitas survei di sidebar.
- Edit tabel atau tambah interval; durasi awal 60 menit adalah asumsi contoh, bukan hasil survei.
- Semua interval harus tidak tumpang tindih dan memiliki cakupan arah yang sama.
- Lihat dashboard, tabel, metode dan kesimpulan, atau unduh CSV.
- Ekuivalensi smp bersifat opsional; masukkan faktor sesuai metode dan kondisi jalan. Nilai awal 1,00 hanya placeholder.
- Arus rata-rata = total kendaraan / total jam pengamatan, bukan rata-rata sederhana arus antarinterval.
- Interval tertinggi dinilai dari arus yang dinormalisasi per jam, bukan otomatis jam puncak terukur.
- Aplikasi belum menyimpan data permanen. Ekspor CSV sebelum menutup halaman.
- Aplikasi belum menghitung kapasitas atau tingkat pelayanan karena data jalan dan acuan belum diberikan.

## Data awal

204 sepeda motor, 82 kendaraan ringan, 41 kendaraan berat. Total = 327 kendaraan.
