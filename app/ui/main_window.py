"""חלון צף ראשי — frameless floating popup."""

import ctypes
import ctypes.wintypes
import tkinter as tk

from app.ui import styles
from app.ui.widgets.search_bar import SearchBar
from app.ui.widgets.clip_list import ClipList
from app.ui.widgets.settings_panel import SettingsPanel
from app.constants import STRINGS

DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2


class MainWindow(tk.Toplevel):
    """חלון ראשי צף ללא מסגרת עם ערכת נושא כהה."""

    def __init__(self, master, repo, config, image_storage, on_paste):
        super().__init__(master)
        self._repo = repo
        self._config = config
        self._image_storage = image_storage
        self._on_paste = on_paste
        self._visible = False
        self._settings_open = False

        self.withdraw()

        # Frameless window setup
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.configure(bg=styles.BG_PRIMARY)

        # Build UI
        self._build_title_bar()
        self._search_bar = SearchBar(self, on_search_changed=self._on_search_changed)
        self._search_bar.pack(fill="x")

        self._clip_list = ClipList(
            self,
            image_storage=image_storage,
            on_item_click=self._on_item_clicked,
        )
        self._clip_list.pack(fill="both", expand=True)

        # Status bar
        self._status_var = tk.StringVar(value="")
        status = tk.Label(
            self, textvariable=self._status_var,
            bg=styles.BG_SURFACE, fg=styles.TEXT_SECONDARY,
            font=styles.FONT_SMALL, anchor="e", padx=8, pady=2,
        )
        status.pack(fill="x", side="bottom")

        # Key bindings
        self.bind("<Escape>", lambda e: self.hide())
        self.bind("<Up>", lambda e: self._clip_list.select_previous())
        self.bind("<Down>", lambda e: self._clip_list.select_next())
        self.bind("<Return>", lambda e: self._paste_selected())
        self.bind("<Delete>", lambda e: self._delete_selected())
        self.bind("<Control-f>", lambda e: self._search_bar.focus_search())

        # Number keys 1-9 for quick paste
        for i in range(1, 10):
            self.bind(str(i), lambda e, idx=i: self._paste_by_index(idx - 1))

        # Resize: cursor + drag on window edges
        self.bind("<Motion>", self._update_cursor)
        self.bind("<ButtonPress-1>", self._on_window_press)
        self.bind("<B1-Motion>", self._on_window_b1_motion)
        self.bind("<ButtonRelease-1>", self._on_window_release)

        # Focus management
        self.bind("<FocusOut>", self._on_focus_out)

        # Drag state
        self._drag_x = 0
        self._drag_y = 0

        # Resize state
        self._resize_edge = None
        self._resize_margin = 6

        # Apply Windows 11 rounded corners
        self.after(50, self._apply_rounded_corners)

    def _build_title_bar(self):
        bar = tk.Frame(self, bg=styles.BG_SURFACE, height=styles.TITLE_BAR_HEIGHT)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        # Close button (left for RTL)
        close_btn = tk.Label(
            bar, text="\u2715", bg=styles.BG_SURFACE, fg=styles.TEXT_SECONDARY,
            font=(styles.FONT_FAMILY, 12), cursor="hand2", padx=8,
        )
        close_btn.pack(side="left")
        close_btn.bind("<Button-1>", lambda e: self.hide())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=styles.DANGER))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=styles.TEXT_SECONDARY))

        # Settings button
        settings_btn = tk.Label(
            bar, text="\u2699", bg=styles.BG_SURFACE, fg=styles.TEXT_SECONDARY,
            font=(styles.FONT_FAMILY, 14), cursor="hand2", padx=4,
        )
        settings_btn.pack(side="left")
        settings_btn.bind("<Button-1>", lambda e: self.show_settings())
        settings_btn.bind("<Enter>", lambda e: settings_btn.config(fg=styles.ACCENT_LIGHT))
        settings_btn.bind("<Leave>", lambda e: settings_btn.config(fg=styles.TEXT_SECONDARY))

        # Title (right side for RTL)
        title = tk.Label(
            bar, text=STRINGS["app_title"], bg=styles.BG_SURFACE,
            fg=styles.TEXT_PRIMARY, font=styles.FONT_TITLE,
        )
        title.pack(side="right", padx=12)

        # Drag bindings
        for w in (bar, title):
            w.bind("<Button-1>", self._start_drag)
            w.bind("<B1-Motion>", self._do_drag)

    def _apply_rounded_corners(self):
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if hwnd:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
                    ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
                    ctypes.sizeof(ctypes.c_int),
                )
        except Exception:
            pass

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_drag(self, event):
        if self._resize_edge:
            return
        x = self.winfo_x() + event.x - self._drag_x
        y = self.winfo_y() + event.y - self._drag_y
        self.geometry(f"+{x}+{y}")

    # --- Resize support for frameless window ---

    def _detect_edge(self, event):
        """זיהוי קצה החלון לפי מיקום העכבר."""
        m = self._resize_margin
        w = self.winfo_width()
        h = self.winfo_height()
        x, y = event.x, event.y

        edge = ""
        if y < m:
            edge += "n"
        elif y > h - m:
            edge += "s"
        if x < m:
            edge += "w"
        elif x > w - m:
            edge += "e"
        return edge or None

    _CURSOR_MAP = {
        "n": "top_side", "s": "bottom_side",
        "w": "left_side", "e": "right_side",
        "nw": "top_left_corner", "ne": "top_right_corner",
        "sw": "bottom_left_corner", "se": "bottom_right_corner",
    }

    def _update_cursor(self, event):
        """עדכון סמן העכבר בהתאם לקצה."""
        edge = self._detect_edge(event)
        cursor = self._CURSOR_MAP.get(edge, "")
        self.configure(cursor=cursor)

    def _on_resize_drag(self, event):
        """גרירת קצה לשינוי גודל."""
        if not self._resize_edge:
            return

        x = self.winfo_x()
        y = self.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()

        # Absolute mouse position
        mx = self.winfo_pointerx()
        my = self.winfo_pointery()

        min_w = styles.MIN_WINDOW_WIDTH
        min_h = styles.MIN_WINDOW_HEIGHT

        if "e" in self._resize_edge:
            w = max(min_w, mx - x)
        if "s" in self._resize_edge:
            h = max(min_h, my - y)
        if "w" in self._resize_edge:
            new_w = max(min_w, x + w - mx)
            x = x + w - new_w
            w = new_w
        if "n" in self._resize_edge:
            new_h = max(min_h, y + h - my)
            y = y + h - new_h
            h = new_h

        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_window_press(self, event):
        edge = self._detect_edge(event)
        if edge:
            self._resize_edge = edge

    def _on_window_b1_motion(self, event):
        if self._resize_edge:
            self._on_resize_drag(event)

    def _on_window_release(self, event):
        self._resize_edge = None

    def show(self):
        if self._visible:
            return

        scale = self._config.get("ui_scale", 100) / 100.0
        base_w = self._config.get("window.width", styles.WINDOW_WIDTH)
        base_h = self._config.get("window.height", styles.WINDOW_HEIGHT)
        width = int(base_w * scale)
        height = int(base_h * scale)

        # Position near cursor
        cx, cy = self.winfo_pointerxy()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = min(cx - width // 2, sw - width - 10)
        x = max(10, x)
        y = min(cy + 20, sh - height - 40)
        y = max(10, y)

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.deiconify()
        self._fade_in()
        self._visible = True

        self._search_bar.clear()
        self.refresh_list()
        self.focus_force()

    def hide(self):
        if not self._visible:
            return
        self._fade_out()
        self._visible = False

    def toggle(self):
        if self._visible:
            self.hide()
        else:
            self.show()

    def refresh_list(self, query="", content_type=None):
        if query:
            entries = self._repo.search(query, content_type=content_type, limit=100)
        else:
            entries = self._repo.get_recent(limit=100)
            if content_type:
                entries = [e for e in entries if e.content_type == content_type]

        self._clip_list.set_entries(entries)

        count = len(entries)
        self._status_var.set(STRINGS["items_count"].format(count=count))

    def on_new_entry_added(self):
        """נקרא מ-thread אחר דרך root.after() כשנוסף פריט חדש."""
        if self._visible:
            self.refresh_list()

    def show_settings(self):
        if self._settings_open:
            return
        self._settings_open = True
        panel = SettingsPanel(
            self, self._config,
            on_save=self._on_settings_saved,
            on_close=self._on_settings_closed,
        )
        panel.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _on_settings_saved(self):
        self._settings_open = False

    def _on_settings_closed(self):
        self._settings_open = False

    def _on_search_changed(self, query, content_type):
        self.refresh_list(query, content_type)

    def _on_item_clicked(self, entry):
        self._do_paste(entry)

    def _paste_selected(self):
        entry = self._clip_list.get_selected_entry()
        if entry:
            self._do_paste(entry)

    def _paste_by_index(self, index):
        entry = self._clip_list.get_entry_by_index(index)
        if entry:
            self._do_paste(entry)

    def _do_paste(self, entry):
        if self._on_paste:
            self._on_paste(entry)
        self.hide()

    def _delete_selected(self):
        entry = self._clip_list.get_selected_entry()
        if entry and entry.id:
            self._repo.delete(entry.id)
            if entry.image_path:
                self._image_storage.delete(entry.image_path)
            self.refresh_list()

    def _on_focus_out(self, event):
        if self._settings_open:
            return
        self.after(150, self._check_focus)

    def _check_focus(self):
        if self._settings_open:
            return
        focused = self.focus_get()
        if focused is None:
            self.hide()

    def _fade_in(self, alpha=0.0):
        target = self._config.get("window.opacity", 0.97)
        if alpha < target:
            self.attributes("-alpha", alpha)
            self.after(15, self._fade_in, min(alpha + 0.12, target))
        else:
            self.attributes("-alpha", target)

    def _fade_out(self, alpha=None):
        if alpha is None:
            alpha = float(self.attributes("-alpha"))
        if alpha > 0.05:
            self.attributes("-alpha", alpha)
            self.after(12, self._fade_out, alpha - 0.15)
        else:
            self.attributes("-alpha", 0.0)
            self.withdraw()
