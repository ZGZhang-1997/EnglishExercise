"""程序入口：初始化运行环境后显示主菜单。"""

import sys

from .paths import ensure_dirs
from .settings import ensure_config, ensure_keys_file


def main() -> int:
    """初始化运行环境并启动主界面。"""
    ensure_dirs()
    ensure_config()
    ensure_keys_file()

    from .theme import disable_ime_for_thread

    disable_ime_for_thread()

    from .text import ensure_nltk_data

    try:
        ensure_nltk_data()
    except Exception as exc:  # 分词数据下载失败时仍允许进入主界面
        print(f"nltk 数据准备失败：{exc}", file=sys.stderr)

    from .ui.home import HomeWindow

    HomeWindow().mainloop()
    return 0
