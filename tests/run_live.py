"""Entry point for the live headless regression runs.

Run from the repo root:  python tests/run_live.py [report_type,market ...]

Without arguments it runs all six (mode x market) cases. Pass one or more
`report_type,market` tokens (e.g. `quick-look,US` `deep-research,Crypto`) to
run a subset. ISK_LIVE is forced on here so you never have to remember it.

Each case invokes Command Code headless and then asserts the `.env`-resolved
output paths, report sections and market wiring — exactly what
`test_skill_integration.py` does via `python -m unittest`.
"""

import os
import sys
import unittest

os.environ["ISK_LIVE"] = "1"

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import test_skill_integration as mod  # noqa: E402

if len(sys.argv) > 1:
    os.environ["ISK_ONE_CASE"] = sys.argv[1]

suite = mod.load_tests(None, None, None)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)