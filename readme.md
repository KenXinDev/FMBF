# 🚀 FMBF Multi-Threaded CLI Tool

A powerful Python-based CLI tool designed to demonstrate advanced concepts such as multi-threading, proxy handling, request automation, and encryption.

> ⚡ Built for educational & research purposes

---

## 📌 Features

* ⚡ Multi-threaded processing (`ThreadPoolExecutor`)
* 🌐 Proxy support (API / file / no proxy)
* 🔄 Automatic proxy validation system
* 🎭 Dynamic Facebook-style User-Agent generator
* 🔐 Password encryption (AES + RSA)
* 📂 File-based input & result handling
* 🧠 Smart password combination generator
* 🎨 Interactive CLI interface with `rich`

---

## 📦 Requirements

Make sure you are using Python **3.8 or higher**

Install dependencies:

```bash
pip install requests rich pycryptodome
```

---

## 📁 Project Structure

```
.
├── data/                  # Session (cookie/token)
├── results/               # Output results
│   ├── success-<date>.txt
│   └── checkpoint-<date>.txt
├── temp/                  # Dump data
├── socks4.txt             # Optional proxy list
└── run.py                # Main script
```

---

## ⚙️ How to Use

Run the tool:

```bash
python main.py
```

### Steps:

1. Choose proxy settings:

   * API (auto fetch)
   * File (`socks4.txt`)
   * No proxy

2. Input required data via CLI

3. Select available menu:

   * Dump data (if applicable)
   * Load from file
   * Process accounts

4. Choose password mode:

   * Auto combination
   * Manual password list

5. Wait until process finished

---

## 🔑 Password Modes

* **Auto Mode**
  Generate passwords based on name patterns

* **Combination Mode**
  Mix name + number patterns

* **Manual Mode**
  Fully custom password list

---

## 🌐 Proxy Support

* ✔ ProxyScrape API integration
* ✔ Local proxy file (`socks4.txt`)
* ✔ Automatic validation (working proxies only)
* ✔ Auto-rotation & removal of dead proxies

---

## 📊 Output Results

All results are saved automatically:

* ✅ Success → `results/success-<date>.txt`
* ⚠️ Checkpoint → `results/checkpoint-<date>.txt`

---

## 🧠 Technical Highlights

* Thread-safe proxy handling using `threading.Lock`
* Randomized device fingerprint simulation
* Session-based request handling (`requests.Session`)
* AES + RSA hybrid encryption
* GraphQL request simulation

---

## ⚠️ Disclaimer

This project is created for **educational and research purposes only**.
It is intended to demonstrate concepts such as:

* Multi-threading
* Network automation
* Proxy systems
* Encryption techniques

The author **does NOT encourage, support, or promote** any form of:

* Unauthorized access
* Account cracking
* Privacy violation
* Abuse of any platform or service

Any misuse of this code that violates:

* Laws and regulations
* Platform terms of service
* User privacy

is entirely the **responsibility of the user**.

By using this project, you agree that:

* You will use it responsibly and ethically
* You will not use it for illegal purposes

The author **is not responsible** for any damage, loss, or legal consequences caused by misuse of this tool.

---

## 👨‍💻 Author

Developed by **KenXinDev**

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub!

---

## 📬 Notes

This tool is intended for:

* Learning purposes
* Experimentation
* Understanding system behavior

Use wisely and responsibly.
