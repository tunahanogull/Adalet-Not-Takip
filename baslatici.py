import urllib.request
import os

# Evden güncellediğin kodun GitHub'daki saf (Raw) linki
GUNCEL_KOD_LINKI = "https://raw.githubusercontent.com/tunahanogull/Adalet-Not-Takip/refs/heads/main/Python/uygulama.py?token=GHSAT0AAAAAAD4ALGZ2YJRPPZF7STKKB7XI2PXK4MQ"

print("⏳ Sunucuya bağlanılıyor, güncellemeler kontrol ediliyor...")

try:
    # 1. İnternetteki en güncel kodu çekiyoruz
    cevap = urllib.request.urlopen(GUNCEL_KOD_LINKI)
    en_yeni_kod = cevap.read().decode('utf-8')

    # 2. İş yerindeki bilgisayarda bulunan eski kodun üzerine yazıyoruz
    with open("adalet_not_takip.py", "w", encoding="utf-8") as dosya:
        dosya.write(en_yeni_kod)
        
    print("✅ Sistem tamamen güncel! Uygulama başlatılıyor...\n")

except Exception as e:
    print("⚠️ İnternet bağlantısı kurulamadı veya sunucuya ulaşılamadı!")
    print("Mevcut sürümle devam ediliyor...\n")

# 3. İndirme bittikten sonra ana uygulamayı çalıştırıyoruz
os.system("python adalet_not_takip.py")