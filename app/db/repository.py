"""CRUD operations + FTS5 search for clipboard entries."""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ClipboardEntry:
    """מייצג רשומה אחת בהיסטוריית הלוח."""
    content_type: str
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    content_preview: str = ""
    image_path: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    content_hash: str = ""
    content_size: int = 0
    source_app: Optional[str] = None
    source_window: Optional[str] = None
    is_pinned: bool = False
    is_favorite: bool = False
    created_at: Optional[str] = None
    last_used_at: Optional[str] = None
    id: Optional[int] = None
    # Transient field — not stored in DB
    _pil_image: object = field(default=None, repr=False)


class ClipboardRepository:
    def __init__(self, db):
        self._db = db

    def insert(self, entry: ClipboardEntry) -> int:
        conn = self._db.get_connection()
        cursor = conn.execute(
            """INSERT INTO clipboard_entries
               (content_type, content_text, content_html, content_preview,
                image_path, image_width, image_height, content_hash,
                content_size, source_app, source_window, is_pinned, is_favorite)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry.content_type,
                entry.content_text,
                entry.content_html,
                entry.content_preview,
                entry.image_path,
                entry.image_width,
                entry.image_height,
                entry.content_hash,
                entry.content_size,
                entry.source_app,
                entry.source_window,
                int(entry.is_pinned),
                int(entry.is_favorite),
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def get_recent(self, limit=50, offset=0) -> List[ClipboardEntry]:
        conn = self._db.get_connection()
        rows = conn.execute(
            """SELECT * FROM clipboard_entries
               ORDER BY is_pinned DESC, created_at DESC
               LIMIT ? OFFSET ?""",
            (limit, offset),
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def search(self, query, content_type=None, date_from=None, date_to=None,
               limit=50, offset=0) -> List[ClipboardEntry]:
        conn = self._db.get_connection()

        if query and query.strip():
            # FTS5 search
            fts_query = query.strip().replace('"', '""')
            sql = """SELECT ce.* FROM clipboard_entries ce
                     JOIN clipboard_fts fts ON ce.id = fts.rowid
                     WHERE clipboard_fts MATCH ?"""
            params = [f'"{fts_query}"']
        else:
            sql = "SELECT * FROM clipboard_entries WHERE 1=1"
            params = []

        if content_type:
            sql += " AND content_type = ?"
            params.append(content_type)
        if date_from:
            sql += " AND created_at >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND created_at <= ?"
            params.append(date_to)

        sql += " ORDER BY is_pinned DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(sql, params).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def get_by_id(self, entry_id) -> Optional[ClipboardEntry]:
        conn = self._db.get_connection()
        row = conn.execute(
            "SELECT * FROM clipboard_entries WHERE id = ?", (entry_id,)
        ).fetchone()
        return self._row_to_entry(row) if row else None

    def delete(self, entry_id):
        conn = self._db.get_connection()
        conn.execute("DELETE FROM clipboard_entries WHERE id = ?", (entry_id,))
        conn.commit()

    def delete_all(self):
        conn = self._db.get_connection()
        conn.execute("DELETE FROM clipboard_entries WHERE is_pinned = 0")
        conn.commit()

    def pin(self, entry_id):
        conn = self._db.get_connection()
        conn.execute(
            "UPDATE clipboard_entries SET is_pinned = 1 WHERE id = ?", (entry_id,)
        )
        conn.commit()

    def unpin(self, entry_id):
        conn = self._db.get_connection()
        conn.execute(
            "UPDATE clipboard_entries SET is_pinned = 0 WHERE id = ?", (entry_id,)
        )
        conn.commit()

    def update_last_used(self, entry_id):
        conn = self._db.get_connection()
        conn.execute(
            """UPDATE clipboard_entries
               SET last_used_at = strftime('%Y-%m-%dT%H:%M:%f', 'now', 'localtime')
               WHERE id = ?""",
            (entry_id,),
        )
        conn.commit()

    def is_duplicate(self, content_hash) -> bool:
        """בדיקה אם הרשומה האחרונה זהה (deduplication)."""
        conn = self._db.get_connection()
        row = conn.execute(
            """SELECT content_hash FROM clipboard_entries
               ORDER BY id DESC LIMIT 1"""
        ).fetchone()
        return row is not None and row["content_hash"] == content_hash

    def get_count(self) -> int:
        conn = self._db.get_connection()
        row = conn.execute("SELECT COUNT(*) as cnt FROM clipboard_entries").fetchone()
        return row["cnt"]

    def delete_oldest(self, keep_count) -> int:
        """מחיקת רשומות ישנות מעבר למגבלה (ללא pinned)."""
        conn = self._db.get_connection()
        cursor = conn.execute(
            """DELETE FROM clipboard_entries
               WHERE is_pinned = 0 AND id NOT IN (
                   SELECT id FROM clipboard_entries
                   ORDER BY created_at DESC LIMIT ?
               )""",
            (keep_count,),
        )
        conn.commit()
        return cursor.rowcount

    def delete_older_than(self, date_str) -> int:
        """מחיקת רשומות ישנות מתאריך מסוים (ללא pinned)."""
        conn = self._db.get_connection()
        cursor = conn.execute(
            """DELETE FROM clipboard_entries
               WHERE is_pinned = 0 AND created_at < ?""",
            (date_str,),
        )
        conn.commit()
        return cursor.rowcount

    def get_image_paths(self) -> List[str]:
        """רשימת כל נתיבי התמונות ב-DB."""
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT image_path FROM clipboard_entries WHERE image_path IS NOT NULL"
        ).fetchall()
        return [r["image_path"] for r in rows]

    @staticmethod
    def _row_to_entry(row) -> ClipboardEntry:
        return ClipboardEntry(
            id=row["id"],
            content_type=row["content_type"],
            content_text=row["content_text"],
            content_html=row["content_html"],
            content_preview=row["content_preview"],
            image_path=row["image_path"],
            image_width=row["image_width"],
            image_height=row["image_height"],
            content_hash=row["content_hash"],
            content_size=row["content_size"],
            source_app=row["source_app"],
            source_window=row["source_window"],
            is_pinned=bool(row["is_pinned"]),
            is_favorite=bool(row["is_favorite"]),
            created_at=row["created_at"],
            last_used_at=row["last_used_at"],
        )
