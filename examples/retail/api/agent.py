"""Retail's shopper runtime: change catalog language without losing provenance."""

from collections.abc import AsyncIterator
from typing import Any, cast

from commerce_common.streaming import AgentEvent
from shopping_agent import ShoppingSessionContext, ShoppingSessionState
from shopping_agent_runtime import ShoppingAgent

from .deepseek import DeepSeekClient, localize_visible_text
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
        pending_text: list[str] = []
        translation_usage: dict[str, int] = {}
        protected = {backend.store_name, *backend.products, *backend.variants}
        protected.update(product.brand for product in backend.products.values() if product.brand)
        async for event in super().stream_turn(messages, session, state):
            if isinstance(self.client, DeepSeekClient) and event.type == "text_delta":
                pending_text.append(event.data["text"])
                continue
            if pending_text:
                text, usage = await localize_visible_text(
                    self.client, self.config.model, "".join(pending_text), protected
                )
                pending_text.clear()
                for key, value in usage.items():
                    translation_usage[key] = translation_usage.get(key, 0) + value
                yield AgentEvent.text_delta(text)
            if event.type == "turn_complete" and translation_usage:
                usage = dict(event.data.get("usage", {}))
                for key, value in translation_usage.items():
                    usage[key] = usage.get(key, 0) + value
                event = event.model_copy(update={"data": {**event.data, "usage": usage}})
            yield event
