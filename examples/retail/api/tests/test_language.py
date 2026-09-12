import json

from retail.api.language import language
from retail.api.mock_retail import MockRetail
from retail.api.tests.test_dataset import package  # noqa: F401
from shopping_agent import SearchFilters


async def test_chinese_search_finds_english_catalog_and_preserves_cart(backend, session):
    token = language.set("zh")
    try:
        products = await backend.search_products(
            session, "家庭露营帐篷", SearchFilters(max_price=250)
        )
        assert {p.product_id for p in products} & {"AR-1201", "AR-1202"}
        tent = await backend.get_product_details(session, "AR-1202")
        assert "帐篷" in tent.title and tent.price == 219 and tent.currency == "USD"
        cart = await backend.add_to_cart(session, "AR-1202", 1)
        assert "帐篷" in cart.items[0].title
        assert "Tent" in backend.product("AR-1202").title
    finally:
        language.reset(token)
    cart = await backend.get_cart(session)
    assert "Tent" in cart.items[0].title
    assert cart.items[0].price == 219 and cart.items[0].quantity == 1


async def test_english_query_finds_chinese_source(package, session):  # noqa: F811
    path = package / "data/catalog.json"
    catalog = json.loads(path.read_text())
    catalog["source_language"] = "zh"
    product = next(p for p in catalog["products"] if p["product_id"] == "AR-1202")
    translations = json.loads((package / "data/translations.json").read_text())
    product.update(
        {key: value for key, value in translations["zh"]["AR-1202"].items() if key != "aliases"}
    )
    assert "family tent" not in json.dumps(product).lower()
    path.write_text(json.dumps(catalog))
    backend = MockRetail(package / "data")
    results = await backend.search_products(session, "family tent", SearchFilters(max_price=250))
    assert "AR-1202" in {p.product_id for p in results}
    assert "Family Tent" in (await backend.get_product_details(session, "AR-1202")).title


def test_public_product_language_headers_are_isolated(client):
    english = client.get("/api/products/AR-1202").json()
    chinese = client.get("/api/products/AR-1202", headers={"X-Demo-Language": "zh"}).json()
    assert "Tent" in english["title"] and "帐篷" in chinese["title"]
    for field in ("product_id", "price", "currency", "image_url"):
        assert english[field] == chinese[field]
    assert client.get("/api/products/AR-1202").json() == english


async def test_chinese_policy_search_reads_translated_terms(backend, session):
    token = language.set("zh")
    try:
        policies = await backend.search_policies(session, "退货政策")
        policy = next(p for p in policies if p.policy_id == "returns")
        assert "30" in policy.content and "退" in policy.content
    finally:
        language.reset(token)


async def test_language_context_isolated_between_concurrent_requests(backend, session):
    import asyncio

    async def read(locale):
        token = language.set(locale)
        try:
            await asyncio.sleep(0)
            return (await backend.get_product_details(session, "AR-1202")).title
        finally:
            language.reset(token)

    chinese, english = await asyncio.gather(read("zh"), read("en"))
    assert "帐篷" in chinese and "Tent" in english


def test_policy_translation_cannot_override_identity(package):  # noqa: F811
    import pytest

    from retail.api.dataset import load_dataset

    path = package / "data/policy-translations.json"
    path.write_text(json.dumps({"zh": {"returns": {"policy_id": "shipping"}}}))
    with pytest.raises(ValueError, match="unsupported fields"):
        load_dataset(package)


async def test_cached_comparison_follows_language_without_losing_provenance(
    backend, session, monkeypatch
):
    from retail.api.agent import RetailShoppingAgent
    from shopping_agent import ShoppingSessionState
    from shopping_agent_runtime import ShoppingAgent

    async def present_only(self, messages, session, state):
        executor = self.executor_class(
            backend=self.backend,
            config=self.config,
            skills=self.skills,
            session=session,
            state=state,
            memory=self.memory,
        )
        result = await executor.execute(
            "present_comparison",
            {"entries": [{"product_id": "AR-1201"}, {"product_id": "AR-1202"}]},
        )
        assert not result.is_error
        for event in result.events:
            yield event

    monkeypatch.setattr(ShoppingAgent, "stream_turn", present_only)
    agent = RetailShoppingAgent(backend=backend, client=object())
    state = ShoppingSessionState()
    state.remember_products([backend.product("AR-1201"), backend.product("AR-1202")])
    for locale, word in [("zh", "帐篷"), ("en", "Tent")]:
        token = language.set(locale)
        try:
            events = [event async for event in agent.stream_turn([], session, state)]
        finally:
            language.reset(token)
        payload = next(event.data["payload"] for event in events if event.type == "ui")
        assert word in payload["entries"][1]["product"]["title"]
        assert payload["entries"][1]["product"]["price"] == 219
        assert set(state.seen_products) == {"AR-1201", "AR-1202"}
