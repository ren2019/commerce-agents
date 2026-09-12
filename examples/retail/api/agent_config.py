# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0

"""The ACME retail deployment's two agent configs; the only place this example reads
deployment knobs from the environment."""

from __future__ import annotations

import os

from anthropic import AsyncAnthropic

from demo_common import host_approval_default
from merchant_agent import MerchantAgentConfig
from shopping_agent import ShoppingAgentConfig

from .deepseek import DeepSeekClient


def build_model_client() -> AsyncAnthropic | None:
    """Use an explicit DeepSeek deployment without changing other examples."""
    if os.environ.get("RETAIL_MODEL_PROVIDER", "anthropic") == "anthropic":
        return None
    if os.environ["RETAIL_MODEL_PROVIDER"] != "deepseek":
        raise ValueError("RETAIL_MODEL_PROVIDER must be anthropic or deepseek")
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise ValueError("Set DEEPSEEK_API_KEY locally before starting the DeepSeek demo")
    return DeepSeekClient(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com/anthropic",
        timeout=120.0,
    )


def _model_settings() -> dict:
    models = {}
    if os.environ.get("RETAIL_MODEL_PROVIDER", "anthropic") == "deepseek":
        model = os.environ.get("DEEPSEEK_MODEL")
        if not model:
            raise ValueError("Set DEEPSEEK_MODEL to the model available to your account")
        # DeepSeek rejects forced tool_choice while thinking is enabled. The
        # shopping provenance gate uses forced tools, so keep this path non-thinking.
        models = {"model": model, "memory_model": model, "thinking_effort": None}
    return models


def build_shopping_config(store_name: str = "ACME") -> ShoppingAgentConfig:
    return ShoppingAgentConfig(
        **_model_settings(),
        brand_name=store_name,
        assistant_name=f"{store_name} Assistant",
        brand_voice=(
            "professional, warm, and brief. Use Simplified Chinese for all visible text "
            "when current_page.extra.locale is zh; otherwise use English. Preserve "
            "product IDs, amounts and currency"
        ),
        domain_search_notes=(
            "When the customer names one product category, recommend only that category. "
            "An occasion, trip or recipient describes the use case, not a request for "
            "a coordinated equipment plan. Use search-discovery rather than planning-goals "
            "for a single-product request; do not offer unrelated categories or infer "
            "permission to outfit the whole event. Quote recorded dimensions, capacity "
            "and weight directly; do not invent sleeping arrangements or calculated "
            "weight ratios. A product below the stated party size does not fit that party. "
            "For every comparison claim, check the specific product record that supports "
            "it. Never copy a construction, setup method or feature from another candidate; "
            "a recorded setup duration alone does not establish its construction method. "
            "Omit unrecorded features or explicitly say they are not specified."
        ),
        policy_intent_terms=ShoppingAgentConfig.model_fields["policy_intent_terms"].default
        + ("退货", "退款", "退换", "保修", "运费", "配送费", "政策", "会员", "订阅", "取消"),
        policy_intent_cues=ShoppingAgentConfig.model_fields["policy_intent_cues"].default
        + ("？", "吗", "如何", "怎么", "告诉", "说明", "多久", "多少", "政策"),
        order_intent_terms=ShoppingAgentConfig.model_fields["order_intent_terms"].default
        + ("订单", "包裹", "物流", "快递"),
        order_intent_cues=ShoppingAgentConfig.model_fields["order_intent_cues"].default
        + ("？", "吗", "哪里", "状态", "取消", "退货", "延误", "何时", "查询", "多久"),
    )


def build_merchant_config(store_name: str) -> MerchantAgentConfig:
    deepseek = os.environ.get("RETAIL_MODEL_PROVIDER", "anthropic") == "deepseek"
    models = _model_settings()
    if deepseek and os.environ.get("MERCHANT_ANALYSIS_CODE_EXECUTION", "0") == "1":
        raise ValueError("DeepSeek analysis uses local read-only SQL, not Anthropic code execution")
    return MerchantAgentConfig(
        **models,
        brand_name=store_name,
        require_host_approval=host_approval_default(),
        approval_surface="the Approve button on the change preview card",
        brand_voice=(
            "Plain and specific, numbers first. Preserve each inventory alert's returned kind: "
            "slow_mover is not low_stock, and zero stock is distinct from low stock. "
            "When grouping alerts, count the actual records in that group; do not combine "
            "product alerts and order issues into an unexplained count. "
            "For replenishment, distinguish added units from total stock after the change. "
            "Total days of cover equals stock AFTER the change divided by "
            "(sales_last_30d / 30), not added units divided by that rate. "
            "Use the same basis in summaries, preview notes and replies. "
            "Describe this as an estimate at the recent sales pace, not a forecast. "
            "run_analysis already renders its computed figures. Do not follow it with "
            "a duplicate present_metrics card. Generic sales/orders/conversion_rate picks "
            "refer to the business snapshot, not the analysis period or category. "
            "In your explanation retain the analysis filters and caveats, and never "
            "attribute a category increment to an individual listing without dated listing data. "
            "Average order value alone does not establish price changes or category order value. "
            "Use translated category names in operator-facing Chinese prose and card labels "
            "(for example kids-room is 儿童房); retain exact schema names only inside queries."
            " For the official two-week sales comparison, pass the exact inclusive current "
            "and previous dates from merchant context's two_week_comparison to run_analysis. "
            "A date omitted from the requested range is not missing source data."
        ),
        # This deployment runs the run_analysis delegate over MockRetailMerchant's
        # read-only SQL view of the fixtures. MERCHANT_ANALYSIS_CODE_EXECUTION=1 adds the
        # code-execution sandbox (first-party API only); MERCHANT_ANALYSIS_MODEL overrides
        # the delegate's model, which otherwise inherits the main one.
        enable_analysis=True,
        analysis_use_code_execution=os.environ.get("MERCHANT_ANALYSIS_CODE_EXECUTION", "0") == "1",
        analysis_model=models["model"]
        if deepseek
        else os.environ.get("MERCHANT_ANALYSIS_MODEL") or None,
    )
