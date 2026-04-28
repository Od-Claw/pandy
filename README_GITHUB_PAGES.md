# GitHub Pages 靜態版 3D 佛堂

這是可上傳到 GitHub Pages 的靜態版 3D 佛堂。它不依賴 Python API，也不依賴 `serve_lan.py`。

## 重要：不要直接雙擊 HTML

不建議用 `file://` 直接開啟 `index.html` 或 `admin.html`。瀏覽器在 `file://` 模式下會限制 ES module、`fetch()`、JSON、貼圖與音樂 manifest 載入，可能造成佛像、佛樂或供養資料顯示不完整。

正確本機預覽方式：

```powershell
cd D:\buddha_hall_3d_github
python -m http.server 8090
```

然後打開：

```text
http://localhost:8090
```

也可以直接雙擊：

```text
start_local_server.bat
```

批次檔會在目前資料夾啟動 `http://localhost:8090`，再用瀏覽器打開即可。

上傳 GitHub Pages 後會使用 `https://`，所以圖片、音樂、JSON 載入會正常。

## 上傳 GitHub Pages

1. 建立 GitHub repo。
2. 將 `D:\buddha_hall_3d_github` 裡的內容放到 repo。
3. 到 GitHub repo 的 Settings → Pages。
4. Source 選 `main` branch / root。
5. 等 GitHub Pages 部署完成。

專案內已有 `.nojekyll`，可避免 GitHub Pages 使用 Jekyll 處理靜態資源。

## 注意事項

- GitHub Pages 是靜態網站。
- 佛堂前台可正常展示。
- 佛樂可播放，但瀏覽器需要使用者按「播放」後才允許播放。
- `admin.html` 只能使用 `localStorage`、匯入 JSON、匯出 JSON。
- GitHub Pages 無法直接把供養人資料寫回 repo 或伺服器檔案。
- 若要多人共享供養名單，需要正式後端或資料庫。

## 佛樂

佛樂位於：

```text
assets/audio/buddha-music/
```

曲目清單：

```text
assets/audio/buddha-music/music_manifest.json
```

替換佛樂時：

1. 將音樂檔放到 `assets/audio/buddha-music/`。
2. 建議使用安全檔名，例如 `music-01.mp3`。
3. 更新 `music_manifest.json`。

支援格式取決於瀏覽器，建議優先使用 `.mp3` 或 `.m4a`。大型音檔在 GitHub Pages 載入會比較慢。

## 圖片資產

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

圖片建議：

- PNG
- 有 alpha channel
- 長邊至少 1024 px

## 主尊切換

前台右側「主尊」面板可切換：

- 釋迦牟尼佛
- 阿彌陀佛
- 藥師佛
- 蓮花生大士

也可在 console 使用：

```js
setMainDeity("阿彌陀佛")
```

## 供養名單

靜態預設資料：

```text
assets/data/shrine_offerings.json
```

GitHub Pages 無法寫回此檔案。後台儲存只會存到目前瀏覽器的 `localStorage`。

匯入供養名單：

1. 打開 `admin.html`。
2. 按「匯入 JSON」。
3. 選擇供養名單 JSON。
4. 按「儲存全部」存入本瀏覽器 `localStorage`。

匯出供養名單：

1. 打開 `admin.html`。
2. 按「匯出 JSON」。
3. 保存下載的 `shrine_offerings.json`。

前台會優先讀取 `assets/data/shrine_offerings.json`，再套用 localStorage 中的更新。
