"""文本模块：书籍读取与分句规则。"""

import pytest

from english_exercise import text


@pytest.fixture(scope="module", autouse=True)
def _nltk_ready():
    """分句依赖 nltk 数据；下载失败时跳过相关测试。"""
    try:
        text.ensure_nltk_data()
    except Exception as exc:  # pragma: no cover - 取决于运行环境
        pytest.skip(f"nltk 数据不可用: {exc}")


def test_load_book_accepts_utf8_bom(tmp_path):
    path = tmp_path / "bom.txt"
    path.write_bytes("\ufeffHello world.".encode("utf-8"))

    assert text.load_book(path) == "Hello world."


def test_split_sentences_keeps_heading_then_prose():
    content = "Chapter One\n\nThe quick brown fox. It jumps over the lazy dog."

    assert text.split_sentences(content) == [
        "Chapter One",
        "The quick brown fox.",
        "It jumps over the lazy dog.",
    ]


def test_split_sentences_splits_short_line_blocks():
    content = "April 1\nApril 2\nApril 3"

    assert text.split_sentences(content) == ["April 1", "April 2", "April 3"]


def test_split_sentences_ignores_blank_content():
    assert text.split_sentences("\n\n  \n\n") == []
