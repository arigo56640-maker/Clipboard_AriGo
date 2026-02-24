# Clipboard_AriGo Project Memory

## Project Overview
- Persistent clipboard history manager for Windows 11
- Python + Tkinter + SQLite + Win32 API
- Hebrew RTL UI, dark theme, frameless floating window
- Entry point: `main.py`

## Key Architecture
- **Clipboard monitoring**: `AddClipboardFormatListener` + `WM_CLIPBOARDUPDATE` (hook-based, not polling)
- **Global hotkey**: `Ctrl+Alt+V` via `RegisterHotKey` Win32 API (Ctrl+Shift+V was taken by Windows)
- **3 threads**: Tkinter main, Win32 message pump, pystray tray icon
- **Cross-thread**: all UI calls via `root.after(0, callback)`
- **DB**: SQLite WAL mode + FTS5 full-text search, thread-local connections
- **Images**: saved as PNG in `data/images/YYYY/MM/`, relative paths in DB
- **Dedup**: SHA-256 hash comparison against last entry
- **Paste-back loop prevention**: `monitor.set_suppress_next()` flag

## Key Files
- `main.py` — entry point, wires all components
- `app/core/clipboard_monitor.py` — Win32 message loop + clipboard listener
- `app/core/clipboard_handler.py` — multi-format read/write (text, HTML, image, files)
- `app/ui/main_window.py` — frameless Tkinter popup with fade animations
- `app/db/database.py` — schema (clipboard_entries, clipboard_fts, blacklisted_apps)
- `app/db/repository.py` — CRUD + FTS5 search + ClipboardEntry dataclass
- `app/config_manager.py` — singleton config backed by config.json

## Dependencies
- pywin32, Pillow, psutil, pystray (all installed)
- tkinter, sqlite3 (built-in)

## Important Implementation Details
- **Hotkey thread safety**: `RegisterHotKey` MUST be called from the monitor thread (not main thread). Uses `WM_USER+1` custom message to defer registration.
- **WM_HOTKEY handling**: `WM_HOTKEY` messages arrive with `hwnd=0`, so they must be caught in the message pump loop BEFORE `DispatchMessageW`, not in `_wnd_proc`.
- **DB location**: `data/clipboard.db` in project folder (OneDrive synced). WAL mode safe for single machine.
- **Consecutive dedup only**: Only prevents saving if hash matches the LAST entry. Same text copied after other entries will be saved again.

## User Preferences
- UI language: Hebrew
- All UI strings in `app/constants.py` STRINGS dict
- Default hotkey: Ctrl+Alt+V (configurable in config.json)

## Build Instructions
- **EXE naming**: When building exe, always name it `Clipboard_AriGo_YYYY-MM-DD_HHMM.exe` with current date/time, and delete the previous exe file.
