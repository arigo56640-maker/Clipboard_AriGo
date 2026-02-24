"""סרגל חיפוש + סינון לפי סוג תוכן."""

import tkinter as tk

from app.ui import styles
from app.ui.rtl_helpers import configure_rtl_entry
from app.constants import STRINGS, ContentType


class SearchBar(tk.Frame):
    """סרגל חיפוש עם שדה טקסט ולחצני סינון סוג."""

    FILTER_OPTIONS = [
        (None, "filter_all"),
        (ContentType.TEXT, "filter_text"),
        (ContentType.IMAGE, "filter_image"),
        (ContentType.HTML, "filter_html"),
        (ContentType.FILE_PATH, "filter_file"),
        (ContentType.URL, "filter_url"),
    ]

    def __init__(self, parent, on_search_changed=None):
        super().__init__(parent, bg=styles.BG_SURFACE, height=styles.SEARCH_BAR_HEIGHT)
        self.pack_propagate(False)
        self._on_search_changed = on_search_changed
        self._active_filter = None
        self._debounce_id = None
        self._filter_buttons = []

        self._build()

    def _build(self):
        # Search entry
        search_frame = tk.Frame(self, bg=styles.BG_SURFACE)
        search_frame.pack(fill="x", padx=8, pady=(6, 2))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_text_changed)

        self._entry = tk.Entry(
            search_frame,
            textvariable=self._search_var,
            bg=styles.BG_INPUT,
            fg=styles.TEXT_PRIMARY,
            insertbackground=styles.TEXT_PRIMARY,
            font=styles.FONT_NORMAL,
            relief="flat",
            borderwidth=0,
        )
        configure_rtl_entry(self._entry)
        self._entry.pack(fill="x", ipady=4, padx=4)

        # Placeholder
        self._placeholder_visible = True
        self._entry.insert(0, STRINGS["search_placeholder"])
        self._entry.configure(fg=styles.TEXT_PLACEHOLDER)
        self._entry.bind("<FocusIn>", self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)

        # Filter buttons row
        filter_frame = tk.Frame(self, bg=styles.BG_SURFACE)
        filter_frame.pack(fill="x", padx=8, pady=(0, 4))

        for content_type, label_key in self.FILTER_OPTIONS:
            btn = tk.Label(
                filter_frame,
                text=STRINGS[label_key],
                bg=styles.BG_SURFACE,
                fg=styles.TEXT_SECONDARY,
                font=styles.FONT_SMALL,
                padx=6,
                pady=1,
                cursor="hand2",
            )
            btn.pack(side="right", padx=2)
            btn.bind("<Button-1>", lambda e, ct=content_type, b=btn: self._set_filter(ct, b))
            self._filter_buttons.append((btn, content_type))

        # Highlight initial filter (All)
        if self._filter_buttons:
            self._highlight_filter_button(self._filter_buttons[0][0])

    def _on_focus_in(self, event=None):
        if self._placeholder_visible:
            self._entry.delete(0, "end")
            self._entry.configure(fg=styles.TEXT_PRIMARY)
            self._placeholder_visible = False

    def _on_focus_out(self, event=None):
        if not self._search_var.get():
            self._placeholder_visible = True
            self._entry.insert(0, STRINGS["search_placeholder"])
            self._entry.configure(fg=styles.TEXT_PLACEHOLDER)

    def _on_text_changed(self, *args):
        if self._placeholder_visible:
            return
        # Debounce: wait 200ms after last keystroke
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(200, self._emit_search)

    def _set_filter(self, content_type, button):
        self._active_filter = content_type
        # Update button highlighting
        for btn, _ in self._filter_buttons:
            btn.configure(bg=styles.BG_SURFACE, fg=styles.TEXT_SECONDARY)
        self._highlight_filter_button(button)
        self._emit_search()

    def _highlight_filter_button(self, button):
        button.configure(bg=styles.ACCENT, fg=styles.TEXT_PRIMARY)

    def _emit_search(self):
        if self._on_search_changed:
            query = "" if self._placeholder_visible else self._search_var.get()
            self._on_search_changed(query, self._active_filter)

    def focus_search(self):
        """מיקוד הקלט על שדה החיפוש."""
        self._on_focus_in()
        self._entry.focus_set()

    def clear(self):
        self._entry.delete(0, "end")
        self._placeholder_visible = False
        self._active_filter = None
        for btn, _ in self._filter_buttons:
            btn.configure(bg=styles.BG_SURFACE, fg=styles.TEXT_SECONDARY)
        if self._filter_buttons:
            self._highlight_filter_button(self._filter_buttons[0][0])
