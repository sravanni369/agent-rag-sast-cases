"""Support agent with tools. HARD NEGATIVE variant.

Asset: money in other customers' orders. Source: the model's tool call.
Sink: REFUNDS.append, the side effect.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    owner: str
    total: float


@dataclass(frozen=True)
class Session:
    user_id: str


ORDERS = {
    "A-1": Order("A-1", "alice", 40.0),
    "B-2": Order("B-2", "bob", 900.0),
}
REFUNDS = []
REFUND_CAP = 100.0


def lookup_order(session, order_id):
    return {"order_id": order_id, "status": "delivered"}


def refund(session, order_id, amount):
    REFUNDS.append((order_id, amount))
    return "refunded"


TOOLS = {"lookup_order": lookup_order}


def run_agent(session, user_message, llm):
    call = llm(user_message)
    tool = TOOLS.get(call["tool"])
    if tool is None:
        return "tool not available"
    return tool(session, **call["args"])
