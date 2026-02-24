"""
Clipboard AriGo — מנהל היסטוריית לוח
נקודת כניסה ראשית.
"""

import os
import sys
import ctypes
import tkinter as tk

# Enable DPI awareness for sharp rendering on high-res displays
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor DPI Aware v2
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Ensure project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from app.constants import MUTEX_NAME, APP_NAME
from app.utils.single_instance import ensure_single_instance
from app.config_manager import ConfigManager
from app.db.database import Database
from app.db.repository import ClipboardRepository
from app.db.cleanup import CleanupManager
from app.core.clipboard_monitor import ClipboardMonitor
from app.core.clipboard_handler import push_to_clipboard
from app.core.startup_manager import set_auto_start
from app.utils.image_storage import ImageStorage
from app.ui.main_window import MainWindow
from app.ui.tray_icon import SystemTrayIcon


def main():
    # 1. Ensure single instance
    _mutex = ensure_single_instance(MUTEX_NAME)

    # 2. Load configuration
    config_path = os.path.join(PROJECT_ROOT, "config.json")
    config = ConfigManager(config_path)

    # 3. Initialize database
    db_path = os.path.join(PROJECT_ROOT, "data", "clipboard.db")
    db = Database(db_path)
    repo = ClipboardRepository(db)

    # 4. Initialize image storage
    images_dir = os.path.join(PROJECT_ROOT, "data", "images")
    image_storage = ImageStorage(images_dir)

    # 5. Create hidden Tkinter root
    root = tk.Tk()
    root.withdraw()
    root.title(APP_NAME)

    # 6. State
    monitor = None
    tray = None
    cleanup = None

    # 7. Define paste callback
    def on_paste(entry):
        if monitor:
            monitor.set_suppress_next()
        push_to_clipboard(entry)
        if entry.id:
            repo.update_last_used(entry.id)

    # 8. Create main popup window
    main_window = MainWindow(root, repo, config, image_storage, on_paste)

    # 9. Callback for new clipboard entries
    def on_new_entry(entry):
        # Deduplication
        if config.get("deduplicate_consecutive") and repo.is_duplicate(entry.content_hash):
            return
        # Save image if needed
        if entry.content_type == "image" and entry._pil_image is not None:
            entry.image_path = image_storage.save(entry._pil_image)
            entry._pil_image = None  # Free memory
        # Insert into DB
        repo.insert(entry)
        # Notify UI (thread-safe)
        root.after(0, main_window.on_new_entry_added)

    # 10. Start clipboard monitor
    monitor = ClipboardMonitor(
        on_new_entry=on_new_entry,
        blacklist=config.get("blacklisted_apps", []),
    )

    def on_hotkey_triggered(_hotkey_id):
        root.after(0, main_window.toggle)

    monitor.set_hotkey_callback(on_hotkey_triggered)
    monitor.start()

    # Register global hotkey
    mods, vk = config.hotkey_to_win32()
    monitor.register_hotkey(mods, vk)

    # 11. Start system tray
    icon_path = os.path.join(PROJECT_ROOT, "assets", "icon.ico")

    def toggle_pause():
        if monitor.is_paused():
            monitor.resume()
            tray.update_pause_state(False)
        else:
            monitor.pause()
            tray.update_pause_state(True)

    def shutdown():
        if monitor:
            monitor.stop()
        if tray:
            tray.stop()
        if cleanup:
            cleanup.cancel()
        db.close()
        root.quit()

    tray = SystemTrayIcon(
        icon_path=icon_path,
        on_show=lambda: root.after(0, main_window.toggle),
        on_settings=lambda: root.after(0, main_window.show_settings),
        on_pause_toggle=lambda: root.after(0, toggle_pause),
        on_exit=lambda: root.after(0, shutdown),
    )
    tray.start()

    # 12. Start cleanup scheduler
    cleanup = CleanupManager(repo, config, image_storage)
    cleanup_interval = config.get("cleanup_interval_minutes", 30)
    cleanup.schedule(cleanup_interval)

    # 13. Apply auto-start setting
    auto_start = config.get("auto_start", False)
    set_auto_start(auto_start)

    # 14. Window close handler
    root.protocol("WM_DELETE_WINDOW", shutdown)

    # 15. Enter main loop
    root.mainloop()


if __name__ == "__main__":
    main()
