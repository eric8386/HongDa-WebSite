#!/bin/sh
# 產生新版本號、寫入 version.json，並重新產生全站頁面（每次更新 commit 前執行）
set -e
cd "$(git rev-parse --show-toplevel)"
V="$(TZ=Asia/Taipei date +%Y.%m.%d-%H%M)"
# 同一分鐘內再次更新時加上秒數，確保每次版本號都不同
grep -q "\"$V\"" version.json 2>/dev/null && V="$(TZ=Asia/Taipei date +%Y.%m.%d-%H%M%S)"
printf '{"version":"%s"}\n' "$V" > version.json
python3 tools/build.py
git add -A
echo "網站版本：$V"
