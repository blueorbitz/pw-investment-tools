#!/usr/bin/env python3
"""Print the resolved Investment Skills Network paths as JSON.

The single source of truth for path resolution. Orchestrators and the report
writer run this FIRST and use its output verbatim for scratch and report
paths — never guess from the current environment or working directory.

Resolution rules (see yahoo_cache.load_workspace_env):
- ISK_NOTES / ISK_CACHE / ISK_ROOT: `.env` in the workspace root is the source
  of truth; relative values resolve against the workspace root.
- Other variables (API keys): real environment wins, `.env` is the fallback.
- Unset paths default to ~/notes and ~/.cache.

Usage:
    python isk_paths.py
"""

import json
import os
import sys

_ROOT = os.environ.get("ISK_ROOT")
if not _ROOT or not os.path.isabs(_ROOT):
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "utility", "shared-lib", "scripts"))

from yahoo_cache import isk_paths  # noqa: E402  (load_workspace_env runs at import)


def main():
    print(json.dumps({"ok": True, **isk_paths()}, indent=2))


if __name__ == "__main__":
    main()
