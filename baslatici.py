import urllib.request
import os
import sys
import subprocess
import tkinter as tk

# --- AYARLAR KISMI ---
GUNCEL_KOD_LINKI = "https://raw.githubusercontent.com/tunahanogull/Adalet-Not-Takip/refs/heads/main/adalet_not_takip.py"
YEREL_DOSYA = "uygulama.py" 

# --- ÇELİK FİLTRE: GÖRÜNMEZ KARAKTERLERİ YOK EDER ---
def kod_temizle(kod_metni):
    if not kod_metni: return ""
    # 1. Satırları ayır (Windows, Mac, Linux tüm enter türlerini eşitler)
    # 2. Her satırın sonundaki görünmez boşlukları sil (rstrip)
    # 3. Hepsini standart birleştir ve baştaki/sondaki boşlukları at
    satirlar = [s.rstrip() for s in kod_metni.splitlines()]
    return '\n'.join(satirlar).strip()

def guncelleme_kontrol():
    try:
        # İnternetteki kodu çek (utf-8-sig ile gizli BOM imzasını siliyoruz)
        cevap = urllib.request.urlopen(GUNCEL_KOD_LINKI, timeout=5)
        en_yeni_kod = cevap.read().decode('utf-8-sig') 
        
        # Bilgisayardaki mevcut kodu oku
        eski_kod = ""
        if os.path.exists(YEREL_DOSYA):
            with open(YEREL_DOSYA, "r", encoding="utf-8-sig") as f:
                eski_kod = f.read()
                
        # KODLARI FİLTREDEN GEÇİRİP SAF HALLERİNİ KIYASLA
        yeni_temiz = kod_temizle(en_yeni_kod)
        eski_temiz = kod_temizle(eski_kod)
                
        if yeni_temiz != eski_temiz:
            durum_etiketi.config(text="🎉 Yeni Güncelleme Bulundu!\nSisteme Entegre Ediliyor...", fg="#a6e3a1") 
            root.update()
            
            # Yeni kodu kaydederken standart utf-8 kullanıyoruz
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
    root.destroy() 
    if os.path.exists(YEREL_DOSYA):
        subprocess.Popen([sys.executable, YEREL_DOSYA]) 
    else:
        print("HATA: Bilgisayarda çalıştırılacak uygulama bulunamadı ve internete bağlanılamadı.")

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

root.mainloop()