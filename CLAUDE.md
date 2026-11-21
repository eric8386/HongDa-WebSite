# 鴻達淨水工程企業社 官網（hongda-tw.com）

純靜態網站，放在 GitHub Pages（`CNAME` = hongda-tw.com，`.nojekyll`），沒有後台。所有更新都由 Claude 在這個資料夾裡完成。

## 回覆語言
- 所有對使用者的回覆、提問、摘要一律用**繁體中文**。

## 架構：資料 → 產生器 → 靜態 HTML
- `data/*.json` 是唯一的內容來源；`tools/build.py`（Python 3，只用標準庫）讀取後輸出全站 HTML。
- **不要手改產生出來的 HTML**：`index.html`、`about.html`、`contact.html`、`faq.html`、`finder.html`、`404.html`、`sitemap.xml`、`robots.txt`，以及 `products/`、`services/`、`knowledge/`、`filters/`、`brands/` 整個資料夾。build 時這些資料夾會先被整個刪掉再重建，手改的內容會消失。要改版面或文字模板，就改 `tools/build.py`。
- 手寫、會保留的檔案：`assets/css/site.css`、`assets/js/site.js`、`assets/img/favicon.svg`、圖片。

### data/
- `site.json`：公司資料、`contact`（電話、地址、`lineId`/`lineUrl`、`hours`）、`brands`（key/name/slug/site/desc）、`categories`（key/name/short/slug/desc/install/seoTitle/seoDesc，可有 `subs`）、`faqs`、`indexable` 開關等。
- `products.json`：所有商品，包含濾心。主要欄位：`id`（同時是頁面檔名 `/products/<id>.html`）、`brand`（對應 brands 的 key）、`cat`（`ro`/`combo`/`whole`/`softener`/`drink`/`filter`）、`sub`（例如全戶淨水的 `pre` 前置過濾、`full` 全戶濾淨）、`image`、`summary`、`points`、`specs`、`price`（沒有就顯示「洽詢」）、`priceNote`、`source`/`sourceText`（價格與規格出處）。
  - 機器與濾心互相連結：機器的 `filters` 列出濾心 id，濾心的 `fits` 列出適用機器 id。沒有對應濾心商品時，可以用 `filterInfo`（model/interval）只顯示文字。濾心的 `interval` 是建議更換週期。
- `services.json`：服務項目（slug、lead、pains、steps、pricing、faqKeys…）。
- `articles.json`：知識文章（slug、title、desc、date、cat、blocks、related，可有 updated、sources），分類固定為 build.py 裡的 `ART_CATS`。blocks 支援 `p`、`h2`、`ul`、`table`（["table", 表頭, 列, 說明]）。

### 圖片
- 商品主圖：`assets/catalog/`（官方圖放在 `official/`）。
- 縮圖：`assets/catalog/thumb/` 底下用相同路徑；有縮圖就用縮圖，沒有就用原圖。縮圖需要另外產生，build 不會自動做。
- 手機用介紹圖：`assets/catalog/m/detail/`（寬 828px），由 `python3 tools/make_mobile.py` 產生；新增或更換介紹圖後要先執行它，build 才會加上 srcset。
- 商品詳情圖：`assets/catalog/detail/<商品 id>/01.jpg…`，build 會自動做成圖庫。

## 每次修改的固定流程
1. 改 `data/` 或 `tools/build.py`（或 css/js）。
2. 執行 `./scripts/bump-version.sh`：寫入新版本號到 `version.json`、重新產生全站、`git add -A`。每次更新都必須換新版本號，右上角會顯示版本，舊頁面也會自動重新載入。
3. 在瀏覽器預覽檢查（`.claude/launch.json` 的 `site`，網址 http://localhost:8765）。
4. `git commit` 並 `git push` 到 origin main。用 SSH 帳號 eric8386，**沒有安裝 gh CLI**。

## 一定要遵守的規則
- **保持 noindex**：`data/site.json` 的 `indexable` 維持 `false`，等使用者明確說「全部完成、可以公開」才能改成 true（build 會一起處理 robots meta 和 robots.txt）。
- **不快取宣告**：每個頁面都要有 Cache-Control/Pragma/Expires 三個 no-cache meta（已寫在 `page()` 裡，新增頁面也要走 `page()`）。GitHub Pages 伺服器本身的快取不用處理，也不用跟使用者提。
- **不能捏造**：沒有證照、施工案例、客戶評價，就不要寫，也不要自己編。價格只放官方建議售價並註明出處；飛利浦在台灣沒有官方價格，機器和濾心都顯示「洽詢」。
- 聯絡資訊**不顯示傳真、不顯示服務地區**。主要的行動呼籲文字是「LINE 預約現場實地勘查」（不是「傳照片估價」）。
- 還沒有 LINE 連結時，LINE 按鈕會自動改連到 `/contact.html`；在 `site.json` 填入 `lineId`/`lineUrl` 就會生效。
- 敏感資料不要放進這個資料夾的 git：這裡的檔案都會公開發布到網站上。
