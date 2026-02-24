"""זיהוי האפליקציה הפעילה ברגע ההעתקה."""

import ctypes
import ctypes.wintypes


def get_foreground_app():
    """
    החזרת (שם_תהליך, כותרת_חלון) של האפליקציה בחזית.
    מחזיר (None, None) אם לא ניתן לזהות.
    """
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return None, None

        # Window title
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        window_title = buf.value if buf.value else None

        # Process ID
        pid = ctypes.wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        if pid.value == 0:
            return None, window_title

        # Process name via psutil (more reliable than OpenProcess)
        try:
            import psutil
            proc = psutil.Process(pid.value)
            app_name = proc.name()
        except Exception:
            app_name = _get_process_name_win32(pid.value)

        return app_name, window_title

    except Exception:
        return None, None


def _get_process_name_win32(pid):
    """Fallback: get process name via Win32 API."""
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    try:
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if not handle:
            return None
        buf = ctypes.create_unicode_buffer(260)
        size = ctypes.wintypes.DWORD(260)
        success = ctypes.windll.kernel32.QueryFullProcessImageNameW(
            handle, 0, buf, ctypes.byref(size)
        )
        ctypes.windll.kernel32.CloseHandle(handle)
        if success and buf.value:
            import os
            return os.path.basename(buf.value)
    except Exception:
        pass
    return None
