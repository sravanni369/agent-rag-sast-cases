"""Two-tenant help desk RAG answerer. HARD NEGATIVE variant.

Asset: Globex's payroll note. Source: STORE documents. Sink: the prompt sent
to the model, and so the answer shown to the user.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Doc:
    tenant_id: str
    text: str


@dataclass(frozen=True)
class Session:
    user_id: str
    tenant_id: str


DOCS = [
    Doc("acme", "Acme refund policy: refunds within 30 days."),
    Doc("globex", "Globex payroll note: CFO salary is 412000 USD."),
]


class Store:
    def __init__(self, docs):
        self.docs = list(docs)

    def search(self, query, tenant_id=None):
        words = set(query.lower().split())
        hits = [d for d in self.docs if words & set(d.text.lower().split())]
        if tenant_id is not None:
            hits = [d for d in hits if d.tenant_id == tenant_id]
        return hits


STORES = {t: Store([d for d in DOCS if d.tenant_id == t]) for t in ("acme", "globex")}


def answer(session, question, llm):
    chunks = STORES[session.tenant_id].search(question)
    context = "\n".join(d.text for d in chunks)
    return llm(f"Context:\n{context}\n\nQuestion: {question}")
