# Real DeepSeek shopper verification

Provider: DeepSeek Anthropic-compatible endpoint; configured and returned model `deepseek-flash`. Credentials were read locally, never captured in evidence. Official protocol reference: https://api-docs.deepseek.com/guides/thinking_mode/ .

The first real smoke reached search and comparison but failed on forced add_to_cart with HTTP 400: Thinking mode does not support this tool_choice. The retail deployment now disables thinking while retaining the upstream provenance gate. Memory extraction also explicitly disables thinking; otherwise the provider default consumed the 600-token budget before proposing facts. The successful log includes main and memory calls using deepseek-flash.

Re-run: `RETAIL_MODEL_PROVIDER=deepseek RETAIL_STATE_DIR=/tmp/commerce-deepseek-official .venv/bin/python scripts/smoke_chat.py --vertical retail`. The isolated state directory has no selected package, so this uses the complete official retail fixtures. `smoke.txt` records all three successful turns and actual model usage.

Browser: full official smoke wording entered in a fresh shopper session on localhost:3013 with API on 8013. Product cards show the $219 four-person and $149 two-person tents. Comparison displays capacity, weight, setup time and budget tradeoffs. The final request adds one four-person tent: cart shows one item/$219 and reply quotes the fixture's 30-day original-condition return policy, five-business-day refund timing and member pickup. Screenshots capture products, comparison, cart and returns. The UI was observed in Working state before streamed results arrived; server smoke confirms ui/cart_update/turn_complete events.

A separate exploratory click on the abbreviated home suggestion produced a broader camping plan; this is not the canonical acceptance script. The recorded accepted run uses the official three prompts unchanged. No real purchase occurred.

Regression: 1114 pytest passed, 1 skipped, two existing dependency warnings. Targeted deployment/memory assertions: 31 passed. Ruff/check.py passed. Web code is unchanged from the preceding successful builds. Merchant DeepSeek and bilingual UI are still separate open tickets.
