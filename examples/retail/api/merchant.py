# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0

"""The ACME retail merchant router: the shared portal routes over ``MockRetailMerchant``,
plus the KPI trends and insight cards the retail portal's home page shows."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter

from commerce_common.memory import MemoryStore
from commerce_common.streaming import AgentEvent
from demo_common import REPO_ROOT, MerchantIdentity, build_merchant_router
from merchant_agent import MerchantSessionContext, MerchantSessionState
from merchant_agent_runtime import MerchantAgent

from .agent_config import build_merchant_config, build_model_client
from .deepseek import DeepSeekClient, localize_events, localize_visible_text
from .language import language
from .mock_merchant import MockRetailMerchant
from .mock_retail import MockRetail

IDENTITY = MerchantIdentity(merchant_id="acme-retail", operator="Avery")


class RetailMerchantAgent(MerchantAgent):
    async def stream_turn(
        self,
        messages: list[dict[str, Any]],
        session: MerchantSessionContext,
        state: MerchantSessionState | None = None,
    ) -> AsyncIterator[AgentEvent]:
        storefront = self.backend.storefront
        protected = {storefront.store_name, *storefront.products, *storefront.variants}
        protected.update(product.brand for product in storefront.products.values() if product.brand)
        async for event in localize_events(
            super().stream_turn(messages, session, state), self.client, self.config.model, protected
        ):
            yield event


def create_merchant_router(storefront: MockRetail, memory_store: MemoryStore) -> APIRouter:
    config = build_merchant_config(storefront.store_name)
    client = build_model_client()

    async def translate_content(text: str, locale: str) -> str:
        token = language.set(locale)
        try:
            protected = {storefront.store_name, *storefront.products, *storefront.variants}
            protected.update(p.brand for p in storefront.products.values() if p.brand)
            translated, _ = await localize_visible_text(
                client, config.model, text, protected, force=True
            )
            return translated
        finally:
            language.reset(token)

    merchant = MockRetailMerchant(
        storefront,
        config,
        data_dir=storefront.data_dir,
        merchant_id=IDENTITY.merchant_id,
        translate_content=translate_content if isinstance(client, DeepSeekClient) else None,
    )
    agent = RetailMerchantAgent(
        backend=merchant,
        skills_dir=REPO_ROOT / "merchant-agent" / "skills",
        config=config,
        client=client,
        memory_store=memory_store,
    )
    return build_merchant_router(
        storefront=storefront,
        backend=merchant,
        agent=agent,
        identity=IDENTITY,
        example_dir="retail",
        overview_extras=lambda: {
            "trends": merchant.kpi_trends(),
            "trends_prior": merchant.kpi_trends(periods_back=1),
            "insights": merchant.home_insights(),
        },
    )
