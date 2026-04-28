# 輝煌 3D 佛堂供佛空間 V2

這個專案是一個可在本機、區網或靜態網站上展示的 Three.js 3D 佛堂。前台負責展示主佛、左右供佛牆、供品、八吉祥與供養人名牌；後台 `admin.html` 可管理左右佛龕的供養人資料。

## 快速啟動

在 Windows PowerShell 執行：

```powershell
cd D:\buddha_hall_3d_v2
python tools\serve_lan.py
```

前台：

```text
http://localhost:8080/
```

後台：

```text
http://localhost:8080/admin.html
```

健康檢查：

```text
http://localhost:8080/api/health
```

供養資料 API：

```text
http://localhost:8080/api/shrine-offerings
```

如果 8080 被占用，改用 8081：

```powershell
$env:PORT="8081"
python tools\serve_lan.py
```

## 同網域 / 區網存取

`serve_lan.py` 啟動時會列出本機與區網網址，例如：

```text
http://localhost:8080/
http://192.168.1.150:8080/
http://192.168.1.150:8080/admin.html
```

同一個 Wi-Fi 或同一個區網內的設備，可以用列出的區網 IP 開啟前台與後台。

Windows 防火牆可能會詢問是否允許 Python 存取私人網路。若要讓手機、平板或其他電腦連入，請允許 Python 在私人網路通訊。此服務只建議用於本機或內網，不要直接暴露到公網。

## 前台操作

- 左鍵拖曳：環視佛堂
- 滾輪：遠近
- 右鍵拖曳：平移
- W / A / S / D 或方向鍵：在佛堂中移動
- R：回到全景
- 右側「主尊」面板：切換主尊
- 右側「供養」面板：加入供品與八吉祥

目前保留的主尊切換：

- 釋迦牟尼佛
- 阿彌陀佛
- 藥師佛
- 蓮花生大士

前台也保留 JavaScript API：

```js
setMainDeity("阿彌陀佛")
updateSponsorName("left-zone-01-row-01-col-01", "王先生供養")
exportShrineOfferings()
importShrineOfferings(data)
applyShrineOfferings(data)
```

## 後台使用

打開：

```text
http://localhost:8080/admin.html
```

後台可管理左右佛龕 180 格供養資料：

- 搜尋姓名、佛像、區域、左右側
- 編輯供養人姓名
- 編輯祈願文字
- 編輯起始日、到期日
- 儲存全部
- 重新載入
- 匯出 JSON
- 匯入 JSON
- 重設為「善信供養」
- 回到佛堂

後台儲存後，重新整理前台即可看到更新後的供養人姓名名牌。

## 後台資料

後台資料 JSON：

```text
assets\data\shrine_offerings.json
```

每次透過 API 寫入前，會先備份到：

```text
assets\data\backups\
```

API 路徑：

```text
GET  /api/health
GET  /api/shrine-offerings
POST /api/shrine-offerings
PUT  /api/shrine-offerings/{id}
```

API 只允許寫入固定資料檔 `assets\data\shrine_offerings.json`，不接受使用者指定檔案路徑。

## 匯入 / 匯出供養名單 JSON

在 `admin.html`：

1. 按「匯出 JSON」可下載目前供養名單。
2. 按「匯入 JSON」可選擇先前匯出的檔案。
3. 匯入後按「儲存全部」寫回後端。

若 API 不可用，後台會自動使用瀏覽器 `localStorage`，並顯示靜態模式提示。

## GitHub Pages 靜態展示限制

本專案可放到 GitHub Pages 作為靜態展示：

- `index.html` 可展示 3D 佛堂。
- `admin.html` 可開啟。
- 主佛、供品、八吉祥、左右佛龕與主尊切換可使用。

但 GitHub Pages 不能執行 Python 後端，也不能把供養資料寫回伺服器檔案。因此在 GitHub Pages 上：

- 後台只能使用本機瀏覽器 `localStorage`。
- 可匯入 / 匯出 JSON。
- 不同設備或不同使用者不會自動共享資料。

若要多設備共享供養人姓名，需要使用 `python tools\serve_lan.py` 或其他後端服務。

## 更新圖片資產

佛像圖片：

```text
assets/images/deities/
```

供品圖片：

```text
assets/images/offerings/
```

八吉祥圖片：

```text
assets/images/symbols/
```

資產要求：

- PNG
- 有 alpha channel
- 長邊至少 1024 px

更新圖片後執行：

```powershell
cd D:\buddha_hall_3d_v2
C:\Users\biung\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe tools\check_assets.py
```

報告輸出：

```text
assets\asset_report.json
```

## 恢復備份

供養資料 API 每次寫入前會備份 JSON 到：

```text
assets\data\backups\
```

要恢復某次供養名單：

1. 停止 `serve_lan.py`。
2. 從 `assets\data\backups\` 找到要恢復的 `shrine_offerings_YYYYMMDD_HHMMSS.json`。
3. 複製並覆蓋：

```text
assets\data\shrine_offerings.json
```

4. 重新啟動：

```powershell
python tools\serve_lan.py
```

如果要恢復整個專案檔案，請使用先前建立的 `D:\buddha_hall_3d_v2_backups\...` 備份資料夾，手動複製對應檔案回專案。
