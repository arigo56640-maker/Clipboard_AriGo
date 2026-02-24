"""ניהול שמירה, טעינה ומחיקה של תמונות מהלוח."""

import hashlib
import os
from datetime import datetime


class ImageStorage:
    def __init__(self, base_dir):
        """base_dir = data/images (absolute path)."""
        self._base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save(self, image) -> str:
        """
        שמירת תמונה (PIL Image) וחזרת נתיב יחסי ל-data/.
        הנתיב היחסי נשמר ב-DB.
        """
        now = datetime.now()
        sub_dir = os.path.join(self._base_dir, now.strftime("%Y"), now.strftime("%m"))
        os.makedirs(sub_dir, exist_ok=True)

        # Unique filename
        img_bytes = image.tobytes()
        short_hash = hashlib.sha256(img_bytes).hexdigest()[:6]
        filename = f"img_{now.strftime('%Y%m%d_%H%M%S')}_{short_hash}.png"
        full_path = os.path.join(sub_dir, filename)

        image.save(full_path, "PNG", optimize=True)

        # Return relative path from data/ directory
        data_dir = os.path.dirname(self._base_dir)
        return os.path.relpath(full_path, data_dir)

    def get_full_path(self, relative_path):
        """המרת נתיב יחסי לנתיב מלא."""
        data_dir = os.path.dirname(self._base_dir)
        return os.path.join(data_dir, relative_path)

    def load_thumbnail(self, relative_path, size=(80, 60)):
        """טעינת תמונה ויצירת thumbnail."""
        full_path = self.get_full_path(relative_path)
        if not os.path.exists(full_path):
            return None
        try:
            from PIL import Image
            img = Image.open(full_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return img
        except Exception:
            return None

    def delete(self, relative_path):
        """מחיקת קובץ תמונה."""
        full_path = self.get_full_path(relative_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except OSError:
                pass

    def get_total_size_bytes(self) -> int:
        """חישוב גודל כולל של כל התמונות."""
        total = 0
        for root, _dirs, files in os.walk(self._base_dir):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
        return total

    def cleanup_orphans(self, valid_paths):
        """מחיקת קבצי תמונה שלא קיימים ב-DB."""
        valid_full = set()
        data_dir = os.path.dirname(self._base_dir)
        for p in valid_paths:
            valid_full.add(os.path.normpath(os.path.join(data_dir, p)))

        deleted = 0
        for root, _dirs, files in os.walk(self._base_dir):
            for f in files:
                full = os.path.normpath(os.path.join(root, f))
                if full not in valid_full:
                    try:
                        os.remove(full)
                        deleted += 1
                    except OSError:
                        pass
        return deleted
