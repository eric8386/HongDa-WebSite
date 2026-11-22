# 給 Codex／其他 AI 工具的工作規則

這是「鴻達淨水工程企業社」官網（hongda-tw.com），純靜態網站，放在 GitHub Pages。
完整說明在 `CLAUDE.md`，動手前請先讀過。以下是最重要的規則。

## 回覆語言
- 一律使用**繁體中文**。

## 只改這些檔案
- 樣式：`assets/css/site.css`
- 互動：`assets/js/site.js`
- 版面結構、文字模板：`tools/build.py`（Python 3，只能用標準庫）
- 內容：`data/*.json`
- 圖片：`assets/` 底下

## 絕對不要手改（都是程式產生的，重新產生時會被整個覆蓋）
`index.html`、`about.html`、`contact.html`、`faq.html`、`finder.html`、`404.html`、`sitemap.xml`、`robots.txt`，
以及 `products/`、`services/`、`knowledge/`、`filters/`、`brands/` 整個資料夾。

## 修改後
1. 執行 `./scripts/bump-version.sh`：換新版本號並重新產生全站。
2. 用 `python3 -m http.server 8765 --bind 127.0.0.1` 開預覽，到 http://localhost:8765 檢查手機與電腦版。
3. **不要 `git commit`，也不要 `git push`**。改完留在工作區，交給 Claude 審查後再提交。
   （bump-version.sh 會執行 `git add -A`，這沒關係，只要不要 commit。）

## 內容規則
- 不能捏造：不要新增證照、施工案例、客戶評價、價格或規格數字。
- 保持 noindex：`data/site.json` 的 `indexable` 維持 `false`。
- 每個頁面都要保留 Cache-Control／Pragma／Expires 三個 no-cache meta（寫在 build.py 的 `page()`，新頁面也要走 `page()`）。
- 聯絡資訊不顯示傳真、不顯示服務地區、不顯示負責人姓名；大標題（H1）不要強調「台南」。
- 主要行動呼籲文字是「LINE 預約現場實地勘查」。不要加回「水質檢測」服務。
- 這個資料夾的檔案都會公開發布，不要放任何敏感資料。
- `.codex-attachments/` 不要加進 git。
