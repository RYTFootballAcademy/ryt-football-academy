"""Launch one FAOS BizPortal workflow in a visible controlled browser."""

from __future__ import annotations

import argparse
import sys

from ai_agent.automation.bizportal import run_workflow


def main() -> int:
    parser = argparse.ArgumentParser(description="FAOS BizPortal browser assistant")
    parser.add_argument("--workflow-id", type=int, required=True)
    args = parser.parse_args()
    return run_workflow(args.workflow_id)


if __name__ == "__main__":
    raise SystemExit(main())
