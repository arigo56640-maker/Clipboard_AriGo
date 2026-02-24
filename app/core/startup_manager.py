"""ניהול הפעלה אוטומטית עם Windows דרך הרגיסטרי."""

import os
import sys
import winreg

REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "ClipboardAriGo"


def is_auto_start_enabled() -> bool:
    """בדיקה אם האפליקציה מוגדרת להפעלה אוטומטית."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_READ
        )
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except OSError:
        return False


def enable_auto_start():
    """הוספת האפליקציה להפעלה אוטומטית."""
    exe_path = _get_executable_path()
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
        return True
    except OSError:
        return False


def disable_auto_start():
    """הסרת האפליקציה מהפעלה אוטומטית."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        return True
    except OSError:
        return False


def set_auto_start(enabled):
    """הגדרה/ביטול הפעלה אוטומטית."""
    if enabled:
        return enable_auto_start()
    else:
        return disable_auto_start()


def _get_executable_path():
    """החזרת הנתיב לקובץ ההפעלה."""
    if getattr(sys, "frozen", False):
        # Running as compiled .exe
        return sys.executable
    else:
        # Running as Python script
        main_script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "main.py",
        )
        return f"{sys.executable} {main_script}"
