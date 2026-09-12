# ACME (retail)

The retail example runs both agents over one catalog with the built-in components only:
the storefront searches, compares, plans, fills the cart, stages checkout, and keeps
memory across restarts; the portal shows the morning digest, stages restocks, listing
fixes, and promotions, and applies them from the preview card. It is also the backend the
SDK consoles and the reference MCP servers load by default.

## Run

```bash
python scripts/run_demo.py retail               # API :8000 + storefront :3000
python scripts/run_demo.py retail --merchant     # API :8000 + portal :3100
python scripts/run_demo.py retail --all          # both web apps over one API
```

Or start the pieces yourself, after `npm ci` in `examples/`:

```bash
uvicorn retail.api.main:app --app-dir examples --reload --port 8000
(cd examples/retail/storefront-web && npm run dev)     # :3000
(cd examples/retail/merchant-web && npm run dev)       # :3100
```

Chat needs `ANTHROPIC_API_KEY` in the repo-root `.env` or the environment; browsing the
catalog and the portal's widgets do not. `MERCHANT_REQUIRE_HOST_APPROVAL=0` lets a chat
approval apply a change; by default the preview card's button applies it.

## Try

Storefront (`scripts/smoke_chat.py --vertical retail` runs the same three turns):

1. I'm taking my partner and our 6-year-old camping for the first time next month. We need a tent — nothing too heavy to deal with, ideally under $250.
2. Compare the top two options for me — mostly care about space and ease of setup.
3. The family one sounds right. Add it to my cart, and remind me what returns look like just in case.

Portal (`scripts/smoke_chat.py --vertical retail --merchant`; the third turn is refused
until the change is approved on its card, and the last two follow the approval):

1. What needs my attention this morning?
2. Restock the ocean wall decals with enough to cover the next month at the current pace, and fix that listing's description so it covers what's been missing. Show me both before anything goes live.
3. Looks right — approve the restock.
4. Kids-room decor feels like it's having a moment. Pull the numbers — is the under-the-sea line really outperforming the rest of the store this month?
5. Why did sales move over the last two weeks — which category or listings drove it, and by how much?

Single prompts, each in a fresh session:

| Surface | Prompt | A good answer |
|---|---|---|
| Storefront | Order me the same resistance band set I bought from you before. | Finds the set in order history, adds one to the cart, and says the price today differs from the price paid then. |
| Storefront | Can I still return the yoga mat I ordered from you a while back? It's unused. | Reads the order and the returns policy, counts 30 days from the delivery date, and says the window has closed. It does not open a return. |
| Storefront | I need a universal travel adapter that can charge a laptop. | Runs one search and shows one product card, the 65 W adapter, without a clarifying question. |
| Storefront | Two couples, first weekend of car camping, and no gear between us. Put together what we need and keep the whole list under $600. | Sizes the plan to four (one family tent, four sleeping bags, one stove, one cooler), totals it, says the sum is over $600, and names what to drop or share to get there. |
| Portal | Which category drove last week's change in sales, and by how much? | Reads the snapshot and the daily series: kids-room, the only category the data breaks out, gained more than the whole store, so the rest slipped; says the data has no full category split. |
| Portal | The ocean wall decals listing is missing wall coverage and material. Fill those in for me. | Reads the listing, finds neither value in the record, and asks for them instead of writing a material or a coverage figure into the page. |

## What is specific to this example

- `api/mock_retail.py`: `MockRetail`, the `StorefrontBackend` over the fixtures, plus
  the price and review summaries the product page shows.
- `api/mock_merchant.py`: `MockRetailMerchant`, the `MerchantBackend` over the same
  catalog; applied changes write back to it, and `execute_analysis_query` serves the
  analysis delegate from a read-only SQLite view of the same state.
- `api/agent_config.py`: the two configs. Analysis is on; `MERCHANT_ANALYSIS_CODE_EXECUTION=1`
  adds the hosted sandbox and `MERCHANT_ANALYSIS_MODEL` overrides the delegate's model.
- `api/main.py`: the storefront's file-backed memory store (`data/.memory-store.json`),
  the product-detail enrichment, and the add-to-cart button route.
- `api/merchant.py`: the overview's KPI trends and insight cards.
- `storefront-web/`, `merchant-web/`: this example's cards, views, and tokens, over `../web-shared/`.

## Data

`data/catalog.json`, `users.json`, `orders.json`, `policies.json`, and `memory-seed.json` feed
the storefront; `merchant_metrics.json`, `merchant_inventory.json`, `merchant_campaigns.json`,
and `merchant_messages.json` feed the portal. Four products come with options (a mattress by
size, a pillowcase set by size and color, a tinted moisturizer by shade, a weighted blanket by
weight): the catalog authors their variants compactly and `demo_common` derives the rest, as
[`docs/backends.md`](../../docs/backends.md) describes.
Product photos in `storefront-web/public/products/` are CC0 category images listed in the
`IMAGE-CREDITS.md` beside them; products without one render as tiles.

Sessions and identity are the shared host code in [`../demo_common/`](../demo_common/): a
session id stands for a demo profile or the one merchant.

## DeepSeek deployment

In your local environment or untracked root `.env`, set `RETAIL_MODEL_PROVIDER=deepseek`,
`DEEPSEEK_API_KEY`, and `DEEPSEEK_MODEL` to an explicit model available to your account.
Restart the API after changing these values. Both retail agents use the DeepSeek
Anthropic-compatible endpoint for conversation and memory extraction. Merchant analysis
uses the same explicit model with local read-only SQL; Anthropic-hosted code execution
is unavailable on this provider. Omitting
`RETAIL_MODEL_PROVIDER` preserves the upstream Anthropic deployment.

Verify with both retail smoke conversations and browsers before presenting.
Provider configuration tests do not establish live model compatibility. On DeepSeek,
MERCHANT_ANALYSIS_MODEL does not override DEEPSEEK_MODEL.

The DeepSeek deployment uses non-thinking requests: provenance gates force selected
tools, which DeepSeek rejects in thinking mode. Memory extraction explicitly disables
thinking so its 600-token budget is used for structured facts.

## External dataset packages

Run `.venv/bin/python scripts/retail_dataset.py validate /absolute/package` to check,
then `.venv/bin/python scripts/retail_dataset.py import /absolute/package` to select it.
Restart the API and refresh both pages after a successful import. Failed validation
leaves the previous selection and running API intact. Imports copy data and images
into `~/.local/share/commerce-agent/retail` (override with `RETAIL_STATE_DIR`), so runtime
memory does not modify the source. `RETAIL_DATASET` is an explicit development override
that directly loads a directory and takes precedence over the imported selection.
A package contains `dataset.json`, `data/` (the retail JSON fixtures), and `images/`.
The version 1 manifest requires `dataset_id` and `store_name`; optional fields are
`logo` (relative to `images/`) and `simulated` (defaults to true). The catalog's
store name must match the manifest. Product images use `/products/<filename>`;
both web applications read the selected package's images from the API.

The loader validates product identities, order references, catalog models and
merchant inventory consistency before constructing the application. Missing product
images appear in dataset warnings; invalid logo references reject the package.
The public `/api/dataset` endpoint reports brand metadata and warnings without
exposing the package's filesystem location. Keep customer packages outside Git.

Optional `data/translations.json` stores `en` and `zh` maps keyed by stable product ID.
Each product may contain `title`, `short_description`, `long_description` (strings),
`attributes`, `specs` (string maps), and `aliases`, `review_highlights` (string lists). Unknown product IDs,
locales or fields are rejected. This sidecar preserves language-neutral pricing and
identity and is retained during import. `catalog.json.source_language` is `en` by
default, or `zh` for Chinese source content. `api/language.py` projects request-scoped
content selected by `X-Demo-Language`; search uses both language maps. Optional
`data/policy-translations.json` maps locales and existing policy IDs to `title`,
`content`, and `aliases`. It cannot override IDs or other policy fields.

The shopper runtime in `api/agent.py` reprojects previously seen product content
for each turn so subsequent cards follow the selected language; IDs, prices and
write provenance stay intact. Existing conversation prose remains as originally spoken.

The DeepSeek client in `api/deepseek.py` appends the host-selected output language
after session context, preserving the cached prefix. The shopper also buffers visible
text between tool events and translates language-mismatched segments through DeepSeek.
The translator has no tools; numerical tokens, catalog IDs and brand names are checked
before display. Its token usage is included in the turn totals. Stored conversation
and tool data are not rewritten.

The storefront language control uses the optional `web-shared/language.tsx` context.
Changing language retains the session and cart, and refreshes catalog and order views.

### Switch and reset

Use `scripts/retail_dataset.py switch /absolute/other-package` with the repository's
Python environment to select a fresh runtime for another prepared package. Use
`scripts/retail_dataset.py reset` to restore the selected package's imported baseline,
even if its original source has subsequently changed. Both commands require an API
restart followed by refreshing both browser pages. The current process keeps its
current data until restarted; this is deliberate, so an active turn is not interrupted
halfway through a change. API restart invalidates both role sessions and clears their
in-memory carts and change ledgers; the fresh runtime also starts with seeded memory.
Previous runtime copies are retained. Clear `RETAIL_DATASET` when using these commands,
since that explicit development override bypasses the saved selection.

## Prepare a catalog

Use [the preparation guide](../../../docs/retail-data-preparation.md) when converting
customer catalogs into external packages. The [public two-product example](sample-catalog/README.md)
includes source records, bilingual content, image provenance and generated operating data.

The merchant portal uses the same optional language context; its interface copy
lives in `merchant-web/lib/chinese.ts`. Merchant bilingual data and approval-card
coverage are under development in issue 5.

Merchant listing and inventory views reuse the catalog language projections.
Under the DeepSeek deployment, content edits stage both the entered text and its
translation as separate before/after rows. No catalog content changes while the
translation is prepared. Approval applies both language versions to the shared
catalog, preserving the source language and refreshing the other language view.
Translation failure leaves no staged change. These extra translation requests use
the configured DeepSeek model; they add preparation latency and are not included
in the conversation runtime's usage total. Runtime changes still reset with the
selected dataset. The default non-DeepSeek path retains source-language editing;
non-source-language content edits require the DeepSeek translator.

Operational fixture files may carry root-level `translations` by locale and
existing issue/campaign ID. Messages translate only summary and quoted excerpt;
campaigns translate name, objective and channel. Dataset validation rejects
identity, amount, status and date overrides. Home insights calculate the same
figures in both languages and localize their descriptions at read time.
