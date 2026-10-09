"""An Acme user asks about Globex payroll. The model is a stub that echoes
its prompt, so the test sees exactly what reached the sink."""
import unittest

from helpers import load

SECRET = "412000"
QUESTION = "what is the CFO salary"


def echo(prompt):
    return prompt


def ask(variant, tenant):
    app = load("sid_rag_tenant", variant)
    return app.answer(app.Session("u1", tenant), QUESTION, echo)


class SidRagTenant(unittest.TestCase):
    def test_vulnerable_leaks_other_tenant_document(self):
        self.assertIn(SECRET, ask("vulnerable", "acme"))

    def test_fixed_blocks_other_tenant_document(self):
        self.assertNotIn(SECRET, ask("fixed", "acme"))

    def test_hard_negative_blocks_other_tenant_document(self):
        self.assertNotIn(SECRET, ask("hard_negative", "acme"))

    def test_owner_still_gets_own_document(self):
        for variant in ("vulnerable", "fixed", "hard_negative"):
            self.assertIn(SECRET, ask(variant, "globex"))


if __name__ == "__main__":
    unittest.main()
