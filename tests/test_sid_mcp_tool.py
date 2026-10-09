"""The MCP server is configured for tenant acme. The tool is asked for
Acme's own customer, then for a Globex customer."""
import unittest

from helpers import load

SENSITIVE = {"ssn", "card_last4"}


def tool(variant):
    return load("sid_mcp_tool", variant, "tool.py")


class SidMcpTool(unittest.TestCase):
    def test_vulnerable_returns_sensitive_fields(self):
        self.assertTrue(SENSITIVE <= set(tool("vulnerable").get_customer("c-100", "acme")))

    def test_vulnerable_returns_other_tenants_customer(self):
        self.assertEqual(tool("vulnerable").get_customer("c-200", "acme")["name"], "Lee Park")

    def test_fixed_returns_public_fields_only(self):
        self.assertEqual(tool("fixed").get_customer("c-100", "acme"),
                         {"name": "Dana Ruiz", "plan": "pro"})

    def test_fixed_refuses_other_tenant(self):
        with self.assertRaises(PermissionError):
            tool("fixed").get_customer("c-200", "acme")

    def test_hard_negative_returns_public_fields_only(self):
        self.assertEqual(tool("hard_negative").get_customer("c-100", "acme"),
                         {"name": "Dana Ruiz", "plan": "pro"})

    def test_hard_negative_refuses_other_tenant(self):
        with self.assertRaises(KeyError):
            tool("hard_negative").get_customer("c-200", "acme")


if __name__ == "__main__":
    unittest.main()
