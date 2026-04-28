# Project Status

## 完成狀態

`D:\buddha_hall_3d_v2` 目前已完成可運行的 3D 佛堂前台、供養人名牌後台、LAN JSON API、資產檢查報告與靜態模式 fallback。

## 前台功能

- Three.js 3D 佛堂場景。
- 高清 PNG 主佛。
- 主尊切換：釋迦牟尼佛、阿彌陀佛、藥師佛、蓮花生大士。
- 主供桌與供品：供燈、供香、供水、供花、供果、食子、曼扎。
- 八吉祥圖像供養。
- 左右供佛牆共 180 格：每側 3 排 x 30 欄。
- 每尊小佛像下方有 sponsorName 名牌。
- 前台 API：
  - `setMainDeity(deityName)`
  - `updateSponsorName(id, sponsorName)`
  - `applyShrineOfferings(data)`
  - `exportShrineOfferings()`
  - `importShrineOfferings(data)`
- 後端資料優先讀取 `/api/shrine-offerings`；API 不可用時 fallback 到 `localStorage`。

## 後台功能

- `admin.html` 管理左右佛龕供養資料。
- 顯示 ID、側邊、區域、佛像、位置、供養人姓名、祈願文字、起始日、到期日。
- 搜尋姓名、佛像、區域、左右側。
- 編輯 `sponsorName`、`wishText`、`startDate`、`endDate`。
- 儲存全部。
- 重新載入。
- 匯出 JSON。
- 匯入 JSON。
- 重設為「善信供養」。
- API 不可用時使用 `localStorage`。
- 提供回到佛堂連結。

## API 功能

由 `tools/serve_lan.py` 提供：

- `GET /api/health`
- `GET /api/shrine-offerings`
- `POST /api/shrine-offerings`
- `PUT /api/shrine-offerings/{id}`

資料檔：

```text
assets\data\shrine_offerings.json
```

備份：

```text
assets\data\backups\
```

安全邊界：

- 只寫入固定 JSON 檔。
- 不接受任意路徑。
- JSON body 限制 2 MB。
- 適合本機 / 區網使用，不建議暴露到公網。

## 資產清單

資產檢查報告：

```text
assets\asset_report.json
```

目前檢查通過：

- 佛像圖片：10 / 10
- 供品圖片：7 / 7
- 八吉祥圖片：8 / 8
- 全部為 PNG。
- 全部含 alpha channel。
- 全部長邊 >= 1024 px。

## 已知限制

- GitHub Pages 無法執行 Python 後端，因此不能跨設備共享或寫回 server JSON。
- 靜態模式資料只存在使用者瀏覽器 `localStorage`。
- `serve_lan.py` 是輕量內網工具，不是正式公開網站後端。
- 若要長期多人維護，建議改用正式後端、帳號權限與資料庫。

## GitHub Pages 注意事項

可直接展示：

- 3D 佛堂前台。
- 主佛、供品、八吉祥。
- 左右佛龕與主尊切換。
- 後台頁面本身。

限制：

- 後台只能 localStorage。
- 匯入 / 匯出 JSON 需手動操作。
- 不同設備不會自動同步資料。

## 下一步建議

- 加入登入與權限控管。
- 將 JSON 儲存升級為 SQLite 或雲端資料庫。
- 為每格佛龕加入詳細供養紀錄頁。
- 加入到期提醒與續供管理。
- 將前端打包成正式部署流程。
- 增加手機版後台表格操作優化。
