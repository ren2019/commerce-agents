"""Validate and import private retail packages without writing customer data to Git."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

from retail.api.dataset import import_dataset, load_dataset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "import"])
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    try:
        dataset = (import_dataset if args.command == "import" else load_dataset)(args.package)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {"dataset_id": dataset.manifest.dataset_id, "warnings": dataset.warnings},
            ensure_ascii=False,
        )
    )
    if args.command == "import":
        print("Imported successfully. Restart the retail API and refresh both pages to activate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
