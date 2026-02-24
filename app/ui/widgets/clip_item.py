"""Widget עבור שורת פריט בודד בהיסטוריית הלוח."""

import tkinter as tk
from PIL import ImageTk

from app.ui import styles
from app.ui.widgets.tooltip import Tooltip
from app.constants import STRINGS, CONTENT_TYPE_ICONS
from app.utils.date_utils import relative_time


class ClipItem(tk.Frame):
    """שורת פריט בודד ברשימת ההיסטוריה."""

    def __init__(self, parent, entry, image_storage=None, on_click=None,
                 on_delete=None, on_pin_toggle=None, index=0, selected=False):
        super().__init__(parent, bg=styles.BG_PRIMARY, cursor="hand2")
        self.entry = entry
        self._on_click = on_click
        self._on_delete = on_delete
        self._on_pin_toggle = on_pin_toggle
        self._image_storage = image_storage
        self._index = index
        self._selected = selected
        self._thumbnail_ref = None  # Keep reference to prevent GC

        self._build()
        self._bind_events()
        self.set_selected(selected)

    def _build(self):
        self.configure(height=styles.ITEM_HEIGHT, padx=0, pady=0)
        self.pack_propagate(False)

        # Main row container
        row = tk.Frame(self, bg=self.cget("bg"))
        row.pack(fill="both", expand=True, padx=styles.ITEM_PADDING_X,
                 pady=styles.ITEM_PADDING_Y)

        # Left side: index number + actions
        left = tk.Frame(row, bg=row.cget("bg"))
        left.pack(side="left", fill="y")

        # Index number (1-9 for quick access)
        if self._index < 9:
            idx_label = tk.Label(
                left, text=str(self._index + 1),
                bg=left.cget("bg"), fg=styles.TEXT_SECONDARY,
                font=styles.FONT_SMALL, width=2,
            )
            idx_label.pack(side="top", anchor="w")

        # Right side: content type icon
        icon_key = CONTENT_TYPE_ICONS.get(self.entry.content_type, "icon_text")
        icon_text = STRINGS.get(icon_key, "")

        right = tk.Frame(row, bg=row.cget("bg"))
        right.pack(side="right", fill="y", padx=(0, 4))

        icon_label = tk.Label(
            right, text=icon_text,
            bg=right.cget("bg"), fg=styles.TEXT_SECONDARY,
            font=(styles.FONT_FAMILY, 14),
        )
        icon_label.pack(side="top")

        # Pin indicator
        if self.entry.is_pinned:
            pin_label = tk.Label(
                right, text="📌",
                bg=right.cget("bg"), fg=styles.PIN_COLOR,
                font=styles.FONT_SMALL,
            )
            pin_label.pack(side="top")

        # Center: preview text + metadata
        center = tk.Frame(row, bg=row.cget("bg"))
        center.pack(side="right", fill="both", expand=True, padx=(4, 4))

        # Preview text or thumbnail
        if self.entry.content_type == "image" and self._image_storage and self.entry.image_path:
            thumb = self._image_storage.load_thumbnail(self.entry.image_path, size=(60, 40))
            if thumb:
                self._thumbnail_ref = ImageTk.PhotoImage(thumb)
                preview_label = tk.Label(
                    center, image=self._thumbnail_ref,
                    bg=center.cget("bg"),
                )
                preview_label.pack(side="top", anchor="e")
            else:
                self._make_text_preview(center)
        else:
            self._make_text_preview(center)

        # Metadata: source app + time
        meta_frame = tk.Frame(center, bg=center.cget("bg"))
        meta_frame.pack(side="bottom", fill="x")

        time_text = relative_time(self.entry.created_at)
        meta_text = time_text
        if self.entry.source_app:
            meta_text = f"{self.entry.source_app}  |  {time_text}"

        meta_label = tk.Label(
            meta_frame, text=meta_text,
            bg=meta_frame.cget("bg"), fg=styles.TEXT_SECONDARY,
            font=styles.FONT_SMALL, anchor="e", justify="right",
        )
        meta_label.pack(side="right")

        # Tooltip with full text
        if self.entry.content_text:
            full_text = self.entry.content_text[:500]
            Tooltip(self, full_text)

        # Bottom separator line
        sep = tk.Frame(self, bg=styles.BORDER, height=1)
        sep.pack(side="bottom", fill="x")

    def _make_text_preview(self, parent):
        preview = self.entry.content_preview or ""
        if not preview and self.entry.content_text:
            preview = self.entry.content_text[:200]

        label = tk.Label(
            parent, text=preview,
            bg=parent.cget("bg"), fg=styles.TEXT_PRIMARY,
            font=styles.FONT_NORMAL, anchor="e", justify="right",
            wraplength=280,
        )
        label.pack(side="top", anchor="e")

    def set_selected(self, selected):
        self._selected = selected
        bg = styles.BG_SELECTED if selected else styles.BG_PRIMARY
        self._set_bg_recursive(self, bg)

    def _set_bg_recursive(self, widget, bg):
        try:
            widget.configure(bg=bg)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._set_bg_recursive(child, bg)

    def _bind_events(self):
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        # Bind children too
        for child in self.winfo_children():
            child.bind("<Button-1>", self._click)
            self._bind_children(child)

    def _bind_children(self, widget):
        for child in widget.winfo_children():
            child.bind("<Button-1>", self._click)
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)
            self._bind_children(child)

    def _click(self, event=None):
        if self._on_click:
            self._on_click(self.entry)

    def _on_enter(self, event=None):
        if not self._selected:
            self._set_bg_recursive(self, styles.BG_HOVER)

    def _on_leave(self, event=None):
        if not self._selected:
            self._set_bg_recursive(self, styles.BG_PRIMARY)
