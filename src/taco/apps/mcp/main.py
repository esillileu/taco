from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from .runtime import run_mcp_loop


def main(
    argv: list[str] | None = None,
    cwd: Path | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
) -> int:
    parser = argparse.ArgumentParser(prog="taco-mcp")
    parser.add_argument("--config", default="taco.yaml", help="config file path")
    args = parser.parse_args(argv if argv is not None else [])

    return run_mcp_loop(
        root=cwd or Path.cwd(),
        config=str(args.config),
        stdin=stdin or sys.stdin,
        stdout=stdout or sys.stdout,
    )


if __name__ == "__main__":
    raise SystemExit(main())
