# commerce-agents

For agents working in this repo, commerce-builder plugin users included. The public
reference for commerce agents on Claude: a shopping agent and a merchant agent on three
paths each, four vertical examples, and a Claude Code plugin.

## Layout

- `commerce-common/commerce_common/`: what both roles share; its `__init__` lists the modules.
- `shopping-agent/core/shopping_agent/`: types, `StorefrontBackend`, config, prompt, `tools/`, gates, enrichment, executor.
- `merchant-agent/core/merchant_agent/`: the merchant equivalents, plus `changes.py` and `analysis.py`.
- `*/skills/`: five flows per role, one `SKILL.md` each.
- `*/runtime-messages-api/`: `ShoppingAgent`, `MerchantAgent`, the merchant analysis delegate.
- `*/runtime-agent-sdk/`: each agent as `ClaudeAgentOptions`, with a console.
- `*/managed-agents/`: the manifest directory (with the derived `system.md`) and the role's MCP server.
- `examples/demo_common/` and `examples/web-shared/`: what the verticals' APIs and web apps share; `examples/` is the npm workspace.
- When preparing catalog files or product images, follow `docs/retail-data-preparation.md`; `examples/retail/sample-catalog/` is the public preparation example.
- `examples/retail/merchant-web/lib/chinese.ts`: merchant interface dictionary for the shared optional language context.
- `examples/retail/api/agent.py`: shopper runtime projects cached product content into the selected language while retaining provenance.
- `examples/retail/api/deepseek.py`: DeepSeek client response-language directive after the cached context.
- `examples/retail/api/language.py`: request-scoped catalog and policy translations over unchanged business IDs and amounts.
- `examples/retail/api/dataset.py`: external package validation and atomic private runtime selection; `scripts/retail_dataset.py` is its local import command.
- `examples/<vertical>/`: `api/`, `data/`, `storefront-web/`, `merchant-web/`; ports 8000-8003, 3000-3003, 3100-3103.
- `plugins/commerce-builder/`: six skills, four commands; `.claude-plugin/marketplace.json` points at it.
- `docs/`: `safety.md`, `backends.md`, `deployment.md`. `scripts/`: install, demo, smoke, screenshots, check, deploy, verify.
- `tests/`: the suites that span packages (both roles on all three paths); each package keeps its own `tests/`.

`requirements.txt` installs the seven packages and their pinned dependencies (`requirements-dev.txt`
adds pytest and ruff); `scripts/install.sh` runs it.

## Design rules

- One model owns the conversation; a rule goes in a tool description, the prompt, or a skill by how often it applies.
- The static prompt and `tools[]` are the same bytes on every turn; per-request data goes in the fenced block after the breakpoint.
- UI is presentation tool calls, validated and filled in on the server, streamed as `ui` events.
- Third-party content is fenced data; writes are provenance-gated and capped in code; `checkout` charges nothing; merchant writes apply only through host approval.
- Core is domain-neutral; a vertical adds UI through `PresentationExtension` and keeps the rest to itself.
- Each mechanism is defined once, in `commerce_common` or a role core, and shared by all three paths.

## Fictional and original

No real company, brand, product, or person appears: the only company is ACME and its
lines; every brand, prompt, schema, and figure is invented here. Two exceptions:
deployment and integration targets (the README's "MCP connectors" section; platform and
SDK names in `docs/deployment.md`, the README's deploying section, and the platform tests),
and CC0 category photos listed in the `IMAGE-CREDITS.md` beside them. When in doubt,
redesign rather than rename.

## Conventions

- Python 3.11+, `ruff` (root `ruff.toml`), `pytest` (root `pytest.ini`), type hints, `pydantic` schemas; web apps are Next.js and TypeScript.
- Skill descriptions name the request class, without sample utterances; tool descriptions say when the tool applies; examples stay schematic.
- A change to prompt text, a tool description, a skill, or a fence notice re-derives `system.md`; `scripts/check.py` compares them.
- Prose: plain declarative sentences; one term per thing; each fact once, naming its module; each role in its own terms; a README says what a thing is, how to run it, and where its interfaces are; no history, dates, or process narrative; cut before restyling.
- A new module updates this file and its README.

## Verify

```bash
ruff check . && ruff format --check . && pytest && python scripts/check.py
python scripts/verify_all.py          # adds deploy dry runs and web builds
```

## Agent skills

### Issue tracker
Issues 和规格使用 ren2019/commerce-agents 的 GitHub Issues。
操作前读取 docs/agents/issue-tracker.md。

### Triage labels
使用五个默认分流标签。应用标签前读取 docs/agents/triage-labels.md。

### Domain docs
采用 single-context。探索和设计前读取 docs/agents/domain.md。
