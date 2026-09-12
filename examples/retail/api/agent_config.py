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


def build_model_client() -> AsyncAnthropic | None:
    """Use an explicit DeepSeek deployment without changing other examples."""
    if os.environ.get("RETAIL_MODEL_PROVIDER", "anthropic") == "anthropic":
        return None
    if os.environ["RETAIL_MODEL_PROVIDER"] != "deepseek":
        raise ValueError("RETAIL_MODEL_PROVIDER must be anthropic or deepseek")
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise ValueError("Set DEEPSEEK_API_KEY locally before starting the DeepSeek demo")
    return AsyncAnthropic(
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
            "professional, warm, and brief. Use Simplified Chinese for all replies and "
            "presentation text when current_page.extra.locale is zh; otherwise use English. "
            "Keep product IDs, amounts, and currency unchanged"
        ),
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
