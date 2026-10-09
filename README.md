# agent-rag-sast-cases

Three small, runnable agent and RAG cases for checking what a static analysis tool can and can't see in GenAI application code. Each case has a vulnerable version, a fixed version, and a hard negative: code that looks like the vulnerable one to a pattern matcher and is safe.

| Case | Risk | Surface | Vulnerable | Fixed | Hard negative |
|---|---|---|---|---|---|
| `sid_rag_tenant` | Sensitive Information Disclosure | RAG retrieval | Shared store searched with no tenant filter | Filter by the session's tenant | Same unfiltered call, on a store that only holds that tenant's documents |
| `ea_refund_tool` | Excessive Agency | Tool calling | Refund tool pays out on any order | Owner check, then a cap that sends large refunds to a person | Same unchecked function, not registered as a tool |
| `sid_mcp_tool` | Sensitive Information Disclosure | MCP tool output | Tool returns the whole customer record, any tenant | Tenant check, public fields only | Same `return dict(record)`, on a view that is already tenant-scoped and redacted |

The trace, authorization context, root cause, severity and residual risk for each case are in [FINDINGS.md](FINDINGS.md).

## Result

Run on 2026-10-09 with Semgrep 1.180.0 and CodeQL 2.27.2. Ground truth: only the vulnerable variant of each case is a finding, and the tests prove it.

| Scanner | Rules | Vulnerable caught | Fixed flagged | Hard negatives flagged |
|---|---|---|---|---|
| Semgrep, 4 custom rules in `rules/` (one in taint mode) | written for these cases | 3 of 3 | 0 of 3 | 3 of 3 |
| CodeQL, `python-security-extended` (50 queries) | stock | 0 of 3 | 0 of 3 | 0 of 3 |
| CodeQL, 1 custom query in `codeql-queries/` (RAG case only) | written for this case | 1 of 1 | 0 of 1 | 1 of 1 |

What that says:

- The stock CodeQL suite found nothing. None of these bugs has a classic sink such as SQL or a shell command. The bug is a missing authorization decision, and the stock queries have no model of tenants or tool registries.
- Rules written for the pattern caught every vulnerable variant and also every hard negative. Semgrep made 8 findings on 6 files, and 3 of those files are safe. The rule sees `search(question)` with one argument. It can't see that the store behind it only holds one tenant's documents, or that the refund function was never registered as a tool.
- So on this set, a rule hit is right half the time. Telling the two apart took the test, not the scanner.

The limits: three cases, one author, rules written by the same person who wrote the cases. This shows the method. It is not a benchmark of Semgrep or CodeQL.

Raw output is in `results/`: `semgrep.json`, `codeql.sarif`, `codeql-custom.sarif`.

## Run it

Tests need only the Python standard library. The model is a stub in every test, so every run gives the same result.

```
python -m unittest discover -s tests -v
```

14 tests. For each case: the vulnerable variant leaks or acts, the fixed variant doesn't, the hard negative doesn't.

Semgrep:

```
pip install semgrep
semgrep scan --config rules/ --metrics=off --json -o results/semgrep.json cases/
python scripts/scorecard.py results/semgrep.json
```

MCP server over stdio (needs `pip install "mcp>=2"`). The tenant comes from the server's configuration, never from the model:

```
CRM_TENANT=acme python cases/sid_mcp_tool/server.py fixed
```

CodeQL steps are in [RUN.md](RUN.md).

## How this was built

I wrote the cases, rules and tests with an AI coding assistant, then ran the tests and both scanners myself and checked each result against the code.
