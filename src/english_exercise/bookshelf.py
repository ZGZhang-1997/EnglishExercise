"""书架：扫描 books 文件夹里的书籍，并记录上次选择的那一本。"""

import json
from dataclasses import dataclass
from pathlib import Path

from .paths import BOOKS_DIR, DATA_DIR
from .progress import get_book_progress

STATE_PATH = DATA_DIR / "settings.json"


@dataclass(frozen=True)
class Book:
    """一本书的展示信息。"""

    path: Path
    title: str
    size_kb: int
    progress: int  # 0 表示尚未开始


def list_books() -> list[Book]:
    """返回 books 文件夹内的全部 txt 书籍，按标题排序。"""
    if not BOOKS_DIR.is_dir():
        return []

    books = []
    for path in BOOKS_DIR.iterdir():
        if not path.is_file() or path.suffix.lower() != ".txt":
            continue
        try:
            size_kb = max(1, path.stat().st_size // 1024)
        except OSError:
            continue
        progress = get_book_progress(path)
        books.append(
            Book(
                path=path,
                title=path.stem,
                size_kb=size_kb,
                progress=int(progress) if progress else 0,
            )
        )

    books.sort(key=lambda book: book.title.lower())
    return books


def load_last_book() -> Path | None:
    """返回上次练习的书籍路径，文件已不存在时返回 None。"""
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    last = data.get("last_book")
    if not last:
        return None
    path = Path(last)
    return path if path.is_file() else None


def save_last_book(book_path: str | Path) -> None:
    """记录本次练习的书籍，下次打开书架时自动选中。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps({"last_book": str(Path(book_path).resolve())}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
