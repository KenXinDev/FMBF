# 🚀 Multi-Threaded Facebook Tool

Script `run.py` adalah tool berbasis Python yang dirancang untuk melakukan proses otomatisasi dengan sistem multi-threading, dilengkapi dukungan proxy, enkripsi password, dan tampilan CLI yang interaktif.

> ⚠️ Disclaimer: Tool ini dibuat untuk tujuan edukasi dan pengujian keamanan (security testing). Segala penyalahgunaan bukan tanggung jawab developer.

---

## 📌 Fitur Utama

- ⚡ Multi-threaded execution (cepat & efisien)
- 🌐 Dukungan proxy (API & file lokal)
- 🔐 Enkripsi password (Facebook-style encryption)
- 📊 Logging hasil (success & checkpoint)
- 🎨 CLI interaktif (Rich UI support + fallback)
- 🧠 Auto proxy validation
- 📁 Auto generate folder (results, data, temp)

---

## 📂 Struktur Folder

```

project/
├── run.py
├── data/
│   ├── cookie.txt
│   └── token.txt
├── results/
│   ├── success-<date>.txt
│   └── checkpoint-<date>.txt
├── temp/
└── socks4.txt (optional)

````

---

## ⚙️ Requirements

Pastikan sudah install dependency berikut:

```bash
pip install requests pycryptodome rich
````

---

## ▶️ Cara Menjalankan

```bash
python run.py
```

---

## 🌐 Penggunaan Proxy

Saat menjalankan script, kamu akan diberi pilihan:

1. Ambil proxy dari API
2. Gunakan proxy dari file `socks4.txt`
3. Tanpa proxy

Format `socks4.txt`:

```
ip:port
ip:port
```

---

## 📊 Output Hasil

Hasil akan tersimpan di folder:

* ✅ `results/success-<tanggal>.txt`
* ⚠️ `results/checkpoint-<tanggal>.txt`

---

## 🧠 Cara Kerja Singkat

1. Load proxy (optional)
2. Validasi proxy
3. Generate request multi-thread
4. Enkripsi password
5. Kirim request ke endpoint
6. Simpan hasil

---

## ⚠️ Disclaimer

* Tool ini hanya untuk pembelajaran dan testing
* Dilarang digunakan untuk aktivitas ilegal
* Gunakan dengan bijak dan tanggung risiko sendiri

---

## 👨‍💻 Author

**KenXinDev**
Multi-threading & automation enthusiast

---

## ⭐ Support

Jika project ini membantu:

* ⭐ Star repo
* 🔥 Share ke teman
* 💬 Feedback untuk update selanjutnya
