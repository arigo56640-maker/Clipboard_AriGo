"""קריאה וכתיבה מהלוח — תמיכה בטקסט, HTML, תמונות, וקבצים."""

import io
import struct
import ctypes
import ctypes.wintypes

import win32clipboard
import win32con

from app.constants import ContentType
from app.db.repository import ClipboardEntry
from app.utils.text_utils import compute_hash, truncate, strip_html, is_url


# Register HTML clipboard format
CF_HTML = None


def _ensure_cf_html():
    global CF_HTML
    if CF_HTML is None:
        CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")


def read_clipboard():
    """
    קריאת תוכן הלוח הנוכחי.
    מחזיר ClipboardEntry או None אם הלוח ריק/לא נתמך.
    """
    _ensure_cf_html()
    try:
        win32clipboard.OpenClipboard()
    except Exception:
        return None

    try:
        entry = None

        # Priority 1: File paths (CF_HDROP)
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            entry = _read_file_drop()

        # Priority 2: HTML
        if entry is None and CF_HTML and win32clipboard.IsClipboardFormatAvailable(CF_HTML):
            entry = _read_html()

        # Priority 3: Unicode text
        if entry is None and win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            entry = _read_text()

        # Priority 4: Image (CF_DIB)
        if entry is None and win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
            entry = _read_image()

        return entry

    except Exception:
        return None
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass


def _read_text():
    """קריאת טקסט רגיל מהלוח."""
    try:
        text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        if not text or not text.strip():
            return None
        content_type = ContentType.URL if is_url(text) else ContentType.TEXT
        return ClipboardEntry(
            content_type=content_type,
            content_text=text,
            content_preview=truncate(text),
            content_hash=compute_hash(text),
            content_size=len(text.encode("utf-8")),
        )
    except Exception:
        return None


def _read_html():
    """קריאת HTML מהלוח (כולל חילוץ טקסט רגיל)."""
    try:
        raw = win32clipboard.GetClipboardData(CF_HTML)
        if isinstance(raw, bytes):
            html_text = raw.decode("utf-8", errors="replace")
        else:
            html_text = raw

        if not html_text:
            return None

        # Extract the HTML fragment from the CF_HTML envelope
        fragment = _extract_html_fragment(html_text)
        plain_text = strip_html(fragment) if fragment else strip_html(html_text)

        # Also grab plain text if available
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            try:
                plain_text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            except Exception:
                pass

        return ClipboardEntry(
            content_type=ContentType.HTML,
            content_text=plain_text,
            content_html=fragment or html_text,
            content_preview=truncate(plain_text),
            content_hash=compute_hash(html_text),
            content_size=len(html_text.encode("utf-8")),
        )
    except Exception:
        return None


def _extract_html_fragment(cf_html_data):
    """חילוץ הפרגמנט מפורמט CF_HTML."""
    try:
        start_idx = cf_html_data.find("StartFragment:")
        end_idx = cf_html_data.find("EndFragment:")
        if start_idx == -1 or end_idx == -1:
            return None
        start_pos = int(cf_html_data[start_idx + 14:cf_html_data.index("\r", start_idx)])
        end_pos = int(cf_html_data[end_idx + 12:cf_html_data.index("\r", end_idx)])
        # CF_HTML uses byte offsets on the raw bytes
        raw_bytes = cf_html_data.encode("utf-8") if isinstance(cf_html_data, str) else cf_html_data
        return raw_bytes[start_pos:end_pos].decode("utf-8", errors="replace")
    except Exception:
        return None


def _read_file_drop():
    """קריאת רשימת קבצים מהלוח (CF_HDROP)."""
    try:
        file_list = win32clipboard.GetClipboardData(win32con.CF_HDROP)
        if not file_list:
            return None
        paths = "\n".join(file_list)
        return ClipboardEntry(
            content_type=ContentType.FILE_PATH,
            content_text=paths,
            content_preview=truncate(paths),
            content_hash=compute_hash(paths),
            content_size=len(paths.encode("utf-8")),
        )
    except Exception:
        return None


def _read_image():
    """קריאת תמונה מהלוח (CF_DIB) באמצעות Pillow."""
    try:
        from PIL import ImageGrab
        image = ImageGrab.grabclipboard()
        if image is None:
            return None
        # Compute hash from image bytes
        img_bytes = image.tobytes()
        entry = ClipboardEntry(
            content_type=ContentType.IMAGE,
            content_preview="[תמונה]",
            image_width=image.width,
            image_height=image.height,
            content_hash=compute_hash(img_bytes),
            content_size=len(img_bytes),
        )
        entry._pil_image = image
        return entry
    except Exception:
        return None


def push_to_clipboard(entry):
    """
    דחיפת רשומה בחזרה ללוח המערכת.
    מחזיר True אם הצליח.
    """
    _ensure_cf_html()
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()

        if entry.content_type in (ContentType.TEXT, ContentType.URL, ContentType.FILE_PATH):
            win32clipboard.SetClipboardData(
                win32con.CF_UNICODETEXT, entry.content_text
            )

        elif entry.content_type == ContentType.HTML:
            if entry.content_html:
                cf_html_data = _build_cf_html(entry.content_html)
                win32clipboard.SetClipboardData(CF_HTML, cf_html_data.encode("utf-8"))
            if entry.content_text:
                win32clipboard.SetClipboardData(
                    win32con.CF_UNICODETEXT, entry.content_text
                )

        elif entry.content_type == ContentType.IMAGE:
            if entry.image_path:
                _push_image_to_clipboard(entry.image_path)

        win32clipboard.CloseClipboard()
        return True

    except Exception:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
        return False


def _build_cf_html(html_fragment):
    """בניית מעטפת CF_HTML סביב פרגמנט HTML."""
    header_template = (
        "Version:0.9\r\n"
        "StartHTML:{start_html:010d}\r\n"
        "EndHTML:{end_html:010d}\r\n"
        "StartFragment:{start_frag:010d}\r\n"
        "EndFragment:{end_frag:010d}\r\n"
    )
    prefix = "<html><body>\r\n<!--StartFragment-->"
    suffix = "<!--EndFragment-->\r\n</body></html>"

    # Calculate with placeholder
    dummy = header_template.format(start_html=0, end_html=0, start_frag=0, end_frag=0)
    start_html = len(dummy.encode("utf-8"))
    start_frag = start_html + len(prefix.encode("utf-8"))
    end_frag = start_frag + len(html_fragment.encode("utf-8"))
    end_html = end_frag + len(suffix.encode("utf-8"))

    header = header_template.format(
        start_html=start_html, end_html=end_html,
        start_frag=start_frag, end_frag=end_frag,
    )
    return header + prefix + html_fragment + suffix


def _push_image_to_clipboard(image_path):
    """דחיפת תמונה ללוח כ-CF_DIB."""
    try:
        from PIL import Image
        img = Image.open(image_path)
        output = io.BytesIO()
        img.convert("RGB").save(output, "BMP")
        bmp_data = output.getvalue()
        # Strip the 14-byte BMP file header to get DIB
        win32clipboard.SetClipboardData(win32con.CF_DIB, bmp_data[14:])
    except Exception:
        pass
