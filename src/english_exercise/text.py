"""书籍文本处理：加载 txt 内容并拆分为可练习的句子。"""

import re
import sys
from pathlib import Path

import nltk
from nltk.tokenize import sent_tokenize

from .paths import NLTK_DATA_DIR

MIN_HEADING_LEN = 80
PUNKT_RESOURCE = "tokenizers/punkt_tab"


def ensure_nltk_data() -> None:
    """确保分句所需的数据在项目目录内可用，需要时下载到 data/nltk_data。"""
    if getattr(sys, "frozen", False):
        nltk.data.path.insert(0, str(Path(sys._MEIPASS) / "nltk_data"))

    local_dir = str(NLTK_DATA_DIR)
    if local_dir not in nltk.data.path:
        nltk.data.path.insert(0, local_dir)

    try:
        nltk.data.find(PUNKT_RESOURCE, paths=[local_dir])
    except LookupError:
        NLTK_DATA_DIR.mkdir(parents=True, exist_ok=True)
        nltk.download("punkt_tab", download_dir=local_dir, quiet=True)


def load_book(filepath: str | Path) -> str:
    """读取整本 txt 书籍内容并返回字符串。"""
    # utf-8-sig 兼容带 BOM 的文件；errors="replace" 让个别坏字节不至于打不开书
    return Path(filepath).read_text(encoding="utf-8-sig", errors="replace")


def split_sentences(text: str) -> list[str]:
    """按标题、短行和正文规则将文本拆分成句子列表。"""
    ensure_nltk_data()
    results: list[str] = []

    for paragraph in re.split(r"\n\s*\n", text):
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue

        # 多行且都较短时（章节标题、日期等），每行各自成句
        if len(lines) > 1 and all(len(line) < MIN_HEADING_LEN for line in lines):
            results.extend(lines)
            continue

        joined = " ".join(lines)
        # 单行短句（标题、数字等）不含句末标点时按原样保留
        if len(joined) < MIN_HEADING_LEN and not any(c in joined for c in ".!?"):
            results.append(joined)
            continue

        for sentence in sent_tokenize(joined, language="english"):
            sentence = sentence.strip()
            if sentence:
                results.append(sentence)

    return results

