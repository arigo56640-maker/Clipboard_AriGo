"""ניהול קיצורי מקשים גלובליים באמצעות Win32 RegisterHotKey."""

import ctypes
import win32con


HOTKEY_ID_SHOW = 1

# Mapping for config strings to Win32 modifier constants
MOD_MAP = {
    "ctrl": win32con.MOD_CONTROL,
    "shift": win32con.MOD_SHIFT,
    "alt": win32con.MOD_ALT,
    "win": win32con.MOD_WIN,
}

# Mapping for special key names to virtual key codes
VK_MAP = {
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "space": 0x20, "tab": 0x09, "enter": 0x0D,
    "escape": 0x1B, "backspace": 0x08, "delete": 0x2E,
    "insert": 0x2D, "home": 0x24, "end": 0x23,
    "pageup": 0x21, "pagedown": 0x22,
}


def parse_hotkey_config(modifiers_list, key_str):
    """
    המרת הגדרת hotkey מ-config לערכים של Win32.
    מחזיר (modifiers_int, vk_int).
    """
    mods = 0
    for m in modifiers_list:
        mods |= MOD_MAP.get(m.lower(), 0)

    key_lower = key_str.lower()
    if key_lower in VK_MAP:
        vk = VK_MAP[key_lower]
    elif len(key_str) == 1:
        vk = ord(key_str.upper())
    else:
        vk = ord("V")  # fallback

    return mods, vk


def register_hotkey(hwnd, hotkey_id, modifiers, vk):
    """רישום hotkey גלובלי. מחזיר True אם הצליח."""
    return bool(ctypes.windll.user32.RegisterHotKey(hwnd, hotkey_id, modifiers, vk))


def unregister_hotkey(hwnd, hotkey_id):
    """ביטול רישום hotkey."""
    ctypes.windll.user32.UnregisterHotKey(hwnd, hotkey_id)
