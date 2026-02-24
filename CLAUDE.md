# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Clipboard AriGo — persistent clipboard history manager for Windows 11.
Python + Tkinter + SQLite (WAL + FTS5) + Win32 API. Hebrew RTL UI, dark theme, frameless floating window.

## Running

```bash
pip install -r requirements.txt
python main.py
```

Single-instance enforced via Windows mutex. Close existing instance (system tray → Exit) before restarting.

## Architecture

### Threading Model (3 threads)

1. **Tkinter main thread** — UI rendering, event loop (`root.mainloop()`)
2. **Win32 message pump thread** (daemon) — `ClipboardMonitor._run()` handles `WM_CLIPBOARDUPDATE` and `WM_HOTKEY`
3. **System tray thread** (daemon) — pystray event loop

Cross-thread rule: all UI calls from other threads go through `root.after(0, callback)`.

### Critical Win32 Threading Constraints

- `RegisterHotKey` **must** be called from the monitor thread. Main thread sends `WM_USER+1` custom message to defer registration.
- `WM_HOTKEY` arrives with `hwnd=0` — must be caught in the message pump loop **before** `DispatchMessageW`, not in `_wnd_proc`.
- Paste-back loop prevention: `monitor.set_suppress_next()` flag skips the next clipboard change.

### Database

SQLite WAL mode with thread-local connections (`threading.local()`). Schema:
- `clipboard_entries` — main data (content_type, content_hash SHA-256, image_path relative, is_pinned, source_app, created_at)
- `clipboard_fts` — FTS5 virtual table synced via triggers
- Consecutive dedup only: blocks save if hash matches the **last** entry

### Clipboard Format Priority

1. CF_HDROP (file paths) → 2. CF_HTML → 3. CF_UNICODETEXT (or URL detection) → 4. CF_DIB (images via PIL)

### Image Storage

Images saved as PNG in `data/images/YYYY/MM/img_YYYYMMDD_HHMMSS_HASH.png`. Relative paths stored in DB.

## Localization

- UI language: **Hebrew** (RTL)
- All UI strings live in `app/constants.py` → `STRINGS` dict
- RTL helpers in `app/ui/rtl_helpers.py`
- Relative time formatting (Hebrew) in `app/utils/date_utils.py`

## Configuration

`config.json` at project root, loaded by singleton `ConfigManager`. Supports dot-notation access (`config.get("hotkey.modifiers")`). Deep-merges with defaults on load.

Global hotkey default: **Ctrl+Alt+V** (Ctrl+Shift+V is taken by Windows).

## Key Modules

| Module | Role |
|--------|------|
| `main.py` | Entry point, wires all components |
| `app/core/clipboard_monitor.py` | Win32 message loop, clipboard + hotkey listeners |
| `app/core/clipboard_handler.py` | Multi-format clipboard read/write |
| `app/db/repository.py` | CRUD + FTS5 search, `ClipboardEntry` dataclass |
| `app/ui/main_window.py` | Frameless popup with fade, resize, keyboard shortcuts |
| `app/ui/styles.py` | Dark theme constants (colors, fonts, dimensions) |
| `app/config_manager.py` | Singleton config with defaults and deep merge |

## UI Keyboard Shortcuts

Escape=hide, Up/Down=navigate, Enter=paste, Delete=remove, 1-9=quick paste, Ctrl+F=search.
