"""翻译模块：无 Key 时不联网，命中缓存时直接返回。"""

import json

from english_exercise.translation import DeepLTranslator


def test_disabled_translator_returns_empty(tmp_path):
    translator = DeepLTranslator("", cache_dir=tmp_path)

    assert translator.enabled is False
    assert translator.translate("Hello there.") == ""
    assert not (tmp_path / "translation_cache.json").exists()


def test_uses_cached_translation(tmp_path):
    first = DeepLTranslator("", cache_dir=tmp_path)
    key = first._key("Good morning.")
    (tmp_path / "translation_cache.json").write_text(
        json.dumps({key: "早上好。"}), encoding="utf-8"
    )

    second = DeepLTranslator("", cache_dir=tmp_path)

    assert second.translate("Good morning.") == "早上好。"
