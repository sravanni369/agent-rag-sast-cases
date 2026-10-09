"""CRM lookup behind an MCP tool. HARD NEGATIVE variant.

Asset: ssn and card_last4, and any other tenant's customer. Source: CUSTOMERS.
Sink: the tool result, which goes straight into the model's context.
"""

CUSTOMERS = {
    "c-100": {"tenant": "acme", "name": "Dana Ruiz", "plan": "pro",
              "ssn": "000-12-3456", "card_last4": "4242"},
    "c-200": {"tenant": "globex", "name": "Lee Park", "plan": "free",
              "ssn": "000-98-7654", "card_last4": "1881"},
}
PUBLIC_FIELDS = ("name", "plan")



def public_view(tenant):
    return {cid: {k: r[k] for k in PUBLIC_FIELDS}
            for cid, r in CUSTOMERS.items() if r["tenant"] == tenant}


def get_customer(customer_id, tenant):
    record = public_view(tenant)[customer_id]
    return dict(record)
