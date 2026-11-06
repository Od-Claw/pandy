import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

SPEC = importlib.util.spec_from_file_location('recovery_updater', Path(__file__).resolve().parents[1] / 'scripts/update_stock_reports.py')
U = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(U)


class QuoteRecoveryTests(unittest.TestCase):
    def test_partial_batches_retry_only_missing_and_keep_first_success(self):
        calls = []
        def fetch(url, params):
            calls.append(params['ex_ch'])
            if len(calls) == 1:
                return {'msgArray': [{'c': '1111', 'z': '10', 'ex': 'tse'}]}
            if len(calls) == 2:
                raise requests.Timeout('temporary')
            return {'msgArray': [{'c': '2222', 'z': '-', 'trade': {'z': '273.5'}, 'y': '298', 'ex': 'tse'}]}
        with patch.object(U, 'request_json', side_effect=fetch), patch.object(U.time, 'sleep'):
            prices = U.twse_quotes({'1111', '2222'})
        self.assertEqual(prices, {'1111': 10, '2222': 273.5})
        self.assertTrue(all('1111' not in call for call in calls[1:]))

    def test_persistent_missing_is_not_fabricated(self):
        with patch.object(U, 'request_json', return_value={'msgArray': []}) as fetch, patch.object(U.time, 'sleep'):
            self.assertEqual(U.twse_quotes({'1111'}), {})
        self.assertEqual(fetch.call_count, 6)

    def test_network_timeout_and_invalid_json_recover(self):
        response = Mock(); response.json.side_effect = ValueError('broken JSON')
        success = Mock(); success.json.return_value = {'ok': 1}
        with patch.object(U.requests, 'get', side_effect=[requests.Timeout(), response, success]) as fetch, patch.object(U.time, 'sleep'):
            self.assertEqual(U.request_json('https://official.example/api'), {'ok': 1})
        self.assertEqual(fetch.call_count, 3)

    def test_permanent_403_does_not_retry(self):
        response = Mock(status_code=403)
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
        with patch.object(U.requests, 'get', return_value=response) as fetch, patch.object(U.time, 'sleep'):
            with self.assertRaises(requests.HTTPError):
                U.request_json('https://official.example/api')
        self.assertEqual(fetch.call_count, 1)

    def test_unknown_code_wrong_market_and_non_finite_are_ignored(self):
        payload = {'msgArray': [{'c': '9999', 'z': '1'}, {'c': '1111', 'z': 'nan'}, {'c': '1111', 'z': '42', 'ex': 'wrong'}]}
        with patch.object(U, 'request_json', return_value=payload), patch.object(U.time, 'sleep'):
            self.assertEqual(U.twse_quotes({'1111'}), {})

    def test_snapshot_reuses_validated_quotes_and_rejects_changed_source(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'snapshot.json'
            watchlists = {'pandy': [{'code': '3023', 'name': '信邦'}], 'stock': []}
            rows = [['3023', '信邦']]
            U.save_quote_snapshot(path, watchlists, rows, {'3023': 273.5})
            self.assertEqual(U.load_quote_snapshot(path, watchlists, rows), {'3023': 273.5})
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                U.load_quote_snapshot(path, {'pandy': [], 'stock': []}, rows)
            data = json.loads(path.read_text())
            data['created_at'] = (dt.datetime.now(U.TAIPEI) - dt.timedelta(minutes=11)).isoformat()
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'expired'):
                U.load_quote_snapshot(path, watchlists, rows)

    def test_dry_run_and_generation_use_one_identical_quote_fetch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'data').mkdir()
            watchlists = json.loads((U.ROOT / 'data/stock_watchlists.json').read_text(encoding='utf-8'))
            (root / 'data/stock_watchlists.json').write_text(json.dumps(watchlists), encoding='utf-8')
            prof = (U.ROOT / 'prof_data.html').read_text(encoding='utf-8')
            (root / 'prof_data.html').write_text(prof, encoding='utf-8')
            quotes = {entry['code']: 10.0 for entries in watchlists.values() for entry in entries if entry.get('code')}
            quotes.update({'symbol:'+entry['symbol']: 10.0 for entries in watchlists.values() for entry in entries if entry.get('symbol')})
            quotes.update({row[0]: 10.0 for row in U.table_rows(prof)})
            argv = ['update', '--root', str(root), '--quote-snapshot', str(root / 'snapshot.json')]
            with patch.object(U, 'quote_map', return_value=quotes) as fetch:
                with patch.object(U.sys, 'argv', argv+['--dry-run']):
                    self.assertEqual(U.main(), 0)
                with patch.object(U.sys, 'argv', argv):
                    self.assertEqual(U.main(), 0)
            self.assertEqual(fetch.call_count, 1)
            self.assertEqual(json.loads((root/'data/stock_watchlists.json').read_text())['stock'], watchlists['stock'])


if __name__ == '__main__':
    unittest.main()
