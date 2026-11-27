""" Validate every route file against the shared schema, headlessly.

The editor gives live diagnostics; this gives the same contract CI gate 
so the rules hold for anyone who never opens VS Code.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

ROOT =  Path(__file__).parent
SCHEMA = json.loads((ROOT / "schemas/route.schema.json").read_text(encoding="utf-8"))
COMMON = json.loads((ROOT / "schemas/common.schema.json").read_text(encoding="utf-8"))

def validator() -> Draft202012Validator: 
        store = {SCHEMA["$id"]: SCHEMA, COMMON["$id"]: COMMON, "common.schema.json": COMMON}
        resolver = RefResolver(base_uri=SCHEMA["$id"], referrer=SCHEMA, store=store)
        return Draft202012Validator(SCHEMA, resolver=resolver)

def main() -> int: 
    check = validator()
    failures = 0

    for path in sorted((ROOT / "routes").glob("*.json")): 
        document = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(check.iter_errors(document), key=lambda e: list(e.path))
        if not errors: 
             print(f"{path.relative_to(ROOT)}: ok")
             continue
        failures += 1
        for error in errors: 
            where = "/".join(str(p) for p in error.path) or "(root)"
            print (f"{path.relative_to(ROOT)}: {where}: {error.message}")

    print(f"\n{failures} route file(s) failed validation")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())