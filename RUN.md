# Run it yourself, then publish

Do these in order, from this folder, in PowerShell. Each step says what you should see.

## 1. Tests

```
python -m unittest discover -s tests -v
```

Expect: `Ran 14 tests` and `OK`.

## 2. Semgrep

```
pip install semgrep
semgrep scan --config rules/ --metrics=off --json -o results/semgrep.json cases/
python scripts/scorecard.py results/semgrep.json
```

Expect: 8 findings, and the last line `TP 3, FN 0, FP 3, TN 3`.

If `pip install semgrep` fails on Windows, skip to step 5. The GitHub workflow runs the same commands for you.

## 3. MCP server

```
pip install "mcp>=2"
$env:CRM_TENANT = "acme"
python cases/sid_mcp_tool/server.py fixed
```

Expect: it starts and waits for input. Press Ctrl+C to stop.

## 4. Read the three diffs

Open the vulnerable, fixed and hard_negative file of each case side by side. You should be able to point at the one or two lines that differ and say why, without notes.

## 5. Publish

Create an empty public repo on GitHub named `agent-rag-sast-cases`, then:

```
mkdir .github\workflows
copy ci-templates\*.yml .github\workflows\
git init
git add .
git commit -m "Three SID and Excessive Agency cases with variants, tests and scanner results"
git branch -M main
git remote add origin https://github.com/sravanni369/agent-rag-sast-cases.git
git push -u origin main
```

## 6. Check the two workflows on GitHub

- Actions, `tests-and-semgrep`: the job summary shows the same scorecard as step 2.
- Actions, `codeql`, then Security, Code scanning: expect 2 alerts from the custom query (the vulnerable and hard-negative RAG files) and none from the stock suite.

If the CodeQL numbers on GitHub differ from the README, the README is wrong. Fix the README.
