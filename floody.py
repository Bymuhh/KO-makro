# -*- coding: utf-8 -*-
"""
Floody — KO chat flood sayfası (ana pencere içinde).
4 mesaj döngüsü, kopyala-yapıştır / donanımsal klavye modları.
"""
import time
import threading
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk

# Ana makro temasıyla uyumlu koyu renkler
BG      = "#0b0b1e"
BG2     = "#12122a"
BG3     = "#0d0d22"
CARD    = "#12122a"
CYAN    = "#00d4e8"
YELLOW  = "#f0c000"
RED     = "#cc2200"
PINK    = "#e85d75"
GREEN   = "#00cc66"
GREEN2  = "#2e7d32"
WHITE   = "#e8e8f0"
GRAY    = "#555570"
MUTED   = "#3a3a55"

_TR_MAP = str.maketrans({
    "ş": "s", "Ş": "S", "ı": "i", "İ": "I", "ğ": "g", "Ğ": "G",
    "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C",
})

def tr_to_en(text):
    return text.translate(_TR_MAP)

# ── SendInput (64-bit uyumlu, VK + scancode) ──
ULONG_PTR = ctypes.c_size_t

class _KI(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class _MI(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class _HI(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class _IU(ctypes.Union):
    _fields_ = [("ki", _KI), ("mi", _MI), ("hi", _HI)]

class _INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("_input", _IU)]

_KEYEVENTF_KEYUP = 0x0002
_KEYEVENTF_SCANCODE = 0x0008
_INPUT_KEYBOARD = 1

_SW = ctypes.windll.user32.SendInput
_user32 = ctypes.windll.user32
_MapVirtualKeyW = _user32.MapVirtualKeyW

_SC = {
    "0": 0x0B, "1": 0x02, "2": 0x03, "3": 0x04, "4": 0x05,
    "5": 0x06, "6": 0x07, "7": 0x08, "8": 0x09, "9": 0x0A,
    "a": 0x1E, "b": 0x30, "c": 0x2E, "d": 0x20, "e": 0x12,
    "f": 0x21, "g": 0x22, "h": 0x23, "i": 0x17, "j": 0x24,
    "k": 0x25, "l": 0x26, "m": 0x32, "n": 0x31, "o": 0x18,
    "p": 0x19, "q": 0x10, "r": 0x13, "s": 0x1F, "t": 0x14,
    "u": 0x16, "v": 0x2F, "w": 0x11, "x": 0x2D, "y": 0x15,
    "z": 0x2C,
    "space": 0x39, "enter": 0x1C, "ctrl": 0x1D,
}

VK_RETURN = 0x0D
VK_CONTROL = 0x11
VK_SPACE = 0x20
VK_V = 0x56


def _send_vk(vk, up=False):
    flags = _KEYEVENTF_KEYUP if up else 0
    scan = _MapVirtualKeyW(vk, 0) & 0xFF
    i = _INPUT(
        type=_INPUT_KEYBOARD,
        _input=_IU(ki=_KI(
            wVk=vk, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=0)))
    n = _SW(1, ctypes.byref(i), ctypes.sizeof(i))
    if n != 1:
        # yedek: sadece scancode
        sc = _SC.get(chr(vk).lower()) if 0x41 <= vk <= 0x5A else None
        if sc is None and vk == VK_SPACE:
            sc = _SC["space"]
        elif vk == VK_RETURN:
            sc = _SC["enter"]
        elif vk == VK_CONTROL:
            sc = _SC["ctrl"]
        elif vk == VK_V:
            sc = _SC["v"]
        if sc is not None:
            flags2 = _KEYEVENTF_SCANCODE | (_KEYEVENTF_KEYUP if up else 0)
            i2 = _INPUT(
                type=_INPUT_KEYBOARD,
                _input=_IU(ki=_KI(
                    wVk=0, wScan=sc, dwFlags=flags2, time=0, dwExtraInfo=0)))
            _SW(1, ctypes.byref(i2), ctypes.sizeof(i2))


def _tap_vk(vk, hold=0.04, after=0.03):
    _send_vk(vk, up=False)
    time.sleep(hold)
    _send_vk(vk, up=True)
    time.sleep(after)


def _ctrl_v(delay):
    _send_vk(VK_CONTROL, up=False)
    time.sleep(0.03)
    _tap_vk(VK_V, hold=0.05, after=0.03)
    _send_vk(VK_CONTROL, up=True)
    time.sleep(delay)


def _enter(delay):
    _tap_vk(VK_RETURN, hold=0.05, after=delay)


def _type_hardware(text, delay):
    for ch in text.lower():
        if ch == " ":
            _tap_vk(VK_SPACE, after=delay * 0.3)
        elif "a" <= ch <= "z":
            _tap_vk(ord(ch.upper()), after=delay * 0.25)
        elif "0" <= ch <= "9":
            _tap_vk(ord(ch), after=delay * 0.25)


class FloodyPage(tk.Frame):
    """Ana pencere içinde Floody sayfası."""

    MODLAR = (
        "1. Kopyala-Yapıştır (ÖNERİLEN: Tüm İşaretler)",
        "2. Donanımsal Klavye (Güvenli Mod)",
    )
    HOTKEYS = ["f6", "f7", "f8", "f9", "f10", "f11", "f12"] + list(
        "abcdefghijklmnopqrstuvwxyz"
    )
    BASLANGIC_GERI_SAYIM = 3.0  # hedef pencereye tıklama süresi

    def __init__(self, master, app, on_back=None, **kw):
        super().__init__(master, bg=BG, **kw)
        self.app = app
        self.root = app.win
        self.on_back = on_back

        self._running = False
        self._stop_evt = threading.Event()
        self._thread = None
        self._msg_idx = 0
        self._next_in = 0.0
        self._hotkey_armed = False
        self._poll_active = False
        self._msgs_cache = []
        self._lock = threading.Lock()

        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=12, pady=(8, 4))
        tk.Button(
            top, text="← Makro", command=self._geri,
            bg=BG2, fg=CYAN, activebackground=BG3, activeforeground=CYAN,
            relief="flat", font=("Arial", 8), cursor="hand2", width=10
        ).pack(side="left")
        tk.Label(top, text="Floody", bg=BG, fg=WHITE,
                 font=("Arial", 14, "bold")).pack(side="left", padx=10)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=4)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = tk.LabelFrame(
            body, text="  Gönderilecek Mesajlar  ",
            bg=CARD, fg=WHITE, font=("Arial", 9, "bold"),
            bd=1, relief="solid", labelanchor="nw")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self._entries = []
        for i in range(4):
            e = tk.Entry(
                left, bg=BG3, fg=WHITE, insertbackground=WHITE,
                relief="flat", font=("Arial", 9),
                highlightthickness=1, highlightbackground=MUTED,
                highlightcolor=CYAN)
            e.pack(fill="x", padx=10,
                   pady=(8 if i == 0 else 4, 4 if i < 3 else 10), ipady=6)
            e._ph = "%d. Mesajı buraya yazın..." % (i + 1)
            self._set_placeholder(e)
            self._entries.append(e)

        right = tk.LabelFrame(
            body, text="  Makro Ayarları  ",
            bg=CARD, fg=WHITE, font=("Arial", 9, "bold"),
            bd=1, relief="solid", labelanchor="nw")
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="Yazım Modu Seçin:", bg=CARD, fg=GRAY,
                 font=("Arial", 7)).pack(anchor="w", padx=10, pady=(8, 2))
        self._mod_var = tk.StringVar(value=self.MODLAR[0])
        ttk.Combobox(
            right, textvariable=self._mod_var, values=self.MODLAR,
            state="readonly", font=("Arial", 8)
        ).pack(fill="x", padx=10, pady=(0, 6))

        tk.Label(right, text="Döngü Süresi (Saniye):", bg=CARD, fg=GRAY,
                 font=("Arial", 7)).pack(anchor="w", padx=10)
        self._loop_var = tk.DoubleVar(value=3.0)
        tk.Spinbox(
            right, from_=0.5, to=600, increment=0.5, textvariable=self._loop_var,
            bg=BG3, fg=WHITE, buttonbackground=BG2, relief="flat",
            font=("Arial", 9), width=10
        ).pack(anchor="w", padx=10, pady=(2, 6))

        tk.Label(right, text="Gecikme Süresi (Saniye):", bg=CARD, fg=GRAY,
                 font=("Arial", 7)).pack(anchor="w", padx=10)
        self._delay_var = tk.DoubleVar(value=0.30)
        tk.Spinbox(
            right, from_=0.05, to=5.0, increment=0.05, textvariable=self._delay_var,
            bg=BG3, fg=WHITE, buttonbackground=BG2, relief="flat",
            font=("Arial", 9), width=10
        ).pack(anchor="w", padx=10, pady=(2, 6))

        self._timer_lbl = tk.Label(
            right, text="Sonraki: 0.0s", bg="#050510", fg=YELLOW,
            font=("Consolas", 10, "bold"), anchor="center", pady=6)
        self._timer_lbl.pack(fill="x", padx=10, pady=(2, 6))

        tk.Label(right, text="Kısayol Tuşu Seçin:", bg=CARD, fg=GRAY,
                 font=("Arial", 7)).pack(anchor="w", padx=10)
        self._hotkey_var = tk.StringVar(value="f8")
        ttk.Combobox(
            right, textvariable=self._hotkey_var, values=self.HOTKEYS,
            state="readonly", width=6, font=("Arial", 9)
        ).pack(anchor="w", padx=10, pady=(2, 6))

        self._topmost_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            right, text="Her Zaman Üstte Tut", variable=self._topmost_var,
            bg=CARD, fg=WHITE, selectcolor=BG3, activebackground=CARD,
            activeforeground=WHITE, font=("Arial", 8),
            command=self._apply_topmost
        ).pack(anchor="w", padx=10, pady=(2, 10))

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=10, pady=(4, 2))

        master_f = tk.Frame(bottom, bg=BG)
        master_f.pack(side="left", padx=(0, 10))
        tk.Label(master_f, text="MASTER SWITCH\n(Güvenlik)", bg=BG, fg=GRAY,
                 font=("Arial", 6), justify="left").pack(anchor="w")
        self._master_var = tk.BooleanVar(value=False)
        self._master_btn = tk.Label(
            master_f, text="  OFF  ", bg=RED, fg=WHITE,
            font=("Arial", 10, "bold"), cursor="hand2", padx=8, pady=4)
        self._master_btn.pack(anchor="w", pady=2)
        self._master_btn.bind("<Button-1>", self._toggle_master)

        bf = tk.Frame(bottom, bg=BG)
        bf.pack(side="left", fill="x", expand=True)
        tk.Button(
            bf, text="BAŞLAT", command=self.start,
            bg=GREEN2, fg=WHITE, activebackground=GREEN, activeforeground=WHITE,
            relief="flat", font=("Arial", 11, "bold"), cursor="hand2", height=2
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(
            bf, text="DURDUR", command=self.stop,
            bg=PINK, fg=WHITE, activebackground=RED, activeforeground=WHITE,
            relief="flat", font=("Arial", 11, "bold"), cursor="hand2", height=2
        ).pack(side="left", fill="x", expand=True)

        self._status = tk.Label(
            self, text="Durum: BEKLİYOR — Master ON → BAŞLAT → Notepad'e tıkla",
            bg=BG3, fg=PINK, font=("Arial", 8, "bold"), anchor="w", padx=12, pady=6)
        self._status.pack(side="bottom", fill="x")

    def on_show(self):
        self._apply_topmost()
        if not self._poll_active:
            self._poll_active = True
            self._poll_hotkey()
            self._tick_timer()

    def on_hide(self):
        pass

    def _geri(self):
        if self.on_back:
            self.on_back()

    def _set_placeholder(self, entry):
        ph = entry._ph
        entry.insert(0, ph)
        entry.config(fg=MUTED)

        def on_in(_e):
            if entry.get() == ph:
                entry.delete(0, "end")
                entry.config(fg=WHITE)

        def on_out(_e):
            if not entry.get().strip():
                entry.delete(0, "end")
                entry.insert(0, ph)
                entry.config(fg=MUTED)

        entry.bind("<FocusIn>", on_in)
        entry.bind("<FocusOut>", on_out)

    def _messages(self):
        out = []
        for e in self._entries:
            t = e.get().strip()
            if t and t != getattr(e, "_ph", ""):
                out.append(tr_to_en(t))
        return out

    def _refresh_msgs_cache(self):
        with self._lock:
            self._msgs_cache = self._messages()

    def _cached_msgs(self):
        with self._lock:
            return list(self._msgs_cache)

    def _apply_topmost(self):
        try:
            self.root.attributes("-topmost", self._topmost_var.get())
        except tk.TclError:
            pass

    def _toggle_master(self, _e=None):
        self._master_var.set(not self._master_var.get())
        on = self._master_var.get()
        self._master_btn.config(
            text="  ON   " if on else "  OFF  ",
            bg=GREEN if on else RED)
        if not on and self._running:
            self.stop()

    def _set_status(self, text, running=False):
        try:
            self._status.config(text="Durum: %s" % text, fg=GREEN if running else PINK)
        except tk.TclError:
            pass

    def _floody_odakta_mi(self):
        """Kısayol: Floody kendi Entry'sinde yazarken tetiklenmesin."""
        try:
            w = self.root.focus_get()
            if w is not None and str(w).startswith(str(self)):
                return True
        except tk.TclError:
            pass
        return False

    def start(self):
        if not self._master_var.get():
            self._set_status("MASTER SWITCH KAPALI — önce ON yap")
            return
        self._refresh_msgs_cache()
        msgs = self._cached_msgs()
        if not msgs:
            self._set_status("MESAJ YOK — en az 1 mesaj yaz")
            return
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._msg_idx = 0
        self._next_in = self.BASLANGIC_GERI_SAYIM
        self._set_status(
            "GERİ SAYIM — %d sn içinde Notepad/oyuna TIKLA!" % int(self.BASLANGIC_GERI_SAYIM),
            running=True)
        # Odak Floody'de kalmasın diye pencereyi bırak
        try:
            self.root.focus_force()
            self.root.focus_set()
        except tk.TclError:
            pass
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self._stop_evt.set()
        self._next_in = 0.0
        self._set_status("DURDURULDU")

    def _loop(self):
        # Hedef pencereye tıklama süresi
        end = time.time() + self.BASLANGIC_GERI_SAYIM
        while time.time() < end:
            if self._stop_evt.is_set() or not self._running:
                self._running = False
                self._next_in = 0.0
                try:
                    self.root.after(0, lambda: self._set_status("DURDURULDU"))
                except tk.TclError:
                    pass
                return
            left = end - time.time()
            self._next_in = max(0.0, left)
            try:
                self.root.after(
                    0,
                    lambda s=left: self._set_status(
                        "HEDEFE TIKLA — %.1fs" % s, running=True))
            except tk.TclError:
                pass
            time.sleep(0.05)

        while self._running and not self._stop_evt.is_set():
            if not self._master_var.get():
                break
            try:
                self.root.after(0, self._refresh_msgs_cache)
            except tk.TclError:
                pass
            time.sleep(0.05)
            msgs = self._cached_msgs()
            if not msgs:
                break
            text = msgs[self._msg_idx % len(msgs)]
            self._msg_idx += 1
            try:
                self.root.after(
                    0,
                    lambda t=text: self._set_status(
                        "YAZIYOR: %s" % (t[:40] + ("…" if len(t) > 40 else "")),
                        running=True))
            except tk.TclError:
                pass
            try:
                self._send_one(text)
            except Exception as e:
                print("[FLOODY]", e)
                try:
                    self.root.after(
                        0, lambda err=str(e): self._set_status("HATA: %s" % err))
                except tk.TclError:
                    pass
            try:
                # DoubleVar ana thread dışında riskli; cache'ten oku
                loop_s = float(self._loop_var.get())
            except Exception:
                loop_s = 3.0
            loop_s = max(0.3, loop_s)
            self._next_in = loop_s
            end = time.time() + loop_s
            while time.time() < end:
                if self._stop_evt.is_set() or not self._running:
                    break
                self._next_in = max(0.0, end - time.time())
                time.sleep(0.05)
        self._running = False
        self._next_in = 0.0
        try:
            self.root.after(0, lambda: self._set_status("BEKLİYOR"))
        except tk.TclError:
            pass

    def _send_one(self, text):
        try:
            delay = float(self._delay_var.get())
        except Exception:
            delay = 0.3
        delay = max(0.05, delay)
        paste = self._mod_var.get().startswith("1.")

        if paste:
            done = threading.Event()

            def _clip():
                try:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
                    self.root.update()
                finally:
                    done.set()

            self.root.after(0, _clip)
            if not done.wait(timeout=2.0):
                print("[FLOODY] clipboard timeout")
            time.sleep(max(0.15, delay * 0.5))
            # KO chat: Enter (aç) → yapıştır → Enter (gönder)
            _enter(delay)
            _ctrl_v(delay)
            _enter(delay)
        else:
            safe = "".join(c for c in text.lower() if c.isalnum() or c == " ")
            _enter(delay)
            _type_hardware(safe, delay)
            _enter(delay)

    def _hotkey_vk(self):
        k = self._hotkey_var.get().lower().strip()
        if len(k) == 1 and "a" <= k <= "z":
            return ord(k.upper())
        f_map = {
            "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
            "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
            "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
        }
        return f_map.get(k)

    def _poll_hotkey(self):
        try:
            if not self.root.winfo_exists():
                self._poll_active = False
                return
        except tk.TclError:
            self._poll_active = False
            return
        visible = self.winfo_ismapped()
        if (visible or self._running) and not self._floody_odakta_mi():
            vk = self._hotkey_vk()
            if vk is not None:
                down = bool(_user32.GetAsyncKeyState(vk) & 0x8000)
                if down and not self._hotkey_armed:
                    self._hotkey_armed = True
                    if self._running:
                        self.stop()
                    elif visible:
                        self.start()
                elif not down:
                    self._hotkey_armed = False
        else:
            self._hotkey_armed = False
        self.root.after(80, self._poll_hotkey)

    def _tick_timer(self):
        try:
            if not self.root.winfo_exists():
                return
        except tk.TclError:
            return
        try:
            if self.winfo_ismapped():
                self._timer_lbl.config(text="Sonraki: %.1fs" % self._next_in)
        except tk.TclError:
            pass
        self.root.after(100, self._tick_timer)
