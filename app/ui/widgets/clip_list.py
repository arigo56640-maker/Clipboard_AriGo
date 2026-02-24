"""רשימה גלילה של פריטי לוח — Scrollable list of clipboard items."""

import tkinter as tk

from app.ui import styles
from app.ui.widgets.clip_item import ClipItem
from app.constants import STRINGS


class ClipList(tk.Frame):
    """רשימת פריטים עם גלילה ותמיכה בניווט מקלדת."""

    def __init__(self, parent, image_storage=None, on_item_click=None,
                 on_item_delete=None, on_pin_toggle=None):
        super().__init__(parent, bg=styles.BG_PRIMARY)
        self._image_storage = image_storage
        self._on_item_click = on_item_click
        self._on_item_delete = on_item_delete
        self._on_pin_toggle = on_pin_toggle
        self._items = []
        self._entries = []
        self._selected_index = -1

        self._build()

    def _build(self):
        # Canvas for scrolling
        self._canvas = tk.Canvas(
            self, bg=styles.BG_PRIMARY, highlightthickness=0,
            borderwidth=0,
        )
        self._scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self._canvas.yview,
            width=styles.SCROLLBAR_WIDTH,
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side="left", fill="y")
        self._canvas.pack(side="right", fill="both", expand=True)

        # Inner frame
        self._inner = tk.Frame(self._canvas, bg=styles.BG_PRIMARY)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw",
        )

        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Empty state label
        self._empty_label = tk.Label(
            self._inner, text=STRINGS["empty_history"],
            bg=styles.BG_PRIMARY, fg=styles.TEXT_SECONDARY,
            font=styles.FONT_LARGE, anchor="center", justify="center",
        )

    def set_entries(self, entries):
        """עדכון רשימת הפריטים."""
        # Clear existing items
        for item in self._items:
            item.destroy()
        self._items.clear()
        self._entries = entries
        self._selected_index = -1

        if not entries:
            self._empty_label.pack(fill="both", expand=True, pady=80)
            return

        self._empty_label.pack_forget()

        for i, entry in enumerate(entries):
            item = ClipItem(
                self._inner,
                entry=entry,
                image_storage=self._image_storage,
                on_click=self._on_item_click,
                on_delete=self._on_item_delete,
                on_pin_toggle=self._on_pin_toggle,
                index=i,
                selected=False,
            )
            item.pack(fill="x")
            self._items.append(item)

        # Select first item
        if self._items:
            self.select(0)

    def select(self, index):
        """בחירת פריט לפי אינדקס."""
        if not self._items:
            return
        index = max(0, min(index, len(self._items) - 1))

        # Deselect previous
        if 0 <= self._selected_index < len(self._items):
            self._items[self._selected_index].set_selected(False)

        self._selected_index = index
        self._items[index].set_selected(True)

        # Scroll into view
        self._scroll_to_item(index)

    def select_next(self):
        if self._items:
            self.select(self._selected_index + 1)

    def select_previous(self):
        if self._items:
            self.select(self._selected_index - 1)

    def get_selected_entry(self):
        if 0 <= self._selected_index < len(self._entries):
            return self._entries[self._selected_index]
        return None

    def get_entry_by_index(self, index):
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

    def _scroll_to_item(self, index):
        """גלילה אוטומטית לפריט."""
        if not self._items or index >= len(self._items):
            return
        self._inner.update_idletasks()
        item = self._items[index]
        item_y = item.winfo_y()
        item_h = item.winfo_height()
        canvas_h = self._canvas.winfo_height()
        scroll_top = self._canvas.canvasy(0)
        scroll_bottom = scroll_top + canvas_h

        if item_y < scroll_top:
            self._canvas.yview_moveto(item_y / self._inner.winfo_reqheight())
        elif item_y + item_h > scroll_bottom:
            target = (item_y + item_h - canvas_h) / self._inner.winfo_reqheight()
            self._canvas.yview_moveto(target)

    def _on_inner_configure(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
