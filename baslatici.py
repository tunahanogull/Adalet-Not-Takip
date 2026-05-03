import urllib.request
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import base64
import hashlib
import random
import string
from tkcalendar import Calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials, db

# --- AYARLAR KISMI ---
GUNCEL_KOD_LINKI = "https://raw.githubusercontent.com/tunahanogull/Adalet-Not-Takip/main/adalet_not_takip.py"
YEREL_DOSYA = "adalet_not_takip.py" 
UYGULAMAYA_GEC = False  # Motor kontrol bayrağı

def kod_temizle(kod_metni):
    if not kod_metni: return ""
    satirlar = [s.rstrip() for s in kod_metni.splitlines()]
    return '\n'.join(satirlar).strip()

def guncelleme_kontrol():
    try:
        cevap = urllib.request.urlopen(GUNCEL_KOD_LINKI, timeout=5)
        en_yeni_kod = cevap.read().decode('utf-8-sig') 
        
        eski_kod = ""
        if os.path.exists(YEREL_DOSYA):
            with open(YEREL_DOSYA, "r", encoding="utf-8-sig") as f:
                eski_kod = f.read()
                
        yeni_temiz = kod_temizle(en_yeni_kod)
        eski_temiz = kod_temizle(eski_kod)
                
        if yeni_temiz != eski_temiz:
            durum_etiketi.config(text="🎉 Yeni Güncelleme Bulundu!\nSisteme Entegre Ediliyor...", fg="#a6e3a1") 
            root.update()
            
            with open(YEREL_DOSYA, "w", encoding="utf-8") as f:
                f.write(en_yeni_kod)
            
            root.after(2000, uygulamayi_baslat) 
        else:
            durum_etiketi.config(text="✅ Sistem Zaten Güncel!\nUygulama Başlatılıyor...", fg="#89b4fa") 
            root.update()
            
            root.after(1000, uygulamayi_baslat)
            
    except Exception as e:
        durum_etiketi.config(text="⚠️ Sunucuya Bağlanılamadı!\nMevcut Sürüm Açılıyor...", fg="#f38ba8") 
        root.update()
        root.after(2000, uygulamayi_baslat)

def uygulamayi_baslat():
    global UYGULAMAYA_GEC
    UYGULAMAYA_GEC = True
    root.destroy() # Başlatıcının motorunu güvenle durdurup pencereyi yok eder

# --- BAŞLATICI ARAYÜZÜ ---
root = tk.Tk()
root.title("Adalet Not Takip Updater")
root.geometry("400x160")
root.configure(bg="#1e1e2e") 
root.overrideredirect(True) 

ekran_genisligi = root.winfo_screenwidth()
ekran_yuksekligi = root.winfo_screenheight()
x = (ekran_genisligi / 2) - (400 / 2)
y = (ekran_yuksekligi / 2) - (160 / 2)
root.geometry(f'400x160+{int(x)}+{int(y)}')

cerceve = tk.Frame(root, bg="#313244", bd=2, relief="groove")
cerceve.pack(fill="both", expand=True, padx=5, pady=5)

tk.Label(cerceve, text="ADALET NOT TAKİP", font=("Segoe UI", 16, "bold"), bg="#313244", fg="#cdd6f4").pack(pady=(20, 5))

durum_etiketi = tk.Label(cerceve, text="⏳ Sunucuya bağlanılıyor...", font=("Segoe UI", 11), bg="#313244", fg="#a6adc8")
durum_etiketi.pack(pady=10)

root.after(500, guncelleme_kontrol)

# Başlatıcının kendi motoru burada çalışır ve kapanana kadar alt satıra geçmez.
root.mainloop()

# --- MOTORLARIN AYRILDIĞI NOKTA ---
if UYGULAMAYA_GEC and os.path.exists(YEREL_DOSYA):
    with open(YEREL_DOSYA, "r", encoding="utf-8") as f:
        ana_kod = f.read()
    
    # Motorun çalışması için gerekli ortamı hazırlıyoruz
    calisma_alani = globals().copy()
    calisma_alani['__name__'] = '__main__'
    
    try:
        # Kodları çalıştır
        exec(ana_kod, calisma_alani)
    except Exception as e:
        # EĞER BİR HATA OLURSA SESSİZCE KAPANMASIN, EKRANA YAZSIN!
        import traceback
        print("\n" + "="*50)
        print("KRİTİK BİR HATA OLUŞTU! İŞTE DETAYI:")
        print("="*50)
        traceback.print_exc()
        input("\nKapatmak için Enter'a basın...")