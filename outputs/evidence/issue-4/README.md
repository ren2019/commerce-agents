# Issue 4: bilingual shopper verification

The current real DeepSeek runs are `chinese-api-story-guarded.json` and
`english-api-story-current.json`. Each contains three turns: tent search,
comparison, then adding the family tent and checking returns. Their matching
cart files confirm AR-1202, quantity 1, subtotal 219 USD. These are actual model
responses, not fixture-generated responses. Both comparison cards recommend the
four-person tent and identify the two-person capacity constraint.

The original `chinese-api-story.json` is an earlier functional milestone: it
contains an English pre-tool opener and is not full language acceptance evidence.
The current deployment buffers shopper text segments and translates a mismatched
segment through the same DeepSeek model, without tools. Numerical tokens, brands
and identifiers are checked before emitting translated text; usage includes that
extra request. This can add latency. Stored history is not rewritten.

The catalog includes English and Chinese content for 108 products/variants,
43 review-highlight records and 11 policies. Numerical-token checks do not replace
a semantic review. Tests cover both cross-language search directions, unchanged
business identity and amounts, request isolation, policy search, translation
validation, and newly generated comparisons after switching language. Existing
conversation prose retains its original language; interface controls, catalog
views and subsequent replies follow the selected language.

`chinese-product-details.txt` and `.jpg` record the latest production browser
check: product image, long Chinese description, specifications, review highlights,
price chart and controls render together in the original layout. Earlier browser
captures are development observations, not final recording approval.

Verification at this checkpoint:

- Python: 1128 passed, 1 skipped; two existing dependency warnings.
- Ruff lint and format checks and scripts/check.py: passed.
- Retail shopper production build: passed.
- All eight example apps passed TypeScript checks during shared-module work.
- React Doctor full scan: baseline 30660b3 and current code both score 55;
  reported issues decreased from 114 to 108. Changed scans cover different file
  counts and their raw scores are not comparable. The current changed scan has
  one existing merchant-page complexity warning.

`chinese-checkout.txt` and `.jpg` additionally verify Chinese simulated checkout
after adding a product from its detail view; `chinese-orders.txt` and
`chinese-order-status.txt` verify order filters, delay explanations and the
model-generated status card. Amounts remain 79 USD for that separate dog-bed flow.

Final browser story and variant-option checks are recorded below. Merchant bilingual work (5) and autonomous delivery checks
(8) remain outstanding. No human operation or recording gate is claimed passed.

Variant browser check: `chinese-variants.txt` records standard/king sizes and
colors, selecting the standard ivory variant for 29 USD. Switching to English
(`english-variants-cart.txt`) preserves both cart lines and the 108 USD subtotal.
The Chinese capture exposed untranslated option values in quantity-button
accessibility labels; CartPanel now applies the same option translation to those
labels and generated quantity/removal messages. TypeScript verification passed.

The latest production build after the variant-label fix passed. A fresh Chinese
browser story (`chinese-tent-browser-final.txt`, comparison screenshot) completed
all three turns, with Chinese prose and cards and a 219 USD cart. Visual review
confirmed matching tent fallback icons and readable comparison columns. One
grounding discrepancy remains: the comparison calls the family tent freestanding,
although that attribute is recorded only for the two-person tent. This observation
is not a clean factual-accuracy acceptance; resolve it before closing issue 4.

Grounding retest after requiring each comparison claim to use its own product
record: `chinese-api-story-grounding-retest.json` completed all three real DeepSeek
turns. The family-tent comparison no longer borrows the freestanding construction;
that claim appears only on AR-1201. The matching cart remains AR-1202, one item,
219 USD. Targeted language/deployment tests passed (11 tests). This fixes the
observed discrepancy; it is not a guarantee that future model output is error-free.

Issue 4 acceptance is covered by the two current real-model language stories,
bidirectional search and identity tests, production build, detail/variant/checkout/
order browser observations, and readable Chinese comparison screenshot. The
final integrated both-role recording rehearsal remains in issue 8.
