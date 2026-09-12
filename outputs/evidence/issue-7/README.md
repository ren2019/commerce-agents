# Public catalog preparation and import evidence

Source: `examples/retail/sample-catalog/source-catalog.md`, two fictional upstream ACME products. The coding agent prepared Chinese fields, checked both images visually against their declared category association, and ran `prepare.py /tmp/commerce-playroom-sample`, followed by the normal validate/import CLI. Validation returned no warnings. The API was restarted on port 8013 using the selected external runtime; browser pages at 3013 and 3113 were refreshed.

`api.json` records both product readbacks, image SHA-256 values, the merchant overview and shopper order count. Product ID, price and image references agree across shopper and merchant interfaces. Served image bytes equal the prepared assets. Both English and Chinese records cover the two IDs. The complete prepared source contains 60 orders, $1,590 sales, 30 units sold per product; each daily metric was derived from those orders. The current weekly view has 14 orders, $371 sales, 2% conversion and $26.50 average order value. Stock reads 3 and 20. The shopper API intentionally returns its usual latest 20 orders, not all 60.

Screenshots show the shopper product/order images, merchant simulated-data label and metrics, and the merchant catalog's two listings, prices and stock. At narrow widths the merchant header hides the brand, so the simulation label is in the page content and remains visible there.

Source provenance records category illustrations rather than exact model photos. Missing exact photos and AR-1407's absent specification table/long description remain documented; no model-specific parameter or image claim was invented. This is a data preparation example, not the complete official retail story and not real customer operating data.

Validation: 1114 pytest passed, 1 skipped, two existing dependency warnings; Ruff and scripts/check.py passed; both retail production builds and TypeScript passed. React Doctor scored 88/100 with two page-complexity warnings, no correctness/security finding. Bilingual display/search and real DeepSeek calls are outside this ticket and remain unverified.
