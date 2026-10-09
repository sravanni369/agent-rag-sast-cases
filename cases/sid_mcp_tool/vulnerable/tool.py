"""CRM lookup behind an MCP tool. VULNERABLE variant.

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



def get_customer(customer_id, tenant):
    record = CUSTOMERS[customer_id]
    return dict(record)
