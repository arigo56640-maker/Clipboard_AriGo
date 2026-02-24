"""כלי עזר לתמיכה בעברית RTL ב-Tkinter."""

import tkinter as tk

# Unicode directional marks
RLM = "\u200F"  # Right-to-Left Mark
RLE = "\u202B"  # Right-to-Left Embedding
PDF = "\u202C"  # Pop Directional Formatting


def rtl_wrap(text):
    """עטיפת טקסט בסימני RTL לתצוגה נכונה."""
    if not text:
        return text
    return f"{RLE}{text}{PDF}"


def configure_rtl_entry(entry):
    """הגדרת Entry widget לכתיבה מימין לשמאל."""
    entry.configure(justify="right")


def configure_rtl_label(label):
    """הגדרת Label לתצוגה מימין לשמאל."""
    label.configure(anchor="e", justify="right")


def configure_rtl_text(text_widget):
    """הגדרת Text widget ל-RTL."""
    text_widget.tag_configure("rtl", justify="right")


def is_hebrew(text):
    """בדיקה אם הטקסט מכיל תווים בעברית."""
    if not text:
        return False
    for ch in text:
        if "\u0590" <= ch <= "\u05FF":
            return True
    return False
