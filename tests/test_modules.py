import contextlib
import io
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main as pc  # noqa: E402


def run_demo(fn):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        fn(demo=True)
    return out.getvalue()


class DemoModules(unittest.TestCase):
    def test_portfolio_builder(self):
        out = run_demo(pc.module_portfolio_builder)
        self.assertIn("$72,475.00", out)       # total market value
        self.assertIn("33.77%", out)           # net exposure
        self.assertIn("FLAG: OVERSIZED", out)  # MELI/SPY above the 8% limit

    def test_capital_simulation(self):
        out = run_demo(pc.module_capital_simulation)
        self.assertIn("4,757", out)            # VNET shares = floor(50,000 / 10.51)
        self.assertIn("1.98x", out)            # (13.50 - 10.51) / (10.51 - 9.00)
        self.assertIn("2.35x", out)            # 34,149.43 / 14,532.07

    def test_risk_budget(self):
        out = run_demo(pc.module_risk_budget)
        self.assertIn("$4,725.00", out)        # 755 + 3,220 + 750
        self.assertIn("approximately 12 more", out)


class Inputs(unittest.TestCase):
    def test_prompt_float_rejects_non_positive(self):
        with mock.patch("builtins.input", side_effect=["0", "-5", "abc", "250"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(pc.prompt_float("x"), 250.0)


if __name__ == "__main__":
    unittest.main()
