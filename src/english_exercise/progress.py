"""练习进度：按书籍内容哈希分别保存与读取句子序号。"""

import datetime
import hashlib
import json
from pathlib import Path

from .paths import DATA_DIR

PROGRESS_PATH = DATA_DIR / "progress.json"


def _file_hash(book_path: str | Path) -> str:
    """计算书籍文件内容的 SHA256，用于校验进度是否仍然有效。"""
    digest = hashlib.sha256()
    with Path(book_path).open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load() -> dict:
    """读取全部进度记录，并兼容早期只保存单本书的格式。"""
    if not PROGRESS_PATH.exists():
        return {}
    try:
        data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}

    books = data.get("books")
    if isinstance(books, dict):
        return books

    # 旧格式：{"book_path": ..., "sentence_index": ..., "book_hash": ...}
    if data.get("book_hash"):
        return {
            data["book_hash"]: {
                "path": data.get("book_path", ""),
                "sentence_index": data.get("sentence_index", 0),
            }
        }
    return {}


def _save(books: dict) -> None:
    """把全部进度记录写回磁盘。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(
        json.dumps({"books": books}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_book_progress(book_path: str | Path):
    """返回某本书已保存的句子序号；没有记录或文件已变化时返回 None。"""
    path = Path(book_path)
    if not path.is_file():
        return None
    try:
        record = _load().get(_file_hash(path))
    except OSError:
        return None
    if not record:
        return None
    return record.get("sentence_index")


def load_progress(book_path: str | Path) -> int:
    """读取指定书籍的进度，没有记录则从 0 开始。"""
    try:
        return max(0, int(get_book_progress(book_path)))
    except (TypeError, ValueError):
        return 0


def save_progress(book_path: str | Path, sentence_index: int) -> None:
    """保存某本书当前的句子序号。"""
    path = Path(book_path)
    books = _load()
    books[_file_hash(path)] = {
        "path": str(path.resolve()),
        "sentence_index": sentence_index,
        "updated_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    _save(books)


def clear_progress(book_path: str | Path | None = None) -> None:
    """删除某本书的进度；不传参数时清空全部进度。"""
    if book_path is None:
        PROGRESS_PATH.unlink(missing_ok=True)
        return
    books = _load()
    if books.pop(_file_hash(book_path), None) is not None:
        _save(books)
