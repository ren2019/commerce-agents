from unittest.mock import patch

import pytest

from retail.api.agent_config import build_shopping_client, build_shopping_config


def test_default_deployment_is_unchanged(monkeypatch):
    monkeypatch.delenv("RETAIL_MODEL_PROVIDER", raising=False)
    assert build_shopping_client() is None
    assert build_shopping_config().model.startswith("claude-")


def test_deepseek_routes_chat_and_memory_to_explicit_model(monkeypatch):
    monkeypatch.setenv("RETAIL_MODEL_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deployment-model")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only")
    config = build_shopping_config()
    assert config.model == config.memory_model == "deployment-model"
    assert config.thinking_request_fields() == {"thinking": {"type": "disabled"}}
    with patch("retail.api.agent_config.AsyncAnthropic") as client:
        assert build_shopping_client() is client.return_value
        assert client.call_args.kwargs["base_url"] == "https://api.deepseek.com/anthropic"
        assert client.call_args.kwargs["api_key"] == "test-only"


def test_deepseek_requires_explicit_local_configuration(monkeypatch):
    monkeypatch.setenv("RETAIL_MODEL_PROVIDER", "deepseek")
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(ValueError, match="DEEPSEEK_MODEL"):
        build_shopping_config()
    with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
        build_shopping_client()
