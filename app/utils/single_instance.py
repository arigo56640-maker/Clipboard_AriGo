"""מניעת הפעלת מופע כפול של האפליקציה באמצעות Windows Mutex."""

import ctypes
import sys


def ensure_single_instance(mutex_name):
    """יצירת mutex — אם כבר קיים, האפליקציה כבר רצה."""
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()

    ERROR_ALREADY_EXISTS = 183
    if last_error == ERROR_ALREADY_EXISTS:
        import tkinter.messagebox as mb
        mb.showwarning("Clipboard AriGo", "האפליקציה כבר רצה.")
        sys.exit(0)

    return mutex
