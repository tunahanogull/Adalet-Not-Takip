import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import base64
import hashlib
import random
import string
from tkcalendar import Calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- SİSTEM AYARLARI ---
ADMIN_KEY = base64.b64decode("YW5hZG9sdWFkYWxldC4zNA==").decode('utf-8') 
KULLANICI_VERITABANI = "kullanicilar.json"
AYARLAR_DOSYASI = "ayarlar.json"

# --- TEMA SİSTEMİ ---
THEMES = {
    "dark": {
        "bg": "#1e1e2e", "fg": "#cdd6f4", "accent": "#313244", "sidebar": "#181825",
        "btn_fg": "#1e1e2e", "blue": "#89b4fa", "red": "#f38ba8", "green": "#a6e3a1", "gray": "#a6adc8", "purple": "#cba6f7"
    },
    "light": {
        "bg": "#f4f4f9", "fg": "#333333", "accent": "#ffffff", "sidebar": "#e5e5ea",
        "btn_fg": "#ffffff", "blue": "#4a90e2", "red": "#e74c3c", "green": "#2ecc71", "gray": "#888888", "purple": "#9b59b6"
    }
}

def ayar_yukle():
    if os.path.exists(AYARLAR_DOSYASI):
        with open(AYARLAR_DOSYASI, "r") as f:
            return json.load(f)
    return {"tema": "dark"}

def ayar_kaydet(ayarlar_dict):
    with open(AYARLAR_DOSYASI, "w") as f:
        json.dump(ayarlar_dict, f, indent=4)

def sifre_hashle(sifre):
    return hashlib.sha256(sifre.encode()).hexdigest()

class GirisEkrani:
    def __init__(self, root):
        self.root = root
        self.root.title("Yıldız  - Giriş")
        self.root.geometry("450x650")
        self.ayarlar = ayar_yukle()
        self.tema_adi = self.ayarlar.get("tema", "dark")
        self.t = THEMES[self.tema_adi]
        self.root.configure(bg=self.t["bg"])
        
        if not os.path.exists(KULLANICI_VERITABANI):
            with open(KULLANICI_VERITABANI, "w") as f:
                json.dump({}, f)
                
        # --- OTOMATİK GİRİŞ (BENİ HATIRLA) KONTROLÜ ---
        if self.ayarlar.get("beni_hatirla") and self.ayarlar.get("son_kullanici"):
            k_adi = self.ayarlar["son_kullanici"]
            sifre_b64 = self.ayarlar.get("son_sifre", "")
            try:
                sifre = base64.b64decode(sifre_b64.encode()).decode()
                if self.sessiz_giris(k_adi, sifre):
                    return # Başarılıysa giriş ekranını hiç çizmeden atla
            except: pass
            
        self.sayfa_giris()

    def sessiz_giris(self, k_adi, sifre):
        with open(KULLANICI_VERITABANI, "r") as f:
            kullanicilar = json.load(f)
            
        if k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre_hashle(sifre):
            gizli_anahtar = kullanicilar[k_adi]["gizli_anahtar"]
            self.ekrani_temizle()
            NotUygulamasi(self.root, k_adi, gizli_anahtar) 
            return True
        return False

    def ekrani_temizle(self):
        for w in self.root.winfo_children(): w.destroy()
        self.root.configure(bg=self.t["bg"])

    def sayfa_giris(self):
        self.ekrani_temizle()
        
        ust_panel = tk.Frame(self.root, bg=self.t["bg"])
        ust_panel.pack(fill="x", pady=10, padx=10)
        tk.Button(ust_panel, text="☀️/🌙 Tema", bg=self.t["accent"], fg=self.t["fg"], bd=0, 
                  font=("Segoe UI", 9, "bold"), cursor="hand2", command=self.tema_degistir).pack(side="right")

        frame = tk.Frame(self.root, bg=self.t["bg"])
        frame.pack(expand=True, fill="both", padx=50)

        tk.Label(frame, text="Adalet Not Takip", bg=self.t["bg"], fg=self.t["blue"], font=("Segoe UI", 24, "bold")).pack(pady=(20, 5))
        tk.Label(frame, text="Sisteme Giriş Yapın", bg=self.t["bg"], fg=self.t["gray"], font=("Segoe UI", 10)).pack(pady=(0, 30))

        tk.Label(frame, text="Kullanıcı Adı", bg=self.t["bg"], fg=self.t["fg"], font=("Segoe UI", 11)).pack(anchor="w")
        kullanici_ent = tk.Entry(frame, font=("Segoe UI", 13), bg=self.t["accent"], fg=self.t["fg"], insertbackground=self.t["fg"], bd=0)
        kullanici_ent.pack(fill="x", pady=(5, 15), ipady=10)

        tk.Label(frame, text="Şifre", bg=self.t["bg"], fg=self.t["fg"], font=("Segoe UI", 11)).pack(anchor="w")
        sifre_ent = tk.Entry(frame, font=("Segoe UI", 13), bg=self.t["accent"], fg=self.t["fg"], show="*", bd=0, insertbackground=self.t["fg"])
        sifre_ent.pack(fill="x", pady=(5, 10), ipady=10)

        # --- BENİ HATIRLA VE ŞİFREMİ UNUTTUM SATIRI ---
        alt_frame = tk.Frame(frame, bg=self.t["bg"])
        alt_frame.pack(fill="x", pady=(0, 20))
        
        self.beni_hatirla_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(alt_frame, text="Beni Hatırla", variable=self.beni_hatirla_var, bg=self.t["bg"], fg=self.t["fg"], 
                            selectcolor=self.t["accent"], activebackground=self.t["bg"], activeforeground=self.t["fg"], bd=0, font=("Segoe UI", 10))
        cb.pack(side="left")

        tk.Button(alt_frame, text="Şifremi Unuttum", bg=self.t["bg"], fg=self.t["blue"], bd=0, font=("Segoe UI", 9, "underline"), 
                  cursor="hand2", command=self.sayfa_sifre_unuttum).pack(side="right", pady=2)

        tk.Button(frame, text="GİRİŞ YAP", bg=self.t["blue"], fg=self.t["btn_fg"], font=("Segoe UI", 12, "bold"), 
                  bd=0, cursor="hand2", command=lambda: self.giris_yap(kullanici_ent.get(), sifre_ent.get())).pack(fill="x", ipady=12)
                  
        tk.Button(frame, text="Yeni Hesap Oluştur", bg=self.t["accent"], fg=self.t["fg"], font=("Segoe UI", 10, "bold"), 
                  bd=0, cursor="hand2", command=self.sayfa_kayit).pack(fill="x", pady=15, ipady=10)

    def sayfa_kayit(self):
        self.ekrani_temizle()
        frame = tk.Frame(self.root, bg=self.t["bg"])
        frame.pack(expand=True, fill="both", padx=50, pady=30)

        tk.Label(frame, text="Kayıt Ol", bg=self.t["bg"], fg=self.t["green"], font=("Segoe UI", 22, "bold")).pack(pady=(0, 20))

        tk.Label(frame, text="Kullanıcı Adı", bg=self.t["bg"], fg=self.t["fg"], font=("Segoe UI", 10)).pack(anchor="w")
        k_ent = tk.Entry(frame, font=("Segoe UI", 12), bg=self.t["accent"], fg=self.t["fg"], bd=0, insertbackground=self.t["fg"])
        k_ent.pack(fill="x", pady=(2, 10), ipady=8)

        tk.Label(frame, text="E-posta Adresi (Şifre sıfırlama için)", bg=self.t["bg"], fg=self.t["fg"], font=("Segoe UI", 10)).pack(anchor="w")
        mail_ent = tk.Entry(frame, font=("Segoe UI", 12), bg=self.t["accent"], fg=self.t["fg"], bd=0, insertbackground=self.t["fg"])
        mail_ent.pack(fill="x", pady=(2, 10), ipady=8)

        tk.Label(frame, text="Şifre", bg=self.t["bg"], fg=self.t["fg"], font=("Segoe UI", 10)).pack(anchor="w")
        sifre_ent = tk.Entry(frame, font=("Segoe UI", 12), bg=self.t["accent"], fg=self.t["fg"], show="*", bd=0, insertbackground=self.t["fg"])
        sifre_ent.pack(fill="x", pady=(2, 10), ipady=8)

        tk.Label(frame, text="Admin Kayıt Anahtarı", bg=self.t["bg"], fg=self.t["red"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        admin_ent = tk.Entry(frame, font=("Segoe UI", 12), bg=self.t["accent"], fg=self.t["red"], show="*", bd=0, insertbackground=self.t["fg"])
        admin_ent.pack(fill="x", pady=(2, 20), ipady=8)

        tk.Button(frame, text="KAYDI TAMAMLA", bg=self.t["green"], fg=self.t["btn_fg"], font=("Segoe UI", 11, "bold"), 
                  bd=0, cursor="hand2", command=lambda: self.kayit_ol(k_ent.get(), mail_ent.get(), sifre_ent.get(), admin_ent.get())).pack(fill="x", ipady=10)
                  
        tk.Button(frame, text="Giriş Ekranına Dön", bg=self.t["bg"], fg=self.t["gray"], bd=0, font=("Segoe UI", 10), 
                  cursor="hand2", command=self.sayfa_giris).pack(pady=15)

    def sayfa_sifre_unuttum(self):
        self.ekrani_temizle()
        frame = tk.Frame(self.root, bg=self.t["bg"])
        frame.pack(expand=True, fill="both", padx=50, pady=50)

        tk.Label(frame, text="Şifre Sıfırlama", bg=self.t["bg"], fg=self.t["purple"], font=("Segoe UI", 22, "bold")).pack(pady=(0, 20))
        tk.Label(frame, text="Kayıtlı kullanıcı adınızı girin.\nE-posta adresinize geçici şifre iletilecektir.", bg=self.t["bg"], fg=self.t["gray"], font=("Segoe UI", 10)).pack(pady=(0, 20))

        tk.Label(frame, text="Kullanıcı Adınız", bg=self.t["bg"], fg=self.t["fg"], font=("Segoe UI", 11)).pack(anchor="w")
        k_ent = tk.Entry(frame, font=("Segoe UI", 13), bg=self.t["accent"], fg=self.t["fg"], bd=0, insertbackground=self.t["fg"])
        k_ent.pack(fill="x", pady=(5, 20), ipady=10)

        tk.Button(frame, text="YENİ ŞİFRE GÖNDER", bg=self.t["purple"], fg=self.t["btn_fg"], font=("Segoe UI", 11, "bold"), 
                  bd=0, cursor="hand2", command=lambda: self.sifre_sifirla(k_ent.get())).pack(fill="x", ipady=10)
                  
        tk.Button(frame, text="İptal ve Geri Dön", bg=self.t["bg"], fg=self.t["gray"], bd=0, font=("Segoe UI", 10), 
                  cursor="hand2", command=self.sayfa_giris).pack(pady=15)

    def tema_degistir(self):
        self.tema_adi = "light" if self.tema_adi == "dark" else "dark"
        self.ayarlar["tema"] = self.tema_adi
        ayar_kaydet(self.ayarlar)
        self.t = THEMES[self.tema_adi]
        self.sayfa_giris()

    def giris_yap(self, k_adi, sifre):
        k_adi = k_adi.strip().lower()
        if not k_adi or not sifre:
            messagebox.showwarning("Hata", "Alanlar boş bırakılamaz!")
            return

        with open(KULLANICI_VERITABANI, "r") as f:
            kullanicilar = json.load(f)

        if k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre_hashle(sifre):
            
            # --- BENİ HATIRLA İŞLEMİ ---
            if self.beni_hatirla_var.get():
                self.ayarlar["beni_hatirla"] = True
                self.ayarlar["son_kullanici"] = k_adi
                self.ayarlar["son_sifre"] = base64.b64encode(sifre.encode()).decode()
            else:
                self.ayarlar["beni_hatirla"] = False
                self.ayarlar.pop("son_kullanici", None)
                self.ayarlar.pop("son_sifre", None)
            ayar_kaydet(self.ayarlar)

            gizli_anahtar = kullanicilar[k_adi]["gizli_anahtar"]
            self.ekrani_temizle()
            NotUygulamasi(self.root, k_adi, gizli_anahtar) 
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!\nSisteme erişim engellendi.")

    def kayit_ol(self, k_adi, mail, sifre, admin_key):
        k_adi = k_adi.strip().lower()
        if not k_adi or not mail or not sifre or not admin_key:
            messagebox.showwarning("Hata", "Tüm alanları doldurmalısınız!")
            return
            
        if admin_key != ADMIN_KEY:
            messagebox.showerror("Güvenlik İhlali", "Admin Key hatalı! Kayıt işlemi reddedildi.")
            return

        with open(KULLANICI_VERITABANI, "r") as f:
            kullanicilar = json.load(f)

        if k_adi in kullanicilar:
            messagebox.showwarning("Hata", "Bu kullanıcı adı zaten alınmış!")
            return

        kisisel_anahtar = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        kullanicilar[k_adi] = {
            "sifre": sifre_hashle(sifre),
            "eposta": mail, 
            "gizli_anahtar": kisisel_anahtar
        }

        with open(KULLANICI_VERITABANI, "w") as f:
            json.dump(kullanicilar, f, indent=4)

        messagebox.showinfo("Başarılı", "Kayıt başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.")
        self.sayfa_giris()

    def sifre_sifirla(self, k_adi):
        k_adi = k_adi.strip().lower()
        with open(KULLANICI_VERITABANI, "r") as f:
            kullanicilar = json.load(f)

        if k_adi not in kullanicilar:
            messagebox.showerror("Hata", "Sistemde böyle bir kullanıcı bulunamadı!")
            return

        yeni_sifre = str(random.randint(100000, 999999))
        kullanicilar[k_adi]["sifre"] = sifre_hashle(yeni_sifre)
        k_mail = kullanicilar[k_adi].get("eposta", "Bilinmiyor")

        with open(KULLANICI_VERITABANI, "w") as f:
            json.dump(kullanicilar, f, indent=4)

        gonderen_mail = "adaletnottakip@gmail.com" 
        uygulama_sifresi = "jvomdgdepznwskxw" 

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Adalet Not Takip - Şifre Sıfırlama Talebi'
            msg['From'] = f"Adalet Not Takip <{gonderen_mail}>"
            msg['To'] = k_mail

            logo_linki = "https://i.postimg.cc/GhdKVf2L/3ebb5f0b-36a6-46f5-842d-dd1a00b3c173-Picsart-Background-Remover.png"

            duz_yazi = f"Adalet Not Takip\nGeçici Şifreniz: {yeni_sifre}\nLütfen sisteme giriş yapıp şifrenizi güncelleyin."
            msg.attach(MIMEText(duz_yazi, 'plain', 'utf-8'))

            html_icerik = f"""
            <html>
              <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; margin: 0; padding: 40px 20px;">
                <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 40px 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center;">
                  
                  <img src="{logo_linki}" alt="Adalet Not Takip Logo" style="width: 300px; margin-bottom: 15px;">
                  
                  <h2 style="color: #313244; margin-bottom: 20px; font-size: 24px;">Şifre Sıfırlama Talebi</h2>
                  <p style="color: #555555; font-size: 16px; text-align: left; line-height: 1.6;">Merhaba,</p>
                  <p style="color: #555555; font-size: 16px; text-align: left; line-height: 1.6;">
                    <strong>Adalet Not Takip</strong> sistemine giriş yapabilmeniz için geçici şifreniz başarıyla oluşturulmuştur.
                  </p>
                  
                  <div style="background-color: #4a90e2; color: #ffffff; padding: 15px; font-size: 32px; font-weight: bold; border-radius: 6px; margin: 30px 0; letter-spacing: 5px;">
                    {yeni_sifre}
                  </div>
                  
                  <p style="color: #555555; font-size: 15px; text-align: left; line-height: 1.6;">
                    Güvenliğiniz için lütfen sisteme giriş yaptıktan sonra <b>Ayarlar</b> menüsünden şifrenizi güncelleyiniz.
                  </p>
                  
                  <br>
                  <p style="color: #555555; font-size: 15px; text-align: left;">
                    İyi çalışmalar dileriz,<br>
                    <strong style="color: #313244;">Adalet Not Takip Asistanı</strong>
                  </p>
                  
                  <hr style="border: none; border-top: 1px solid #eeeeee; margin-top: 40px; margin-bottom: 20px;">
                  <p style="color: #999999; font-size: 12px;">
                    Bu e-posta sistem tarafından otomatik olarak gönderilmiştir. Lütfen bu mesaja yanıt vermeyiniz.
                  </p>
                </div>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html_icerik, 'html', 'utf-8'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls() 
            server.login(gonderen_mail, uygulama_sifresi)
            server.send_message(msg) 
            server.quit()

            messagebox.showinfo("Başarılı", f"Geçici şifreniz {k_mail} adresine başarıyla gönderildi!")
            
        except Exception as e:
            messagebox.showerror("Mail Hatası", f"Mail gönderilemedi. Lütfen internet bağlantınızı ve mail ayarlarınızı kontrol edin.\nHata detayı: {e}")
        
        self.sayfa_giris()

# --- ANA UYGULAMA (ADALET NOT TAKİP) ---
class NotUygulamasi:
    def __init__(self, root, kullanici_adi, gizli_anahtar):
        self.root = root
        self.kullanici_adi = kullanici_adi
        self.gizli_anahtar = gizli_anahtar 
        self.data_file = f"data_{self.kullanici_adi}.json"
        
        self.ayarlar = ayar_yukle()
        self.tema_adi = self.ayarlar.get("tema", "dark")
        self.t = THEMES[self.tema_adi]
        
        self.root.title(f"Adalet Not Takip - {self.kullanici_adi.capitalize()}")
        self.root.geometry("900x650")
        
        self.oncelikler = {
            "1 - Yüksek": self.t["red"], "2 - Orta": self.t["blue"], 
            "3 - Düşük": self.t["green"], "4 - Sözlü Gün": self.t["purple"]
        }
        
        self.notlar = self.veri_yukle()
        self.widget = None
        self.arayuz_kur()
        self.hatirlatici_kontrol()

    def sifrele(self, metin, anahtar):
        xorlanmis = "".join(chr(ord(m) ^ ord(anahtar[i % len(anahtar)])) for i, m in enumerate(metin))
        return base64.b64encode(xorlanmis.encode('utf-8')).decode('utf-8')

    def coz(self, sifreli_metin, anahtar):
        try:
            decode_edilmis = base64.b64decode(sifreli_metin.encode('utf-8')).decode('utf-8')
            return "".join(chr(ord(m) ^ ord(anahtar[i % len(anahtar)])) for i, m in enumerate(decode_edilmis))
        except: return ""

    def veri_yukle(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    sifreli_veri = f.read()
                    if not sifreli_veri: return []
                    cozulmus = json.loads(self.coz(sifreli_veri, self.gizli_anahtar))
                    return cozulmus
            except:
                messagebox.showerror("Hata", "Veri dosyası okunamadı!")
                return []
        return []

    def veri_kaydet(self):
        veri_str = json.dumps(self.notlar, ensure_ascii=False)
        with open(self.data_file, "w", encoding="utf-8") as f:
            f.write(self.sifrele(veri_str, self.gizli_anahtar))

    def arayuz_kur(self):
        for w in self.root.winfo_children(): w.destroy()
        self.root.configure(bg=self.t["bg"])
        
        self.oncelikler = {
            "1 - Yüksek": self.t["red"], "2 - Orta": self.t["blue"], 
            "3 - Düşük": self.t["green"], "4 - Sözlü Gün": self.t["purple"]
        }

        self.sidebar = tk.Frame(self.root, bg=self.t["sidebar"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text=f"👤 {self.kullanici_adi.upper()}", bg=self.t["sidebar"], fg=self.t["blue"], font=("Segoe UI", 14, "bold")).pack(pady=30)

        # MENÜYE "HESAP DEĞİŞTİR" EKLENDİ
        menus = [
            ("📝 Yeni Not Ekle", self.sayfa_yeni_not),
            ("📚 Tüm İşler", lambda: self.sayfa_not_listesi("Tümü")),
            ("📌 Sözlü Gün", lambda: self.sayfa_not_listesi("Sözlü")),
            ("⚙️ Ayarlar", self.sayfa_ayarlar),
            ("🔄 Hesap Değiştir", self.hesap_degistir)
        ]

        for metin, komut in menus:
            btn = tk.Button(self.sidebar, text=metin, bg=self.t["sidebar"], fg=self.t["fg"], font=("Segoe UI", 11, "bold"), 
                            bd=0, anchor="w", padx=20, cursor="hand2", activebackground=self.t["accent"], command=komut)
            btn.pack(fill="x", pady=5, ipady=10)

        # ÇIKIŞ YAP ARTIK UYGULAMAYI KAPATACAK
        tk.Button(self.sidebar, text="🚪 Çıkış Yap", bg=self.t["red"], fg=self.t["btn_fg"], font=("Segoe UI", 10, "bold"), 
                  bd=0, cursor="hand2", command=self.cikis_yap).pack(side="bottom", fill="x", ipady=10)

        self.icerik_alani = tk.Frame(self.root, bg=self.t["bg"])
        self.icerik_alani.pack(side="right", fill="both", expand=True)

        self.widget_kur()
        self.sayfa_yeni_not()

    def icerigi_temizle(self):
        for w in self.icerik_alani.winfo_children(): w.destroy()

    def sayfa_yeni_not(self):
        self.icerigi_temizle()
        tk.Label(self.icerik_alani, text="Yeni Not Ekle", bg=self.t["bg"], fg=self.t["fg"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=30, pady=(30, 20))

        kutu = tk.Frame(self.icerik_alani, bg=self.t["accent"], padx=20, pady=20)
        kutu.pack(fill="x", padx=30)

        tk.Label(kutu, text="Eklemek İstediğiniz Notunuz :", bg=self.t["accent"], fg=self.t["gray"], font=("Segoe UI", 10)).pack(anchor="w")
        self.not_metni = tk.Entry(kutu, bg=self.t["bg"], fg=self.t["fg"], bd=0, font=("Segoe UI", 12), insertbackground=self.t["fg"])
        self.not_metni.pack(fill="x", ipady=10, pady=(5, 15))

        alt_satir = tk.Frame(kutu, bg=self.t["accent"])
        alt_satir.pack(fill="x")

        self.oncelik_cb = ttk.Combobox(alt_satir, values=list(self.oncelikler.keys()), state="readonly", width=15)
        self.oncelik_cb.set("2 - Orta")
        self.oncelik_cb.pack(side="left")

        tk.Label(alt_satir, text="📅", bg=self.t["accent"], fg=self.t["fg"]).pack(side="left", padx=(15, 2))
        self.tarih_var = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        self.tarih_entry = tk.Label(alt_satir, textvariable=self.tarih_var, bg=self.t["bg"], fg=self.t["fg"], width=11, anchor="center", font=("Segoe UI", 10))
        self.tarih_entry.pack(side="left", ipady=4)

        tk.Button(alt_satir, text="▼ Seç", bg=self.t["blue"], fg=self.t["btn_fg"], font=("Segoe UI", 8, "bold"), bd=0, cursor="hand2", command=self.takvim_ac).pack(side="left", ipady=3, ipadx=5, padx=(0, 15))

        tk.Label(alt_satir, text="⏰", bg=self.t["accent"], fg=self.t["fg"]).pack(side="left", padx=(15, 2))
        self.vakit_entry = tk.Entry(alt_satir, bg=self.t["bg"], fg=self.t["fg"], width=8, bd=0, justify="center")
        self.vakit_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.vakit_entry.pack(side="left", ipady=4)

        tk.Button(kutu, text="KAYDET", bg=self.t["green"], fg=self.t["btn_fg"], font=("Segoe UI", 11, "bold"), 
                  bd=0, cursor="hand2", command=self.not_ekle).pack(fill="x", pady=(20, 0), ipady=10)

    def takvim_ac(self):
        if hasattr(self, "takvim_pop") and self.takvim_pop.winfo_exists(): self.takvim_pop.destroy()
        self.takvim_pop = tk.Toplevel(self.root)
        self.takvim_pop.overrideredirect(True)
        self.takvim_pop.geometry(f"+{self.root.winfo_pointerx()}+{self.root.winfo_pointery()}")
        self.takvim_pop.attributes("-topmost", True)
        
        c = tk.Frame(self.takvim_pop, bg=self.t["blue"], padx=2, pady=2)
        c.pack(fill="both", expand=True)
        
        cal = Calendar(c, font=("Segoe UI", 10), selectmode='day', locale='tr_TR',
            background=self.t["blue"], foreground="white", headersbackground=self.t["accent"], headersforeground=self.t["fg"], 
            selectbackground=self.t["green"], selectforeground=self.t["bg"], normalbackground=self.t["bg"], normalforeground=self.t["fg"], 
            weekendbackground=self.t["bg"], weekendforeground=self.t["red"], othermonthbackground=self.t["bg"], othermonthforeground=self.t["gray"], borderwidth=0)
        cal.pack()
        tk.Button(c, text="Kapat", bg=self.t["red"], fg="white", font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2", command=self.takvim_pop.destroy).pack(fill="x", pady=(2, 0), ipady=2)
        
        def tarih_sec(e):
            self.tarih_var.set(cal.selection_get().strftime("%d.%m.%Y"))
            self.takvim_pop.destroy()
        cal.bind("<<CalendarSelected>>", tarih_sec)

    def sayfa_not_listesi(self, filtre="Tümü"):
        self.icerigi_temizle()
        baslik = "Tüm İşlerim" if filtre == "Tümü" else "📌 Sözlü Gün"
        tk.Label(self.icerik_alani, text=baslik, bg=self.t["bg"], fg=self.t["fg"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=30, pady=(30, 20))

        canvas = tk.Canvas(self.icerik_alani, bg=self.t["bg"], highlightthickness=0)
        scroll_y = ttk.Scrollbar(self.icerik_alani, orient="vertical", command=canvas.yview)
        liste_frame = tk.Frame(canvas, bg=self.t["bg"])

        liste_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=liste_frame, anchor="nw", width=620)
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(30, 0), pady=(0, 30))
        scroll_y.pack(side="right", fill="y", padx=(0, 30), pady=(0, 30))

        sirali = sorted(self.notlar, key=lambda x: x["oncelik"])
        gosterilen_sayi = 0

        for n in sirali:
            if filtre == "Tümü" and "Sözlü" in n["oncelik"]: continue 
            if filtre == "Sözlü" and "Sözlü" not in n["oncelik"]: continue 

            gosterilen_sayi += 1
            renk = self.oncelikler.get(n["oncelik"], self.t["blue"])
            satir = tk.Frame(liste_frame, bg=self.t["accent"], pady=15, padx=15)
            satir.pack(fill="x", pady=5)
            
            tk.Label(satir, text="●", fg=renk, bg=self.t["accent"], font=("Arial", 14)).pack(side="left")
            lbl_metin = f"{n['metin']}\n⏳ {n['zaman']}  |  Kategori: {n['oncelik'].split('-')[1].strip()}"
            tk.Label(satir, text=lbl_metin, bg=self.t["accent"], fg=self.t["fg"], font=("Segoe UI", 11), justify="left", wraplength=450).pack(side="left", padx=15)
            
            tk.Button(satir, text="Tamamla ✔", bg=self.t["bg"], fg=self.t["green"], bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", command=lambda id=n["id"]: self.not_sil(id, filtre)).pack(side="right", ipady=5, padx=10)

        if gosterilen_sayi == 0:
            tk.Label(liste_frame, text="Burada henüz kayıt yok.", bg=self.t["bg"], fg=self.t["gray"], font=("Segoe UI", 11, "italic")).pack(pady=20)

    def sayfa_ayarlar(self):
        self.icerigi_temizle()
        tk.Label(self.icerik_alani, text="Sistem Ayarları", bg=self.t["bg"], fg=self.t["fg"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=30, pady=(30, 20))

        ayar_kutusu = tk.Frame(self.icerik_alani, bg=self.t["accent"], padx=20, pady=20)
        ayar_kutusu.pack(fill="x", padx=30, pady=(0, 20))
        tk.Label(ayar_kutusu, text="Görünüm Teması:", bg=self.t["accent"], fg=self.t["fg"], font=("Segoe UI", 12)).pack(side="left")
        t_metin = "🌞 Light Moda Geç" if self.tema_adi == "dark" else "🌙 Dark Moda Geç"
        tk.Button(ayar_kutusu, text=t_metin, bg=self.t["blue"], fg=self.t["btn_fg"], font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.tema_degistir_ana_uygulama).pack(side="right", ipady=8, padx=10)

        sifre_kutu = tk.Frame(self.icerik_alani, bg=self.t["accent"], padx=20, pady=20)
        sifre_kutu.pack(fill="x", padx=30)
        
        tk.Label(sifre_kutu, text="Hesap Şifresini Değiştir", bg=self.t["accent"], fg=self.t["fg"], font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 15))
        
        tk.Label(sifre_kutu, text="Eski Şifreniz", bg=self.t["accent"], fg=self.t["gray"], font=("Segoe UI", 9)).pack(anchor="w")
        eski_ent = tk.Entry(sifre_kutu, font=("Segoe UI", 11), bg=self.t["bg"], fg=self.t["fg"], show="*", bd=0, insertbackground=self.t["fg"])
        eski_ent.pack(fill="x", pady=(2, 10), ipady=5)

        tk.Label(sifre_kutu, text="Yeni Şifre", bg=self.t["accent"], fg=self.t["gray"], font=("Segoe UI", 9)).pack(anchor="w")
        yeni_ent = tk.Entry(sifre_kutu, font=("Segoe UI", 11), bg=self.t["bg"], fg=self.t["fg"], show="*", bd=0, insertbackground=self.t["fg"])
        yeni_ent.pack(fill="x", pady=(2, 10), ipady=5)

        tk.Button(sifre_kutu, text="ŞİFREYİ GÜNCELLE", bg=self.t["purple"], fg=self.t["btn_fg"], font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", 
                  command=lambda: self.sifre_degistir(eski_ent.get(), yeni_ent.get())).pack(fill="x", pady=(10, 0), ipady=8)

    def sifre_degistir(self, eski, yeni):
        if not eski or not yeni:
            messagebox.showwarning("Uyarı", "Lütfen şifre alanlarını doldurun.")
            return
            
        with open(KULLANICI_VERITABANI, "r") as f:
            kullanicilar = json.load(f)
            
        if kullanicilar[self.kullanici_adi]["sifre"] == sifre_hashle(eski):
            kullanicilar[self.kullanici_adi]["sifre"] = sifre_hashle(yeni)
            with open(KULLANICI_VERITABANI, "w") as f:
                json.dump(kullanicilar, f, indent=4)
            messagebox.showinfo("Başarılı", "Şifreniz başarıyla güncellendi!")
            self.sayfa_ayarlar() 
        else:
            messagebox.showerror("Hata", "Eski şifrenizi yanlış girdiniz!")

    def tema_degistir_ana_uygulama(self):
        self.tema_adi = "light" if self.tema_adi == "dark" else "dark"
        self.ayarlar["tema"] = self.tema_adi
        ayar_kaydet(self.ayarlar)
        self.t = THEMES[self.tema_adi]
        if self.widget: self.widget.destroy()
        self.arayuz_kur()

    def not_ekle(self):
        metin, tarih, saat = self.not_metni.get().strip(), self.tarih_var.get().strip(), self.vakit_entry.get().strip()
        if not metin:
            messagebox.showwarning("Uyarı", "Not metni boş olamaz!")
            return
        self.notlar.append({"id": os.urandom(4).hex(), "metin": metin, "oncelik": self.oncelik_cb.get(), "zaman": f"{tarih} {saat}", "uyarildi": False})
        self.veri_kaydet()
        messagebox.showinfo("Başarılı", "Başarıyla eklendi!")
        self.sayfa_yeni_not()
        self.widget_guncelle()

    def not_sil(self, not_id, aktif_filtre):
        self.notlar = [n for n in self.notlar if n["id"] != not_id]
        self.veri_kaydet()
        self.sayfa_not_listesi(aktif_filtre)
        self.widget_guncelle()

    def widget_kur(self):
        if self.widget: self.widget.destroy()
        self.widget = tk.Toplevel(self.root)
        self.widget.geometry("280x300+150+150")
        self.widget.configure(bg=self.t["accent"])
        self.widget.overrideredirect(True)
        self.widget_sabit = True
        self.widget.attributes("-topmost", self.widget_sabit)
        self.widget.bind("<ButtonPress-1>", lambda e: setattr(self.widget, 'x', e.x) or setattr(self.widget, 'y', e.y))
        self.widget.bind("<B1-Motion>", lambda e: self.widget.geometry(f"+{self.widget.winfo_pointerx() - self.widget.x}+{self.widget.winfo_pointery() - self.widget.y}"))
        bf = tk.Frame(self.widget, bg=self.t["sidebar"])
        bf.pack(fill="x")
        tk.Label(bf, text="📌 Tüm İşler", bg=self.t["sidebar"], fg=self.t["fg"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=10, ipady=5)
        self.pin_btn = tk.Button(bf, text="📌", bg=self.t["sidebar"], fg=self.t["green"], font=("Segoe UI", 10), bd=0, cursor="hand2", command=self.w_sabitle)
        self.pin_btn.pack(side="right", padx=10)
        self.w_icerik = tk.Frame(self.widget, bg=self.t["accent"])
        self.w_icerik.pack(fill="both", expand=True, padx=10, pady=5)
        self.widget_guncelle()

    def w_sabitle(self):
        self.widget_sabit = not self.widget_sabit
        if self.widget_sabit:
            self.pin_btn.configure(fg=self.t["green"])
            self.widget.attributes("-topmost", True)
            self.widget.lift() 
        else:
            self.pin_btn.configure(fg=self.t["gray"])
            self.widget.attributes("-topmost", False)

    def widget_guncelle(self):
        for w in self.w_icerik.winfo_children(): w.destroy()
        gecerli = [n for n in self.notlar if "Sözlü" not in n["oncelik"]]
        sirali = sorted(gecerli, key=lambda x: x["oncelik"])
        if not sirali:
            tk.Label(self.w_icerik, text="Süper, işin yok!", bg=self.t["accent"], fg=self.t["gray"]).pack(pady=30)
            return
        for n in sirali:
            satir = tk.Frame(self.w_icerik, bg=self.t["accent"])
            satir.pack(fill="x", pady=3)
            tk.Label(satir, text="●", bg=self.t["accent"], fg=self.oncelikler.get(n["oncelik"])).pack(side="left")
            o_metin = n["oncelik"].split("-")[1].strip()
            kisalt = n["metin"] if len(n["metin"]) <= 14 else n["metin"][:11] + "..."
            tk.Label(satir, text=f"{kisalt} ({o_metin})", bg=self.t["accent"], fg=self.t["fg"], font=("Segoe UI", 9)).pack(side="left")

    def hatirlatici_kontrol(self):
        su_an = datetime.now().strftime("%d.%m.%Y %H:%M")
        for n in self.notlar:
            if n["zaman"] == su_an and not n.get("uyarildi"):
                if self.widget: self.widget.lift()
                baslik = "Sözlü Vakti!" if "Sözlü" in n["oncelik"] else "Zamanı Geldi!"
                messagebox.showinfo(baslik, f"GÖREV: {n['metin']}\nÖncelik: {n['oncelik'].split('-')[1].strip()}")
                n["uyarildi"] = True
                self.veri_kaydet()
        if self.widget and self.widget.winfo_exists():
            if getattr(self, 'widget_sabit', True): self.widget.attributes("-topmost", True)
            else: self.widget.attributes("-topmost", False)
        self.root.after(1000, self.hatirlatici_kontrol)

    # --- YENİ EKLENEN: HESAP DEĞİŞTİR FONKSİYONU ---
    def hesap_degistir(self):
        self.ayarlar["beni_hatirla"] = False
        self.ayarlar.pop("son_kullanici", None)
        self.ayarlar.pop("son_sifre", None)
        ayar_kaydet(self.ayarlar)
        
        if self.widget: self.widget.destroy()
        for w in self.root.winfo_children(): w.destroy()
        GirisEkrani(self.root)

    # --- GÜNCELLENEN: KOMPLE ÇIKIŞ YAP FONKSİYONU ---
    def cikis_yap(self):
        if self.widget: self.widget.destroy()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GirisEkrani(root)
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()