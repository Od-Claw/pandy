import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('partial_updater', Path(__file__).resolve().parents[1] / 'scripts/update_stock_reports.py')
U = importlib.util.module_from_spec(spec)
spec.loader.exec_module(U)


class PartialPricesTests(unittest.TestCase):
    def setUp(self):
        self.entries = [{'code': '8999', 'name': '缺價'}, {'code': '2330', 'name': '台積電'}, {'code': '8999', 'name': '刻意重複'}]
        self.watch = {'pandy': self.entries, 'stock': self.entries}
        self.rows = [['8999', '缺價', '999', '2', '9', '0', '10', '1', '未公告']]

    def validate(self, quotes, **kwargs):
        with patch.dict(U.EXPECTED_COUNTS, stock=3, prof=1):
            U.validate_inputs_and_quotes(self.watch, self.rows, quotes, expected_pandy_count=3, **kwargs)

    def test_partial_allowed_and_diagnostics_preserve_duplicate_rows(self):
        self.validate({'2330': 100}, allow_missing_prices=True)
        missing = U.missing_quote_details(self.watch, self.rows, {'2330': 100})
        self.assertEqual(len(missing), 5)
        self.assertEqual([r['position'] for r in missing[:2]], [1, 3])

    def test_strict_mode_retained(self):
        with self.assertRaises(RuntimeError):
            self.validate({'2330': 100})

    def test_invalid_values_and_count_still_block(self):
        for price in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(RuntimeError):
                self.validate({'2330': price}, allow_missing_prices=True)
        self.watch['pandy'].append({'code': '1111', 'name': 'extra'})
        with self.assertRaises(RuntimeError):
            self.validate({}, allow_missing_prices=True)

    def test_render_dash_preserves_order_and_not_old_price(self):
        page = U.render_quote_page('test', self.entries, {'2330': 100}, '2026-11-13 13:50:00')
        self.assertEqual(U.table_rows(page), [['缺價', '-'], ['台積電', '100'], ['刻意重複', '-']])
        self.assertIn('未取得：2', page)
        prof = U.table_rows(U.render_prof_page(self.rows, {}, '2026-11-13 13:50:00'))[0]
        self.assertEqual((prof[2], prof[4], prof[7]), ('-', '-', '-'))

    def test_complete_outage_does_not_fabricate_prices(self):
        self.validate({}, allow_missing_prices=True)
        self.assertEqual(len(U.table_rows(U.render_quote_page('test', self.entries, {}, 'now'))), 3)
