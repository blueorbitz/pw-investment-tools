"""Offline regression contract for the skills network.

These tests never touch the network or the LLM. They pin the *wiring* of the
two orchestrators (quick-look, deep-research) for all three markets (US,
Bursa, Crypto): every skill and script an orchestrator is documented to invoke
must actually exist on disk, and the orchestrator must still reference it.

If one of these breaks, a real headless run would silently skip a market
factor or crash on a missing script, so the suite catches wiring regressions
cheaply and deterministically. The live headless runs live in
`test_skill_integration.py`.
"""

import os
import unittest

from isk_test_util import (
    MARKETS,
    REPORT_TYPES,
    REPO,
    SRC,
    resolve_isk_paths,
    skill_md_exists,
)

# ---------------------------------------------------------------------------
# Expected wiring, from orchestrator/quick-look and orchestrator/deep-research
# ---------------------------------------------------------------------------

# Data scripts each market must run in both modes. Crypto has no annual
# statements, so it omits financials_fetch.
QUICK_SCRIPTS = {
    "US": ["price_history.py", "financials_fetch.py", "quote_fetch.py"],
    "Bursa": ["price_history.py", "financials_fetch.py", "quote_fetch.py"],
    "Crypto": ["price_history.py", "quote_fetch.py"],
}

# Map each script to the *skill directory* that owns it (the script lives in
# that skill's scripts/ subfolder).
SCRIPT_OWNER = {
    "price_history.py": ["data", "price-history"],
    "financials_fetch.py": ["data", "fundamentals"],
    "quote_fetch.py": ["data", "fundamentals"],
}

# Market-conditional *data skills* deep-research fans out.
DEEP_DATA_SKILLS = {
    "US": ["data/price-history", "data/us-filings"],
    "Bursa": [
        "data/price-history",
        "data/bursa-fundamentals",
        "data/bursa-announcements",
    ],
    "Crypto": [
        "data/price-history",
        "data/crypto-fundamentals",
        "data/crypto-onchain",
        "data/crypto-derivatives",
    ],
}

# Market-conditional *analysis* skills deep-research fans out.
DEEP_ANALYSIS_SKILLS = {
    "US": [
        "analysis/quality-gate",
        "analysis/us-technical",
        "analysis/us-sentiment",
        "analysis/macro-context",
        "analysis/verdict-synthesis",
        "analysis/valuation-baseline",
    ],
    "Bursa": [
        "analysis/quality-gate",
        "analysis/bursa-valuation",
        "analysis/bursa-technical",
        "analysis/bursa-sentiment",
        "analysis/macro-context",
        "analysis/verdict-synthesis",
    ],
    "Crypto": [
        "analysis/quality-gate",
        "analysis/crypto-valuation",
        "analysis/crypto-technical",
        "analysis/crypto-onchain-analysis",
        "analysis/crypto-sentiment",
        "analysis/macro-context",
        "analysis/verdict-synthesis",
    ],
}

ORCHESTRATORS = {t: f"orchestrator/{t}" for t in REPORT_TYPES}

# Substrings each orchestrator body must still name, so its wiring reflects
# the same contract (a skill that stopped being referenced breaks quickly).
DEEP_MARKET_ANCHORS_MENTION = {
    "US": ["us-technical", "us-sentiment", "us-macro"],
    "Bursa": ["bursa-valuation", "bursa-technical", "bursa-sentiment"],
    "Crypto": [
        "crypto-valuation",
        "crypto-technical",
        "crypto-onchain",
        "crypto-sentiment",
    ],
}


class TestSkillContract(unittest.TestCase):
    def test_resolver_respects_env(self):
        """The path resolver returns repo-relative paths from `.env`."""
        resolved = resolve_isk_paths()
        assert resolved["ok"] is True
        # `.env` sets ISK_ROOT=src / ISK_NOTES=./.notes, so the resolved
        # absolute paths must point inside this repo (never `~/notes`).
        assert resolved["isk_root"] == os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
        )
        assert resolved["isk_notes"].endswith(".notes")
        assert resolved["isk_cache"].endswith(".cache")

    def test_orchestrators_have_skil_md(self):
        for _, rel in ORCHESTRATORS.items():
            assert skill_md_exists(*rel.split("/")), f"missing {rel}/SKILL.md"

    def test_market_contract_used_everywhere(self):
        assert set(MARKETS) == {"US", "Bursa", "Crypto"}
        assert set(REPORT_TYPES) == {"quick-look", "deep-research"}

    def test_quick_scripts_exist_for_every_market(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for market in MARKETS:
            for script in QUICK_SCRIPTS[market]:
                owner = SCRIPT_OWNER[script]
                assert skill_md_exists(*owner), f"{market}: {script} owner {owner}"
                path = os.path.join(root, "src", *owner, "scripts", script)
                assert os.path.isfile(path), f"missing {path}"

    def test_deep_data_skills_exist_for_every_market(self):
        for market in MARKETS:
            for rel in DEEP_DATA_SKILLS[market]:
                assert skill_md_exists(*rel.split("/")), f"{market}: {rel}"

    def test_deep_analysis_skills_exist_for_every_market(self):
        for market in MARKETS:
            for rel in DEEP_ANALYSIS_SKILLS[market]:
                assert skill_md_exists(*rel.split("/")), f"{market}: {rel}"

    def test_shared_analysis_skills_exist(self):
        for rel in ("analysis/verdict-synthesis", "analysis/macro-context",
                    "utility/report-writer", "utility/web-search",
                    "utility/cache-cleanup"):
            assert skill_md_exists(*rel.split("/")), rel

    def test_ticker_display_util_exists(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src", "utility", "shared-lib", "scripts", "ticker_display.py",
        )
        assert os.path.isfile(path), path

    def test_shared_rubric_and_math_exist(self):
        base = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src", "utility", "shared-lib",
        )
        assert os.path.isfile(os.path.join(base, "verdict_rubric.md"))
        assert os.path.isfile(
            os.path.join(base, "scripts", "verdict_math.py")
        )

    def test_orchestrators_still_mention_market_skills(self):
        for market in MARKETS:
            body = self._read_orchestrator_body("deep-research")
            for anchor in DEEP_MARKET_ANCHORS_MENTION[market]:
                assert anchor in body, f"deep-research missing `{anchor}`"
        # quick-look is market-agnostic in skill wiring (scripts only).

    def test_verdict_math_accepts_all_market_weight_names(self):
        body = self._read_orchestrator_body("quick-look")
        assert "verdict_math.py --market" in body

    def _read_orchestrator_body(self, name):
        with open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src", "orchestrator", name, "SKILL.md",
        ), encoding="utf-8") as fh:
            return fh.read()