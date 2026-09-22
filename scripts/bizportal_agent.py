"""Launch one FAOS BizPortal workflow in a visible controlled browser."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Running a file from scripts/ makes that directory sys.path[0]. Add the
# repository root explicitly so the local ai_agent package is importable on
# Windows and other platforms without requiring PYTHONPATH configuration.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ai_agent.automation.bizportal import run_workflow


def main() -> int:
    parser = argparse.ArgumentParser(description="FAOS BizPortal browser assistant")
    parser.add_argument("--workflow-id", type=int, required=True)
    args = parser.parse_args()
    return run_workflow(args.workflow_id)


if __name__ == "__main__":
    raise SystemExit(main())
