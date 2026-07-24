# Auto Key — Knight Online Makro Asistanı

Oyun içinde tekrar eden işleri azaltmak, dikkatinizi savaş ve harekete vermek için tasarlanmış bir **Windows yardımcı paneli**.  
Auto Key; pot, buff, debuff, restore ve combo gibi rutinleri tek yerden yönetmenize yardımcı olur. İsterseniz **Floody** sekmesiyle sohbet/flood döngüsünü de aynı pencereden kontrol edebilirsiniz.

> **Önemli uyarı:** Bu yazılım kendi sorumluluğunuzdadır. Oyun kuralları, anti-cheat (ör. Xigncode) ve hesap güvenliği riskleri size aittir. Yönetici yetkisiyle çalıştırılması önerilir.

---

## Program ne yapabilir? (Sırayla)

Aşağıdaki yetenekler, Auto Key’in sunduğu ana işlevlerdir:

1. **Oto HP Pot**  
   Seçtiğiniz HP bar bölgesini izler. Can yüzdeniz belirlediğiniz eşiğin altına düşerse, seçtiğiniz pot tuşuna basar.

2. **Oto MP Pot**  
   Mana barını aynı mantıkla izler. Mana eşik altına inince pot tuşuna basar.  
   **Öncelik kuralı:** HP ve MP aynı anda düşükse, o turda önce **MP** basılır; HP bir sonraki uygun turda devam eder.

3. **Oto Wolf**  
   Ekrandaki wolf buff ikonunu (`Icon/wolf.png`) takip eder. Buff kaybolunca kısa bir beklemenin ardından skill tuşunuza basar.

4. **Oto Cure**  
   `Icon/cure` klasöründeki debuff görsellerinden herhangi biri, sizin seçtiğiniz **küçük bölgede** görünürse cure skill tuşuna basar. Tüm ekranı taramaz; bu yüzden daha hızlı ve odaklıdır.

5. **Restore Silme**  
   Restore ikonunun olduğu alanı seçersiniz. **R** tuşunu yaklaşık **0,3 saniye** basılı tutunca program ikonu bulur ve **tek seferde 2 sol tık** atar. R’yi bırakana kadar tekrarlamaz.

6. **Combo [Space]**  
   **Space** tuşunu yaklaşık **0,30 saniye** basılı tutunca combo başlar: `3 → r → r`, sonra **0,10 sn** bekleme, ardından **11 kez r**. Space basılı kaldığı sürece döngü tekrar eder; bırakınca durur.

7. **Floody (Chat Flood)**  
   Üstteki **Floody** sekmesinden 4 mesajlık döngü, yazım modu, süre ve kısayol ayarlarıyla sohbet flood’u yönetebilirsiniz.

8. **Mini panel & bekleme**  
   Pencereyi küçültünce küçük, sürüklenebilir bir panel açılır. **■** ile makro beklemeye alınır, **▲** ile devam eder. Her zaman üstte kalabilir.

9. **KO pencere seçimi**  
   Tuşların doğru pencereye gitmesi için Knight Online penceresini listeden seçebilirsiniz.

---

## Nasıl kullanılır? (Adım adım)

### 1) Kurulum (sıfırdan bilgisayar)

#### Adım 1 — Python’u kurun
1. https://www.python.org/downloads/ adresinden Windows **64-bit** Python indirin.  
2. Kurulumda **Add python.exe to PATH** kutusunu işaretleyin.  
3. Kurulumu bitirin; yeni bir CMD/PowerShell açın:

```bat
python --version
pip --version
```

#### Adım 2 — Kütüphaneleri kurun

```bat
pip install mss numpy opencv-python
```

| Kütüphane | Rolü |
|-----------|------|
| `mss` | Hızlı ekran yakalama |
| `numpy` | Görüntü matrisleri |
| `opencv-python` | Şablon eşleştirme (ikon / debuff) |

Doğrulama:

```bat
python -c "import mss, numpy, cv2; print('OK')"
```

#### Adım 3 — Projeyi indirin
- GitHub’da **Code → Download ZIP** ile indirip masaüstüne açın  
  **veya**

```bat
cd %USERPROFILE%\Desktop
git clone https://github.com/Bymuhh/KO-makro.git
cd KO-makro
```

Klasör yapısı şöyle olmalıdır:

```text
KO-makro/
├── Auto Key.py          ← ana program
├── floody.py            ← Floody sayfası
├── BASLAT.bat           ← kolay başlatıcı
├── BUILD_EXE.bat        ← exe derleme (isteğe bağlı)
├── Icon/
│   ├── restore.png
│   ├── wolf.png
│   └── cure/            ← debuff şablonları
└── README.md
```

#### Adım 4 — Programı başlatın
- `BASLAT.bat` dosyasına çift tıklayın  
  **veya**

```bat
python "Auto Key.py"
```

- UAC / yönetici onayı gelirse **Evet** deyin.  
- Knight Online yönetici modundaysa Auto Key de yönetici olmalıdır.

---

### 2) İlk kullanım (oyun içinde)

1. **Üst bar → KO Pencere Seç**  
   Açık pencerelerden Knight Online’ı seçin.

2. **Makro sekmesi** (varsayılan)  
   Sol üstte **Makro | Floody** sekmeleri vardır; Makro’da kalın.

3. **HP Bar kartı**  
   - **Bölge Seç** → HP barını sürükleyerek işaretleyin  
   - Eşik (%), pot tuşu (1–9, 0), bekleme (ms) ayarlayın  
   - **Kaydet** → **Aktif** switch’ini açın  

4. **MP Bar kartı**  
   Aynı adımları mana barı için tekrarlayın.

5. **Oto Wolf**  
   `Icon/wolf.png` hazırsa skill tuşunu seçip özelliği açın.

6. **Oto Cure**  
   - **Bölge Seç** → debuff ikonlarının göründüğü buff alanını seçin  
   - Cure skill tuşunu seçin  
   - Özelliği açın  
   - Yeni PNG eklediyseniz debuff listesini yenileyin  

7. **Restore [R]**  
   - **Bölge Seç** → restore ikonunun olduğu yeri seçin  
   - Hassasiyeti gerekirse ayarlayın  
   - Özelliği açın  
   - Oyunda **R**’yi ~0,3 sn basılı tutun → 2 sol tık  

8. **Combo [Space]**  
   Özelliği açın; savaşta **Space**’i ~0,30 sn basılı tutun. Bırakınca durur.

9. **Floody sekmesi**  
   Mesajları yazın, döngü/gecikme/kısayol seçin, Master Switch’i ON yapıp BAŞLAT’a basın.

10. **Üstte switch** (sağ üst)  
    Paneli her zaman diğer pencerelerin üstünde tutar.

11. **Küçült**  
    Mini panel açılır: sürükleyin, **■** ile duraklatın, **▲** ile devam ettirin. Maksimize / genişlet ile tam panele dönün.

---

## Arayüz haritası (kısa)

| Bölge | Ne var? |
|-------|---------|
| Sol üst | **Makro** / **Floody** sekmeleri |
| Sağ üst | KO Pencere Seç + **Üstte** switch |
| Orta | HP/MP kartları, Wolf, Cure, Restore, Combo |
| Alt | Durum özeti: MP pot, HP pot, Restore |

---

## Exe üretmek (isteğe bağlı)

Python kurulu bir bilgisayarda:

```bat
BUILD_EXE.bat
```

Oluşan dosya: `Auto Key.exe`  
`Icon` klasörünü exe ile aynı klasörde tutun. Exe de yönetici onayı ister.

> Not: Bu depoda büyük `.exe` dosyası tutulmaz; kaynak kod ve derleme scripti yeterlidir.

---

## Sık karşılaşılan sorunlar

| Belirti | Ne yapmalısınız? |
|---------|------------------|
| `python` tanınmıyor | PATH ile Python’u yeniden kurun; terminali kapatıp açın |
| `No module named mss` / `cv2` / `numpy` | `pip install mss numpy opencv-python` |
| Tuşlar oyuna gitmiyor | Yönetici çalıştırın + KO penceresini seçin |
| Restore / Cure bulamıyor | Bölgeyi yeniden seçin; `Icon` dosyalarını kontrol edin |
| Cure şablon yok | `Icon/cure` içine PNG ekleyin ve yenileyin |
| Mini panel yanlışlıkla açıldı | Sadece gerçek küçültmede açılır; bölge seçimi mini moda düşürmez |

---

## Gereksinim özeti

1. Windows 10 / 11 (64-bit)  
2. Python 3.10+ (**Add to PATH**)  
3. `pip install mss numpy opencv-python`  
4. Bu depo: `Auto Key.py` + `floody.py` + `Icon`  
5. Yönetici yetkisi  

---

## Sorumluluk reddi

Auto Key eğitim / kişisel otomasyon amaçlı bir yardımcıdır.  
Hesap cezası, ban veya anti-cheat müdahalesi riski tamamen kullanıcıya aittir. Oyunun resmi kurallarına saygı gösterin.

---

**Repo:** https://github.com/Bymuhh/KO-makro  
İyi oyunlar — dikkatiniz savaşta, rutinler Auto Key’de kalsın.
