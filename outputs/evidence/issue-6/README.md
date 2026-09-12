# Dataset switch and reset evidence

Two public fictional fixture variants were used: A (`field-demo`, ACME Field) and B (`studio-demo`, ACME Studio, renamed coffee maker). Both were copied from the upstream retail fixtures; no customer data or credentials are included.

The local CLI switched A → B → A and reset A after deleting a seeded memory fact. The API process on port 8013 was stopped and restarted after each selection; both browser pages (3013 and 3113) were refreshed. Screenshots capture B, returned A and reset A. API readbacks confirm old shopper/operator sessions return 401, the new cart is empty, memory returns from 2 to 3 facts, stock is back at 3, and no applied changes remain.

`examples/retail/api/tests/test_dataset_reset.py` additionally exercises cart changes and staged/applied inventory changes, then rebuilds the complete application through B, A and reset. It asserts the public overview has no pending or applied changes after each rebuild. Mutation setup uses the existing provenance/backend test seam; it does not claim a real model conversation or host-approval demonstration. A separate test changes the original source after import and verifies reset still uses the imported baseline, leaving the source and previous runtime intact.

Validation: full pytest 1114 passed, 1 skipped (two existing dependency warnings); Ruff and scripts/check.py passed. The prior issue-3 production builds cover unchanged web code. Real DeepSeek story validation remains on issues #1/#2.
