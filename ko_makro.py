"""
KO Makro - Knight Online Makro Asistani
Gereksinimler: pip install mss numpy opencv-python
"""
import sys
import os
import time
import threading
import subprocess
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ══════════════════════════════════════════════
#  YÖNETİCİ YETKİSİ KONTROLÜ
#  Knight Online yönetici olarak çalışıyorsa
#  makronun da yönetici yetkisine ihtiyacı var.
# ══════════════════════════════════════════════
def _yonetici_mi():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

if not _yonetici_mi():
    # Yönetici yetkisiyle yeniden başlat
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,                          # hwnd
            "runas",                       # "Yönetici olarak çalıştır"
            sys.executable,               # python.exe
            " ".join(f'"{a}"' for a in sys.argv),  # argümanlar
            None,                          # çalışma dizini
            1                              # SW_SHOWNORMAL
        )
        if ret > 32:
            sys.exit(0)   # Yeni süreç açıldı, eskisini kapat
        r = tk.Tk(); r.withdraw()
        messagebox.showwarning(
            "Yonetici Yetkisi",
            "UAC iptal edildi veya yetki alinamadi.\n\n"
            "Knight Online yonetici modundaysa makro da yonetici olarak "
            "calistirilmalidir; aksi halde tuslar oyuna gitmeyebilir.",
            parent=r)
        r.destroy()
    except Exception:
        pass

# ── BASLAT.bat otomatik olustur (sadece .py modunda) ──
if not getattr(sys, "frozen", False):
    try:
        _bat_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BASLAT.bat")
        _py_yolu = sys.executable.replace("/", "\\")
        _script_yolu = os.path.abspath(__file__).replace("/", "\\")
        with open(_bat_yolu, "w", encoding="utf-8") as _f:
            _f.write(
                "@echo off\n"
                "chcp 65001 >nul\n"
                "title KO Makro\n"
                f'"{_py_yolu}" "{_script_yolu}"\n'
                "if errorlevel 1 (\n"
                "    echo.\n"
                "    echo HATA! Yukardaki mesaji kopyalayip ilet.\n"
                "    pause\n"
                ")\n"
            )
    except Exception:
        pass

# ══════════════════════════════════════════════
#  PAKET KONTROLU
# ══════════════════════════════════════════════
def _paket_kontrol():
    eksik = []
    for modul, pip_adi in [("mss","mss"),("numpy","numpy"),("cv2","opencv-python")]:
        try:
            __import__(modul)
        except ImportError:
            eksik.append(pip_adi)
    if not eksik:
        return True
    r = tk.Tk(); r.withdraw()
    ok = messagebox.askyesno(
        "Eksik Kutuphane",
        "Su paketler eksik:\n  " + ", ".join(eksik) +
        "\n\nOtomatik yuklensin mi?\n(Yüklendikten sonra makroyu yeniden başlatın!)")
    r.destroy()
    if ok:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + eksik)
            r2 = tk.Tk(); r2.withdraw()
            messagebox.showinfo("Tamam",
                "Paketler yuklendi!\nLutfen makroyu yeniden baslatın.")
            r2.destroy()
        except Exception as e:
            r3 = tk.Tk(); r3.withdraw()
            messagebox.showerror("Hata", f"Yukleme basarisiz:\n{e}")
            r3.destroy()
    sys.exit(0)

if not getattr(sys, "frozen", False):
    _paket_kontrol()

import numpy as np
import mss as _mss_lib
import cv2

# ══════════════════════════════════════════════
#  GIRIS MOTORU — ctypes SendInput (scan code)
#  Knight Online DirectInput ile uyumlu,
#  surucü gerektirmez.
# ══════════════════════════════════════════════

# Scan code tablosu (USB HID / PS/2 Set 1)
_SC = {
    '0':0x0B,'1':0x02,'2':0x03,'3':0x04,'4':0x05,
    '5':0x06,'6':0x07,'7':0x08,'8':0x09,'9':0x0A,
    'a':0x1E,'b':0x30,'c':0x2E,'d':0x20,'e':0x12,
    'f':0x21,'g':0x22,'h':0x23,'i':0x17,'j':0x24,
    'k':0x25,'l':0x26,'m':0x32,'n':0x31,'o':0x18,
    'p':0x19,'q':0x10,'r':0x13,'s':0x1F,'t':0x14,
    'u':0x16,'v':0x2F,'w':0x11,'x':0x2D,'y':0x15,
    'z':0x2C,
    'f1':0x3B,'f2':0x3C,'f3':0x3D,'f4':0x3E,
    'f5':0x3F,'f6':0x40,'f7':0x41,'f8':0x42,
    'f9':0x43,'f10':0x44,'f11':0x57,'f12':0x58,
    'space':0x39,'enter':0x1C,'esc':0x01,
}

# Windows SendInput yapıları
class _KI(ctypes.Structure):
    _fields_ = [("wVk",wintypes.WORD),("wScan",wintypes.WORD),
                 ("dwFlags",wintypes.DWORD),("time",wintypes.DWORD),
                 ("dwExtraInfo",ctypes.POINTER(ctypes.c_ulong))]

class _MI(ctypes.Structure):
    _fields_ = [("dx",wintypes.LONG),("dy",wintypes.LONG),
                 ("mouseData",wintypes.DWORD),("dwFlags",wintypes.DWORD),
                 ("time",wintypes.DWORD),
                 ("dwExtraInfo",ctypes.POINTER(ctypes.c_ulong))]

class _IU(ctypes.Union):
    _fields_ = [("ki",_KI),("mi",_MI)]

class _INPUT(ctypes.Structure):
    _fields_ = [("type",wintypes.DWORD),("_input",_IU)]

_KEYEVENTF_SCANCODE = 0x0008
_KEYEVENTF_KEYUP    = 0x0002
_MOUSEEVENTF_MOVE   = 0x0001
_MOUSEEVENTF_ABS    = 0x8000
_MOUSEEVENTF_LDOWN  = 0x0002
_MOUSEEVENTF_LUP    = 0x0004

# Insan benzeri tus zamanlamasi (cok hizli basim tespit riskini azaltir)
TUS_BASILI_SURE = 0.055   # tus basili tutma (~55 ms)
TUS_BIRAK_SONRA = 0.045   # birakma sonrasi ara (~45 ms)
ODAK_BEKLE      = 0.065   # KO odaklanma beklemesi
MOUSE_TIK_ARA   = 0.070   # cift tik araligi

_SW = ctypes.windll.user32.SendInput
_GW = ctypes.windll.user32.GetSystemMetrics
_extra = ctypes.pointer(ctypes.c_ulong(0))

def _key(scan, up=False):
    flags = _KEYEVENTF_SCANCODE | (_KEYEVENTF_KEYUP if up else 0)
    i = _INPUT(type=1, _input=_IU(ki=_KI(wVk=0,wScan=scan,
               dwFlags=flags,time=0,dwExtraInfo=_extra)))
    _SW(1, ctypes.byref(i), ctypes.sizeof(i))

def _mouse_move(x, y):
    ax = int(x * 65535 / _GW(0))
    ay = int(y * 65535 / _GW(1))
    i = _INPUT(type=0, _input=_IU(mi=_MI(dx=ax,dy=ay,mouseData=0,
               dwFlags=_MOUSEEVENTF_MOVE|_MOUSEEVENTF_ABS,
               time=0,dwExtraInfo=_extra)))
    _SW(1, ctypes.byref(i), ctypes.sizeof(i))

def _mouse_click(down=True):
    flag = _MOUSEEVENTF_LDOWN if down else _MOUSEEVENTF_LUP
    i = _INPUT(type=0, _input=_IU(mi=_MI(dx=0,dy=0,mouseData=0,
               dwFlags=flag,time=0,dwExtraInfo=_extra)))
    _SW(1, ctypes.byref(i), ctypes.sizeof(i))

def _scan_bas(sc):
    _key(sc, up=False)
    time.sleep(TUS_BASILI_SURE)
    _key(sc, up=True)
    time.sleep(TUS_BIRAK_SONRA)

class _RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

# Aktif KO penceresi
_ko_hwnd = 0

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

def _ko_odak_getir(hwnd):
    """KO penceresini one getirir (pot/restore icin)."""
    my_tid  = _kernel32.GetCurrentThreadId()
    fg_hwnd = _user32.GetForegroundWindow()
    fg_tid  = _user32.GetWindowThreadProcessId(fg_hwnd, None)
    ko_tid  = _user32.GetWindowThreadProcessId(hwnd, None)
    _user32.AttachThreadInput(my_tid, fg_tid, True)
    _user32.AttachThreadInput(my_tid, ko_tid, True)
    _user32.ShowWindow(hwnd, 5)
    _user32.SetForegroundWindow(hwnd)
    _user32.BringWindowToTop(hwnd)
    time.sleep(ODAK_BEKLE)
    _user32.AttachThreadInput(my_tid, fg_tid, False)
    _user32.AttachThreadInput(my_tid, ko_tid, False)

def _hwnd_bolge(hwnd):
    r = _RECT()
    if _user32.GetWindowRect(hwnd, ctypes.byref(r)):
        w, h = r.right - r.left, r.bottom - r.top
        if w > 0 and h > 0:
            return {"top": r.top, "left": r.left, "width": w, "height": h}
    return None

def _ko_tus_bas(hwnd, k, odak_zorla=False):
    """
    DirectInput uyumlu tus basma.
    odak_zorla=True  → KO'yu one getirip bas (pot/restore)
    odak_zorla=False → KO zaten odaktaysa bas, degilse atla (combo)
    """
    sc = _SC.get(str(k).lower(), 0)
    if not sc:
        print(f"[GIRIS] Bilinmeyen tus: {k}")
        return

    if odak_zorla:
        _ko_odak_getir(hwnd)
    elif _user32.GetForegroundWindow() != hwnd:
        return

    _scan_bas(sc)

class _G:
    @staticmethod
    def press(k, odak_zorla=True):
        global _ko_hwnd
        if _ko_hwnd and _user32.IsWindow(_ko_hwnd):
            _ko_tus_bas(_ko_hwnd, k, odak_zorla=odak_zorla)
        else:
            sc = _SC.get(str(k).lower(), 0)
            if sc:
                _scan_bas(sc)

    @staticmethod
    def moveTo(x, y, duration=0.12):
        _mouse_move(x, y)

    @staticmethod
    def ikiSolTik():
        """Tam 2 kez sol tik (restore icin)."""
        _mouse_click(True)
        time.sleep(MOUSE_TIK_ARA * 0.5)
        _mouse_click(False)
        time.sleep(MOUSE_TIK_ARA * 0.4)
        _mouse_click(True)
        time.sleep(MOUSE_TIK_ARA * 0.5)
        _mouse_click(False)

    @staticmethod
    def doubleClick():
        for _ in range(2):
            _mouse_click(True);  time.sleep(MOUSE_TIK_ARA * 0.6)
            _mouse_click(False); time.sleep(MOUSE_TIK_ARA)

giris = _G()
INPUT_MOTOR = "DirectInput (AttachThread+ScanCode)"
print(f"[GIRIS] Motor: {INPUT_MOTOR}")

# ── KO Pencere Tespiti ─────────────────────────
_KO_BASLIKLAR = [
    "KnightOnLine Client","KnightOnLine","Knight OnLine",
    "Knight Online","USKO","XTKO","MYKO","DRAKO","EPKO",
]

def pencere_listesi():
    """Tüm görünür pencereleri döndür: [(hwnd, başlık)]"""
    sonuc = []
    _CB = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_size_t, ctypes.c_size_t)
    def _cb(hwnd, _):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
            t = buf.value.strip()
            if t:
                sonuc.append((hwnd, t))
        return True
    ctypes.windll.user32.EnumWindows(_CB(_cb), 0)
    return sorted(sonuc, key=lambda x: x[1].lower())

def ko_bul_otomatik():
    global _ko_hwnd
    for hwnd, baslik in pencere_listesi():
        bl = baslik.lower()
        for ko in _KO_BASLIKLAR:
            if ko.lower() in bl:
                _ko_hwnd = hwnd
                print(f"[KO] Otomatik bulundu: {baslik} ({hwnd:#x})")
                return hwnd
    return 0

# Başlangıçta otomatik ara
ko_bul_otomatik()

# ══════════════════════════════════════════════
#  DEGISKENLER
# ══════════════════════════════════════════════
mana_alani = None
mana_aktif = False
mana_esik  = 30
mana_tus   = "1"

hp_alani = None
hp_aktif = False
hp_esik  = 30
hp_tus   = "2"

wolf_aktif = False
wolf_tus   = "3"
WOLF_BEKLE = 3.0
_wolf_sablon = None
_wolf_goruldu = False
_wolf_gitti_zamani = 0.0
_wolf_durum_fn = None

cure_aktif = False
cure_alani = None
cure_tus   = "4"
CURE_BEKLE = 1.0
_cure_sablonlar = []   # [(ad, img), ...]
_cure_son_basma = 0.0
_cure_durum_fn = None

POT_BEKLE = 0.3
RESTORE_BEKLE = 0.3

restore_aktif   = False
restore_alani   = None
ESLESME_ESIGI   = 0.80
_restore_sablon = None
_VK_RESTORE = 0x52   # R
_restore_islemde = False
_restore_baslangic = 0.0
_restore_tetiklendi = False
_restore_durum_fn = None

combo_aktif  = False
_VK_COMBO = 0x20     # Space
COMBO_BEKLE     = 0.30
COMBO_3RR_BEKLE = 0.10
COMBO_R_SAYISI  = 11   # rrrrrrrrrrr
DONGU_ARA    = 0.09
_combo_baslangic = None
makro_duraklatildi = False


def _combo_basili():
    return bool(_user32.GetAsyncKeyState(_VK_COMBO) & 0x8000)

def _combo_adim(k):
    """Combo adimi: Space birakildiysa veya kapaliysa False doner."""
    if makro_duraklatildi or not combo_aktif or not _combo_basili():
        return False
    giris.press(k, odak_zorla=False)
    return True

def combo_dongusu():
    global _combo_baslangic
    while True:
        if makro_duraklatildi or not combo_aktif or not _combo_basili():
            _combo_baslangic = None
            time.sleep(DONGU_ARA)
            continue
        simdi = time.time()
        if _combo_baslangic is None:
            _combo_baslangic = simdi
            time.sleep(DONGU_ARA)
            continue
        if simdi - _combo_baslangic < COMBO_BEKLE:
            time.sleep(DONGU_ARA)
            continue
        try:
            ok = True
            for k in ("3", "r", "r"):
                if not _combo_adim(k):
                    ok = False
                    break
            if ok and combo_aktif and _combo_basili():
                time.sleep(COMBO_3RR_BEKLE)
                for _ in range(COMBO_R_SAYISI):
                    if not _combo_adim("r"):
                        break
        except Exception as e:
            print(f"[COMBO] {e}")

def _uygulama_dizinleri():
    """Script veya PyInstaller .exe konumlari."""
    dizinler = []
    if getattr(sys, "frozen", False):
        dizinler.append(os.path.dirname(os.path.abspath(sys.executable)))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            dizinler.append(meipass)
    else:
        try:
            dizinler.append(os.path.dirname(os.path.abspath(__file__)))
        except Exception:
            pass
        try:
            dizinler.append(os.path.dirname(os.path.abspath(sys.argv[0])))
        except Exception:
            pass
    dizinler.append(os.getcwd())
    seen, out = set(), []
    for d in dizinler:
        if d and d not in seen:
            seen.add(d)
            out.append(d)
    return out

# restore.png yolu — Icon klasoru
def _restore_yolu_bul():
    deneme = _uygulama_dizinleri()
    for d in deneme:
        p = os.path.join(d, "Icon", "restore.png")
        if os.path.isfile(p):
            return p
    for d in deneme:
        if os.path.isdir(d):
            return os.path.join(d, "Icon", "restore.png")
    return os.path.join(os.getcwd(), "Icon", "restore.png")

RESTORE_YOL = _restore_yolu_bul()

def _wolf_yolu_bul():
    deneme = _uygulama_dizinleri()
    for d in deneme:
        p = os.path.join(d, "Icon", "wolf.png")
        if os.path.isfile(p):
            return p
    for d in deneme:
        if os.path.isdir(d):
            return os.path.join(d, "Icon", "wolf.png")
    return os.path.join(os.getcwd(), "Icon", "wolf.png")

WOLF_YOL = _wolf_yolu_bul()

def _cure_klasor_bul():
    for d in _uygulama_dizinleri():
        p = os.path.join(d, "Icon", "cure")
        if os.path.isdir(p):
            return p
    return os.path.join(os.getcwd(), "Icon", "cure")

CURE_KLASOR = _cure_klasor_bul()

def _gorsel_oku(yol):
    """Windows Turkce yol uyumlu PNG okuma."""
    try:
        buf = np.fromfile(yol, dtype=np.uint8)
        if buf.size == 0:
            return None
        return cv2.imdecode(buf, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"[GORSEL] Okuma hatasi: {e}")
        return None

def sablon_yukle(yol=None):
    global _restore_sablon, RESTORE_YOL
    hedef = yol or RESTORE_YOL
    _restore_sablon = None
    if os.path.isfile(hedef):
        img = _gorsel_oku(hedef)
        if img is not None and img.size > 0:
            _restore_sablon = img
            RESTORE_YOL = hedef
            print(f"[RESTORE] Yuklendi: {hedef}  ({img.shape[1]}x{img.shape[0]})")
            return True
        print(f"[RESTORE] Bozuk dosya: {hedef}")
    else:
        print(f"[RESTORE] Bulunamadi: {hedef}")
    return False

def wolf_sablon_yukle(yol=None):
    global _wolf_sablon, WOLF_YOL
    hedef = yol or WOLF_YOL
    _wolf_sablon = None
    if os.path.isfile(hedef):
        img = _gorsel_oku(hedef)
        if img is not None and img.size > 0:
            _wolf_sablon = img
            WOLF_YOL = hedef
            print(f"[WOLF] Yuklendi: {hedef}  ({img.shape[1]}x{img.shape[0]})")
            return True
        print(f"[WOLF] Bozuk dosya: {hedef}")
    else:
        print(f"[WOLF] Bulunamadi: {hedef}")
    return False

def cure_sablonlari_yukle(klasor=None):
    """Icon/cure altindaki tum PNG debuff sablonlarini yukle."""
    global _cure_sablonlar, CURE_KLASOR
    hedef = klasor or _cure_klasor_bul()
    CURE_KLASOR = hedef
    _cure_sablonlar = []
    if not os.path.isdir(hedef):
        print(f"[CURE] Klasor yok: {hedef}")
        return 0
    for ad in sorted(os.listdir(hedef)):
        if not ad.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            continue
        yol = os.path.join(hedef, ad)
        img = _gorsel_oku(yol)
        if img is not None and img.size > 0:
            _cure_sablonlar.append((ad, img))
            print(f"[CURE] Yuklendi: {ad}  ({img.shape[1]}x{img.shape[0]})")
        else:
            print(f"[CURE] Okunamadi: {ad}")
    print(f"[CURE] Toplam {len(_cure_sablonlar)} debuff sablonu")
    return len(_cure_sablonlar)

sablon_yukle()
wolf_sablon_yukle()
cure_sablonlari_yukle()

# ══════════════════════════════════════════════
#  MAKRO MANTIGI
# ══════════════════════════════════════════════
def _sablon_skor(sablon):
    """Ekranda sablon skorunu dondurur (0.0 - 1.0)."""
    offset_x = offset_y = 0
    grab_bolge = None
    if _ko_hwnd and _user32.IsWindow(_ko_hwnd):
        grab_bolge = _hwnd_bolge(_ko_hwnd)
    with _mss_lib.mss() as sct:
        if grab_bolge:
            bgr = np.array(sct.grab(grab_bolge))[:, :, :3]
        else:
            bgr = np.array(sct.grab(sct.monitors[0]))[:, :, :3]
    res = cv2.matchTemplate(bgr, sablon, cv2.TM_CCOEFF_NORMED)
    _, val, _, _ = cv2.minMaxLoc(res)
    return float(val)

def mana_oku():
    if not mana_alani: return 100
    try:
        sx, sy, gn, yk = mana_alani
        if gn <= 0 or yk <= 0: return 100
        bolge = {"top":int(sy),"left":int(sx),"width":int(gn),"height":int(yk)}
        with _mss_lib.mss() as sct:
            bgr = np.array(sct.grab(bolge))[:,:,:3]
        mavi = toplam = 0
        for x in range(0, gn, 2):
            for y in range(0, yk, 2):
                b,g,r = int(bgr[y,x,0]),int(bgr[y,x,1]),int(bgr[y,x,2])
                toplam += 1
                if b > 80 and b > r*1.4 and b > g*1.2:
                    mavi += 1
        return 0 if toplam == 0 else (mavi/toplam)*100
    except Exception as e:
        print(f"[MP] Okuma hatasi: {e}")
        return 100

def hp_oku():
    if not hp_alani:
        return 100
    try:
        sx, sy, gn, yk = hp_alani
        if gn <= 0 or yk <= 0:
            return 100
        bolge = {"top": int(sy), "left": int(sx), "width": int(gn), "height": int(yk)}
        with _mss_lib.mss() as sct:
            bgr = np.array(sct.grab(bolge))[:, :, :3]
        kirmizi = toplam = 0
        for x in range(0, gn, 2):
            for y in range(0, yk, 2):
                b, g, r = int(bgr[y, x, 0]), int(bgr[y, x, 1]), int(bgr[y, x, 2])
                toplam += 1
                if r > 80 and r > b * 1.4 and r > g * 1.2:
                    kirmizi += 1
        return 0 if toplam == 0 else (kirmizi / toplam) * 100
    except Exception as e:
        print(f"[HP] Okuma hatasi: {e}")
        return 100

def _bolge_grab(alani):
    """Secili ekran bolgesini yakala -> (bgr, sol, ust) veya None."""
    if not alani:
        return None
    try:
        sx, sy, gn, yk = alani
        if gn <= 0 or yk <= 0:
            return None
        bolge = {"top": int(sy), "left": int(sx), "width": int(gn), "height": int(yk)}
        with _mss_lib.mss() as sct:
            bgr = np.array(sct.grab(bolge))[:, :, :3]
        return bgr, int(sx), int(sy)
    except Exception as e:
        print(f"[BOLGE] Yakalama hatasi: {e}")
        return None

def restore_tara():
    if _restore_sablon is None or not restore_alani:
        return False
    try:
        grabbed = _bolge_grab(restore_alani)
        if grabbed is None:
            return False
        bgr, offset_x, offset_y = grabbed
        sh, sw = _restore_sablon.shape[:2]
        if bgr.shape[0] < sh or bgr.shape[1] < sw:
            print("[RESTORE] Secili bolge sablondan kucuk")
            if _restore_durum_fn:
                _restore_durum_fn("Bölge çok küçük!", RED)
            return False
        res = cv2.matchTemplate(bgr, _restore_sablon, cv2.TM_CCOEFF_NORMED)
        _, val, _, loc = cv2.minMaxLoc(res)
        if val >= ESLESME_ESIGI:
            mx = loc[0] + sw // 2 + offset_x
            my = loc[1] + sh // 2 + offset_y
            if _ko_hwnd and _user32.IsWindow(_ko_hwnd):
                _ko_odak_getir(_ko_hwnd)
            giris.moveTo(mx, my, duration=0.12)
            time.sleep(0.10)
            giris.ikiSolTik()
            print(f"[RESTORE] 2x sol tik ({mx},{my}) skor={val:.2f}")
            if _restore_durum_fn:
                _restore_durum_fn(f"Restore silindi (skor {val:.0%})", GREEN)
            return True
        print(f"[RESTORE] Bulunamadi (en yuksek skor {val:.2f})")
        if _restore_durum_fn:
            _restore_durum_fn(f"Restore bulunamadi ({val:.0%})", RED)
    except Exception as e:
        print(f"[RESTORE] Hata: {e}")
        if _restore_durum_fn:
            _restore_durum_fn(f"Restore hatasi: {e}", RED)
    return False

def wolf_kontrol():
    """Wolf buf ekrandan gidince 3 sn sonra skill tusuna bas."""
    global _wolf_goruldu, _wolf_gitti_zamani
    if not wolf_aktif or _wolf_sablon is None:
        return
    try:
        skor = _sablon_skor(_wolf_sablon)
        bulundu = skor >= ESLESME_ESIGI
        simdi = time.time()
        if bulundu:
            _wolf_goruldu = True
            _wolf_gitti_zamani = 0.0
            if _wolf_durum_fn:
                _wolf_durum_fn(f"Wolf aktif (%{int(skor*100)})", GREEN)
            return
        if not _wolf_goruldu:
            if _wolf_durum_fn:
                _wolf_durum_fn("Wolf bekleniyor...", CYAN)
            return
        if _wolf_gitti_zamani == 0.0:
            _wolf_gitti_zamani = simdi
            print("[WOLF] Buf gitti, 3 saniye bekleniyor...")
            if _wolf_durum_fn:
                _wolf_durum_fn("Wolf gitti — 3 sn bekleniyor...", YELLOW)
            return
        kalan = WOLF_BEKLE - (simdi - _wolf_gitti_zamani)
        if kalan > 0:
            if _wolf_durum_fn:
                _wolf_durum_fn(f"Wolf — {kalan:.1f} sn kaldi...", YELLOW)
            return
        giris.press(wolf_tus, odak_zorla=True)
        print(f"[WOLF] Tus basildi ({wolf_tus})")
        _wolf_goruldu = False
        _wolf_gitti_zamani = 0.0
        if _wolf_durum_fn:
            _wolf_durum_fn(f"Wolf basildi (tus {wolf_tus.upper()})", GREEN)
        time.sleep(1.6)
    except Exception as e:
        print(f"[WOLF] Hata: {e}")
        if _wolf_durum_fn:
            _wolf_durum_fn(f"Wolf hatasi: {e}", RED)

def cure_kontrol():
    """Secili bolgede herhangi bir debuff gorunurse cure tusuna bas."""
    global _cure_son_basma
    if not cure_aktif or not cure_alani or not _cure_sablonlar:
        return
    simdi = time.time()
    if simdi - _cure_son_basma < CURE_BEKLE:
        return
    try:
        grabbed = _bolge_grab(cure_alani)
        if grabbed is None:
            return
        bgr, _, _ = grabbed
        bh, bw = bgr.shape[:2]
        en_iyi = None
        en_skor = 0.0
        for ad, sablon in _cure_sablonlar:
            sh, sw = sablon.shape[:2]
            if bh < sh or bw < sw:
                continue
            res = cv2.matchTemplate(bgr, sablon, cv2.TM_CCOEFF_NORMED)
            _, val, _, _ = cv2.minMaxLoc(res)
            if val > en_skor:
                en_skor = float(val)
                en_iyi = ad
        if en_iyi is not None and en_skor >= ESLESME_ESIGI:
            giris.press(cure_tus, odak_zorla=True)
            _cure_son_basma = time.time()
            print(f"[CURE] {en_iyi} skor={en_skor:.2f} → tus {cure_tus}")
            if _cure_durum_fn:
                _cure_durum_fn(f"Cure: {en_iyi} (%{int(en_skor*100)}) → {cure_tus.upper()}", GREEN)
            time.sleep(0.15)
        elif _cure_durum_fn:
            _cure_durum_fn(f"Cure taraniyor (max %{int(en_skor*100)})", CYAN)
    except Exception as e:
        print(f"[CURE] Hata: {e}")
        if _cure_durum_fn:
            _cure_durum_fn(f"Cure hatasi: {e}", RED)

def _restore_kontrol():
    """R 0.3 sn basili tutulunca tek sefer 2 sol tik; R birakilana kadar tekrarlamaz."""
    global _restore_islemde, _restore_baslangic, _restore_tetiklendi
    if _restore_islemde:
        return
    basili = bool(_user32.GetAsyncKeyState(_VK_RESTORE) & 0x8000)
    simdi = time.time()
    if not basili:
        _restore_baslangic = 0.0
        _restore_tetiklendi = False
        return
    if _restore_baslangic == 0.0:
        _restore_baslangic = simdi
        return
    if _restore_tetiklendi:
        return
    if simdi - _restore_baslangic < RESTORE_BEKLE:
        return
    _restore_tetiklendi = True
    _restore_islemde = True
    try:
        print("[RESTORE] R 0.3 sn — tek sefer 2x sol tik")
        restore_tara()
    finally:
        _restore_islemde = False

def pot_dongusu():
    while True:
        try:
            if makro_duraklatildi:
                time.sleep(DONGU_ARA)
                continue
            # Ikisi de esigin altindaysa once MP; ayni turda HP pot basma
            mp_basildi = False
            if mana_aktif and mana_alani:
                y = mana_oku()
                if y < mana_esik:
                    giris.press(mana_tus, odak_zorla=True)
                    print(f"[MP] Pot ({mana_tus}) %{y:.1f}")
                    time.sleep(POT_BEKLE)
                    mp_basildi = True
            if not mp_basildi and hp_aktif and hp_alani:
                y = hp_oku()
                if y < hp_esik:
                    giris.press(hp_tus, odak_zorla=True)
                    print(f"[HP] Pot ({hp_tus}) %{y:.1f}")
                    time.sleep(POT_BEKLE)
            if restore_aktif:
                _restore_kontrol()
            if cure_aktif:
                cure_kontrol()
            if wolf_aktif:
                wolf_kontrol()
        except Exception as e:
            print(f"[DONGU] {e}")
        time.sleep(DONGU_ARA)

# ══════════════════════════════════════════════
#  RENKLER
# ══════════════════════════════════════════════
BG      = "#0b0b1e"
BG2     = "#12122a"
BG3     = "#0d0d22"
CYAN    = "#00d4e8"
CDIM    = "#007788"
YELLOW  = "#f0c000"
RED     = "#cc2200"
WHITE   = "#e8e8f0"
GRAY    = "#555570"
GREEN   = "#00cc66"

# ══════════════════════════════════════════════
#  TOGGLE SWITCH
# ══════════════════════════════════════════════
class Toggle(tk.Canvas):
    W=44; H=22; R=10
    def __init__(self, parent, var, cmd=None, **kw):
        super().__init__(parent, width=self.W, height=self.H,
                         bg=parent["bg"], highlightthickness=0, **kw)
        self._v = var; self._c = cmd
        self.bind("<Button-1>", self._flip)
        self._v.trace_add("write", lambda *_: self._draw())
        self._draw()
    def _flip(self,_=None):
        self._v.set(not self._v.get())
        if self._c: self._c()
    def _draw(self):
        self.delete("all")
        on = self._v.get(); col = CYAN if on else GRAY
        self.create_arc(2,2,2+2*self.R,2+2*self.R,start=90,extent=180,fill=col,outline=col)
        self.create_arc(self.W-2-2*self.R,2,self.W-2,2+2*self.R,start=270,extent=180,fill=col,outline=col)
        self.create_rectangle(2+self.R,2,self.W-2-self.R,self.H-2,fill=col,outline=col)
        kx = self.W-4-self.R if on else 4+self.R
        self.create_oval(kx-self.R+2,3,kx+self.R-2,self.H-3,fill=WHITE,outline="")

# ══════════════════════════════════════════════
#  EKRAN SECICI
# ══════════════════════════════════════════════
class Secici:
    def __init__(self, parent, cb, msg="Alani surukleyin — ESC iptal", iptal_cb=None):
        self._cb = cb
        self._iptal_cb = iptal_cb
        self.top = tk.Toplevel(parent)
        self.top.attributes("-alpha",0.25,"-fullscreen",True,"-topmost",True)
        self.top.config(cursor="cross")
        c = tk.Canvas(self.top, bg="grey", highlightthickness=0)
        c.pack(fill="both",expand=True)
        c.create_text(self.top.winfo_screenwidth()//2,40,text=msg,
                      fill="white",font=("Arial",14,"bold"))
        self._c=c; self.bx=self.by=self.rc=None
        c.bind("<ButtonPress-1>",  self._s)
        c.bind("<B1-Motion>",      self._m)
        c.bind("<ButtonRelease-1>",self._e)
        self.top.bind("<Escape>",  self._iptal)
        self.top.protocol("WM_DELETE_WINDOW", self._iptal)
    def _s(self,e):
        self.bx,self.by=e.x,e.y
        self.rc=self._c.create_rectangle(e.x,e.y,e.x+1,e.y+1,outline="red",width=2)
    def _m(self,e): self._c.coords(self.rc,self.bx,self.by,e.x,e.y)
    def _e(self,e):
        sol=min(self.bx,e.x); ust=min(self.by,e.y)
        self.top.destroy()
        self._cb((sol,ust,abs(self.bx-e.x),abs(self.by-e.y)))
    def _iptal(self, e=None):
        self.top.destroy()
        if self._iptal_cb:
            self._iptal_cb()

# ══════════════════════════════════════════════
#  YARDIMCILAR
# ══════════════════════════════════════════════
def btn(p, t, c, col=CYAN, w=12):
    return tk.Button(p, text=t, command=c, bg=BG2, fg=col,
                     activebackground=BG3, activeforeground=col,
                     highlightbackground=col, highlightthickness=1,
                     relief="flat", bd=0, font=("Arial", 8), width=w, cursor="hand2")

def lbl(p, t, col=CYAN, fnt=("Arial", 9), **kw):
    return tk.Label(p, text=t, bg=p["bg"], fg=col, font=fnt, **kw)

def sep(p):
    tk.Frame(p, bg=CDIM, height=1).pack(fill="x", padx=10, pady=4)

# ══════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════
class App:
    ANA_GEOM = "500x680"
    MINI_GEOM = "128x36"   # yaklasik 3cm x 1cm (tutamak + tuslar)

    def __init__(self):
        self.win = tk.Tk()
        self.win.title("KO Makro")
        self.win.geometry(self.ANA_GEOM)
        self.win.resizable(False, False)
        self.win.config(bg=BG)
        self.win.attributes("-topmost", True)
        self._mini_mod = False
        self._kucultuyor = False
        self._buyultuyor = False
        self._bolge_seciliyor = False
        self._drag_moved = False
        self._drag_x = 0
        self._drag_y = 0
        self._win_x = 0
        self._win_y = 0

        self._ana = tk.Frame(self.win, bg=BG)
        self._ana.pack(fill="both", expand=True)
        self._build_topbar()
        sep(self._ana)
        self._build_satirlar()
        sep(self._ana)
        self._build_status()

        self._mini = tk.Frame(self.win, bg=BG)
        self._build_mini()

        self.win.bind("<Unmap>", self._on_unmap)

        global _restore_durum_fn, _wolf_durum_fn, _cure_durum_fn
        _restore_durum_fn = self._restore_durum_guncelle
        _wolf_durum_fn = self._wolf_durum_guncelle
        _cure_durum_fn = self._cure_durum_guncelle

    def _build_mini(self):
        f = self._mini
        f.config(bg=BG, cursor="fleur")
        ic = tk.Frame(f, bg=BG, cursor="fleur")
        ic.pack(expand=True, fill="both", padx=2, pady=2)

        # Sol tutamak — sürükle
        grip = tk.Label(ic, text="⠿", bg=BG2, fg=GRAY,
                        font=("Arial", 10, "bold"), width=2, cursor="fleur")
        grip.pack(side="left", fill="both", padx=(0, 1))

        self._btn_play = tk.Label(
            ic, text="▲", bg=BG2, fg=GREEN,
            font=("Arial", 12, "bold"), width=2, cursor="hand2")
        self._btn_play.pack(side="left", expand=True, fill="both", padx=(0, 1))

        self._btn_pause = tk.Label(
            ic, text="■", bg=BG2, fg=YELLOW,
            font=("Arial", 12, "bold"), width=2, cursor="hand2")
        self._btn_pause.pack(side="left", expand=True, fill="both", padx=(0, 1))

        # Tam pencereye don
        btn_max = tk.Label(ic, text="▢", bg=BG2, fg=CYAN,
                           font=("Arial", 11, "bold"), width=2, cursor="hand2")
        btn_max.pack(side="left", fill="both")

        # Surukleme: tutamak + bos alan; tiklama esigi ile ayristir
        for w in (f, ic, grip):
            w.bind("<ButtonPress-1>", self._mini_drag_basla)
            w.bind("<B1-Motion>", self._mini_drag_hareket)
            w.bind("<ButtonRelease-1>", self._mini_drag_birak)
            w.bind("<Double-Button-1>", lambda e: self._buyult_panel())

        self._btn_play.bind("<ButtonPress-1>", self._mini_drag_basla)
        self._btn_play.bind("<B1-Motion>", self._mini_drag_hareket)
        self._btn_play.bind("<ButtonRelease-1>",
                            lambda e: self._mini_tik_veya_surukle(self._makro_baslat))

        self._btn_pause.bind("<ButtonPress-1>", self._mini_drag_basla)
        self._btn_pause.bind("<B1-Motion>", self._mini_drag_hareket)
        self._btn_pause.bind("<ButtonRelease-1>",
                             lambda e: self._mini_tik_veya_surukle(self._makro_bekle))

        btn_max.bind("<ButtonPress-1>", self._mini_drag_basla)
        btn_max.bind("<B1-Motion>", self._mini_drag_hareket)
        btn_max.bind("<ButtonRelease-1>",
                     lambda e: self._mini_tik_veya_surukle(self._buyult_panel))

        self._mini_guncelle()

    def _mini_drag_basla(self, e):
        self._drag_moved = False
        self._drag_x = e.x_root
        self._drag_y = e.y_root
        self._win_x = self.win.winfo_x()
        self._win_y = self.win.winfo_y()

    def _mini_drag_hareket(self, e):
        if not self._mini_mod:
            return
        dx = e.x_root - self._drag_x
        dy = e.y_root - self._drag_y
        if abs(dx) > 2 or abs(dy) > 2:
            self._drag_moved = True
            self.win.geometry(f"+{self._win_x + dx}+{self._win_y + dy}")

    def _mini_drag_birak(self, e):
        pass

    def _mini_tik_veya_surukle(self, fn):
        if not self._drag_moved:
            fn()

    def _mini_guncelle(self):
        if makro_duraklatildi:
            self._btn_play.config(bg=BG2, fg=GRAY)
            self._btn_pause.config(bg="#3a3010", fg=YELLOW)
        else:
            self._btn_play.config(bg="#16301f", fg=GREEN)
            self._btn_pause.config(bg=BG2, fg=GRAY)

    def _makro_bekle(self):
        global makro_duraklatildi
        makro_duraklatildi = True
        self._mini_guncelle()
        print("[MAKRO] Bekleme (duraklatildi)")

    def _makro_baslat(self):
        global makro_duraklatildi
        makro_duraklatildi = False
        self._mini_guncelle()
        print("[MAKRO] Devam")

    def _on_unmap(self, event):
        if event.widget is not self.win or self._kucultuyor or self._buyultuyor:
            return
        if self._bolge_seciliyor:
            return
        if self.win.state() == "iconic":
            self.win.after(0, self._kucult_panel)

    def _bolge_sec_ac(self, cb, msg):
        """Gecici gizle + bolge secici; mini panele dusmemeli."""
        self._bolge_seciliyor = True
        self.win.withdraw()
        self.win.after(200, lambda: Secici(
            self.win, cb, msg, iptal_cb=self._bolge_sec_iptal))

    def _bolge_sec_bitir(self):
        self._bolge_seciliyor = False
        if not self._mini_mod:
            self.win.deiconify()
            self.win.lift()

    def _bolge_sec_iptal(self):
        self._bolge_sec_bitir()

    def _kucult_panel(self):
        if self._mini_mod or self._kucultuyor or self._bolge_seciliyor:
            return
        self._kucultuyor = True
        try:
            self._mini_mod = True
            self.win.deiconify()
            self.win.state("normal")
            self.win.overrideredirect(True)
            self.win.attributes("-topmost", True)
            self._ana.pack_forget()
            self._mini.pack(fill="both", expand=True)
            # Onceki mini konum varsa orada ac, yoksa sag-ust
            if getattr(self, "_mini_pos", None):
                x, y = self._mini_pos
            else:
                sw = self.win.winfo_screenwidth()
                x, y = sw - 140, 20
            self.win.geometry(f"{self.MINI_GEOM}+{x}+{y}")
            self._mini_guncelle()
        finally:
            self._kucultuyor = False

    def _buyult_panel(self):
        if not self._mini_mod or self._buyultuyor:
            return
        self._buyultuyor = True
        try:
            self._mini_pos = (self.win.winfo_x(), self.win.winfo_y())
            self._mini_mod = False
            self.win.overrideredirect(False)
            self.win.state("normal")
            self._mini.pack_forget()
            self._ana.pack(fill="both", expand=True)
            self.win.resizable(False, False)
            self.win.geometry(self.ANA_GEOM)
            self.win.attributes("-topmost", self._v_ustte.get())
            self.win.deiconify()
            self.win.lift()
        finally:
            self._buyultuyor = False

    # ── Üst bar ────────────────────────────────
    def _build_topbar(self):
        f = tk.Frame(self._ana, bg=BG)
        f.pack(fill="x", padx=12, pady=(10, 4))
        self._v_ustte = tk.BooleanVar(value=True)
        Toggle(f, self._v_ustte,
               cmd=lambda: self.win.attributes("-topmost", self._v_ustte.get())).pack(side="left")
        lbl(f, " Üstte", col=WHITE).pack(side="left", padx=(4, 8))
        btn(f, "🎮 KO Pencere Seç", self._pencere_sec, col=YELLOW, w=16).pack(side="left", padx=4)
        self._lbl_pencere = lbl(f, "Pencere: Seçilmedi", col=RED, fnt=("Arial", 7))
        self._lbl_pencere.pack(side="left", padx=4)
        if _ko_hwnd:
            buf = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetWindowTextW(_ko_hwnd, buf, 256)
            self._lbl_pencere.config(text=f"✓ {buf.value[:20]}", fg=GREEN)

    # ── Satırlar ───────────────────────────────
    def _build_satirlar(self):
        f = tk.Frame(self._ana, bg=BG)
        f.pack(fill="x", padx=14, pady=4)

        # Oto MP
        self._v_mp = tk.BooleanVar(value=False)
        row_mp = tk.Frame(f, bg=BG)
        row_mp.pack(fill="x", pady=3)
        Toggle(row_mp, self._v_mp, cmd=self._mp_toggle).pack(side="left")
        lbl(row_mp, "  Oto MP", col=WHITE, fnt=("Arial", 9, "bold")).pack(side="left")
        self._btn_mp_esik = btn(row_mp, f"Eşik: %{mana_esik}", self._mp_esik, col=RED, w=10)
        self._btn_mp_esik.pack(side="right", padx=(4, 0))
        self._btn_mp_bar = btn(row_mp, "MP Bar Seç", self._mp_sec, col=CYAN, w=11)
        self._btn_mp_bar.pack(side="right", padx=4)
        self._btn_mp_tus = btn(row_mp, f"⌨  Tuş: {mana_tus.upper()}", self._mp_tus_sec, col=CYAN, w=12)
        self._btn_mp_tus.pack(side="right", padx=4)
        self._row_mp = {"ob": self._btn_mp_tus, "sb": self._btn_mp_bar, "esik": self._btn_mp_esik}

        # Oto HP
        self._v_hp = tk.BooleanVar(value=False)
        row_hp = tk.Frame(f, bg=BG)
        row_hp.pack(fill="x", pady=3)
        Toggle(row_hp, self._v_hp, cmd=self._hp_toggle).pack(side="left")
        lbl(row_hp, "  Oto HP", col=WHITE, fnt=("Arial", 9, "bold")).pack(side="left")
        self._btn_hp_esik = btn(row_hp, f"Eşik: %{hp_esik}", self._hp_esik, col=RED, w=10)
        self._btn_hp_esik.pack(side="right", padx=(4, 0))
        self._btn_hp_bar = btn(row_hp, "HP Bar Seç", self._hp_sec, col=CYAN, w=11)
        self._btn_hp_bar.pack(side="right", padx=4)
        self._btn_hp_tus = btn(row_hp, f"⌨  Tuş: {hp_tus.upper()}", self._hp_tus_sec, col=CYAN, w=12)
        self._btn_hp_tus.pack(side="right", padx=4)
        self._row_hp = {"ob": self._btn_hp_tus, "sb": self._btn_hp_bar, "esik": self._btn_hp_esik}

        # Oto Wolf
        self._v_wolf = tk.BooleanVar(value=False)
        if _wolf_sablon is not None:
            wt, wc = "✓ wolf.png hazır", GREEN
        else:
            wt, wc = "✗ Dosya Seç →", RED
        self._row_wolf = self._satir(f, "Oto Wolf", self._v_wolf, self._wolf_toggle,
                                     f"⌨  Tuş: {wolf_tus.upper()}", self._wolf_tus_sec,
                                     wt, self._wolf_dosya, CYAN, orta_renk=wc)

        # Oto Cure
        self._v_cure = tk.BooleanVar(value=False)
        row_cure = tk.Frame(f, bg=BG)
        row_cure.pack(fill="x", pady=3)
        Toggle(row_cure, self._v_cure, cmd=self._cure_toggle).pack(side="left")
        lbl(row_cure, "  Oto Cure", col=WHITE, fnt=("Arial", 9, "bold")).pack(side="left")
        self._btn_cure_bolge = btn(row_cure, "Bölge Seç", self._cure_bolge_sec, col=CYAN, w=11)
        self._btn_cure_bolge.pack(side="right", padx=(4, 0))
        n_cure = len(_cure_sablonlar)
        ct, cc = (f"✓ {n_cure} debuff", GREEN) if n_cure else ("✗ Icon/cure", RED)
        self._btn_cure_yenile = btn(row_cure, ct, self._cure_yenile, col=cc, w=12)
        self._btn_cure_yenile.pack(side="right", padx=4)
        self._btn_cure_tus = btn(row_cure, f"⌨  Tuş: {cure_tus.upper()}", self._cure_tus_sec, col=CYAN, w=12)
        self._btn_cure_tus.pack(side="right", padx=4)

        # Restore [R]
        self._v_rs = tk.BooleanVar(value=False)
        row_rs = tk.Frame(f, bg=BG)
        row_rs.pack(fill="x", pady=3)
        Toggle(row_rs, self._v_rs, cmd=self._rs_toggle).pack(side="left")
        lbl(row_rs, "  Restore [R]", col=WHITE, fnt=("Arial", 9, "bold")).pack(side="left")
        self._btn_rs_hass = btn(row_rs, "Hassasiyet", self._hassasiyet, col=CYAN, w=10)
        self._btn_rs_hass.pack(side="right", padx=(4, 0))
        self._btn_rs_bolge = btn(row_rs, "Bölge Seç", self._rs_bolge_sec, col=CYAN, w=11)
        self._btn_rs_bolge.pack(side="right", padx=4)
        if _restore_sablon is not None:
            rt, rc = "✓ restore.png", GREEN
        else:
            rt, rc = "✗ Dosya Seç", RED
        self._btn_rs_dosya = btn(row_rs, rt, self._rs_dosya, col=rc, w=14)
        self._btn_rs_dosya.pack(side="right", padx=4)
        self._row_rs = {"ob": self._btn_rs_dosya, "sb": self._btn_rs_bolge}

        # Combo [Space]
        self._v_cb = tk.BooleanVar(value=False)
        self._row_cb = self._satir(f, "Combo [Space]", self._v_cb, self._cb_toggle,
                                   "Space 0.30sn tut", None,
                                   "Aktif", None, YELLOW, orta_renk=YELLOW)

    def _satir(self, parent, label, var, vcmd, orta_t, orta_c, sag_t, sag_c, sag_col, orta_renk=CYAN):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=3)
        Toggle(row, var, cmd=vcmd).pack(side="left")
        lbl(row, f"  {label}", col=WHITE, fnt=("Arial", 9, "bold")).pack(side="left")
        if sag_c:
            sb = btn(row, sag_t, sag_c, col=sag_col, w=10)
        else:
            sb = tk.Label(row, text=sag_t, bg=BG, fg=sag_col,
                          font=("Arial", 8, "bold"), width=10)
        sb.pack(side="right", padx=(4, 0))
        if orta_c:
            ob = btn(row, orta_t, orta_c, col=orta_renk, w=14)
        else:
            ob = tk.Label(row, text=orta_t, bg=BG, fg=orta_renk,
                          font=("Arial", 8), width=18, anchor="w")
        ob.pack(side="right", padx=4)
        return {"ob": ob, "sb": sb}

    # ── Status panel ───────────────────────────
    def _durum_bagla(self, var, hedef, acik_txt, kapali_txt):
        def upd(*_):
            if var.get():
                hedef.config(text=acik_txt, fg=GREEN)
            else:
                hedef.config(text=kapali_txt, fg=GRAY)
        var.trace_add("write", upd)
        upd()

    def _build_status(self):
        sf = tk.Frame(self._ana, bg=BG3)
        sf.pack(fill="x", padx=10, pady=(0, 10))
        lbl(sf, "Durum ozeti (ana satirdaki anahtarlardan kontrol edilir)",
            col=GRAY, fnt=("Arial", 7, "italic")).pack(anchor="w", padx=8, pady=(6, 2))

        r1 = tk.Frame(sf, bg=BG3)
        r1.pack(fill="x", padx=8, pady=1)
        lbl(r1, "Oto MP  ", fnt=("Arial", 8)).pack(side="left")
        self._lbl_mp_durum = lbl(r1, "Kapali", col=GRAY, fnt=("Arial", 8, "bold"))
        self._lbl_mp_durum.pack(side="left", padx=4)
        self._durum_bagla(self._v_mp, self._lbl_mp_durum, "● Acik", "Kapali")
        self._lbl_mp_tus = lbl(r1, f"Tuş: {mana_tus.upper()}", fnt=("Arial", 8))
        self._lbl_mp_tus.pack(side="right")

        r_hp = tk.Frame(sf, bg=BG3)
        r_hp.pack(fill="x", padx=8, pady=1)
        lbl(r_hp, "Oto HP  ", fnt=("Arial", 8)).pack(side="left")
        self._lbl_hp_durum = lbl(r_hp, "Kapali", col=GRAY, fnt=("Arial", 8, "bold"))
        self._lbl_hp_durum.pack(side="left", padx=4)
        self._durum_bagla(self._v_hp, self._lbl_hp_durum, "● Acik", "Kapali")
        self._lbl_hp_tus = lbl(r_hp, f"Tuş: {hp_tus.upper()}", fnt=("Arial", 8))
        self._lbl_hp_tus.pack(side="right")

        r_wolf = tk.Frame(sf, bg=BG3)
        r_wolf.pack(fill="x", padx=8, pady=1)
        lbl(r_wolf, "Oto Wolf  ", fnt=("Arial", 8)).pack(side="left")
        self._lbl_wolf_durum = lbl(r_wolf, "Kapali", col=GRAY, fnt=("Arial", 8, "bold"))
        self._lbl_wolf_durum.pack(side="left", padx=4)
        self._durum_bagla(self._v_wolf, self._lbl_wolf_durum, "● Acik", "Kapali")
        self._lbl_wolf_tus = lbl(r_wolf, f"Wolf Tuş: {wolf_tus.upper()}", fnt=("Arial", 8))
        self._lbl_wolf_tus.pack(side="right")

        r_cure = tk.Frame(sf, bg=BG3)
        r_cure.pack(fill="x", padx=8, pady=1)
        lbl(r_cure, "Oto Cure  ", fnt=("Arial", 8)).pack(side="left")
        self._lbl_cure_durum = lbl(r_cure, "Kapali", col=GRAY, fnt=("Arial", 8, "bold"))
        self._lbl_cure_durum.pack(side="left", padx=4)
        self._durum_bagla(self._v_cure, self._lbl_cure_durum, "● Acik", "Kapali")
        self._lbl_cure_tus = lbl(r_cure, f"Cure Tuş: {cure_tus.upper()}", fnt=("Arial", 8))
        self._lbl_cure_tus.pack(side="right")

        r2 = tk.Frame(sf, bg=BG3)
        r2.pack(fill="x", padx=8, pady=1)
        lbl(r2, "Restore [R]  ", fnt=("Arial", 8)).pack(side="left")
        self._lbl_rs_durum = lbl(r2, "Kapali", col=GRAY, fnt=("Arial", 8, "bold"))
        self._lbl_rs_durum.pack(side="left", padx=4)
        self._durum_bagla(self._v_rs, self._lbl_rs_durum, "● R 0.3sn", "Kapali")
        self._lbl_has = lbl(r2, f"Hassasiyet: %{int(ESLESME_ESIGI * 100)}", fnt=("Arial", 8))
        self._lbl_has.pack(side="right")

        r3 = tk.Frame(sf, bg=BG3)
        r3.pack(fill="x", padx=8, pady=1)
        lbl(r3, "Combo [Space]  ", col=YELLOW, fnt=("Arial", 8)).pack(side="left")
        self._lbl_combo = lbl(r3, "Kapali", col=GRAY, fnt=("Arial", 8, "bold"))
        self._lbl_combo.pack(side="left", padx=4)
        self._durum_bagla(self._v_cb, self._lbl_combo, "● Space 0.30sn", "Kapali")
        lbl(r3, "Space 0.30sn tut → 3rr → 0.10s → r×11", col=GRAY, fnt=("Arial", 7, "italic")).pack(side="right")

        r4 = tk.Frame(sf, bg=BG3)
        r4.pack(fill="x", padx=8, pady=1)
        self._lbl_mp = lbl(r4, "MP Pot Durumu : Normal.", fnt=("Arial", 8))
        self._lbl_mp.pack(side="left")

        r5 = tk.Frame(sf, bg=BG3)
        r5.pack(fill="x", padx=8, pady=1)
        self._lbl_hp = lbl(r5, "HP Pot Durumu : Normal.", fnt=("Arial", 8))
        self._lbl_hp.pack(side="left")

        r6 = tk.Frame(sf, bg=BG3)
        r6.pack(fill="x", padx=8, pady=1)
        self._lbl_wolf = lbl(r6, "Wolf Durumu : Bekleniyor.", fnt=("Arial", 8))
        self._lbl_wolf.pack(side="left")

        r6b = tk.Frame(sf, bg=BG3)
        r6b.pack(fill="x", padx=8, pady=1)
        n0 = len(_cure_sablonlar)
        self._lbl_cure = lbl(r6b,
            f"Cure: {n0} debuff yüklü — önce bölge seçin." if n0 else "Cure: Icon/cure klasörü boş!",
            fnt=("Arial", 8))
        self._lbl_cure.pack(side="left")

        r7 = tk.Frame(sf, bg=BG3)
        r7.pack(fill="x", padx=8, pady=(1, 8))
        self._lbl_rs = lbl(r7, "Restore: Önce bölge seçin, R'yi 0.3 sn basılı tutun.", fnt=("Arial", 8))
        self._lbl_rs.pack(side="left")

    def _restore_durum_guncelle(self, msg, col):
        self.win.after(0, lambda: self._lbl_rs.config(text=msg, fg=col))

    def _wolf_durum_guncelle(self, msg, col):
        self.win.after(0, lambda: self._lbl_wolf.config(text=msg, fg=col))

    def _cure_durum_guncelle(self, msg, col):
        self.win.after(0, lambda: self._lbl_cure.config(text=msg, fg=col))

    # ── MP mantığı ─────────────────────────────
    def _mp_sec(self):
        self._bolge_sec_ac(self._mp_cb, "Mana barını sürükleyin — ESC iptal")

    def _mp_cb(self, veri):
        global mana_alani
        self._bolge_sec_bitir()
        s, u, g, y = veri
        if g > 5 and y > 2:
            mana_alani = (s, u, g, y)
            self._btn_mp_bar.config(text="✓ Seçildi", fg=GREEN)
        else:
            self._btn_mp_bar.config(text="Küçük!", fg=RED)

    def _mp_tus_sec(self):
        self._tus_sec_dialog("MP Pot Tuşunu Seç:", mana_tus,
                             lambda t: self._mp_tus_atandi(t))

    def _mp_tus_atandi(self, tus):
        global mana_tus
        mana_tus = tus
        self._btn_mp_tus.config(text=f"⌨  Tuş: {mana_tus.upper()}")
        self._lbl_mp_tus.config(text=f"Tuş: {mana_tus.upper()}")

    def _mp_esik(self):
        w = tk.Toplevel(self.win)
        w.title("MP Eşik")
        w.geometry("260x130")
        w.config(bg=BG)
        w.attributes("-topmost", True)
        lbl(w, "Pot basma eşiği (MP %):").pack(pady=8)
        v = tk.IntVar(value=mana_esik)
        lv = lbl(w, f"%{mana_esik}", col=YELLOW)
        lv.pack()
        tk.Scale(w, from_=5, to=95, resolution=1, orient="horizontal",
                 variable=v, bg=BG, fg=YELLOW, troughcolor=BG2,
                 highlightthickness=0, sliderrelief="flat", showvalue=False,
                 command=lambda x: lv.config(text=f"%{int(float(x))}")
                 ).pack(fill="x", padx=16)

        def ok():
            global mana_esik
            mana_esik = v.get()
            self._btn_mp_esik.config(text=f"Eşik: %{mana_esik}")
            w.destroy()

        btn(w, "Onayla", ok, w=10).pack(pady=6)

    def _mp_toggle(self):
        global mana_aktif
        if not self._v_mp.get():
            mana_aktif = False
            return
        if not mana_alani:
            self._v_mp.set(False)
            self._btn_mp_bar.config(text="Önce seç!", fg=RED)
            return
        mana_aktif = True

    # ── HP mantığı ─────────────────────────────
    def _hp_sec(self):
        self._bolge_sec_ac(self._hp_cb, "HP barını sürükleyin — ESC iptal")

    def _hp_cb(self, veri):
        global hp_alani
        self._bolge_sec_bitir()
        s, u, g, y = veri
        if g > 5 and y > 2:
            hp_alani = (s, u, g, y)
            self._btn_hp_bar.config(text="✓ Seçildi", fg=GREEN)
        else:
            self._btn_hp_bar.config(text="Küçük!", fg=RED)

    def _hp_tus_sec(self):
        self._tus_sec_dialog("HP Pot Tuşunu Seç:", hp_tus,
                             lambda t: self._hp_tus_atandi(t))

    def _hp_tus_atandi(self, tus):
        global hp_tus
        hp_tus = tus
        self._btn_hp_tus.config(text=f"⌨  Tuş: {hp_tus.upper()}")
        self._lbl_hp_tus.config(text=f"Tuş: {hp_tus.upper()}")

    def _hp_esik(self):
        w = tk.Toplevel(self.win)
        w.title("HP Eşik")
        w.geometry("260x130")
        w.config(bg=BG)
        w.attributes("-topmost", True)
        lbl(w, "Pot basma eşiği (HP %):").pack(pady=8)
        v = tk.IntVar(value=hp_esik)
        lv = lbl(w, f"%{hp_esik}", col=YELLOW)
        lv.pack()
        tk.Scale(w, from_=5, to=95, resolution=1, orient="horizontal",
                 variable=v, bg=BG, fg=YELLOW, troughcolor=BG2,
                 highlightthickness=0, sliderrelief="flat", showvalue=False,
                 command=lambda x: lv.config(text=f"%{int(float(x))}")
                 ).pack(fill="x", padx=16)

        def ok():
            global hp_esik
            hp_esik = v.get()
            self._btn_hp_esik.config(text=f"Eşik: %{hp_esik}")
            w.destroy()

        btn(w, "Onayla", ok, w=10).pack(pady=6)

    def _hp_toggle(self):
        global hp_aktif
        if not self._v_hp.get():
            hp_aktif = False
            return
        if not hp_alani:
            self._v_hp.set(False)
            self._btn_hp_bar.config(text="Önce seç!", fg=RED)
            return
        hp_aktif = True

    # ── Wolf mantığı ───────────────────────────
    def _wolf_tus_sec(self):
        self._tus_sec_dialog("Wolf Skill Tuşunu Seç:", wolf_tus,
                             lambda t: self._wolf_tus_atandi(t))

    def _wolf_tus_atandi(self, tus):
        global wolf_tus
        wolf_tus = tus
        self._row_wolf["ob"].config(text=f"⌨  Tuş: {wolf_tus.upper()}")
        self._lbl_wolf_tus.config(text=f"Wolf Tuş: {wolf_tus.upper()}")

    def _wolf_dosya(self):
        yol = filedialog.askopenfilename(
            parent=self.win, title="wolf.png seç",
            filetypes=[("PNG", "*.png"), ("Tümü", "*.*")],
            initialdir=os.path.dirname(WOLF_YOL))
        if not yol:
            return
        if wolf_sablon_yukle(yol):
            self._row_wolf["sb"].config(text="✓ wolf.png hazır", fg=GREEN)
            self._lbl_wolf.config(text=f"Yüklendi: {os.path.basename(yol)}", fg=GREEN)
        else:
            messagebox.showerror("Hata", "Dosya okunamadı!", parent=self.win)

    def _wolf_toggle(self):
        global wolf_aktif, _wolf_goruldu, _wolf_gitti_zamani
        if not self._v_wolf.get():
            wolf_aktif = False
            return
        if _wolf_sablon is None:
            self._v_wolf.set(False)
            self._lbl_wolf.config(text="wolf.png bulunamadı!", fg=RED)
            if messagebox.askokcancel("wolf.png Yok",
                                      f"Aranan: {WOLF_YOL}\n\nDosyayı elle seçmek ister misin?",
                                      parent=self.win):
                self._wolf_dosya()
            return
        wolf_aktif = True
        _wolf_goruldu = False
        _wolf_gitti_zamani = 0.0
        self._lbl_wolf.config(text="Wolf: Taranıyor...", fg=GREEN)

    # ── Oto Cure mantığı ───────────────────────
    def _cure_bolge_sec(self):
        self._bolge_sec_ac(
            self._cure_bolge_cb,
            "Debuff alanını sürükleyin (cure bölgesi) — ESC iptal")

    def _cure_bolge_cb(self, veri):
        global cure_alani
        self._bolge_sec_bitir()
        s, u, g, y = veri
        if g > 10 and y > 10:
            cure_alani = (s, u, g, y)
            self._btn_cure_bolge.config(text="✓ Bölge", fg=GREEN)
            self._lbl_cure.config(
                text=f"Cure bölgesi: {g}x{y} px — debuff gelince {cure_tus.upper()}", fg=CYAN)
        else:
            self._btn_cure_bolge.config(text="Küçük!", fg=RED)

    def _cure_tus_sec(self):
        self._tus_sec_dialog("Cure Skill Tuşunu Seç:", cure_tus,
                             lambda t: self._cure_tus_atandi(t))

    def _cure_tus_atandi(self, tus):
        global cure_tus
        cure_tus = tus
        self._btn_cure_tus.config(text=f"⌨  Tuş: {cure_tus.upper()}")
        self._lbl_cure_tus.config(text=f"Cure Tuş: {cure_tus.upper()}")

    def _cure_yenile(self):
        n = cure_sablonlari_yukle()
        if n:
            self._btn_cure_yenile.config(text=f"✓ {n} debuff", fg=GREEN)
            self._lbl_cure.config(text=f"Cure: {n} debuff yüklendi ({CURE_KLASOR})", fg=GREEN)
        else:
            self._btn_cure_yenile.config(text="✗ Icon/cure", fg=RED)
            self._lbl_cure.config(text=f"Cure: Klasör boş veya yok!\n{CURE_KLASOR}", fg=RED)
            messagebox.showwarning(
                "Cure Şablon Yok",
                f"Debuff PNG bulunamadı.\n\nKlasör: {CURE_KLASOR}",
                parent=self.win)

    def _cure_toggle(self):
        global cure_aktif
        if not self._v_cure.get():
            cure_aktif = False
            self._lbl_cure.config(text="Cure Durumu: Kapalı.", fg=CYAN)
            return
        if not _cure_sablonlar:
            self._v_cure.set(False)
            self._lbl_cure.config(text="Icon/cure boş — önce PNG ekleyin!", fg=RED)
            if messagebox.askokcancel(
                    "Cure Şablon Yok",
                    f"Klasör: {CURE_KLASOR}\n\nYeniden taransın mı?",
                    parent=self.win):
                self._cure_yenile()
            return
        if not cure_alani:
            self._v_cure.set(False)
            self._btn_cure_bolge.config(text="Önce seç!", fg=RED)
            self._lbl_cure.config(text="Cure için önce bölge seçin!", fg=RED)
            return
        cure_aktif = True
        self._lbl_cure.config(
            text=f"Cure: {len(_cure_sablonlar)} debuff taranıyor → {cure_tus.upper()}", fg=GREEN)

    # ── Restore mantığı ────────────────────────
    def _rs_bolge_sec(self):
        self._bolge_sec_ac(
            self._rs_bolge_cb,
            "Restore ikonunun olduğu bölgeyi sürükleyin — ESC iptal")

    def _rs_bolge_cb(self, veri):
        global restore_alani
        self._bolge_sec_bitir()
        s, u, g, y = veri
        if g > 10 and y > 10:
            restore_alani = (s, u, g, y)
            self._btn_rs_bolge.config(text="✓ Bölge", fg=GREEN)
            self._lbl_rs.config(
                text=f"Restore bölgesi: {g}x{y} px — R'yi 0.3 sn basılı tutun.", fg=CYAN)
        else:
            self._btn_rs_bolge.config(text="Küçük!", fg=RED)

    def _rs_dosya(self):
        yol = filedialog.askopenfilename(
            parent=self.win, title="restore.png seç",
            filetypes=[("PNG", "*.png"), ("Tümü", "*.*")],
            initialdir=os.path.dirname(RESTORE_YOL))
        if not yol:
            return
        if sablon_yukle(yol):
            self._row_rs["ob"].config(text="✓ restore.png", fg=GREEN)
            self._lbl_rs.config(text=f"Yüklendi: {os.path.basename(yol)}", fg=GREEN)
        else:
            messagebox.showerror("Hata", "Dosya okunamadı!", parent=self.win)

    def _hassasiyet(self):
        w = tk.Toplevel(self.win)
        w.title("Hassasiyet")
        w.geometry("260x130")
        w.config(bg=BG)
        w.attributes("-topmost", True)
        lbl(w, "Eşleşme Hassasiyeti:").pack(pady=8)
        v = tk.DoubleVar(value=ESLESME_ESIGI)
        lv = lbl(w, f"%{int(ESLESME_ESIGI * 100)}", col=YELLOW)
        lv.pack()
        tk.Scale(w, from_=0.50, to=0.99, resolution=0.01, orient="horizontal",
                 variable=v, bg=BG, fg=YELLOW, troughcolor=BG2,
                 highlightthickness=0, sliderrelief="flat", showvalue=False,
                 command=lambda x: lv.config(text=f"%{int(float(x) * 100)}")
                 ).pack(fill="x", padx=16)

        def ok():
            global ESLESME_ESIGI
            ESLESME_ESIGI = round(v.get(), 2)
            self._lbl_has.config(text=f"Hassasiyet: %{int(ESLESME_ESIGI * 100)}")
            w.destroy()

        btn(w, "Onayla", ok, w=10).pack(pady=6)

    def _rs_toggle(self):
        global restore_aktif
        if not self._v_rs.get():
            restore_aktif = False
            self._lbl_rs.config(text="Restore Durumu: Kapalı.", fg=CYAN)
            return
        if _restore_sablon is None:
            self._v_rs.set(False)
            self._lbl_rs.config(text="restore.png bulunamadı!", fg=RED)
            if messagebox.askokcancel("restore.png Yok",
                                      f"Aranan: {RESTORE_YOL}\n\nDosyayı elle seçmek ister misin?",
                                      parent=self.win):
                self._rs_dosya()
            return
        if not restore_alani:
            self._v_rs.set(False)
            self._btn_rs_bolge.config(text="Önce seç!", fg=RED)
            self._lbl_rs.config(text="Restore için önce bölge seçin!", fg=RED)
            return
        restore_aktif = True
        self._lbl_rs.config(text="Restore: R 0.3 sn tut → 1x 2 tik", fg=GREEN)

    # ── Combo mantığı ──────────────────────────
    def _cb_toggle(self):
        global combo_aktif
        combo_aktif = self._v_cb.get()

    # ── Tuş seçici (1-9, 0) ────────────────────
    def _tus_sec_dialog(self, baslik, mevcut, onay_cb):
        w = tk.Toplevel(self.win)
        w.title("Tuş Seç")
        w.geometry("220x120")
        w.config(bg=BG)
        w.attributes("-topmost", True)
        lbl(w, baslik).pack(pady=10)
        v = tk.StringVar(value=mevcut)
        liste = [str(i) for i in range(1, 10)] + ["0"]
        ttk.Combobox(w, textvariable=v, values=liste,
                     width=8, state="readonly", font=("Arial", 10)).pack(pady=4)

        def ok():
            onay_cb(v.get())
            w.destroy()

        btn(w, "Onayla", ok, w=10).pack(pady=6)

    # ── KO Pencere Seçici ──────────────────────
    def _pencere_sec(self):
        liste = pencere_listesi()
        if not liste:
            messagebox.showinfo("Pencere Yok", "Açık pencere bulunamadı.", parent=self.win)
            return
        w = tk.Toplevel(self.win)
        w.title("KO Penceresi Seç")
        w.geometry("400x320")
        w.config(bg=BG)
        w.attributes("-topmost", True)
        lbl(w, "Knight Online penceresini seç:", col=CYAN,
            fnt=("Arial", 9, "bold")).pack(pady=(10, 4))
        lb = tk.Listbox(w, bg=BG2, fg=WHITE, selectbackground=CYAN,
                        selectforeground=BG, font=("Arial", 9),
                        relief="flat", bd=1, highlightthickness=0)
        lb.pack(fill="both", expand=True, padx=10, pady=4)
        hwnd_map = {}
        for i, (hwnd, baslik) in enumerate(liste):
            goster = f"{baslik[:55]}"
            lb.insert("end", goster)
            hwnd_map[goster] = hwnd
            for ko in _KO_BASLIKLAR:
                if ko.lower() in baslik.lower():
                    lb.itemconfig(i, fg=YELLOW)
        bf = tk.Frame(w, bg=BG)
        bf.pack(fill="x", padx=10, pady=6)

        def onayla():
            global _ko_hwnd
            sel = lb.curselection()
            if not sel:
                return
            goster = lb.get(sel[0])
            h = hwnd_map.get(goster, 0)
            if h:
                _ko_hwnd = h
                baslik = liste[sel[0]][1]
                self._lbl_pencere.config(text=f"✓ {baslik[:22]}", fg=GREEN)
                print(f"[KO] Secildi: {baslik} ({h:#x})")
            w.destroy()

        btn(bf, "✓ Seç", onayla, col=GREEN, w=10).pack(side="left", padx=4)
        btn(bf, "İptal", w.destroy, col=GRAY, w=8).pack(side="left")

    # ── Canlı göstergeler ──────────────────────
    def _tick(self):
        if not self._mini_mod:
            if mana_alani:
                y = mana_oku()
                if y < mana_esik:
                    self._lbl_mp.config(text=f"MP: %{y:.0f} — Pot basılıyor!", fg=RED)
                else:
                    self._lbl_mp.config(text=f"MP: %{y:.0f} — Normal.", fg=CYAN)
            if hp_alani:
                y = hp_oku()
                if y < hp_esik:
                    self._lbl_hp.config(text=f"HP: %{y:.0f} — Pot basılıyor!", fg=RED)
                else:
                    self._lbl_hp.config(text=f"HP: %{y:.0f} — Normal.", fg=CYAN)
        self.win.after(600, self._tick)

    def run(self):
        threading.Thread(target=pot_dongusu, daemon=True).start()
        threading.Thread(target=combo_dongusu, daemon=True).start()
        self.win.after(600, self._tick)
        self.win.mainloop()

# ══════════════════════════════════════════════
#  BASLAT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    try:
        App().run()
    except Exception:
        import traceback
        hata = traceback.format_exc()
        print(hata)
        try:
            r = tk.Tk()
            r.withdraw()
            messagebox.showerror("HATA", hata)
            r.destroy()
        except Exception:
            pass
        input("\nCikmak icin Enter'a basin...")
