#!/usr/bin/env python3
"""Regenerate the three Od-Claw/pandy stock reports from verified watchlists."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import time
import urllib.parse
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
TAIPEI = dt.timezone(dt.timedelta(hours=8))
TWSE_URL = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; OdClawStockUpdater/1.0)",
    "Referer": "https://mis.twse.com.tw/stock/fibest.jsp?lang=zh_tw",
}


def text_of(value: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(value)).strip()


def table_rows(page: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.I | re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.I | re.S)
        if cells:
            rows.append([text_of(cell) for cell in cells])
    return rows


def as_float(value: str) -> float | None:
    try:
        return float(value.replace(",", "").replace("%", "").strip())
    except (AttributeError, ValueError):
        return None


def price_text(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def request_json(url: str, params: dict[str, str]) -> dict:
    response = requests.get(url, params=params, headers=HEADERS, timeout=25)
    response.raise_for_status()
    return response.json()


def twse_quotes(codes: set[str]) -> dict[str, float]:
    """Fetch listed/OTC prices in batches and use the previous close off-market."""
    quotes: dict[str, float] = {}
    ordered = sorted(code for code in codes if code)
    for market in ("tse", "otc"):
        for start in range(0, len(ordered), 40):
            batch = ordered[start : start + 40]
            channels = "|".join(f"{market}_{code}.tw" for code in batch)
            try:
                payload = request_json(TWSE_URL, {"ex_ch": channels, "json": "1", "delay": "0"})
            except Exception:
                continue
            for item in payload.get("msgArray", []):
                code = str(item.get("c") or "").strip()
                if not code or code in quotes:
                    continue
                quote = as_float(str(item.get("z") or ""))
                if quote is None:
                    quote = as_float(str(item.get("y") or ""))
                if quote is not None:
                    quotes[code] = quote
            time.sleep(0.25)
    return quotes


def yahoo_chart_price(symbol: str) -> float | None:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol, safe='^')}"
    try:
        payload = request_json(url, {"range": "1d", "interval": "1d"})
        result = payload["chart"]["result"][0]
        quote = as_float(str(result.get("meta", {}).get("regularMarketPrice") or ""))
        if quote is not None:
            return quote
        closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
        return next((float(value) for value in reversed(closes) if value is not None), None)
    except Exception:
        return None


def load_watchlists(path: Path) -> dict[str, list[dict[str, str]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("pandy"), list) or not isinstance(data.get("stock"), list):
        raise ValueError("watchlists.json must include pandy and stock lists")
    return data


def quote_map(watchlists: dict[str, list[dict[str, str]]], prof_rows: list[list[str]]) -> dict[str, float]:
    codes = {entry.get("code", "") for group in watchlists.values() for entry in group}
    codes.update(row[0] for row in prof_rows if row)
    quotes = twse_quotes(codes)
    for group in watchlists.values():
        for entry in group:
            symbol = entry.get("symbol")
            if symbol:
                value = yahoo_chart_price(symbol)
                if value is not None:
                    quotes[f"symbol:{symbol}"] = value
                    code = entry.get("code", "")
                    if code:
                        quotes[code] = value
    return quotes


def page_shell(title: str, timestamp: str, count: int, unavailable: int, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang=\"zh-TW\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{html.escape(title)}</title><style>
:root{{--bg:#f5f7fa;--panel:#fff;--text:#1f2937;--muted:#64748b;--border:#d7dee8;--accent:#1f7a4f;--soft:#e9f6ef;--danger:#c2410c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:Arial,\"Microsoft JhengHei\",sans-serif}}main{{width:min(1120px,calc(100% - 32px));margin:28px auto}}header{{display:flex;align-items:end;justify-content:space-between;gap:16px;margin-bottom:16px}}h1{{margin:0 0 6px;font-size:clamp(24px,3vw,34px)}}.meta{{color:var(--muted);font-size:14px}}.summary{{display:flex;gap:8px;flex-wrap:wrap}}.badge{{border:1px solid var(--border);border-radius:6px;background:var(--panel);padding:7px 10px;font-size:14px}}.wrap{{overflow-x:auto;border-radius:8px;box-shadow:0 8px 24px rgba(15,23,42,.08)}}table{{width:100%;border-collapse:collapse;background:var(--panel)}}th,td{{padding:10px 12px;border-bottom:1px solid var(--border);text-align:left;white-space:nowrap}}th{{position:sticky;top:0;background:var(--accent);color:#fff}}tbody tr:nth-child(even){{background:#fbfcfd}}tbody tr:hover{{background:var(--soft)}}.price,.number{{text-align:right;font-variant-numeric:tabular-nums}}.price{{font-weight:700}}.no-price{{color:var(--danger);font-weight:700}}.positive{{color:#b91c1c;font-weight:700}}.negative{{color:#047857;font-weight:700}}@media(max-width:720px){{header{{display:block}}.summary{{margin-top:10px}}th,td{{padding:9px 10px}}}}
</style></head><body><main><header><div><h1>{html.escape(title)}</h1><div class=\"meta\">更新時間：{timestamp} ｜ 資料來源：TWSE MIS（Yahoo 指數備援）</div></div><div class=\"summary\"><div class=\"badge\">筆數：{count}</div><div class=\"badge\">未取得：{unavailable}</div></div></header><div class=\"wrap\"><table>{body}</table></div></main></body></html>\n"""


def render_quote_page(title: str, entries: list[dict[str, str]], quotes: dict[str, float], timestamp: str) -> str:
    rows: list[str] = []
    missing = 0
    for entry in entries:
        value = quotes.get(entry.get("code", ""))
        if entry.get("symbol"):
            value = quotes.get(f"symbol:{entry['symbol']}")
        name = html.escape(entry["name"])
        if value is None:
            missing += 1
            price = '<span class="no-price">-</span>'
        else:
            price = price_text(value)
        rows.append(f"<tr><td>{name}</td><td class=\"price\">{price}</td></tr>")
    body = "<thead><tr><th>名稱</th><th>股價</th></tr></thead><tbody>" + "\n".join(rows) + "</tbody>"
    return page_shell(title, timestamp, len(entries), missing, body)


def sortable_table_script() -> str:
    return """<script>
document.addEventListener("DOMContentLoaded", () => {
  const table = document.querySelector("table");
  if (!table || !table.tHead || !table.tBodies.length) return;

  const style = document.createElement("style");
  style.textContent = "th.sortable{cursor:pointer;user-select:none}th.sortable:hover,th.sortable:focus{background:#17633f;outline:2px solid #0f5132;outline-offset:-2px}th.sortable[data-sort='asc']::after{content:' ▲'}th.sortable[data-sort='desc']::after{content:' ▼'}";
  document.head.appendChild(style);

  const headers = Array.from(table.tHead.rows[0].cells);
  let sortedColumn = -1;
  let ascending = true;
  const compareValues = (left, right) => {
    const leftNumber = Number.parseFloat(left.replace(/[% ,]/g, ""));
    const rightNumber = Number.parseFloat(right.replace(/[% ,]/g, ""));
    if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber)) return leftNumber - rightNumber;
    if (!Number.isNaN(leftNumber)) return -1;
    if (!Number.isNaN(rightNumber)) return 1;
    return left.localeCompare(right, "zh-Hant", { numeric: true });
  };
  const sortBy = (index) => {
    ascending = sortedColumn === index ? !ascending : true;
    sortedColumn = index;
    const rows = Array.from(table.tBodies[0].rows);
    rows.sort((a, b) => {
      const result = compareValues(a.cells[index].innerText.trim(), b.cells[index].innerText.trim());
      return ascending ? result : -result;
    });
    rows.forEach((row) => table.tBodies[0].appendChild(row));
    headers.forEach((header, headerIndex) => {
      const active = headerIndex === index;
      header.dataset.sort = active ? (ascending ? "asc" : "desc") : "";
      header.setAttribute("aria-sort", active ? (ascending ? "ascending" : "descending") : "none");
    });
  };
  headers.forEach((header, index) => {
    header.classList.add("sortable");
    header.tabIndex = 0;
    header.setAttribute("role", "button");
    header.setAttribute("aria-sort", "none");
    header.addEventListener("click", () => sortBy(index));
    header.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        sortBy(index);
      }
    });
  });
});
</script>"""


def render_prof_page(rows: list[list[str]], quotes: dict[str, float], timestamp: str) -> str:
    rendered: list[str] = []
    for row in rows:
        if len(row) < 9:
            continue
        code, name, _old_price, dividend, _yield, holding, dec_price, _performance, ex_rights = row[:9]
        price = quotes.get(code)
        dividend_number = as_float(dividend)
        dec_number = as_float(dec_price)
        yield_value = dividend_number / price * 100 if dividend_number is not None and price else None
        performance = (price / dec_number - 1) * 100 if price is not None and dec_number else None
        performance_class = "positive" if performance is not None and performance >= 0 else "negative"
        values = [
            code, name, price_text(price), dividend, "-" if yield_value is None else f"{yield_value:.2f}%",
            holding, dec_price, "-" if performance is None else f"{performance:.2f}%", ex_rights,
        ]
        cells = []
        for index, value in enumerate(values):
            cls = "number" if index in (2, 3, 4, 5, 6, 7) else ""
            if index == 7 and performance is not None:
                cls = f"number {performance_class}"
            cells.append(f"<td class=\"{cls}\">{html.escape(value)}</td>")
        rendered.append("<tr>" + "".join(cells) + "</tr>")
    header = "<thead><tr><th>股號</th><th>股票名稱</th><th>現價</th><th>預估股利</th><th>預估殖利率</th><th>應持有比例</th><th>12月31日股價</th><th>今年績效</th><th>除權息</th></tr></thead>"
    body = header + sortable_table_script() + "<tbody>" + "\n".join(rendered) + "</tbody>"
    return page_shell("殖利率資料", timestamp, len(rendered), sum("-" in item for item in rendered), body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update the three Od-Claw/pandy stock reports.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root containing the three HTML files")
    parser.add_argument("--watchlists", type=Path, default=None, help="Path to stock_watchlists.json")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and render without writing files")
    args = parser.parse_args()
    root = args.root.resolve()
    watchlists_path = args.watchlists or root / "data" / "stock_watchlists.json"
    prof_path = root / "prof_data.html"
    prof_rows = table_rows(prof_path.read_text(encoding="utf-8"))
    watchlists = load_watchlists(watchlists_path)
    quotes = quote_map(watchlists, prof_rows)
    timestamp = dt.datetime.now(TAIPEI).strftime("%Y-%m-%d %H:%M:%S")
    pages = {
        "pandy_data.html": render_quote_page("Pandorabox 股票股價更新", watchlists["pandy"], quotes, timestamp),
        "stock_data.html": render_quote_page("股票股價更新", watchlists["stock"], quotes, timestamp),
        "prof_data.html": render_prof_page(prof_rows, quotes, timestamp),
    }
    if not args.dry_run:
        for filename, content in pages.items():
            (root / filename).write_text(content, encoding="utf-8", newline="\n")
    print(json.dumps({"updated_at": timestamp, "quotes": len(quotes), "files": list(pages), "dry_run": args.dry_run}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
