from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pandy_updater", ROOT / "scripts" / "update_stock_reports.py")
UPDATER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(UPDATER)


class PandoraboxExchangeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write_export(self, items):
        path = self.root / "exchange.json"
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "target": "pandorabox",
                    "source_board": "Pandorabox",
                    "items": items,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return path

    def test_valid_exchange_preserves_order_duplicates_and_status(self):
        path = self.write_export(
            [
                {"position": 1, "code": "1111", "name": "甲", "enabled": True, "visibility_scope": "shared"},
                {"position": 2, "code": "1111", "name": "甲別名", "enabled": True, "visibility_scope": "shared"},
                {"position": 3, "code": "2809", "name": "京城銀", "enabled": False, "status": "已終止上市", "visibility_scope": "shared"},
            ]
        )
        rows = UPDATER.load_pandorabox_export(path)
        self.assertEqual([row["name"] for row in rows], ["甲", "甲別名", "京城銀"])
        self.assertEqual([row["code"] for row in rows], ["1111", "1111", "2809"])
        self.assertEqual(rows[-1]["status"], "已終止上市")

    def test_private_or_corrupt_exchange_is_rejected(self):
        private = self.write_export(
            [{"position": 1, "code": "2222", "name": "私人", "enabled": True, "visibility_scope": "private"}]
        )
        with self.assertRaisesRegex(ValueError, "non-public"):
            UPDATER.load_pandorabox_export(private)
        private.write_text("{broken", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid"):
            UPDATER.load_pandorabox_export(private)

    def test_atomic_watchlist_sync_changes_only_pandy_section(self):
        target = self.root / "stock_watchlists.json"
        payload = {"pandy": [{"name": "舊", "code": "0000"}], "stock": [{"name": "保留", "code": "9999"}]}
        UPDATER.write_watchlists_atomic(target, {**payload, "pandy": [{"name": "新", "code": "1111"}]})
        saved = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(saved["pandy"], [{"name": "新", "code": "1111"}])
        self.assertEqual(saved["stock"], payload["stock"])


if __name__ == "__main__":
    unittest.main()
