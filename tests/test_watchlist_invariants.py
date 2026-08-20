from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_141_SHA256 = "be1684a4529f9f2e9ab5b2af3f246d5ac867c9b273b5c7ac33799b390efecb7d"


class PandoraboxWatchlistTests(unittest.TestCase):
    def test_original_rows_are_unchanged_and_6024_is_appended(self):
        payload = json.loads((ROOT / "data" / "stock_watchlists.json").read_text(encoding="utf-8"))
        rows = payload["pandy"]
        self.assertEqual(len(rows), 142)
        self.assertEqual(rows[-3], {"name": "沛亨", "code": "6291"})
        self.assertEqual(rows[-2], {"name": "樺漢", "code": "6414"})
        self.assertEqual(rows[-1], {"name": "群益期", "code": "6024"})
        original_bytes = json.dumps(
            rows[:141], ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(hashlib.sha256(original_bytes).hexdigest(), ORIGINAL_141_SHA256)

    def test_updater_expected_count_matches_watchlist(self):
        updater_path = ROOT / "scripts" / "update_stock_reports.py"
        namespace: dict[str, object] = {
            "__name__": "watchlist_updater_test",
            "__file__": str(updater_path),
        }
        exec(compile(updater_path.read_text(encoding="utf-8"), str(updater_path), "exec"), namespace)
        payload = json.loads((ROOT / "data" / "stock_watchlists.json").read_text(encoding="utf-8"))
        self.assertEqual(namespace["EXPECTED_COUNTS"]["pandy"], len(payload["pandy"]))


if __name__ == "__main__":
    unittest.main()
