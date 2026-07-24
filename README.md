# Auto Key (KO Makro)

Knight Online yardımcı makro: Oto MP/HP pot, Wolf, Cure (7 debuff), Restore silme, Combo ve **Floody** (chat flood).

> **Uyarı:** Kendi riskinizle kullanın. Anti-cheat / ban riski size aittir. Yönetici yetkisi gerekir.

---

## Sıfırdan kurulum (Python olmayan PC)

### 1) Gerekli olanlar
| Ne | Neden |
|----|--------|
| Windows 10/11 (64-bit) | Program Windows için |
| Python 3.10+ | `Auto Key.py` çalışır |
| `pip install mss numpy opencv-python` | Ekran / görüntü |
| Bu repo + `Icon` klasörü | Kod ve şablonlar |
| Yönetici yetkisi | Oyuna tuş göndermek için |

### 2) Python kur
1. https://www.python.org/downloads/ → Windows 64-bit
2. **Add python.exe to PATH** işaretle
3. Kontrol: `python --version` / `pip --version`

### 3) Projeyi indir
- **Code → Download ZIP** veya:
```bat
git clone https://github.com/Bymuhh/KO-makro.git
cd KO-makro
```

### 4) Paketler
```bat
pip install mss numpy opencv-python
```

### 5) Çalıştır
- `BASLAT.bat` çift tıkla  
  veya: `python "Auto Key.py"`
- UAC / yönetici onayı verin

### Klasör yapısı
```text
KO-makro/
├── Auto Key.py      ← ana makro
├── floody.py        ← Floody chat sayfası
├── BASLAT.bat
├── BUILD_EXE.bat    ← isteğe bağlı exe derleme
└── Icon/
    ├── restore.png
    ├── wolf.png
    └── cure/        ← debuff PNG'leri
```

---

## Özellikler
| Özellik | Tetik |
|---------|--------|
| Oto MP / HP | Eşik altı (öncelik MP) |
| Oto Wolf | Buff kaybolunca |
| Oto Cure | Seçili bölgede debuff |
| Restore | **R** 0.3 sn basılı |
| Combo | **Space** 0.30 sn → 3rr → 0.10s → r×11 |
| Floody | Üstteki **💬 Floody** butonu |

Küçültünce mini panel: **▲** devam, **■** bekleme (sürüklenebilir).

---

## Exe (isteğe bağlı)
```bat
BUILD_EXE.bat
```
Çıktı: `Auto Key.exe` — `Icon` klasörü yanında kalsın.
