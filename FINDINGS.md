# Findings

One section per case. Line numbers refer to the vulnerable variant unless stated.

## 1. sid_rag_tenant: another tenant's document reaches the prompt

- Risk class: Sensitive Information Disclosure.
- Asset: Globex's payroll note.
- Actor: an authenticated Acme user, `Session("u1", "acme")`.
- Authorization context: a user may read documents whose `tenant_id` equals the session's tenant. Purpose: answering that user's question. Recipient: that user only.
- Source: `DOCS`, through `STORE.search(question)` at `app.py:43`.
- Path: `chunks` (43) to `context` (44) to the prompt string (45).
- Sink: `llm(...)` at `app.py:45`, and from there the answer shown to the user.
- Missing control: the tenant filter. `Store.search` supports one and the caller doesn't pass it.
- Root cause: the retriever is called with the question only, so authorization depends on a parameter the caller forgot.
- Severity: high. Any user of one tenant can read another tenant's documents by asking about them. No special access needed.
- Fix (`fixed/app.py:43`): `STORE.search(question, tenant_id=session.tenant_id)`. One line.
- Hard negative (`hard_negative/app.py:39,43`): the call is still `search(question)` with no filter, but it runs on `STORES[session.tenant_id]`, a store built with only that tenant's documents. The isolation is in the data layout, not in the call.
- Test: `tests/test_sid_rag_tenant.py`. The stub model echoes its prompt, so the test reads exactly what reached the sink.
- Residual risk after the fix: the filter trusts `session.tenant_id`. If the session can be forged or the tenant ID comes from the request body, the filter is bypassed. Documents with a wrong `tenant_id` at ingestion also leak.

## 2. ea_refund_tool: the agent refunds an order the user doesn't own

- Risk class: Excessive Agency (excessive permissions, and no approval step for a high-impact action).
- Asset: money in other customers' orders.
- Actor: an authenticated user, `Session("alice")`, plus whatever the model decides to call.
- Authorization context: a user may refund their own order, up to the order total and the refund cap. Larger refunds need a person. Nobody may refund another user's order.
- Source: the model's tool call, `llm(user_message)` at `app.py:42`. It is untrusted. A prompt can make the model ask for any order ID and amount.
- Path: `call` (42) to the `TOOLS` lookup (43) to `tool(session, **call["args"])` (46) to `refund` (33).
- Sink: `REFUNDS.append(...)` at `app.py:34`, the side effect.
- Missing control: no ownership check and no amount limit before the side effect.
- Root cause: the tool acts with the application's authority and never compares the order's owner with the session's user.
- Severity: critical. Direct financial loss, triggered by text.
- Fix (`fixed/app.py:34-38`): look up the order, deny when `order.owner != session.user_id`, return "needs human approval" above `min(order.total, REFUND_CAP)`.
- Hard negative (`hard_negative/app.py:38`): the unchecked `refund` function is unchanged, but `TOOLS` only registers `lookup_order`. The dangerous code exists and the agent can't reach it. The finding is not code-reachable.
- Test: `tests/test_ea_refund_tool.py`. The stub model always asks to refund Bob's 900 dollar order from Alice's session.
- Residual risk after the fix: the cap is per call, so repeated small refunds on one order aren't stopped. In the hard negative, the unchecked function becomes a live finding the day someone adds it to `TOOLS`.

## 3. sid_mcp_tool: an MCP tool hands the model the whole customer record

- Risk class: Sensitive Information Disclosure.
- Asset: `ssn` and `card_last4` on every customer, and any other tenant's customer record.
- Actor: the agent connected to this MCP server. The server is configured for one tenant through `CRM_TENANT`.
- Authorization context: the agent may read `name` and `plan` for customers of the server's own tenant. Purpose: support lookups. Recipient: the model's context, which can end up in an answer or a log.
- Source: `CUSTOMERS[customer_id]` at `tool.py:18`.
- Sink: `return dict(record)` at `tool.py:19`. The MCP result goes straight into the model's context.
- Missing control: no tenant check and no field allowlist.
- Root cause: the tool returns the storage record as the API response.
- Severity: high. Two disclosures in one line: sensitive fields for the right tenant, and everything for the wrong one.
- Fix (`fixed/tool.py:19-21`): raise `PermissionError` when the record's tenant isn't the server's, then return only `PUBLIC_FIELDS`.
- Hard negative (`hard_negative/tool.py:17-24`): the function still ends in `return dict(record)`, but `record` comes from `public_view(tenant)`, which is already filtered to the tenant and to the public fields.
- Test: `tests/test_sid_mcp_tool.py`.
- Residual risk after the fix: `name` is still personal data. The tenant is whatever the server was started with, so a misconfigured deployment serves the wrong tenant correctly.

## Controls recommended across the three

1. Pass identity into every retrieval and tool call from the session, never from model output.
2. Give each tool the user's permissions, not the application's.
3. Register only the tools the task needs. Treat the registry as the reachability boundary and review changes to it.
4. Allowlist the fields a tool returns.
5. Put a person in front of high-impact actions, and show them the order, the amount and the recipient.
