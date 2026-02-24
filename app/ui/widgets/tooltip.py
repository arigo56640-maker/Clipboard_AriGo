"""Tooltip מותאם אישית עבור Tkinter."""

import tkinter as tk
from app.ui import styles


class Tooltip:
    """tooltip שצץ מעל widget כשהעכבר מרחף."""

    def __init__(self, widget, text="", delay=500):
        self._widget = widget
        self._text = text
        self._delay = delay
        self._tip_window = None
        self._after_id = None

        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._cancel, add="+")
        widget.bind("<Button>", self._cancel, add="+")

    def update_text(self, text):
        self._text = text

    def _schedule(self, event=None):
        self._cancel()
        self._after_id = self._widget.after(self._delay, self._show)

    def _cancel(self, event=None):
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self):
        if not self._text:
            return
        x = self._widget.winfo_rootx() + self._widget.winfo_width() // 2
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4

        self._tip_window = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)
        tw.configure(bg=styles.BG_SURFACE)

        label = tk.Label(
            tw,
            text=self._text,
            bg=styles.BG_SURFACE,
            fg=styles.TEXT_PRIMARY,
            font=styles.FONT_SMALL,
            padx=8,
            pady=4,
            wraplength=300,
            justify="right",
        )
        label.pack()

        tw.update_idletasks()
        tw_width = tw.winfo_width()
        tw_height = tw.winfo_height()

        # Keep within screen bounds
        screen_w = self._widget.winfo_screenwidth()
        screen_h = self._widget.winfo_screenheight()
        if x + tw_width > screen_w:
            x = screen_w - tw_width - 10
        if y + tw_height > screen_h:
            y = self._widget.winfo_rooty() - tw_height - 4

        tw.wm_geometry(f"+{x}+{y}")

    def _hide(self):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None
