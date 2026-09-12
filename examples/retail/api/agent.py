"""Retail's shopper runtime: change catalog language without losing provenance."""

from collections.abc import AsyncIterator
from typing import Any, cast

from commerce_common.streaming import AgentEvent
from shopping_agent import ShoppingSessionContext, ShoppingSessionState
from shopping_agent_runtime import ShoppingAgent

from .deepseek import localize_events
from .mock_retail import MockRetail


class RetailShoppingAgent(ShoppingAgent):
    async def stream_turn(
        self,
        messages: list[dict[str, Any]],
        session: ShoppingSessionContext,
        state: ShoppingSessionState | None = None,
    ) -> AsyncIterator[AgentEvent]:
        backend = cast(MockRetail, self.backend)
        # Presentation enrichment reads the session's previously seen products.
        # Re-project content on every turn, retaining IDs, prices and write provenance.
        if state is not None:
            for product_id, seen in state.seen_products.items():
                if current := backend.view_product(product_id):
                    state.seen_products[product_id] = seen.model_copy(
                        update={
                            "title": current.title,
                            "short_description": current.short_description,
                            "attributes": current.attributes,
                        }
                    )
        protected = {backend.store_name, *backend.products, *backend.variants}
        protected.update(product.brand for product in backend.products.values() if product.brand)
        async for event in localize_events(
            super().stream_turn(messages, session, state), self.client, self.config.model, protected
        ):
            yield event
