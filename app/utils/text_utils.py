"""כלי עזר לטקסט — חישוב hash, קיצור, ניקוי HTML."""

import hashlib
import html
import re


def compute_hash(content) -> str:
    """SHA-256 hash של תוכן (str או bytes)."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def truncate(text, max_len=200) -> str:
    """קיצור טקסט עם '...' אם ארוך מדי."""
    if not text:
        return ""
    text = text.replace("\r\n", " ").replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def strip_html(html_content) -> str:
    """הסרת תגיות HTML והחזרת טקסט רגיל."""
    if not html_content:
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", html_content)
    # Decode HTML entities
    text = html.unescape(text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_url(text) -> bool:
    """בדיקה אם הטקסט הוא URL."""
    if not text:
        return False
    text = text.strip()
    return bool(re.match(
        r"^https?://[^\s]+$|^www\.[^\s]+$|^ftp://[^\s]+$",
        text,
        re.IGNORECASE,
    ))
