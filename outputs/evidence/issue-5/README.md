# Issue 5: merchant bilingual work in progress

The merchant language selector, navigation, assistant entry copy, change controls,
before/after labels and summary/metric labels are implemented. Full page coverage,
operational fixture text, analysis presentation and both complete real-model
stories remain outstanding; this is not issue 5 acceptance.

Merchant listing/detail/inventory views reuse shopper translations without changing
identifiers, prices, currency or inventory. The DeepSeek deployment prepares a
second language row for textual listing edits before staging. Both rows are
reviewable and apply together after the existing host approval gate. Source-language
catalog content and translated views then agree; a translation failure stages
nothing. Tests exercise edits initiated in either language and unchanged catalog
state before approval.

Actual DeepSeek verification:

- `bilingual-content-preview.json`: Chinese request to simplify AR-2102 description;
  the preview contains the Chinese edit and English translation as separate rows.
  The script asserted the listing response was unchanged before approval.
- `bilingual-content-approved.json`: approval through the application host-action
  endpoint and readback of both merchant language views. New descriptions are
  “36张海洋主题墙贴” and “36 ocean-themed wall stickers”. Price stays 24 USD and stock 3.
- `shopper-after-content-approval.json`: shopper API reads the same two new texts.

This run used the configured real DeepSeek deployment in an isolated private copy
of the public retail dataset. It does not substitute for the pending browser
approval rehearsal or for the complete morning/restock/description/analysis story.

Validation: 1132 Python tests passed, 1 skipped; two existing dependency warnings.
Ruff and generated-document/data checks passed. Merchant TypeScript passed after
the UI labels; all eight apps passed TypeScript during shared-card changes. The
merchant production build passed before the final small auxiliary-label changes;
the final integrated build and browser pass remain required.

Page-localization checkpoint: inventory, catalog/detail and order UI labels now
follow the language context; language changes refetch the relevant resources.
Option labels accept a translation function while business values stay unchanged.
The production browser inventory/detail captures record progress and exposed
remaining English auxiliary labels, subsequently translated in code. The detail
screenshot also exposed a flex-shrink issue hiding the facts row; the shared Sheet
scroll body now prevents child shrinking. A fresh visual recheck is still required.
Two untranslated catalog titles (AR-1723 and AR-1902-TWIN) were corrected.

All eight TypeScript projects passed before the last small label and Sheet fixes;
merchant TypeScript passes afterward. The production build passed for the page
changes. React Doctor score remains 64; it now reports seven maintainability
complexity warnings in modified merchant page components, no correctness errors.
Home-page content, dynamic business fixture text and full merchant stories remain
in progress. These captures are not final acceptance evidence.

Home and operational-data checkpoint:

- Home date, KPI/queue labels and recent-record controls now follow the language.
  Operational messages and campaigns contain optional, validated locale maps.
  Computed insights use unchanged figures with localized descriptions.
- `chinese-home.txt` / `.jpg` show the real Chinese overview. The screenshot exposed
  narrow columns while the assistant rail is open; the page now uses its container
  width for the two-column breakpoint. This adjustment awaits a fresh visual check.
- `chinese-change-previews.txt`: actual DeepSeek restock (3 to 27) and bilingual
  description preview. `chinese-chat-approval-rejected.txt` and corresponding state
  JSON prove chat consent left both changes unapplied.
- `chinese-browser-approved.txt` and `chinese-browser-approved-views.json`: clicking
  both actual approval buttons applied stock 27 and new descriptions in both
  languages. Material and wall coverage remain missing; no invented values were
  added to those fields.

The run is progress evidence, not final language/analysis acceptance. Its morning
summary misclassifies one slow mover as low stock, and a generated restock note
says 14 days after replenishment while the deterministic card correctly calculates
16 days for total stock 27. These presentation discrepancies remain to resolve or
clearly separate from authoritative inventory values before the final rehearsal.
Full Chinese/English analysis and English complete-story regression remain pending.

Latest backend validation: 1135 passed, 1 skipped; Ruff and check.py passed.
Merchant production build passed before the last home responsive-layout change;
TypeScript passed after that change. React Doctor has no correctness warning,
score 64, with eight remaining component-complexity warnings.

Analysis and layout checkpoint:

- `chinese-home-layout-fixed.jpg` and `chinese-listing-layout-fixed.jpg` were
  visually inspected after the production rebuild: the home main column remains
  readable with the assistant rail open, and listing facts no longer collapse.
  The official AR-2102 fixture has no image; its placeholder is preserved rather
  than substituting an unrelated product photo.
- `chinese-analysis-before-scope-fix.txt` and
  `chinese-two-week-before-scope-fix.txt` preserve real analysis results and a
  presentation failure: the subsequent model-selected card used weekly snapshot
  metrics under an analysis-window heading. The deployment now instructs the
  merchant to retain the automatically rendered analysis card without duplicating
  it with snapshot picks. This requires a new real-model regression.
- The first analysis attempt timed out while reading the DeepSeek stream; a retry
  returned results. No timeout is counted as a pass. Generic error text and analysis
  chart annotations now have Chinese presentation.
- `chinese-morning-classification-retest.txt` correctly separates slow movers and
  low stock but includes an English pre-tool sentence. Both retail roles now share
  the existing complete-text language validator, including token accounting and
  unchanged tool-event ordering. The subsequent real browser retest is pending.

Validation after extracting the shared language filter: 1136 passed, 1 skipped,
two existing warnings. Merchant production build passed for the latest UI changes;
React Doctor score 70 with eight complexity warnings and no correctness warnings.
These checkpoints do not close issue 5.

Further real retest:

- `chinese-morning-language-validated.txt` has a Chinese pre-tool sentence after
  shared validation. The model's aggregate zero-stock count still needs care:
  its prose says three while the source contains four; individual records remain
  authoritative. This is not a blanket factual pass.
- `chinese-restock-cover-retest.txt` correctly reports stock 3 to 27 and 15.6 days
  of total cover, matching the host card's rounded 16 days. Its content preview
  remains unapplied in this new isolated run.
- `chinese-analysis-scope-retest.txt` no longer includes the duplicate snapshot
  card. Inspection of the actual tool input exposed a different error: the main
  model requested Aug 15–27 as a supposedly 14-day prior window. The delegate then
  treated the omitted Aug 14 as absent source data. The backend now supplies exact
  inclusive two-week comparison windows in merchant context; a source-row test
  verifies two disjoint 14-day windows spanning the latest 28 days. Real retesting
  of this correction remains required. Category schema names still occur in some
  Chinese analysis labels.

All eight apps pass TypeScript after the latest shared error rendering change.

Exact-window and English API checks:

- `chinese-exact-window-retest.json`: the real DeepSeek tool request now uses
  Aug 28–Sep 10 and Aug 14–27, both inclusive. Figures are 34393.86 versus 32889.71
  in sales, with 1756.78 growth in children's-room sales and -252.63 elsewhere.
  `two-week-source-totals.json` independently sums the public source rows using
  decimal arithmetic and matches the core figures. The returned follow-up card
  resolves analysis figures rather than mismatched weekly snapshot values.
- `english-official-smoke.txt`: all six official merchant steps pass with actual
  DeepSeek, including chat approval refusal, portal application and both analyses.
- The analysis UI translates the internal kids-room category label only when
  rendering Chinese cards. Stored analysis data and SQL keys remain unchanged.

The attempted browser continuation encountered a locked Mac. No new browser pass
is claimed while locked. English browser approval and final integrated rehearsal
remain outstanding. API checks alone do not establish visual acceptance.
