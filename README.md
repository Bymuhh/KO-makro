# KO Makro (Auto Key)

Knight Online için yardımcı makro: otomatik MP/HP pot, Oto Wolf, Oto Cure (7 debuff), Restore silme ve Combo.

> **Uyarı:** Bu araç kendi riskinizle kullanılır. Oyun kuralları / anti-cheat (Xigncode) riski size aittir. Yönetici yetkisi gerekir.

---

## Sıfırdan kurulum (Python olmayan yeni bilgisayar)

### 1) Gerekli olanlar

| Ne | Neden |
|----|--------|
| **Windows 10/11 (64-bit)** | Program Windows için yazıldı |
| **Python 3.10+** | `ko_makro.py` çalıştırır |
| **pip paketleri** | `mss`, `numpy`, `opencv-python` |
| **Bu repo dosyaları** | Kod + `Icon` klasörü |
| **Yönetici yetkisi** | Oyuna tuş göndermek için (UAC) |

İsteğe bağlı: Git (repo klonlamak için). Olmasa da ZIP indirmeyi kullanabilirsiniz.

---

### 2) Python kur

1. https://www.python.org/downloads/ adresinden **Windows installer (64-bit)** indirin.
2. Kurulumda mutlaka işaretleyin:
   - **Add python.exe to PATH**
3. Kurulumu tamamlayın.
4. Yeni bir **CMD** veya **PowerShell** açıp kontrol edin:

```bat
python --version
pip --version
```

Sürüm görünüyorsa Python hazırdır.

---

### 3) Projeyi indir

**Yöntem A – ZIP (en kolay)**

1. Bu sayfada yeşil **Code** → **Download ZIP**
2. ZIP’i masaüstüne çıkarın (ör. `KO-makro-main`)
3. Klasörün içinde `ko_makro.py`, `BASLAT.bat` ve `Icon` olmalı

**Yöntem B – Git**

```bat
cd %USERPROFILE%\Desktop
git clone https://github.com/Bymuhh/KO-makro.git
cd KO-makro
```

---

### 4) Python paketlerini kur

Proje klasöründe CMD/PowerShell açın:

```bat
cd masaüstü\KO-makro-main
pip install mss numpy opencv-python
```

> İlk açılışta program eksik paketleri de sorabilir; yine de önceden kurmak daha sağlıklıdır.

---

### 5) Klasör yapısı (bozmayın)

```text
KO-makro/
├── ko_makro.py          ← ana program
├── BASLAT.bat           ← çift tıkla başlat
├── Icon/
│   ├── restore.png      ← restore ikonu
│   ├── wolf.png         ← wolf buff ikonu
│   └── cure/            ← debuff şablonları
│       ├── atack.png
│       ├── malice.png
│       ├── massive.png
│       ├── parazit.png
│       ├── Reserlife.png
│       ├── superparazit.png
│       └── tourment.png
└── README.md
```

`Icon` klasörü `ko_makro.py` ile **aynı dizinde** kalmalıdır.

---

### 6) Çalıştırma

1. `BASLAT.bat` dosyasına **çift tıklayın**  
   veya:

```bat
python ko_makro.py
```

2. Windows **Yönetici olarak çalıştır** / UAC onayı isteyebilir → **Evet** deyin.
3. Knight Online da yönetici modundaysa makro da yönetici olmalıdır; aksi halde tuşlar oyuna gitmeyebilir.

---

### 7) İlk kullanım (program içinde)

1. **KO Pencere Seç** → Knight Online penceresini seçin  
2. **Oto MP / Oto HP**  
   - Bar Seç → ekranda barı sürükleyerek işaretleyin  
   - Tuş (1–9, 0) ve eşik % seçin  
3. **Oto Wolf** → `Icon/wolf.png` otomatik yüklenir; skill tuşunu seçin  
4. **Oto Cure**  
   - Bölge Seç → debuff alanını seçin  
   - Cure skill tuşunu seçin (1–9, 0)  
5. **Restore [R]**  
   - Bölge Seç → restore ikonunun olduğu alanı seçin  
   - Açıkken **R** tuşunu **0.3 sn** basılı tutun → 2 sol tık  
6. **Combo [Space]**  
   - Açıkken **Space**’i **0.30 sn** basılı tutun → `3rr` → 0.10s → `r×11` döngüsü  

Küçültünce mini panel açılır: **▲** devam, **■** bekleme. Panele tutup sürükleyebilirsiniz.

---

## Özellik özeti

| Özellik | Tetik | Not |
|---------|-------|-----|
| Oto MP | Eşik altı | HP ile aynı anda düşükse **önce MP** |
| Oto HP | Eşik altı | MP basıldıysa aynı turda HP basılmaz |
| Oto Wolf | Buff kaybolunca | ~3 sn sonra skill tuşu |
| Oto Cure | Debuff görününce | Sadece seçili bölge taranır |
| Restore | R 0.3 sn basılı | Seçili bölgede ikon bul → 2 sol tık |
| Combo | Space 0.30 sn | Basılı kaldığı sürece tekrarlar |

---

## Sık sorunlar

| Sorun | Çözüm |
|-------|--------|
| `python` bulunamadı | Python’u PATH ile yeniden kurun; terminali kapatıp açın |
| `No module named mss/cv2/numpy` | `pip install mss numpy opencv-python` |
| Tuşlar oyuna gitmiyor | Makroyu **Yönetici** çalıştırın; KO penceresini seçin |
| Restore / Cure bulamıyor | Bölgeyi yeniden seçin; `Icon` dosyalarının yerinde olduğundan emin olun |
| Cure şablon yok | `Icon/cure/*.png` dosyalarını kontrol edin |

---

## Gereksinimler (kısa)

```bat
pip install mss numpy opencv-python
```

- Python 3.10+ (Windows)
- Yönetici yetkisi
- `Icon` klasörü (restore / wolf / cure)

---

## Lisans / sorumluluk

Kişisel kullanım içindir. Oyun hesabı / ban riski kullanıcıya aittir.
