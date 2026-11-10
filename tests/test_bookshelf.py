"""书架模块：扫描 books 目录、排序、记录上次选择。"""

import pytest

from english_exercise import bookshelf, progress


@pytest.fixture
def books_dir(tmp_path, monkeypatch):
    """准备一个干净的 books 目录与状态文件。"""
    target = tmp_path / "books"
    target.mkdir()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setattr(bookshelf, "BOOKS_DIR", target)
    monkeypatch.setattr(bookshelf, "DATA_DIR", data_dir)
    monkeypatch.setattr(bookshelf, "STATE_PATH", data_dir / "settings.json")
    monkeypatch.setattr(progress, "DATA_DIR", data_dir)
    monkeypatch.setattr(progress, "PROGRESS_PATH", data_dir / "progress.json")
    return target


def test_lists_only_txt_sorted_by_title(books_dir):
    (books_dir / "beta.txt").write_text("B", encoding="utf-8")
    (books_dir / "Alpha.txt").write_text("A", encoding="utf-8")
    (books_dir / "notes.md").write_text("# not a book", encoding="utf-8")
    (books_dir / "nested").mkdir()

    titles = [book.title for book in bookshelf.list_books()]

    assert titles == ["Alpha", "beta"]


def test_reports_saved_progress(books_dir):
    book = books_dir / "prose.txt"
    book.write_text("One two three.", encoding="utf-8")
    progress.save_progress(book, 9)

    (entry,) = bookshelf.list_books()

    assert entry.path == book
    assert entry.size_kb == 1
    assert entry.progress == 9


def test_missing_books_dir_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(bookshelf, "BOOKS_DIR", tmp_path / "absent")

    assert bookshelf.list_books() == []


def test_last_book_roundtrip(books_dir):
    book = books_dir / "picked.txt"
    book.write_text("Pick me.", encoding="utf-8")

    bookshelf.save_last_book(book)
    assert bookshelf.load_last_book() == book.resolve()

    book.unlink()
    assert bookshelf.load_last_book() is None


def test_last_book_without_state_file(books_dir):
    assert bookshelf.load_last_book() is None
