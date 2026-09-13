"""Live headless regression runs for the two orchestrators, across all three
markets.

Each case invokes Command Code in non-interactive (headless) mode:

    cmdc -p "<instruction>" --skill <src> --yolo ...

exactly as the orchestrators are driven in cron/harness automation. The tests
then assert, against the paths the resolver produces from `.env`:

  * the command exits successfully,
  * a report lands under the configured notes dir (`ISK_NOTES=./.notes`),
  * the report carries the mode's required sections and the market label,
  * deep-research reports carry a quality-gate verdict.

These runs call the real agent and fetch live market data, so they are
opt-in: set ISK_LIVE=1 to run them.

    ISK_LIVE=1 python -m unittest tests.test_skill_integration -v
"""

import datetime as _dt
import importlib
import os
import subprocess
import time
import unittest

_util = importlib.import_module("isk_test_util")

CMD = os.environ.get("ISK_CMD", "cmdc")
LIVE_ENABLED = os.environ.get("ISK_LIVE") == "1"
RUN_TIMEOUT_SECONDS = 600

# 6 cases: every (mode x market) pair gets its own ticker so a per-ticker
# scratch directory stays clean and one mode's artifacts cannot mask the
# correctness of another's.
CASES = [
    ("quick-look", "US", "AAPL"),
    ("quick-look", "Bursa", "1155"),
    ("quick-look", "Crypto", "ETH/USD"),
    ("deep-research", "US", "NVDA"),
    ("deep-research", "Bursa", "1023"),
    ("deep-research", "Crypto", "BTC/USD"),
]

# Section headings each report type must contain (from report-writer template).
MODE_SECTIONS = {
    "quick-look": ["## Verdict", "## Factor summary", "## Thesis",
                   "## Fundamentals", "## Technical setup"],
    "deep-research": ["## Verdict", "## Thesis", "## Fundamentals",
                      "## Technical setup"],
}


def prompt_for(report_type, ticker):
    if report_type == "quick-look":
        return f"Run the quick-look skill on ticker {ticker}."
    return f"Run the deep-research skill on ticker {ticker}."


def run_cmdc(report_type, ticker, timeout_s=RUN_TIMEOUT_SECONDS):
    env = dict(os.environ)
    # The test's own shell must not leak path overrides past `.env`.
    for key in ("ISK_ROOT", "ISK_NOTES", "ISK_CACHE"):
        env.pop(key, None)
    # Deep-research fans out to many sub-skills, so it needs a generous turn
    # budget; quick-look is a single pass and stays tight.
    max_turns = 250 if report_type == "deep-research" else 80
    # `CMD` is a .cmd/bat shim on Windows; subprocess cannot exec those via a
    # bare argv, so we hand the whole invocation to the shell.
    prompt = prompt_for(report_type, ticker)
    cmd = (
        f'"{CMD}" -p "{prompt}" --skill "{_util.SRC}" '
        '--yolo --permission-mode auto-accept --skip-onboarding '
        f'--no-auto-update --max-turns {max_turns}'
    )
    return subprocess.run(
        cmd,
        cwd=_util.REPO,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        shell=True,
    )


def _configured_cases():
    """CASES, narrowed to one (report_type|market) combo when ISK_ONE_CASE is set.

    Lets a caller run a single market x mode pair without paying for the other
    five live agent runs (each is time- and token-expensive).
    """
    only = os.environ.get("ISK_ONE_CASE")
    if not only:
        return CASES
    tokens = {f"{rt},{m}": (rt, m, t) for (rt, m, t) in CASES}
    return [tokens[only]] if only in tokens else []


class _LiveCase(unittest.TestCase):
    """One headless runtime case; built dynamically for each (mode, market)."""

    report_type = None
    market = None
    ticker = None
    proc = None
    paths = None
    report_path = None
    report_text = ""

    def test_exit_zero(self):
        self.assertEqual(
            self.proc.returncode, 0,
            f"cmdc exited {self.proc.returncode}\n"
            f"--- stdout ---\n{self.proc.stdout}\n--- stderr ---\n{self.proc.stderr}",
        )

    def test_report_lands_in_env_notes_dir(self):
        self.assertIsNotNone(self.report_path,
                             f"no {self.report_type} report for {self.ticker}")
        notes = os.path.abspath(self.paths["isk_notes"])
        self.assertTrue(
            os.path.abspath(self.report_path).startswith(notes),
            f"report outside {notes}: {self.report_path}",
        )

    def test_report_carries_required_sections_and_market(self):
        self.assertIsNotNone(self.report_path,
                             f"no report for {self.ticker}; nothing to inspect")
        for section in MODE_SECTIONS[self.report_type]:
            self.assertIn(section, self.report_text,
                          f"{os.path.basename(self.report_path)} missing {section!r}")
        self.assertIn(f"Market: {self.market}", self.report_text,
                      f"{os.path.basename(self.report_path)} wrong market line")
        for key in ("Action:", "Conviction:", "Current Price:"):
            self.assertIn(key, self.report_text,
                          f"{os.path.basename(self.report_path)} missing {key!r}")

    def test_deep_research_ran_quality_gate(self):
        if self.report_type != "deep-research":
            self.skipTest("quality gate only asserted for deep-research")
        self.assertIsNotNone(self.report_path,
                             f"no deep-research report for {self.ticker}")
        self.assertIn("Quality gate:", self.report_text,
                      f"{os.path.basename(self.report_path)} missing gate verdict")


def _live_cases():
    """Generate the fully-initialized TestCase types for every combo."""
    paths = _util.resolve_isk_paths()
    month = _dt.date.today().strftime("%Y-%m")
    started = time.time()

    for report_type, market, ticker in _configured_cases():
        proc = run_cmdc(report_type, ticker)
        # Fresh runs create the report. But the skills intentionally reuse a
        # same-day report for a ticker that already ran today, so also accept a
        # matching report written at any time (the content checks still run).
        report_path = _find_report(paths["isk_notes"], month, ticker,
                                  report_type, started) or _find_report(
                                  paths["isk_notes"], month, ticker,
                                  report_type, 0.0)
        report_text = ""
        if report_path:
            with open(report_path, encoding="utf-8") as fh:
                report_text = fh.read()
        name = f"test_{report_type.replace('-', '_')}_{market}"
        case_cls = type(name, (_LiveCase,), {
            "report_type": report_type,
            "market": market,
            "ticker": ticker,
            "proc": proc,
            "paths": paths,
            "report_path": report_path,
            "report_text": report_text,
        })
        for method in (
            "test_exit_zero",
            "test_report_lands_in_env_notes_dir",
            "test_report_carries_required_sections_and_market",
            "test_deep_research_ran_quality_gate",
        ):
            yield case_cls(method)


def _find_report(notes_base, month, ticker, report_type, created_after):
    mdir = os.path.join(notes_base, month)
    if not os.path.isdir(mdir):
        return None
    token = _util.ticker_token(ticker)
    best, latest = None, created_after
    for name in os.listdir(mdir):
        if not name.endswith(f"-{report_type}.md") or token not in name:
            continue
        path = os.path.join(mdir, name)
        mtime = os.path.getmtime(path)
        if mtime <= latest:
            continue
        if best is None or mtime > latest:
            best = path
            latest = mtime
    return best


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    if LIVE_ENABLED:
        suite.addTests(_live_cases())
    return suite