from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
class PandoraboxWatchlistTests(unittest.TestCase):
    def test_pandorabox_rows_are_ordered_valid_and_duplicates_are_allowed(self):
        payload = json.loads((ROOT / "data" / "stock_watchlists.json").read_text(encoding="utf-8"))
        rows = payload["pandy"]
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertTrue(str(row.get("name") or "").strip())
            self.assertRegex(str(row.get("code") or ""), r"^[0-9A-Z]{2,12}$")
        # Repeated stocks are an intentional list feature; this test must not
        # deduplicate or sort the administrator-maintained sequence.
        self.assertGreater(len(rows), len({row["code"] for row in rows}))

    def test_updater_keeps_fixed_counts_only_for_the_other_reports(self):
        updater_path = ROOT / "scripts" / "update_stock_reports.py"
        namespace: dict[str, object] = {
            "__name__": "watchlist_updater_test",
            "__file__": str(updater_path),
        }
        exec(compile(updater_path.read_text(encoding="utf-8"), str(updater_path), "exec"), namespace)
        self.assertEqual(namespace["EXPECTED_COUNTS"]["stock"], 111)
        self.assertEqual(namespace["EXPECTED_COUNTS"]["prof"], 95)


if __name__ == "__main__":
    unittest.main()
