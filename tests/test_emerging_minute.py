import datetime as dt
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('minute_updater',Path(__file__).resolve().parents[1]/'scripts/update_stock_reports.py')
U=importlib.util.module_from_spec(spec);spec.loader.exec_module(U)

class MinuteTests(unittest.TestCase):
    def payload(self, **kw):
        t={'date':'115年11月09日 11:31:03','fields':['代號','名稱','成交','成交量','報買價'],
           'data':[['6035','悠遊卡','50.10','56','47.75']]}
        t.update(kw)
        return {'stat':'ok','tables':[t]}
    def test_minute_price_not_yesterday(self):
        now=dt.datetime(2026,11,9,11,40,tzinfo=U.TAIPEI)
        self.assertEqual(U.parse_tpex_live_quotes(self.payload(),{'6035'},now=now),{'6035':50.1})
        self.assertEqual(U.parse_tpex_live_quotes(self.payload(date='115年11月10日 11:31:03'),{'6035'},now=now),{})
    def test_no_trade_unknown_and_invalid_are_not_prices(self):
        for row in [['6035','悠遊卡','-','56','99'],['6035','悠遊卡','50','0','99'],['9999','其他','50','56','99']]:
            self.assertEqual(U.parse_tpex_live_quotes(self.payload(data=[row]),{'6035'},now=dt.datetime(2026,11,9,12,tzinfo=U.TAIPEI)),{})
    def test_old_daily_does_not_override_minute(self):
        with patch.object(U,'request_json',side_effect=[self.payload(),[{'Date':'1151106','SecuritiesCompanyCode':'6035','LatestPrice':'47.75'}]]),patch.object(U,'parse_tpex_live_quotes',return_value={'6035':50.1}):
            self.assertEqual(U.tpex_esb_quotes({'6035'}),{'6035':50.1})
    def test_source_failure_uses_dated_fallback_not_previous_average(self):
        with patch.object(U,'request_json',side_effect=[RuntimeError(),[{'Date':'1151106','SecuritiesCompanyCode':'6035','LatestPrice':'47.75'}]]):
            self.assertEqual(U.tpex_esb_quotes({'6035'}),{'6035':47.75})
        with patch.object(U,'request_json',side_effect=[RuntimeError(),[{'Date':'1151106','SecuritiesCompanyCode':'6035','PreviousAveragePrice':'48'}]]):
            self.assertEqual(U.tpex_esb_quotes({'6035'}),{})
