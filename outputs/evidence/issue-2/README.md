# Real DeepSeek merchant story

Both retail agents now share the explicit provider client; merchant conversation, memory and analysis all use configured `deepseek-flash`. Analysis uses the existing local read-only SQL backend. Hosted Anthropic code execution is rejected for this provider, and a stale MERCHANT_ANALYSIS_MODEL cannot route analysis to a different model.

`smoke.txt` is the real official morning arc after the grounding fix: morning briefing, restock/content previews, chat approval held, portal approval, product-line analysis and two-week sales analysis. All expected assertions passed; the log includes DeepSeek main, memory and delegate usage. The prior smoke also passed mechanical checks, but browser review found a bad content preview (unsupported vinyl and 12-square-foot claims). `rejected-preview.json` and `smoke-before-grounding-fix.txt` preserve that failure context. Nothing from that preview was applied.

The static merchant rule now requires source-backed specifications in the preview itself and a catalog skill/full-record read before staging. Unknown fields remain outside the change. The managed-agent derived prompt is synchronized. This improves grounded generation; it is not a deterministic proof that a model can never fabricate. Operator preview approval remains essential.

Browser re-run uses official prompts unchanged at localhost:3113 with the DeepSeek API on 8013. `previews.txt` shows restock 3 → 55 and description edits containing only source claims. Material and wall coverage explicitly remain unknown. `chat-approval-held.json` asserts stock 3, two staged changes, zero applied. After clicking Approve on the restock card, `card-approved.json` asserts stock 55, one applied change and the description still staged. The original fixture files remain unchanged.

`product-line-analysis.txt` reports kids-room growth against the store while identifying absent per-listing time series/traffic. `two-week-analysis.txt` reports $1,504.15 growth, $1,756.78 from kids-room and -$252.63 from the remainder; it explicitly declines unsupported individual listing/category attribution. Screenshots preserve visible cards and results. Some generated chart headings reach the existing length cap and appear truncated; presentation polish remains for the bilingual/integration tasks.

Regression: 1115 pytest passed, 1 skipped, two existing dependency warnings; Ruff and check.py passed. This includes the existing host-approval and read-only capability-switch contracts. No React source changed in this ticket; preceding builds remain applicable.
