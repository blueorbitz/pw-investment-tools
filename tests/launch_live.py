"""Spawn a live headless regression case as a detached process and return.

Usage:  python tests/launch_live.py <report_type,market>

The child (run_live.py) writes its unittest output to
`tests/_live/<report_type>_<market>.log` and keeps running after this
launcher exits, so it is safe to call from a sandbox that would otherwise
kill long-running foreground/background commands. Check completion with
`tasklist /FI "PID eq <pid>"` or `Wait-Process`, and read the log for the
result.

Exit code: 0 when spawned, 1 on error.
"""

import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python tests/launch_live.py <report_type,market>", file=sys.stderr)
        return 2
    case = sys.argv[1].replace("/", "_")
    tag = case.replace(",", "_")
    log_dir = os.path.join(_HERE, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log = os.path.join(log_dir, f"{tag}.log")
    env = dict(os.environ)
    env["ISK_LIVE"] = "1"
    # run_live.py forces ISK_LIVE itself; this is belt-and-braces.
    with open(log, "w", encoding="utf-8") as fh:
        proc = subprocess.Popen(
            [sys.executable, "-u", os.path.join(_HERE, "run_live.py"), case],
            cwd=_REPO,
            env=env,
            stdout=fh,
            stderr=subprocess.STDOUT,
        )
    print(proc.pid)
    print(f"log: {log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())