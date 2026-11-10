"""配置与密钥：非敏感设置读 ``config.ini``，API Key 统一读根目录 ``keys.ini``。"""

import configparser
import os

from .paths import CONFIG_PATH, KEYS_PATH

DEFAULT_VOICE = "en-US-AriaNeural"
DEEPL = "deepl"
KEY_ALIASES = ("api_key", "key", "token")

KEYS_TEMPLATE = """\
# 本项目的 API Key 汇总文件
# ------------------------------------------------------------
# - 所有服务的密钥都放在这里，不再引用项目之外的密钥文件。
# - 每个服务一个 section，键名统一写 api_key。
# - 本文件包含真实密钥，已在 .gitignore 中排除，不要提交到版本库。
# ------------------------------------------------------------

[deepl]
api_key =
"""


def ensure_config() -> configparser.ConfigParser:
    """确保配置文件存在，并返回已加载的配置对象。"""
    if not CONFIG_PATH.exists():
        cfg = configparser.ConfigParser()
        cfg["audio"] = {"voice": DEFAULT_VOICE}
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            cfg.write(f)
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH, encoding="utf-8")
    return cfg


def ensure_keys_file() -> None:
    """keys.ini 不存在时写出一份带说明的模板（不覆盖已有文件）。"""
    if KEYS_PATH.exists():
        return
    KEYS_PATH.parent.mkdir(parents=True, exist_ok=True)
    KEYS_PATH.write_text(KEYS_TEMPLATE, encoding="utf-8")


def read_keys() -> configparser.ConfigParser:
    """读取 keys.ini。"""
    keys = configparser.ConfigParser()
    keys.read(KEYS_PATH, encoding="utf-8")
    return keys


def get_api_key(service: str) -> str:
    """按服务名取出 Key：环境变量 ``<SERVICE>_API_KEY`` 优先，其次 keys.ini。"""
    env_key = os.environ.get(f"{service.upper()}_API_KEY", "").strip()
    if env_key:
        return env_key

    keys = read_keys()
    for name in KEY_ALIASES:
        value = keys.get(service, name, fallback="").strip()
        if value:
            return value
    return ""


def get_voice(cfg: configparser.ConfigParser) -> str:
    """返回配置中的朗读音色。"""
    return cfg.get("audio", "voice", fallback=DEFAULT_VOICE)


