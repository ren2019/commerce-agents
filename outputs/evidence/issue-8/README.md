# Integrated delivery verification — in progress

`public-clone.json` records an independent HTTPS clone of the public fork at
35f149a, with a fresh Python environment and `npm ci`; it contains neither the
operator's `.env` nor local planning/handoff files. Dependencies resolve against
that clone's packages, not the development checkout. The local SOCKS proxy requires
`socksio` in addition to the repository requirements.

`public-verify-all.txt` records all 14 official verification steps passing there:
lint, formatting, repository consistency, pytest, both managed-agent deployment
dry-runs, and all eight Next.js production builds. No deployment was published.

`public-startup.json` records that clone's actual API on an unused loopback port,
with an empty, independent RETAIL_STATE_DIR and no RETAIL_DATASET override. It
loaded the 87-product public retail dataset and returned merchant overview data.
The configured model is deepseek-flash. Credentials were supplied only in the
process environment from the operator's existing local configuration, not copied
into the public clone or recorded in evidence.

`public-shopper-smoke.txt` passes all three official shopper turns against this
independent API with real DeepSeek: search, comparison, and cart plus returns.

The operator instructions and bilingual scripts are in
`docs/retail-demo-runbook.md`. Source remote readback confirms origin is
https://github.com/ren2019/commerce-agents.git and upstream is
https://github.com/anthropics/commerce-agents.git. The runbook describes reviewing
upstream changes on a separate branch and rerunning verification before inclusion.

A subsequent change makes shared startup/authentication errors provider-neutral;
1137 tests and check.py pass after that text-only Python change. The production
build evidence above applies to the unchanged frontend sources at 35f149a.

This does not complete issue 8. The Mac was locked when browser verification was
attempted; final bilingual browser operation, integrated switch/reset rehearsal,
and the user's own operation gate remain outstanding. Issue 5 is still open.

`integrated-switch-reset.json` extends the switch/reset proof at runtime commit
0d6fc23. In a separate loopback API process and private temporary state directory,
the CLI imports full public retail A, switches to the public two-product sample B,
switches back to A, then resets A. Real DeepSeek adds one product to a shopper cart
in English A and Chinese B. Back on A, it stages four units of AR-2102, and the
host approval endpoint applies stock 3 to 7. Reset restores stock 3. Each restart
rejects both prior role tokens with 401; fresh carts, pending changes and resolved
change lists are empty. The helper terminated its API process after the run.
This is real process/API/model evidence; browser rendering during switching still
requires the Mac to be unlocked.

Final unlocked-browser integration:

- `browser-A-shopper.*` shows full ACME retail before switching.
- `browser-B-shopper.*`, `browser-B-merchant.txt`, and
  `browser-B-merchant-detail.jpg` show the public Playroom sample after CLI switch
  and API restart. The store name changes in both roles; the merchant catalog has
  exactly two listings. The wood-block image appears with AR-1401 in both roles,
  and the jigsaw image stays with AR-1407. No unrelated picture substitutes for
  a missing image. Screenshots were visually inspected.
- `browser-A-restored-merchant.txt` and `browser-A-restored-stock.jpg` show the
  return to 87 products, original ACME branding and AR-2102 stock 3. Prior approval
  state was cleared by the switch. The previously recorded real-model process
  rehearsal separately establishes old-token invalidation and reset after writes.
- `final-verify-all.txt` records all 14 checks passing on the latest functional
  changes. The later small analysis-progress translation additionally passed the
  merchant production build and all eight apps' TypeScript checks. There were
  1137 passing Python tests, one skip and two existing warnings.
- The independent public clone was fast-forwarded from 35f149a to 5d7a4b1 and the
  approval-response fault-injection checks passed there. The earlier full public
  clone install/build/startup and actual DeepSeek shopper proof remain applicable;
  no dependency changes or customer files were introduced.

Issue 5 is closed. Issue 8's human operation gate remains open. The final handoff
uses loopback API 8014, shopper 3014 and merchant 3114, reset to full public retail.
See the runbook for reproducible launch, data preparation and upstream handling.

`final-reset-readback.json` confirms the final CLI reset after API startup:
AR-2102 stock 3, empty shopper cart, no pending or recent changes. Reset startup
was slow under concurrent desktop load; the initial connection-refused probe is
not counted as a pass. Subsequent API readback and fresh browser pages succeeded.
`browser-reset-shopper.txt` and `browser-reset-merchant.txt` record fresh role views.
The local ignored `.env` provider selector is now deepseek; credentials were not
changed or exposed. Standard runbook launch therefore uses the selected provider.
