# Issue 3 verification

External test package: ACME Field, derived from the upstream fictional retail fixtures;
87 listings and the existing category photos. Logo is an original test SVG.
Customer source data was not used.

- All Python tests: 1112 passed, 1 skipped; two dependency warnings.
- Ruff check and format check: passed. Upstream structural check: clean.
- Retail storefront and merchant production builds: passed, including TypeScript.
- Browser: both pages visibly show ACME Field and the package logo. Storefront product
  images and merchant listing detail image render from the selected API package.
- Public API readback and failed-import behavior: api.json.
- Import regression test: failure preserves selected runtime; runtime memory writes
  leave the source package untouched.
- React Doctor changed-scope scans: storefront 88, merchant 89. Both report the existing
  page component control-flow complexity; no security or correctness errors reported.

Screenshots are actual browser captures of the external package, not mockups.
This evidence covers package loading, not bilingual rendering or live DeepSeek chat.
