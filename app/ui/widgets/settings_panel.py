"""פאנל הגדרות — overlay בתוך החלון הראשי."""

import tkinter as tk

from app.ui import styles
from app.ui.rtl_helpers import configure_rtl_entry, configure_rtl_label
from app.constants import STRINGS


class SettingsPanel(tk.Frame):
    """פאנל הגדרות שנפתח כ-overlay מעל הרשימה."""

    def __init__(self, parent, config, on_save=None, on_close=None):
        super().__init__(parent, bg=styles.BG_SURFACE)
        self._config = config
        self._on_save = on_save
        self._on_close = on_close

        self._build()

    def _build(self):
        # Title bar
        title_frame = tk.Frame(self, bg=styles.BG_SURFACE)
        title_frame.pack(fill="x", padx=12, pady=(12, 8))

        close_btn = tk.Label(
            title_frame, text="\u2715", bg=styles.BG_SURFACE,
            fg=styles.TEXT_SECONDARY, font=styles.FONT_NORMAL, cursor="hand2",
        )
        close_btn.pack(side="left")
        close_btn.bind("<Button-1>", lambda e: self._close())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=styles.DANGER))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=styles.TEXT_SECONDARY))

        title = tk.Label(
            title_frame, text=STRINGS["settings"],
            bg=styles.BG_SURFACE, fg=styles.TEXT_PRIMARY, font=styles.FONT_TITLE,
        )
        configure_rtl_label(title)
        title.pack(side="right")

        # Separator
        tk.Frame(self, bg=styles.BORDER, height=1).pack(fill="x", padx=12)

        # Settings fields
        fields_frame = tk.Frame(self, bg=styles.BG_SURFACE)
        fields_frame.pack(fill="both", expand=True, padx=12, pady=8)

        # Max entries
        self._max_entries_var = tk.StringVar(
            value=str(self._config.get("max_entries", 5000))
        )
        self._add_field(fields_frame, STRINGS["settings_max_entries"], self._max_entries_var)

        # Max storage MB
        self._max_storage_var = tk.StringVar(
            value=str(self._config.get("max_storage_mb", 500))
        )
        self._add_field(fields_frame, STRINGS["settings_max_storage"], self._max_storage_var)

        # Max age days
        self._max_age_var = tk.StringVar(
            value=str(self._config.get("max_age_days", 90))
        )
        self._add_field(fields_frame, STRINGS["settings_max_age"], self._max_age_var)

        # UI Scale
        self._ui_scale_var = tk.IntVar(
            value=self._config.get("ui_scale", 100)
        )
        scale_frame = tk.Frame(fields_frame, bg=styles.BG_SURFACE)
        scale_frame.pack(fill="x", pady=4)

        scale_label = tk.Label(
            scale_frame, text=STRINGS["settings_ui_scale"],
            bg=styles.BG_SURFACE, fg=styles.TEXT_PRIMARY, font=styles.FONT_NORMAL,
        )
        configure_rtl_label(scale_label)
        scale_label.pack(side="right")

        self._scale_value_label = tk.Label(
            scale_frame, text=f"{self._ui_scale_var.get()}%",
            bg=styles.BG_SURFACE, fg=styles.ACCENT_LIGHT, font=styles.FONT_BOLD,
            width=5,
        )
        self._scale_value_label.pack(side="left", padx=4)

        self._scale_slider = tk.Scale(
            scale_frame, from_=100, to=300, orient="horizontal",
            variable=self._ui_scale_var,
            bg=styles.BG_SURFACE, fg=styles.TEXT_PRIMARY,
            troughcolor=styles.BG_INPUT, highlightthickness=0,
            font=styles.FONT_SMALL, showvalue=False, length=150,
            command=self._on_scale_changed,
        )
        self._scale_slider.pack(side="left", padx=4)

        # Auto start checkbox
        self._auto_start_var = tk.BooleanVar(
            value=self._config.get("auto_start", False)
        )
        auto_frame = tk.Frame(fields_frame, bg=styles.BG_SURFACE)
        auto_frame.pack(fill="x", pady=4)
        cb = tk.Checkbutton(
            auto_frame, text=STRINGS["settings_auto_start"],
            variable=self._auto_start_var,
            bg=styles.BG_SURFACE, fg=styles.TEXT_PRIMARY,
            selectcolor=styles.BG_INPUT, activebackground=styles.BG_SURFACE,
            activeforeground=styles.TEXT_PRIMARY, font=styles.FONT_NORMAL,
            anchor="e",
        )
        cb.pack(side="right")

        # Blacklisted apps
        bl_label = tk.Label(
            fields_frame, text=STRINGS["settings_blacklist"],
            bg=styles.BG_SURFACE, fg=styles.TEXT_PRIMARY, font=styles.FONT_BOLD,
        )
        configure_rtl_label(bl_label)
        bl_label.pack(fill="x", pady=(8, 2))

        bl_frame = tk.Frame(fields_frame, bg=styles.BG_SURFACE)
        bl_frame.pack(fill="x")

        self._blacklist_text = tk.Text(
            bl_frame, bg=styles.BG_INPUT, fg=styles.TEXT_PRIMARY,
            font=styles.FONT_SMALL, height=4, relief="flat", borderwidth=0,
            wrap="word",
        )
        self._blacklist_text.pack(fill="x", pady=2)
        # Pre-fill
        apps = self._config.get("blacklisted_apps", [])
        self._blacklist_text.insert("1.0", "\n".join(apps))

        # Buttons
        btn_frame = tk.Frame(self, bg=styles.BG_SURFACE)
        btn_frame.pack(fill="x", padx=12, pady=(8, 12))

        save_btn = tk.Label(
            btn_frame, text=STRINGS["settings_save"],
            bg=styles.ACCENT, fg=styles.TEXT_PRIMARY, font=styles.FONT_BOLD,
            padx=16, pady=6, cursor="hand2",
        )
        save_btn.pack(side="right", padx=(4, 0))
        save_btn.bind("<Button-1>", lambda e: self._save())
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg=styles.ACCENT_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=styles.ACCENT))

        cancel_btn = tk.Label(
            btn_frame, text=STRINGS["settings_cancel"],
            bg=styles.BG_HOVER, fg=styles.TEXT_PRIMARY, font=styles.FONT_NORMAL,
            padx=16, pady=6, cursor="hand2",
        )
        cancel_btn.pack(side="right")
        cancel_btn.bind("<Button-1>", lambda e: self._close())

    def _add_field(self, parent, label_text, var):
        frame = tk.Frame(parent, bg=styles.BG_SURFACE)
        frame.pack(fill="x", pady=4)

        entry = tk.Entry(
            frame, textvariable=var,
            bg=styles.BG_INPUT, fg=styles.TEXT_PRIMARY,
            insertbackground=styles.TEXT_PRIMARY,
            font=styles.FONT_NORMAL, relief="flat", borderwidth=0, width=10,
        )
        configure_rtl_entry(entry)
        entry.pack(side="left", ipady=3, padx=4)

        label = tk.Label(
            frame, text=label_text,
            bg=styles.BG_SURFACE, fg=styles.TEXT_PRIMARY, font=styles.FONT_NORMAL,
        )
        configure_rtl_label(label)
        label.pack(side="right")

    def _on_scale_changed(self, value):
        self._scale_value_label.config(text=f"{value}%")

    def _save(self):
        self._config.set("ui_scale", self._ui_scale_var.get())

        try:
            self._config.set("max_entries", int(self._max_entries_var.get()))
        except ValueError:
            pass
        try:
            self._config.set("max_storage_mb", int(self._max_storage_var.get()))
        except ValueError:
            pass
        try:
            self._config.set("max_age_days", int(self._max_age_var.get()))
        except ValueError:
            pass

        self._config.set("auto_start", self._auto_start_var.get())

        # Parse blacklist
        bl_text = self._blacklist_text.get("1.0", "end").strip()
        apps = [a.strip() for a in bl_text.split("\n") if a.strip()]
        self._config.set("blacklisted_apps", apps)

        self._config.save()

        if self._on_save:
            self._on_save()
        self._close()

    def _close(self):
        if self._on_close:
            self._on_close()
        self.destroy()
