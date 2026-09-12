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
