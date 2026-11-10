"""项目目录解析：统一管理书籍、运行期数据与配置文件的位置。

默认把 ``books/``、``data/``、``config.ini`` 放在项目根目录（开发时）或
可执行文件同级目录（打包后）。可用环境变量 ``ENGLISH_EXERCISE_HOME`` 覆盖。
"""

import os
import sys
from pathlib import Path

ENV_HOME = "ENGLISH_EXERCISE_HOME"


def _resolve_root() -> Path:
    """定位应用根目录。"""
    override = os.environ.get(ENV_HOME)
    if override:
        return Path(override).expanduser().resolve()

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    # src/english_exercise/paths.py -> 向上寻找含 pyproject.toml 的项目根目录
    package_dir = Path(__file__).resolve().parent
    for candidate in (package_dir, *package_dir.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return Path.cwd()


ROOT_DIR = _resolve_root()
DATA_DIR = ROOT_DIR / "data"
BOOKS_DIR = ROOT_DIR / "books"
CONFIG_PATH = ROOT_DIR / "config.ini"
KEYS_PATH = ROOT_DIR / "keys.ini"
NLTK_DATA_DIR = DATA_DIR / "nltk_data"


def ensure_dirs() -> None:
    """确保运行期需要的目录都存在。"""
    for directory in (DATA_DIR, BOOKS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
