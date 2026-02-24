"""חיבור SQLite, יצירת סכמה, ומצב WAL."""

import os
import sqlite3
import threading


class Database:
    def __init__(self, db_path):
        self._db_path = db_path
        self._local = threading.local()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.initialize_schema()

    def get_connection(self):
        """החזרת חיבור thread-local ל-SQLite."""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            conn = sqlite3.connect(self._db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")
            self._local.connection = conn
        return self._local.connection

    def initialize_schema(self):
        conn = self.get_connection()
        conn.executescript(SCHEMA_SQL)
        conn.commit()

    def close(self):
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS clipboard_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type    TEXT NOT NULL CHECK(content_type IN ('text', 'html', 'image', 'file_path', 'url')),
    content_text    TEXT,
    content_html    TEXT,
    content_preview TEXT,
    image_path      TEXT,
    image_width     INTEGER,
    image_height    INTEGER,
    content_hash    TEXT NOT NULL,
    content_size    INTEGER NOT NULL DEFAULT 0,
    source_app      TEXT,
    source_window   TEXT,
    is_pinned       INTEGER NOT NULL DEFAULT 0,
    is_favorite     INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f', 'now', 'localtime')),
    last_used_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_created_at ON clipboard_entries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_entries_content_type ON clipboard_entries(content_type);
CREATE INDEX IF NOT EXISTS idx_entries_content_hash ON clipboard_entries(content_hash);
CREATE INDEX IF NOT EXISTS idx_entries_source_app ON clipboard_entries(source_app);
CREATE INDEX IF NOT EXISTS idx_entries_is_pinned ON clipboard_entries(is_pinned);

CREATE VIRTUAL TABLE IF NOT EXISTS clipboard_fts USING fts5(
    content_text,
    content_preview,
    source_window,
    content='clipboard_entries',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON clipboard_entries BEGIN
    INSERT INTO clipboard_fts(rowid, content_text, content_preview, source_window)
    VALUES (new.id, new.content_text, new.content_preview, new.source_window);
END;

CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON clipboard_entries BEGIN
    INSERT INTO clipboard_fts(clipboard_fts, rowid, content_text, content_preview, source_window)
    VALUES ('delete', old.id, old.content_text, old.content_preview, old.source_window);
END;

CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON clipboard_entries BEGIN
    INSERT INTO clipboard_fts(clipboard_fts, rowid, content_text, content_preview, source_window)
    VALUES ('delete', old.id, old.content_text, old.content_preview, old.source_window);
    INSERT INTO clipboard_fts(rowid, content_text, content_preview, source_window)
    VALUES (new.id, new.content_text, new.content_preview, new.source_window);
END;

CREATE TABLE IF NOT EXISTS blacklisted_apps (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS app_meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""
