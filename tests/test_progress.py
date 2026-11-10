"""进度模块：多书互不影响、内容变化失效、旧格式兼容。"""

import json
from pathlib import Path

import pytest

from english_exercise import progress


@pytest.fixture
def store(tmp_path, monkeypatch):
    """把进度文件与数据目录重定向到临时目录。"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setattr(progress, "DATA_DIR", data_dir)
    monkeypatch.setattr(progress, "PROGRESS_PATH", data_dir / "progress.json")
    return data_dir


@pytest.fixture
def book(tmp_path) -> Path:
    """一本可练习的示例书。"""
    path = tmp_path / "book.txt"
    path.write_text("Hello world. How are you?", encoding="utf-8")
    return path


def test_save_load_and_clear(store, book):
    assert progress.load_progress(book) == 0

    progress.save_progress(book, 7)
    assert progress.load_progress(book) == 7

    progress.clear_progress(book)
    assert progress.load_progress(book) == 0


def test_progress_is_isolated_per_book(store, book, tmp_path):
    other = tmp_path / "other.txt"
    other.write_text("Another book entirely.", encoding="utf-8")

    progress.save_progress(book, 3)
    progress.save_progress(other, 11)

    assert progress.load_progress(book) == 3
    assert progress.load_progress(other) == 11


def test_edited_book_loses_stale_progress(store, book):
    progress.save_progress(book, 5)
    book.write_text("Totally different content now.", encoding="utf-8")

    assert progress.load_progress(book) == 0


def test_missing_book_reports_no_progress(store, tmp_path):
    assert progress.get_book_progress(tmp_path / "missing.txt") is None
    assert progress.load_progress(tmp_path / "missing.txt") == 0


def test_legacy_single_book_format(store, book):
    from english_exercise.progress import _file_hash

    payload = {
        "book_path": str(book),
        "sentence_index": 4,
        "book_hash": _file_hash(book),
    }
    progress.PROGRESS_PATH.write_text(json.dumps(payload), encoding="utf-8")

    assert progress.load_progress(book) == 4


def test_corrupt_progress_file_is_ignored(store, book):
    progress.PROGRESS_PATH.write_text("{ not json", encoding="utf-8")

    assert progress.load_progress(book) == 0
