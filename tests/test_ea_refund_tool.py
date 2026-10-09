"""Alice's session, and the model asks to refund Bob's 900 dollar order.
The model is a stub that always returns that tool call."""
import unittest

from helpers import load


def model_wants_refund(_message):
    return {"tool": "refund", "args": {"order_id": "B-2", "amount": 900.0}}


def run(variant):
    app = load("ea_refund_tool", variant)
    reply = app.run_agent(app.Session("alice"), "refund B-2", model_wants_refund)
    return reply, app.REFUNDS


class EaRefundTool(unittest.TestCase):
    def test_vulnerable_refunds_another_users_order(self):
        reply, refunds = run("vulnerable")
        self.assertEqual(refunds, [("B-2", 900.0)])

    def test_fixed_denies_and_has_no_side_effect(self):
        reply, refunds = run("fixed")
        self.assertEqual(reply, "denied: not your order")
        self.assertEqual(refunds, [])

    def test_hard_negative_tool_is_not_reachable(self):
        reply, refunds = run("hard_negative")
        self.assertEqual(reply, "tool not available")
        self.assertEqual(refunds, [])

    def test_fixed_allows_own_small_refund_and_holds_large_one(self):
        app = load("ea_refund_tool", "fixed")
        self.assertEqual(app.refund(app.Session("alice"), "A-1", 40.0), "refunded")
        self.assertEqual(app.refund(app.Session("bob"), "B-2", 900.0), "needs human approval")
        self.assertEqual(app.REFUNDS, [("A-1", 40.0)])


if __name__ == "__main__":
    unittest.main()
