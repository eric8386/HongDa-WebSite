#!/usr/bin/env python3
"""為商品介紹圖產生手機用的較小版本（macOS sips）。

assets/catalog/detail/<id>/NN.jpg（寬度 > 900px）
  → assets/catalog/m/detail/<id>/NN.jpg（寬 828px，JPEG 品質 normal）

build.py 看到對應的小圖就會加上 srcset，讓 2 倍螢幕的手機下載小圖；
3 倍螢幕手機與電腦仍會下載原圖，畫質不變。
已存在且比原圖新的小圖會略過；原圖被刪掉的小圖會一併清掉。
新增或更換介紹圖後執行：python3 tools/make_mobile.py
"""
import os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'catalog', 'detail')
DST = os.path.join(ROOT, 'assets', 'catalog', 'm', 'detail')
WIDTH, MIN_SRC = 828, 900


def width(f):
    o = subprocess.run(['sips', '-g', 'pixelWidth', f], capture_output=True, text=True).stdout
    m = re.search(r'pixelWidth: (\d+)', o)
    return int(m.group(1)) if m else 0


made = kept = removed = 0
wanted = set()
for pid in sorted(os.listdir(SRC)):
    d = os.path.join(SRC, pid)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if not fn.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        src = os.path.join(d, fn)
        out = os.path.join(DST, pid, os.path.splitext(fn)[0] + '.jpg')
        if width(src) <= MIN_SRC:
            continue
        wanted.add(out)
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
            kept += 1
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', 'normal',
                        '--resampleWidth', str(WIDTH), src, '--out', out], capture_output=True, check=True)
        made += 1

if os.path.isdir(DST):
    for base, _, files in os.walk(DST, topdown=False):
        for fn in files:
            f = os.path.join(base, fn)
            if f not in wanted:
                os.remove(f)
                removed += 1
        if not os.listdir(base):
            os.rmdir(base)

print(f'mobile images: {made} made, {kept} up to date, {removed} removed')
