"""DeepL 翻译：调用 API 并把结果缓存到本地 JSON。"""

import hashlib
import json
from pathlib import Path

import deepl

from .paths import DATA_DIR


class DeepLTranslator:
    """DeepL 翻译器封装，带本地 JSON 缓存；未配置 Key 时不做翻译。"""

    def __init__(self, api_key: str, cache_dir: str | Path | None = None):
        """初始化 DeepL 客户端并加载缓存文件。"""
        self.enabled = bool(api_key)
        self._translator = deepl.Translator(api_key) if api_key else None
        self._cache_dir = Path(cache_dir) if cache_dir else DATA_DIR
        self._cache_path = self._cache_dir / "translation_cache.json"
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        """从磁盘读取已有翻译缓存。"""
        if self._cache_path.exists():
            try:
                return json.loads(self._cache_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return {}
        return {}

    def _save_cache(self) -> None:
        """将当前翻译缓存写回磁盘。"""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_path.write_text(
            json.dumps(self._cache, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @staticmethod
    def _key(text: str) -> str:
        """为原文生成稳定的缓存键。"""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def translate(self, sentence: str) -> str:
        """翻译单句文本；未启用返回空串，失败时返回占位提示。"""
        key = self._key(sentence)
        if key in self._cache:
            return self._cache[key]
        if not self._translator:
            return ""
        try:
            result = self._translator.translate_text(sentence, target_lang="ZH")
            translation = result.text
        except Exception:
            # 网络等临时故障不写入缓存，下次进入该句时会重试
            return "[翻译失败]"
        self._cache[key] = translation
        self._save_cache()
        return translation

