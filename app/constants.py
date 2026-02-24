"""קבועים, מחרוזות בעברית, ו-enums עבור Clipboard AriGo."""

APP_NAME = "Clipboard AriGo"
APP_VERSION = "1.0.0"
MUTEX_NAME = "ClipboardAriGoMutex"
WINDOW_CLASS_NAME = "ClipboardAriGoMonitor"

# Content types
class ContentType:
    TEXT = "text"
    HTML = "html"
    IMAGE = "image"
    FILE_PATH = "file_path"
    URL = "url"

ALL_CONTENT_TYPES = [
    ContentType.TEXT,
    ContentType.HTML,
    ContentType.IMAGE,
    ContentType.FILE_PATH,
    ContentType.URL,
]

# Hebrew UI strings
STRINGS = {
    # App
    "app_title": "מנהל הלוח - AriGo",

    # Main window
    "search_placeholder": "חיפוש...",
    "filter_all": "הכל",
    "filter_text": "טקסט",
    "filter_image": "תמונה",
    "filter_html": "טקסט עשיר",
    "filter_file": "קבצים",
    "filter_url": "קישורים",

    # Actions
    "pin": "הצמד",
    "unpin": "בטל הצמדה",
    "delete": "מחק",
    "copy": "העתק",
    "paste": "הדבק",
    "clear_history": "נקה היסטוריה",
    "confirm_clear": "האם למחוק את כל ההיסטוריה?",
    "yes": "כן",
    "no": "לא",

    # Status
    "pinned": "מוצמד",
    "no_results": "לא נמצאו תוצאות",
    "empty_history": "ההיסטוריה ריקה",
    "items_count": "{count} פריטים",

    # Relative time
    "ago_now": "עכשיו",
    "ago_seconds": "לפני {n} שניות",
    "ago_minute": "לפני דקה",
    "ago_minutes": "לפני {n} דקות",
    "ago_hour": "לפני שעה",
    "ago_hours": "לפני {n} שעות",
    "ago_yesterday": "אתמול",
    "ago_days": "לפני {n} ימים",
    "ago_weeks": "לפני {n} שבועות",
    "ago_month": "לפני חודש",
    "ago_months": "לפני {n} חודשים",
    "ago_year": "לפני שנה",
    "ago_years": "לפני {n} שנים",

    # Tray menu
    "tray_show": "הצג חלון",
    "tray_settings": "הגדרות",
    "tray_pause": "השהה ניטור",
    "tray_resume": "המשך ניטור",
    "tray_exit": "יציאה",

    # Settings
    "settings": "הגדרות",
    "settings_hotkey": "קיצור מקשים",
    "settings_max_entries": "מקסימום רשומות",
    "settings_max_storage": "מקסימום אחסון (MB)",
    "settings_max_age": "מחק ישן מ (ימים)",
    "settings_auto_start": "הפעלה אוטומטית עם Windows",
    "settings_blacklist": "אפליקציות חסומות",
    "settings_add_app": "הוסף אפליקציה",
    "settings_remove_app": "הסר",
    "settings_save": "שמור",
    "settings_cancel": "ביטול",
    "settings_saved": "ההגדרות נשמרו",
    "settings_ui_scale": "גודל תצוגה (%)",

    # Content type icons (emoji)
    "icon_text": "📝",
    "icon_html": "🌐",
    "icon_image": "🖼️",
    "icon_file": "📁",
    "icon_url": "🔗",
}

# Map content type to filter label key
CONTENT_TYPE_LABELS = {
    ContentType.TEXT: "filter_text",
    ContentType.HTML: "filter_html",
    ContentType.IMAGE: "filter_image",
    ContentType.FILE_PATH: "filter_file",
    ContentType.URL: "filter_url",
}

CONTENT_TYPE_ICONS = {
    ContentType.TEXT: "icon_text",
    ContentType.HTML: "icon_html",
    ContentType.IMAGE: "icon_image",
    ContentType.FILE_PATH: "icon_file",
    ContentType.URL: "icon_url",
}
