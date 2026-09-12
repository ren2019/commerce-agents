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
