"""ניקוי אוטומטי — מחיקת רשומות ישנות ותמונות יתומות."""

import threading
from datetime import datetime, timedelta


class CleanupManager:
    """מנהל ניקוי תקופתי של היסטוריית הלוח."""

    def __init__(self, repo, config, image_storage):
        self._repo = repo
        self._config = config
        self._image_storage = image_storage
        self._timer = None
        self._running = False

    def schedule(self, interval_minutes=30):
        """תזמון ניקוי תקופתי."""
        self._running = True
        self._run_periodic(interval_minutes)

    def cancel(self):
        """ביטול הניקוי התקופתי."""
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def run_cleanup(self):
        """הרצת ניקוי מיידי."""
        try:
            self._cleanup_by_count()
            self._cleanup_by_age()
            self._cleanup_orphan_images()
        except Exception:
            pass

    def _run_periodic(self, interval_minutes):
        if not self._running:
            return
        self.run_cleanup()
        self._timer = threading.Timer(
            interval_minutes * 60, self._run_periodic, args=[interval_minutes]
        )
        self._timer.daemon = True
        self._timer.start()

    def _cleanup_by_count(self):
        max_entries = self._config.get("max_entries", 5000)
        count = self._repo.get_count()
        if count > max_entries:
            self._repo.delete_oldest(max_entries)

    def _cleanup_by_age(self):
        max_age_days = self._config.get("max_age_days", 90)
        if max_age_days <= 0:
            return
        cutoff = datetime.now() - timedelta(days=max_age_days)
        cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
        self._repo.delete_older_than(cutoff_str)

    def _cleanup_orphan_images(self):
        valid_paths = set(self._repo.get_image_paths())
        self._image_storage.cleanup_orphans(valid_paths)
