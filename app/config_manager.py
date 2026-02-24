"""ניהול הגדרות — טעינה, שמירה, ערכי ברירת מחדל."""

import json
import os

DEFAULTS = {
    "hotkey": {"modifiers": ["ctrl", "alt"], "key": "v"},
    "max_entries": 5000,
    "max_storage_mb": 500,
    "max_age_days": 90,
    "cleanup_interval_minutes": 30,
    "auto_start": False,
    "blacklisted_apps": ["KeePass.exe", "1Password.exe"],
    "deduplicate_consecutive": True,
    "window": {"width": 840, "height": 1040, "opacity": 0.97},
    "ui_scale": 100,
    "ui": {"font_family": "Segoe UI", "font_size": 11, "theme": "dark"},
}


class ConfigManager:
    _instance = None

    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path=None):
        if self._initialized:
            return
        self._config_path = config_path
        self._data = self._deep_copy(DEFAULTS)
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            self._deep_merge(self._data, user_config)
        self._initialized = True

    @staticmethod
    def _deep_copy(d):
        return json.loads(json.dumps(d))

    @staticmethod
    def _deep_merge(base, override):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigManager._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key, default=None):
        keys = key.split(".")
        val = self._data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key, value):
        keys = key.split(".")
        d = self._data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self.save()

    def save(self):
        if self._config_path:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)

    def hotkey_to_win32(self):
        """המרת הגדרת hotkey לפורמט Win32 (modifiers_int, vk_int)."""
        import win32con

        mod_map = {
            "ctrl": win32con.MOD_CONTROL,
            "shift": win32con.MOD_SHIFT,
            "alt": win32con.MOD_ALT,
            "win": win32con.MOD_WIN,
        }
        mods = 0
        for m in self.get("hotkey.modifiers", []):
            mods |= mod_map.get(m.lower(), 0)
        vk = ord(self.get("hotkey.key", "V").upper())
        return mods, vk

    @classmethod
    def reset(cls):
        """Reset singleton (for testing)."""
        cls._instance = None
