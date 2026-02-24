"""אייקון במגש המערכת באמצעות pystray."""

import threading

import pystray
from PIL import Image

from app.constants import STRINGS


class SystemTrayIcon:
    """אייקון במגש המערכת עם תפריט הקשר."""

    def __init__(self, icon_path, on_show, on_settings, on_pause_toggle, on_exit):
        self._icon_path = icon_path
        self._on_show = on_show
        self._on_settings = on_settings
        self._on_pause_toggle = on_pause_toggle
        self._on_exit = on_exit
        self._icon = None
        self._paused = False
        self._thread = None

    def start(self):
        try:
            image = Image.open(self._icon_path)
        except Exception:
            # Fallback: create a simple colored icon
            image = Image.new("RGB", (64, 64), "#7c3aed")

        self._icon = pystray.Icon(
            "ClipboardAriGo",
            image,
            "Clipboard AriGo",
            menu=self._create_menu(),
        )

        self._thread = threading.Thread(
            target=self._icon.run, daemon=True, name="SystemTray"
        )
        self._thread.start()

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def update_pause_state(self, paused):
        self._paused = paused
        if self._icon:
            self._icon.menu = self._create_menu()
            try:
                self._icon.update_menu()
            except Exception:
                pass

    def show_notification(self, title, message):
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass

    def _create_menu(self):
        pause_text = STRINGS["tray_resume"] if self._paused else STRINGS["tray_pause"]
        return pystray.Menu(
            pystray.MenuItem(
                STRINGS["tray_show"], self._on_show, default=True
            ),
            pystray.MenuItem(STRINGS["tray_settings"], self._on_settings),
            pystray.MenuItem(pause_text, self._on_pause_toggle),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(STRINGS["tray_exit"], self._on_exit),
        )
