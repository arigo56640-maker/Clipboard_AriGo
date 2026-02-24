"""מעקב אחר שינויים בלוח באמצעות Win32 WM_CLIPBOARDUPDATE."""

import ctypes
import ctypes.wintypes
import threading
import time

import win32con
import win32gui

from app.core.clipboard_handler import read_clipboard
from app.core.source_detector import get_foreground_app
from app.constants import WINDOW_CLASS_NAME

WM_CLIPBOARDUPDATE = 0x031D
WM_REGISTER_HOTKEY = 0x0400 + 1  # WM_USER + 1
HOTKEY_ID_SHOW = 1


class ClipboardMonitor:
    def __init__(self, on_new_entry, blacklist=None):
        self._on_new_entry = on_new_entry
        self._blacklist = set(
            app.lower() for app in (blacklist or [])
        )
        self._thread = None
        self._hwnd = None
        self._paused = False
        self._running = False
        self._suppress_next = False
        self._hotkey_callback = None
        self._hotkey_registered = False
        self._pending_hotkey = None  # (modifiers, vk) to register after HWND ready
        self._hwnd_ready = threading.Event()

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True, name="ClipboardMonitor")
        self._thread.start()
        # Wait until HWND is created
        self._hwnd_ready.wait(timeout=5)

    def stop(self):
        self._running = False
        if self._hwnd:
            try:
                ctypes.windll.user32.RemoveClipboardFormatListener(self._hwnd)
            except Exception:
                pass
            try:
                win32gui.PostMessage(self._hwnd, win32con.WM_QUIT, 0, 0)
            except Exception:
                pass

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def is_paused(self):
        return self._paused

    def set_suppress_next(self):
        """סימון שהשינוי הבא בלוח הוא שלנו — לא לשמור."""
        self._suppress_next = True

    def update_blacklist(self, apps):
        self._blacklist = set(app.lower() for app in apps)

    def set_hotkey_callback(self, callback):
        self._hotkey_callback = callback

    def register_hotkey(self, modifiers, vk):
        """רישום hotkey — חייב לרוץ ב-thread של הצג ההודעות."""
        self._pending_hotkey = (modifiers, vk)
        # If the monitor thread is already running, post a custom message
        # to trigger registration on the correct thread
        if self._hwnd:
            ctypes.windll.user32.PostMessageW(self._hwnd, WM_REGISTER_HOTKEY, 0, 0)

    def _do_register_hotkey(self, modifiers, vk):
        if self._hotkey_registered:
            ctypes.windll.user32.UnregisterHotKey(self._hwnd, HOTKEY_ID_SHOW)
            self._hotkey_registered = False
        result = ctypes.windll.user32.RegisterHotKey(
            self._hwnd, HOTKEY_ID_SHOW, modifiers, vk
        )
        if result:
            self._hotkey_registered = True
        else:
            err = ctypes.windll.kernel32.GetLastError()
            print(f"[ClipboardAriGo] RegisterHotKey failed (error {err}). "
                  f"The hotkey may be in use by another application.")
            self._hotkey_registered = False

    def _run(self):
        # Register window class
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = WINDOW_CLASS_NAME
        wc.hInstance = win32gui.GetModuleHandle(None)

        try:
            class_atom = win32gui.RegisterClass(wc)
        except Exception:
            # Class may already be registered
            class_atom = WINDOW_CLASS_NAME

        # Create message-only window
        self._hwnd = win32gui.CreateWindow(
            class_atom, WINDOW_CLASS_NAME,
            0, 0, 0, 0, 0,
            win32con.HWND_MESSAGE,
            0, wc.hInstance if hasattr(wc, 'hInstance') else win32gui.GetModuleHandle(None),
            None,
        )

        # Register for clipboard updates
        ctypes.windll.user32.AddClipboardFormatListener(self._hwnd)

        # Register pending hotkey
        if self._pending_hotkey:
            self._do_register_hotkey(*self._pending_hotkey)
            self._pending_hotkey = None

        self._running = True
        self._hwnd_ready.set()

        # Message pump
        msg = ctypes.wintypes.MSG()
        while self._running:
            ret = ctypes.windll.user32.GetMessageW(
                ctypes.byref(msg), None, 0, 0
            )
            if ret <= 0:
                break

            # WM_HOTKEY is posted to the thread queue with hwnd=0,
            # so DispatchMessageW won't deliver it to our wnd_proc.
            # We must handle it directly in the message pump.
            if msg.message == win32con.WM_HOTKEY:
                if msg.wParam == HOTKEY_ID_SHOW and self._hotkey_callback:
                    self._hotkey_callback(msg.wParam)
                continue

            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_CLIPBOARDUPDATE:
            if self._suppress_next:
                self._suppress_next = False
                return 0
            if not self._paused:
                self._handle_clipboard_change()
            return 0

        if msg == WM_REGISTER_HOTKEY:
            # Register pending hotkey on the correct thread
            if self._pending_hotkey:
                self._do_register_hotkey(*self._pending_hotkey)
                self._pending_hotkey = None
            return 0

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _handle_clipboard_change(self):
        # Small delay to ensure clipboard data is fully available
        time.sleep(0.05)

        # Detect source app
        source_app, source_window = get_foreground_app()

        # Blacklist check
        if source_app and source_app.lower() in self._blacklist:
            return

        # Read clipboard
        entry = read_clipboard()
        if entry is None:
            return

        entry.source_app = source_app
        entry.source_window = source_window

        # Notify callback
        try:
            self._on_new_entry(entry)
        except Exception:
            pass
