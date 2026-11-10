"""配置模块：API Key 统一来自 keys.ini，音色来自 config.ini。"""

import configparser

import pytest

from english_exercise import settings

DEEPL_SECTION = "[deepl]\napi_key = {key}\n"


@pytest.fixture
def keys_file(tmp_path, monkeypatch):
    """把 keys.ini 指向临时文件。"""
    path = tmp_path / "keys.ini"
    path.write_text(DEEPL_SECTION.format(key="  abc:fx  "), encoding="utf-8")
    monkeypatch.setattr(settings, "KEYS_PATH", path)
    monkeypatch.delenv("DEEPL_API_KEY", raising=False)
    return path


def make_config(voice: str = "en-GB-SoniaNeural") -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    cfg["audio"] = {"voice": voice}
    return cfg


def test_reads_key_from_keys_file(keys_file):
    assert settings.get_api_key("deepl") == "abc:fx"


def test_env_var_has_priority(keys_file, monkeypatch):
    monkeypatch.setenv("DEEPL_API_KEY", "env-key")

    assert settings.get_api_key("deepl") == "env-key"


def test_missing_section_returns_empty(tmp_path, monkeypatch):
    path = tmp_path / "keys.ini"
    path.write_text(DEEPL_SECTION.format(key=""), encoding="utf-8")
    monkeypatch.setattr(settings, "KEYS_PATH", path)
    monkeypatch.delenv("DEEPL_API_KEY", raising=False)

    assert settings.get_api_key("deepl") == ""
    assert settings.get_api_key("openai") == ""


def test_missing_keys_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "KEYS_PATH", tmp_path / "absent.ini")
    monkeypatch.delenv("DEEPL_API_KEY", raising=False)

    assert settings.get_api_key("deepl") == ""


def test_accepts_alternate_key_names(tmp_path, monkeypatch):
    path = tmp_path / "keys.ini"
    path.write_text("[openai]\ntoken = sk-test\n", encoding="utf-8")
    monkeypatch.setattr(settings, "KEYS_PATH", path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert settings.get_api_key("openai") == "sk-test"


def test_ensure_keys_file_creates_template(tmp_path, monkeypatch):
    path = tmp_path / "keys.ini"
    monkeypatch.setattr(settings, "KEYS_PATH", path)

    settings.ensure_keys_file()

    content = path.read_text(encoding="utf-8")
    assert "[deepl]" in content
    assert "api_key =" in content


def test_ensure_keys_file_keeps_existing_content(tmp_path, monkeypatch):
    path = tmp_path / "keys.ini"
    path.write_text(DEEPL_SECTION.format(key="keep-me"), encoding="utf-8")
    monkeypatch.setattr(settings, "KEYS_PATH", path)

    settings.ensure_keys_file()

    assert "keep-me" in path.read_text(encoding="utf-8")


def test_get_voice():
    assert settings.get_voice(make_config()) == "en-GB-SoniaNeural"


def test_default_voice_when_unset():
    cfg = configparser.ConfigParser()

    assert settings.get_voice(cfg) == settings.DEFAULT_VOICE
