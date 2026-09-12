# Public catalog preparation example

Two fictional ACME Playroom products from the official retail catalog demonstrate
catalog → checked bilingual records → images → simulated operating data → import.
This small package verifies preparation and loading; use the full retail fixtures
for the official camping, office, merchant and analytics stories.

`source-catalog.md` is the supplied catalog excerpt. `translations-zh.json` is the
prepared Chinese content. `prepare.py` packages those records, copies the two
explicitly associated public images, and derives 30 days of sales metrics from
60 simulated orders. Stock is 33/50 opening units less 30 sales, leaving 3/20.
Policies are the original fictional demo policies. No customer files are included.

From the repository root, choose a new directory outside the repository:

```bash
.venv/bin/python examples/retail/sample-catalog/prepare.py /tmp/playroom-demo
.venv/bin/python scripts/retail_dataset.py validate /tmp/playroom-demo
.venv/bin/python scripts/retail_dataset.py import /tmp/playroom-demo
```

Restart the API and refresh both web apps. Check the ACME Playroom Sample brand,
simulation label, block/puzzle images and AR-1401 low stock (3). The package's
`data/provenance.json` records image hashes and missing fields; `simulation.json`
records generated-data assumptions. Preparation refuses to overwrite a directory.

Image review: AR-1401 depicts colored wooden blocks; AR-1407 depicts blank puzzle
pieces. Both are **category illustrations**, not product photography; the puzzle
image does not establish its national-parks design, and the block image does not
establish the exact set count. Source associations and hashes are retained. Exact
model photos are missing for both; AR-1407 has no source long description/spec table.
Do not fill these gaps with invented details.

English and Chinese records are packaged and validated here; UI language switching
and cross-language search remain separate work. See the [preparation guide](../../../docs/retail-data-preparation.md).
