# Auto Key (KO Makro)

Knight Online yardımcı makro: Oto MP/HP pot, Wolf, Cure (7 debuff), Restore silme, Combo ve **Floody** (chat flood).

> **Uyarı:** Kendi riskinizle kullanın. Anti-cheat / ban riski size aittir. Yönetici yetkisi gerekir.

---

## Sıfırdan kurulum (yeni / Python’suz bilgisayar)

Aşağıdaki adımları **sırayla** uygulayın.

### Aşama 1 — Python kur

1. Tarayıcıda açın: https://www.python.org/downloads/
2. **Download Python** (Windows 64-bit) indirin.
3. Kurulumu başlatın.
4. İlk ekranda mutlaka işaretleyin:
   - **Add python.exe to PATH**
5. **Install Now** ile kurun.
6. Kurulum bitince **yeni** bir CMD veya PowerShell açıp kontrol edin:

```bat
python --version
pip --version
```

İkisi de sürüm gösteriyorsa Python hazırdır.  
`python` bulunamadı diyorsa: PATH’i işaretleyip Python’u yeniden kurun, terminali kapatıp açın.

---

### Aşama 2 — Gerekli kütüphaneleri kur

CMD / PowerShell’de:

```bat
pip install mss numpy opencv-python
```

| Paket | Ne işe yarar |
|-------|----------------|
| `mss` | Ekran görüntüsü alma |
| `numpy` | Görüntü verisi |
| `opencv-python` | İkon / debuff eşleştirme (`cv2`) |

Kontrol (isteğe bağlı):

```bat
python -c "import mss, numpy, cv2; print('OK')"
```

`OK` yazarsa paketler tamamdır.

---

### Aşama 3 — Programı indir

**Yöntem A (kolay) — ZIP**

1. Bu sayfada yeşil **Code** → **Download ZIP**
2. ZIP’i masaüstüne çıkarın (ör. `KO-makro-main`)

**Yöntem B — Git**

```bat
cd %USERPROFILE%\Desktop
git clone https://github.com/Bymuhh/KO-makro.git
cd KO-makro
```

Klasörde şunlar olmalı:

```text
KO-makro/
├── Auto Key.py
├── floody.py
├── BASLAT.bat
├── BUILD_EXE.bat
├── Icon/
│   ├── restore.png
│   ├── wolf.png
│   └── cure/          ← debuff PNG’leri
└── README.md
```

`Icon` klasörü `Auto Key.py` ile **aynı dizinde** kalmalıdır.

---

### Aşama 4 — Çalıştır

1. Klasöre girin.
2. `BASLAT.bat` dosyasına **çift tıklayın**  
   veya:

```bat
cd masaüstü\KO-makro-main
python "Auto Key.py"
```

3. Windows **Yönetici / UAC** sorarsa **Evet** deyin.  
   Knight Online yönetici modundaysa makro da yönetici olmalıdır.

---

### Aşama 5 — İlk ayarlar (program içinde)

1. Üstteki **KO Pencere Seç** → Knight Online penceresini seçin  
2. **HP / MP** kartlarında: Bölge Seç → eşik / tuş → Kaydet → Aktif  
3. **Oto Wolf / Cure / Restore / Combo** ihtiyaçlarına göre açın  
4. **Floody** sekmesi: chat flood ayarları  

Küçültünce mini panel: **▲** devam, **■** bekleme (sürüklenebilir).

---

## Özellik özeti

| Özellik | Tetik |
|---------|--------|
| Oto MP / HP | Eşik altı (**öncelik MP**) |
| Oto Wolf | Buff kaybolunca |
| Oto Cure | Seçili bölgede debuff |
| Restore | **R** 0.3 sn basılı |
| Combo | **Space** 0.30 sn → 3rr → 0.10s → r×11 |
| Floody | Üst sekme **Floody** |

---

## Exe derleme (isteğe bağlı)

Python kurulu PC’de:

```bat
BUILD_EXE.bat
```

Çıktı: `Auto Key.exe`  
`Icon` klasörü exe yanında kalsın. Exe için de yönetici onayı gerekir.

---

## Sık sorunlar

| Sorun | Çözüm |
|-------|--------|
| `python` bulunamadı | PATH ile Python’u yeniden kur; terminali yeniden aç |
| `No module named mss` / `cv2` / `numpy` | `pip install mss numpy opencv-python` |
| Tuşlar oyuna gitmiyor | Makroyu **Yönetici** çalıştır; KO penceresini seç |
| Restore / Cure bulamıyor | Bölgeyi yeniden seç; `Icon` dosyalarını kontrol et |
| Cure şablon yok | `Icon/cure/*.png` klasörünü kontrol et |

---

## Kısa gereksinim listesi

1. Windows 10/11 (64-bit)  
2. Python 3.10+ (**Add to PATH**)  
3. `pip install mss numpy opencv-python`  
4. Bu repo (`Auto Key.py` + `floody.py` + `Icon`)  
5. Yönetici yetkisi  

---

## Sorumluluk

Kişisel kullanım içindir. Oyun hesabı / ban riski kullanıcıya aittir.
