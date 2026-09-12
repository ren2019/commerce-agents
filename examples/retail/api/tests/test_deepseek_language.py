import json

import httpx
import pytest

from retail.api.deepseek import DeepSeekClient
from retail.api.language import language


@pytest.mark.parametrize("locale,marker", [("zh", "简体中文"), ("en", "Use English")])
async def test_language_directive_reaches_both_sdk_paths_without_mutating_prefix(locale, marker):
    requests = []

    def respond(request):
        body = json.loads(request.content)
        requests.append(body)
        if body.get("stream"):
            return httpx.Response(200, headers={"content-type": "text/event-stream"}, text="")
        return httpx.Response(
            200,
            json={
                "id": "test-message",
                "type": "message",
                "role": "assistant",
                "model": "test-model",
                "content": [{"type": "text", "text": "ok"}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    prefix = [{"type": "text", "text": "cached rules", "cache_control": {"type": "ephemeral"}}]
    request = {
        "model": "test-model",
        "max_tokens": 20,
        "system": prefix,
        "messages": [{"role": "user", "content": "hello"}],
        "thinking": {"type": "disabled"},
    }
    token = language.set(locale)
    try:
        async with DeepSeekClient(
            api_key="test-key",
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        ) as client:
            await client.messages.create(**request)
            async with client.messages.stream(**request):
                pass
    finally:
        language.reset(token)
    assert len(requests) == 2
    for body in requests:
        assert body["system"][:-1] == prefix
        assert marker in body["system"][-1]["text"]
        assert body["thinking"] == {"type": "disabled"}
        assert body["messages"] == request["messages"]
    assert len(prefix) == 1


@pytest.mark.parametrize(
    "translated,valid",
    [
        ("ACME 帐篷 AR-1202 的价格为 219.00 USD。", True),
        ("ACME 帐篷 AR-1202 的价格为 199.00 USD。", False),
        ("其他品牌帐篷 AR-1202 的价格为 219.00 USD。", False),
    ],
)
async def test_visible_translation_preserves_business_facts(translated, valid):
    from retail.api.deepseek import localize_visible_text

    def respond(request):
        body = json.loads(request.content)
        assert "tools" not in body
        return httpx.Response(
            200,
            json={
                "id": "translation",
                "type": "message",
                "role": "assistant",
                "model": "test-model",
                "content": [{"type": "text", "text": translated}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 10, "output_tokens": 12},
            },
        )

    token = language.set("zh")
    try:
        async with DeepSeekClient(
            api_key="test-key",
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        ) as client:
            call = localize_visible_text(
                client, "test-model", "The ACME tent AR-1202 costs 219.00 USD.", {"ACME", "AR-1202"}
            )
            if valid:
                text, usage = await call
                assert text == translated and usage["output_tokens"] == 12
            else:
                with pytest.raises(ValueError, match="changed"):
                    await call
    finally:
        language.reset(token)


async def test_already_localized_text_does_not_make_an_extra_model_call():
    from retail.api.deepseek import localize_visible_text

    token = language.set("zh")
    try:
        assert await localize_visible_text(None, "unused", "ACME 帐篷已加入购物车。", {"ACME"}) == (
            "ACME 帐篷已加入购物车。",
            {},
        )
    finally:
        language.reset(token)
