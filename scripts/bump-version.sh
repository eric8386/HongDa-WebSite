#!/bin/sh
# 產生新版本號並寫入 index.html 與 version.json（每次更新 commit 前執行）
set -e
cd "$(git rev-parse --show-toplevel)"
V="$(TZ=Asia/Taipei date +%Y.%m.%d-%H%M)"
sed -i '' "s/window.SITE_VERSION='[^']*'/window.SITE_VERSION='$V'/" index.html
printf '{"version":"%s"}\n' "$V" > version.json
git add index.html version.json
echo "網站版本：$V"
