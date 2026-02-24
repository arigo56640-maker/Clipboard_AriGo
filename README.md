# Clipboard AriGo

מנהל היסטוריית לוח עריכה מתמיד עבור Windows 11.

> Persistent clipboard history manager for Windows 11 — Hebrew RTL UI, dark theme, frameless floating window.

---

## תכונות עיקריות

- שמירה אוטומטית של כל מה שמועתק ללוח (טקסט, HTML, תמונות, קבצים)
- ממשק משתמש בעברית עם תמיכה ב-RTL
- חלון צף ללא מסגרת עם אנימציית fade
- חיפוש מלא בהיסטוריה (FTS5)
- הצמדת פריטים חשובים (Pin)
- פתיחה מהירה עם קיצור מקלדת גלובלי `Ctrl+Alt+V`
- אייקון במגש המערכת (System Tray)
- מניעת כפילויות רצופות (SHA-256)
- תמיכה בכל פורמטי הלוח: טקסט, HTML, תמונות, נתיבי קבצים

---

## דרישות מערכת

- Windows 11
- Python 3.10+

---

## התקנה והפעלה

```bash
pip install -r requirements.txt
python main.py
```

> הערה: מופע יחיד בלבד. אם כבר פועל — סגור דרך מגש המערכת ← Exit לפני הפעלה מחדש.

---

## קיצורי מקלדת

| קיצור | פעולה |
|-------|--------|
| `Ctrl+Alt+V` | פתיחת החלון |
| `Up / Down` | ניווט ברשימה |
| `Enter` | הדבקת הפריט הנבחר |
| `Delete` | מחיקת הפריט הנבחר |
| `1`–`9` | הדבקה מהירה לפי מיקום |
| `Ctrl+F` | חיפוש |
| `Escape` | סגירת החלון |

---

## ארכיטקטורה

### 3 Threads

| Thread | תפקיד |
|--------|--------|
| Tkinter main thread | רינדור UI ולולאת אירועים |
| Win32 message pump | `WM_CLIPBOARDUPDATE` + `WM_HOTKEY` |
| System tray | pystray event loop |

### מסד נתונים

SQLite עם WAL mode ו-FTS5 לחיפוש מלא:
- `clipboard_entries` — נתוני הפריטים
- `clipboard_fts` — טבלת חיפוש וירטואלית (מסונכרנת עם triggers)

### עדיפות פורמטי לוח

`CF_HDROP` → `CF_HTML` → `CF_UNICODETEXT` → `CF_DIB`

---

## מודולים מרכזיים

| מודול | תפקיד |
|-------|--------|
| `main.py` | נקודת כניסה |
| `app/core/clipboard_monitor.py` | Win32 message loop |
| `app/core/clipboard_handler.py` | קריאה/כתיבה ללוח |
| `app/db/repository.py` | CRUD + FTS5 |
| `app/ui/main_window.py` | חלון הפופ-אפ |
| `app/config_manager.py` | הגדרות (config.json) |

---

## קונפיגורציה

קובץ `config.json` בתיקיית הפרויקט. תומך בגישה בסימון נקודה:

```json
{
  "hotkey": {
    "modifiers": ["ctrl", "alt"],
    "key": "v"
  }
}
```

---

## טכנולוגיות

`Python` · `Tkinter` · `SQLite (WAL + FTS5)` · `Win32 API` · `Pillow` · `pystray` · `pywin32`
