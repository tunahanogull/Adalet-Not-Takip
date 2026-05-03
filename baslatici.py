import urllib.request
import os
import sys
import subprocess
import tkinter as tk

# --- AYARLAR KISMI ---
GUNCEL_KOD_LINKI = "https://raw.githubusercontent.com/tunahanogull/Adalet-Not-Takip/refs/heads/main/adalet_not_takip.py"
YEREL_DOSYA = "adalet_not_takip.py" # Dosyanın adını ne yaptıysan buraya o gelecek

def guncelleme_kontrol():
    try:
        # İnternetteki kodu çek
        cevap = urllib.request.urlopen(GUNCEL_KOD_LINKI, timeout=5)
        en_yeni_kod = cevap.read().decode('utf-8')
        
        # Bilgisayardaki mevcut kodu oku
        eski_kod = ""
        if os.path.exists(YEREL_DOSYA):
            with open(YEREL_DOSYA, "r", encoding="utf-8") as f:
                eski_kod = f.read()
                
        # KODLARI KARŞILAŞTIR
        if en_yeni_kod != eski_kod:
            durum_etiketi.config(text="🎉 Yeni Güncelleme Bulundu!\nSisteme Entegre Ediliyor...", fg="#a6e3a1") # Yeşil renk
            root.update()
            
            # Yeni kodu eski dosyanın üzerine yaz
            with open(YEREL_DOSYA, "w", encoding="utf-8") as f:
                f.write(en_yeni_kod)
            
            # Güncellendiğini 2 saniye ekranda gösterip uygulamayı aç
            root.after(2000, uygulamayi_baslat) 
        else:
            durum_etiketi.config(text="✅ Sistem Zaten Güncel!\nUygulama Başlatılıyor...", fg="#89b4fa") # Mavi renk
            root.update()
            
            # Güncel olduğunu 1 saniye gösterip uygulamayı aç
            root.after(1000, uygulamayi_baslat)
            
    except Exception as e:
        durum_etiketi.config(text="⚠️ Sunucuya Bağlanılamadı!\nMevcut Sürüm Açılıyor...", fg="#f38ba8") # Kırmızı renk
        root.update()
        root.after(2000, uygulamayi_baslat)

def uygulamayi_baslat():
    root.destroy() # Başlatıcı penceresini kapat
    if os.path.exists(YEREL_DOSYA):
        # sys.executable komutu, adliye bilgisayarındaki Python'ın kurulu olduğu yeri otomatik bulup dosyayı sorunsuz açar
        subprocess.Popen([sys.executable, YEREL_DOSYA]) 
    else:
        # Eğer bilgisayarda hiç kod yoksa ve internet de yoksa uyarı ver (İlk kurulum senaryosu)
        print("HATA: Bilgisayarda çalıştırılacak uygulama bulunamadı ve internete bağlanılamadı.")

# --- BAŞLATICI ARAYÜZÜ (ŞIK AÇILIŞ PENCERESİ) ---
root = tk.Tk()
root.title("Adalet Not Takip Updater")
root.geometry("400x160")
root.configure(bg="#1e1e2e") # Koyu tema arka plan
root.overrideredirect(True) # Pencere kenarlıklarını (Kapat, Küçült tuşlarını) gizler, profesyonel durur

# Pencereyi bilgisayar ekranının tam ortasına sabitleme matematiği
ekran_genisligi = root.winfo_screenwidth()
ekran_yuksekligi = root.winfo_screenheight()
x = (ekran_genisligi / 2) - (400 / 2)
y = (ekran_yuksekligi / 2) - (160 / 2)
root.geometry(f'400x160+{int(x)}+{int(y)}')

# Çerçeve tasarımı
cerceve = tk.Frame(root, bg="#313244", bd=2, relief="groove")
cerceve.pack(fill="both", expand=True, padx=5, pady=5)

tk.Label(cerceve, text="ADALET NOT TAKİP", font=("Segoe UI", 16, "bold"), bg="#313244", fg="#cdd6f4").pack(pady=(20, 5))

durum_etiketi = tk.Label(cerceve, text="⏳ Sunucuya bağlanılıyor...", font=("Segoe UI", 11), bg="#313244", fg="#a6adc8")
durum_etiketi.pack(pady=10)

# Ekrana çıkar çıkmaz güncellemeyi kontrol etmesi için tetikliyoruz
root.after(500, guncelleme_kontrol)

root.mainloop()