#!/usr/bin/env python3
"""鴻達淨水 網站產生器：讀取 data/*.json，輸出靜態 HTML 頁面。

用法：python3 tools/build.py   （通常由 scripts/bump-version.sh 呼叫）
日常更新只需要修改 data/ 內的 JSON，再重新產生即可。
"""
import json, os, html, shutil, datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(name):
    with open(os.path.join(ROOT, 'data', name), encoding='utf-8') as f:
        return json.load(f)

SITE = load('site.json')
PRODUCTS = load('products.json')
SERVICES = load('services.json')
ARTICLES = load('articles.json')
try:
    V = load('../version.json')['version']
except Exception:
    V = 'dev'

PBY = {p['id']: p for p in PRODUCTS}
CATS = {c['key']: c for c in SITE['categories']}
BRANDS = {b['key']: b for b in SITE['brands']}
C = SITE['contact']
DOMAIN = SITE['domain'].rstrip('/')
OUT_PAGES = []  # for sitemap

def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)

def a(path):
    """Versioned asset URL (no-cache by URL)."""
    return '/' + path.lstrip('/') + '?v=' + quote(V)

def tel(n):
    return ''.join(ch for ch in str(n) if ch.isdigit() or ch == '+')

def line_href():
    if C.get('lineUrl'):
        return C['lineUrl']
    if C.get('lineId'):
        return 'https://line.me/R/ti/p/' + quote(C['lineId'])
    return '/contact.html'

def price_html(p, big=False):
    if p.get('price'):
        note = f'<small>{e(p.get("priceNote") or "建議售價")}</small>' if big else ''
        return f'<span class="price"><em>建議售價</em> NT${p["price"]:,}{note}</span>'
    return '<span class="price ask"><em>建議售價</em> 請洽 LINE</span>'

# ---------- icons ----------
ICONS = {
 'drop': '<path d="M12 2.7c3.6 4.3 6.5 8 6.5 11.3a6.5 6.5 0 0 1-13 0c0-3.3 2.9-7 6.5-11.3z"/>',
 'line': '<path d="M12 3C6.5 3 2 6.6 2 11c0 3.9 3.5 7.2 8.3 7.9.3.1.8.2.9.5.1.3.1.7 0 1l-.1.9c0 .3-.2 1 .9.5s6-3.5 8.2-6.1c1.5-1.7 2.3-3.4 2.3-5.2C22 6.6 17.5 3 12 3z"/>',
 'phone': '<path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.6 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.6 3.6a1 1 0 0 1-.25 1z"/>',
 'arrow': '<path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
 'check': '<path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
 'tank': '<path d="M5 6c0-1.7 3.1-3 7-3s7 1.3 7 3v10c0 1.7-3.1 3-7 3s-7-1.3-7-3z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M5 6c0 1.7 3.1 3 7 3s7-1.3 7-3M12 19v3" fill="none" stroke="currentColor" stroke-width="1.8"/>',
 'pipe': '<path d="M3 8h9a3 3 0 0 1 3 3v10M3 13h6a1 1 0 0 1 1 1v7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M17 4.5c1.4 1.7 2.5 3 2.5 4.2a2.5 2.5 0 0 1-5 0c0-1.2 1.1-2.5 2.5-4.2z" fill="currentColor"/>',
 'test': '<path d="M9 3h6M10 3v6.5L5.2 18a2 2 0 0 0 1.8 3h10a2 2 0 0 0 1.8-3L14 9.5V3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M7.5 15h9" stroke="currentColor" stroke-width="1.8"/>',
 'ro': '<rect x="5" y="3" width="10" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M15 7h2.5a1.5 1.5 0 0 1 1.5 1.5V12" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 8h4M8 12h4M8 16h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
 'house': '<path d="M3 11l9-7 9 7M5 9.5V20h14V9.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M12 11.5c1.3 1.6 2.3 2.8 2.3 4a2.3 2.3 0 0 1-4.6 0c0-1.2 1-2.4 2.3-4z" fill="currentColor"/>',
 'sun': '<circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 2.5v2.3M12 19.2v2.3M2.5 12h2.3M19.2 12h2.3M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
 'heat': '<path d="M12 21c-3.6 0-6.5-2.6-6.5-6.2 0-3.4 2.7-5.4 3.9-8.3.3 1.8 1.4 3 2.6 3.6-.2-2.6.9-5 3-6.6.1 3.2 3.5 5.6 3.5 10.6C18.5 18.2 15.6 21 12 21z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M12 18a2.4 2.4 0 0 1-2.4-2.4c0-1.6 1.4-2.4 2.4-4 1 1.6 2.4 2.4 2.4 4A2.4 2.4 0 0 1 12 18z" fill="currentColor"/>',
 'care': '<path d="M14.5 4.5a4 4 0 0 0-5.3 5.3L3.5 15.5a2 2 0 0 0 2.8 2.8l5.7-5.7a4 4 0 0 0 5.3-5.3l-2.5 2.5-2.4-.4-.4-2.4z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
 'menu': '<path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
 'shield': '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M8.5 12l2.5 2.5 4.5-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
 'tag': '<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="7.5" cy="7.5" r="1.5" fill="currentColor"/>',
 'pin': '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="9.5" r="2.5" fill="none" stroke="currentColor" stroke-width="1.8"/>',
 'list': '<path d="M9 6h11M9 12h11M9 18h11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M4 6h.01M4 12h.01M4 18h.01" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>',
 'filter': '<rect x="7" y="3" width="10" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M7 8h10M7 16h10" stroke="currentColor" stroke-width="1.8"/>',
}
def ic(name, cls='ic'):
    filled = name in ('drop', 'line', 'phone')
    fill = 'currentColor' if filled else 'none'
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="{fill}" aria-hidden="true">{ICONS[name]}</svg>'

LOGO = ('<svg class="logo-mark" viewBox="0 0 64 64" aria-hidden="true"><defs><linearGradient id="hdg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#2a9df4"/><stop offset="1" stop-color="#0a3f94"/></linearGradient></defs>'
        '<path d="M32 2.5C32 2.5 8 29.5 8 43.5a24 19.5 0 0 0 48 0C56 29.5 32 2.5 32 2.5z" fill="url(#hdg)"/>'
        '<path d="M21 22h7v31h-7zM36 22h7v31h-7z" fill="#fff"/>'
        '<path d="M14 42c6-6 12-6 18-1s12 5 18-1" fill="none" stroke="#9fdcff" stroke-width="4.5" stroke-linecap="round"/></svg>')

# ---------- layout ----------
NAV = [
    ('/products/', '品牌商品'),
    ('/services/', '服務項目'),
    ('/filters/', '濾心專區'),
    ('/knowledge/', '水質知識'),
    ('/about.html', '關於我們'),
    ('/faq.html', '常見問題'),
]

def header(active):
    cur = ' aria-current="page"'
    links = ''.join(
        f'<a href="{h}"{cur if active == h else ""}>{t}</a>' for h, t in NAV)
    return f'''<header class="site-header">
  <div class="wrap header-inner">
    <a class="logo" href="/" aria-label="{e(SITE["short"])} 首頁">{LOGO}<span><b>{e(SITE["short"])}</b><small>{e(SITE["en"])}</small></span></a>
    <nav class="main-nav" id="main-nav" aria-label="主選單">{links}<a class="nav-finder" href="/finder.html">3 步驟找方案</a></nav>
    <div class="header-actions">
      {f'<a class="header-tel" href="tel:{tel(C["mobile"])}">{ic("phone")}<span>{e(C["mobile"])}</span></a>' if C.get('mobile') else ''}
      <a class="btn btn-line btn-sm" href="{e(line_href())}" data-line>{ic("line")}<span>LINE 諮詢</span></a>
      <button class="nav-toggle" type="button" aria-controls="main-nav" aria-expanded="false" aria-label="開啟選單">{ic("menu")}</button>
    </div>
  </div>
</header>'''

def footer():
    cats = ''.join(f'<li><a href="/products/?cat={c["key"]}">{e(c["name"])}</a></li>' for c in SITE['categories'])
    svcs = ''.join(f'<li><a href="/services/{s["slug"]}.html">{e(s["name"])}</a></li>' for s in SERVICES)
    rows = []
    if C.get('mobile'): rows.append(f'<li>{ic("phone")}<span>手機：<a href="tel:{tel(C["mobile"])}">{e(C["mobile"])}</a>{"（" + e(C["person"]) + "）" if C.get("person") else ""}</span></li>')
    if C.get('phone'): rows.append(f'<li>{ic("phone")}<span>電話：<a href="tel:{tel(C["phone"])}">{e(C["phone"])}</a></span></li>')
    if C.get('fax'): rows.append(f'<li>{ic("list")}傳真：{e(C["fax"])}</li>')
    if C.get('lineId'): rows.append(f'<li>{ic("line")}LINE：{e(C["lineId"])}</li>')
    if C.get('address'): rows.append(f'<li>{ic("pin")}{e(C["address"])}</li>')
    if C.get('hours'): rows.append(f'<li>{ic("list")}{e(C["hours"])}</li>')
    rows.append(f'<li>{ic("pin")}服務地區：{e("、".join(SITE["areas"]))}</li>')
    year = datetime.date.today().year
    return f'''<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a class="logo logo-light" href="/">{LOGO}<span><b>{e(SITE["name"])}</b><small>{e(SITE["en"])}</small></span></a>
      <p class="slogan">{e(SITE.get("slogan",""))}</p><p>{e(SITE["description"])}</p>
      <a class="btn btn-line" href="{e(line_href())}" data-line>{ic("line")}<span>加 LINE 免費諮詢</span></a>
    </div>
    <div><h3>產品分類</h3><ul>{cats}</ul></div>
    <div><h3>服務項目</h3><ul>{svcs}</ul></div>
    <div><h3>聯絡資訊</h3><ul class="contact-list">{"".join(rows)}</ul></div>
  </div>
  <div class="wrap footer-bottom"><span>© {year} {e(SITE["name"])}</span><span>產品規格依各品牌公開資料整理，實際以原廠為準。</span></div>
</footer>
<nav class="mobile-bar" aria-label="快速聯絡">
  <a class="mb-line" href="{e(line_href())}" data-line>{ic("line")}LINE 諮詢</a>
  <a href="/finder.html">{ic("list")}找方案</a>
  {f'<a href="tel:{tel(C.get("mobile") or C["phone"])}">{ic("phone")}撥打電話</a>' if (C.get('mobile') or C.get('phone')) else f'<a href="/services/">{ic("care")}服務項目</a>'}
</nav>'''

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'

def business_ld():
    o = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": SITE['name'],
         "url": DOMAIN + '/', "description": SITE['description'],
         "areaServed": [{"@type": "City", "name": x} for x in SITE['areas']]}
    if C.get('mobile') or C.get('phone'): o['telephone'] = C.get('mobile') or C['phone']
    if C.get('fax'): o['faxNumber'] = C['fax']
    if C.get('address'):
        o['address'] = {"@type": "PostalAddress", "streetAddress": C['address'], "addressLocality": "台南市", "addressCountry": "TW"}
    if SITE.get('slogan'): o['slogan'] = SITE['slogan']
    return o

def crumbs_html(items):
    if not items: return ''
    lis = ''.join(f'<li><a href="{h}">{e(t)}</a></li>' if h else f'<li aria-current="page">{e(t)}</li>' for h, t in items)
    return f'<nav class="crumbs wrap" aria-label="麵包屑"><ol>{lis}</ol></nav>'

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, **({"item": DOMAIN + h} if h else {})}
        for i, (h, t) in enumerate(items)]}

def page(path, title, desc, body, active='', crumbs=None, ld=None, og_image=None, full_title=False):
    t = title if full_title else f'{title}｜{SITE["short"]}・台南淨水工程'
    lds = [business_ld()] if path == '/' else []
    if crumbs: lds.append(crumbs_ld([('/', '首頁')] + crumbs))
    if ld: lds += ld if isinstance(ld, list) else [ld]
    canonical = DOMAIN + path
    ogimg = DOMAIN + '/' + og_image if og_image else ''
    site_js = json.dumps({"lineId": C.get('lineId', ''), "lineUrl": C.get('lineUrl', ''), "version": V}, ensure_ascii=False)
    doc = f'''<!doctype html>
<html lang="zh-Hant-TW">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>{e(t)}</title>
  {'' if SITE.get('indexable') else '<meta name="robots" content="noindex, nofollow">'}
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{e(canonical)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{e(SITE["name"])}">
  <meta property="og:title" content="{e(t)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{e(canonical)}">
  {f'<meta property="og:image" content="{e(ogimg)}">' if ogimg else ''}
  <meta name="theme-color" content="#0a4fb4">
  <link rel="icon" href="{a("assets/img/favicon.svg")}" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{a("assets/css/site.css")}">
  <script>window.SITE={site_js};
  (function(){{var cur=window.SITE.version;fetch('/version.json?t='+Date.now(),{{cache:'no-store'}}).then(function(r){{return r.ok?r.json():null}}).then(function(d){{if(!d||!d.version||d.version===cur)return;var k='hd-reload-'+d.version;try{{if(sessionStorage.getItem(k))return;sessionStorage.setItem(k,'1')}}catch(x){{}}var u=new URL(location.href);u.searchParams.set('v',d.version);location.replace(u.toString())}}).catch(function(){{}})}})();</script>
  {"".join(jsonld(x) for x in lds)}
</head>
<body>
<a class="skip" href="#main">跳到主要內容</a>
<div class="site-version" title="網站版本">v{e(V)}</div>
{header(active)}
{crumbs_html([('/', '首頁')] + crumbs if crumbs else None)}
<main id="main">
{body}
</main>
{footer()}
<script src="{a("assets/js/site.js")}" defer></script>
</body>
</html>
'''
    out = os.path.join(ROOT, path.lstrip('/'))
    if path.endswith('/'): out = os.path.join(out, 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(doc)
    if path != '/404.html':
        OUT_PAGES.append(path)

# ---------- components ----------
def img_html(src, alt, cls='', lazy=True):
    if not src:
        return f'<div class="ph {cls}" role="img" aria-label="{e(alt)}">{ic("filter", "ph-ic")}<span>圖片準備中</span></div>'
    thumb = src.replace('assets/catalog/', 'assets/catalog/thumb/', 1)
    use = thumb if os.path.exists(os.path.join(ROOT, thumb)) else src
    lz = ' loading="lazy"' if lazy else ''
    return f'<img class="{cls}" src="{a(use)}" alt="{e(alt)}"{lz} decoding="async">'

def product_card(p):
    c = CATS[p['cat']]
    return f'''<article class="p-card" data-cat="{p["cat"]}" data-brand="{p["brand"]}">
  <a href="/products/{p["id"]}.html" class="p-link">
    <div class="p-photo">{img_html(p["image"], p["name"] + " 產品照片")}<span class="chip">{e(c["short"])}</span></div>
    <div class="p-body">
      <div class="p-meta"><span>{e(BRANDS[p["brand"]]["name"])}</span><span>{e(p["model"])}</span></div>
      <h3>{e(p["name"])}</h3>
      <p>{e(p["summary"])}</p>
      <div class="p-foot">{price_html(p)}<span class="more">{ic("arrow")}</span></div>
    </div>
  </a>
</article>'''

def service_card(s):
    return f'''<a class="s-card" href="/services/{s["slug"]}.html">
  <span class="s-ic">{ic(s["icon"])}</span>
  <h3>{e(s["name"])}</h3>
  <p>{e(s["lead"])}</p>
  <span class="s-more">了解流程與估價 {ic("arrow")}</span>
</a>'''

def cta_band(title='不確定該選哪一種？先加 LINE 問問看', text='拍下櫥下空間、水塔或總進水管的照片傳給我們，先給初步建議與估價。'):
    return f'''<section class="cta-band"><div class="wrap cta-inner">
  <div><h2>{e(title)}</h2><p>{e(text)}</p></div>
  <div class="cta-actions"><a class="btn btn-line btn-lg" href="{e(line_href())}" data-line>{ic("line")}<span>加 LINE 免費諮詢</span></a>
  <a class="btn btn-ghost-light btn-lg" href="/finder.html">3 步驟找方案</a></div>
</div></section>'''

def faq_html(items):
    return '<div class="faq-list">' + ''.join(
        f'<details class="faq"><summary>{e(f["q"])}</summary><div><p>{e(f["a"])}</p>'
        + (f'<p class="src">資料來源：<a href="{e(f["source"])}" target="_blank" rel="noopener">台灣自來水公司</a></p>' if f.get('source') else '')
        + '</div></details>' for f in items) + '</div>'

def faq_ld(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f['q'], "acceptedAnswer": {"@type": "Answer", "text": f['a']}} for f in items]}

QUIZ = '''<div class="quiz" data-quiz>
  <ol class="quiz-steps" aria-hidden="true"><li class="on">住宅型態</li><li>最在意</li><li>預算</li></ol>
  <form class="quiz-form" novalidate>
    <fieldset class="q-step on" data-step="1"><legend>1. 您住在哪一種房子？</legend>
      <div class="q-opts">
        <label><input type="radio" name="home" value="apt"><span><b>公寓／大樓</b><small>單戶、共用水塔</small></span></label>
        <label><input type="radio" name="home" value="house"><span><b>透天／獨棟</b><small>自家水塔、多樓層</small></span></label>
      </div></fieldset>
    <fieldset class="q-step" data-step="2"><legend>2. 您最在意哪一件事？</legend>
      <div class="q-opts">
        <label><input type="radio" name="need" value="drink"><span><b>想直接生飲</b><small>廚房喝水、煮飯泡茶</small></span></label>
        <label><input type="radio" name="need" value="scale"><span><b>水垢、洗澡用水</b><small>熱水器、衛浴水垢</small></span></label>
        <label><input type="radio" name="need" value="tank"><span><b>水塔、水管髒污</b><small>黃水、沉積物、異味</small></span></label>
        <label><input type="radio" name="need" value="all"><span><b>全屋一次規劃</b><small>喝的、用的都要顧</small></span></label>
      </div></fieldset>
    <fieldset class="q-step" data-step="3"><legend>3. 預算大概是？</legend>
      <div class="q-opts">
        <label><input type="radio" name="budget" value="low"><span><b>2 萬以內</b></span></label>
        <label><input type="radio" name="budget" value="mid"><span><b>2～6 萬</b></span></label>
        <label><input type="radio" name="budget" value="high"><span><b>6 萬以上</b></span></label>
        <label><input type="radio" name="budget" value="unsure"><span><b>還不確定</b></span></label>
      </div></fieldset>
    <div class="q-nav"><button type="button" class="btn btn-ghost" data-prev hidden>上一步</button><span class="q-hint">點選答案即可進入下一步</span></div>
  </form>
  <div class="q-result" hidden aria-live="polite"></div>
</div>'''

# ---------- pages ----------
HERO_TILES = [('ro', 'brita-mypure-gr-1000', 'big'), ('softener', 'clack-cws35-2e10r', ''), ('drink', 'everpoll-evb-398', '')]

def hero_tiles():
    out = ''
    for cat, pid, cls in HERO_TILES:
        p = PBY.get(pid) or next((x for x in PRODUCTS if x['cat'] == cat), None)
        if not p:
            continue
        c = CATS[cat]
        n = sum(1 for x in PRODUCTS if x['cat'] == cat)
        out += f'''<a class="ht {cls}" href="/products/?cat={cat}">
        <span class="ht-img">{img_html(p["image"], c["name"], lazy=False)}</span>
        <span class="ht-txt"><b>{e(c["short"])}</b><small>{n} 款 {ic("arrow")}</small></span></a>'''
    return out

def build_home():
    feat = [PBY[i] for i in SITE['featured'] if i in PBY]
    cats = ''.join(f'''<a class="cat-card" href="/products/?cat={c["key"]}"><span class="cat-ic">{ic({"ro":"ro","combo":"drop","drink":"heat","whole":"house","softener":"shield","filter":"filter"}[c["key"]])}</span>
      <h3>{e(c["name"])}</h3><p>{e(c["desc"])}</p><span class="count">{sum(1 for p in PRODUCTS if p["cat"]==c["key"])} 款</span></a>''' for c in SITE['categories'])
    path_nodes = [
        ('tank', '水塔', '全家用水的第一站。至少每半年清洗一次，避免沉積物流進管路。', '/services/tank-cleaning.html', '水塔清洗'),
        ('pipe', '管路', '管壁的鏽垢與生物膜會讓水色混濁、出水變小。', '/services/pipe-cleaning.html', '管路清洗'),
        ('house', '全戶過濾', '總進水端攔截泥沙、鐵鏽與餘氯，保護全屋設備。', '/products/?cat=whole', '全戶淨水'),
        ('shield', '全戶軟水', '降低鈣鎂硬度，減少熱水器與衛浴水垢。', '/products/?cat=softener', '全戶軟水'),
        ('ro', '廚房飲水', '直輸 RO 處理喝的水，再搭配廚下加熱器，熱水即開即用。', '/products/?cat=ro', '直輸 RO'),
    ]
    nodes = ''.join(f'''<li><button type="button" class="flow-node{" on" if i==0 else ""}" data-flow="{i}" aria-pressed="{"true" if i==0 else "false"}"><span class="fn-ic">{ic(n[0])}</span><b>{e(n[1])}</b></button>
      <template>{ic(n[0], "ic big")}<div><h3>{e(n[1])}</h3><p>{e(n[2])}</p><a href="{n[3]}">看{e(n[4])} {ic("arrow")}</a></div></template></li>''' for i, n in enumerate(path_nodes))
    pains = [
        ('shield', '水垢清不完', '熱水器、蓮蓬頭、玻璃門一層白垢', '/services/whole-house.html'),
        ('drop', '水有味道', '漂白水味、霉味，喝起來不放心', '/products/?cat=ro'),
        ('tank', '水塔多年沒洗', '偶爾出現黃水或細小沉積物', '/services/tank-cleaning.html'),
        ('list', '不知道怎麼選', 'RO、加熱器、全戶、軟水一堆名詞', '/finder.html'),
    ]
    pains_html = ''.join(f'<a class="pain" href="{h}">{ic(i)}<div><h3>{e(t)}</h3><p>{e(d)}</p></div>{ic("arrow", "ic go")}</a>' for i, t, d, h in pains)
    why = [
        ('tag', '建議售價公開', '產品頁直接標示建議售價或詢價方式，安裝與清洗依現場透明報價。'),
        ('list', '多品牌比較', '、'.join(b['name'].split(' ')[0] for b in SITE['brands']) + '，依需求挑選，不綁單一品牌。'),
        ('check', '施工流程公開', '每項服務都列出完整步驟，施工前先說清楚做什麼、要多久。'),
        ('pin', '台南在地服務', '以台南為主要服務範圍，安裝、清洗、換濾心都能就近安排。'),
    ]
    why_html = ''.join(f'<div class="why">{ic(i)}<h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, t, d in why)
    process = [('LINE 傳照片', '櫥下、水塔或總進水管拍照傳給我們'), ('初步建議與估價', '依照片與需求建議方案'),
               ('約時間到府', '現場確認後施工或安裝'), ('完工說明', '說明使用與保養方式'), ('到期提醒', 'LINE 提醒濾心更換與水塔清洗')]
    proc_html = ''.join(f'<li><span class="no">{i+1:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>' for i, (t, d) in enumerate(process))
    hero_p = PBY.get('brita-mypure-gr-600') or PRODUCTS[0]
    hero_p2 = PBY.get('everpoll-jh-r3000') or PRODUCTS[1]
    trust = ''
    if SITE['cases'] or SITE['reviews'] or SITE['certifications']:
        trust = '<section class="sec"><div class="wrap"><div class="sec-head"><span class="eyebrow">實績與評價</span><h2>客戶怎麼說</h2></div></div></section>'
    body = f'''
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <span class="eyebrow">{e(SITE.get("tagline") or "台南在地淨水工程")}</span>
      <h1>從水塔到水龍頭，<br><span class="hl">全家用水一次顧好</span></h1>
      <p class="lead">淨水設備安裝、水塔清洗、自來水管路清洗、水質檢測與定期保養。先了解你家的水，再推薦真正需要的方案。</p>
      <div class="hero-cta">
        <a class="btn btn-line btn-lg" href="{e(line_href())}" data-line>{ic("line")}<span>加 LINE 免費諮詢</span></a>
        <a class="btn btn-primary btn-lg" href="#finder">3 步驟找出適合方案 {ic("arrow")}</a>
      </div>
      <ul class="hero-points"><li>{ic("check")}建議售價公開</li><li>{ic("check")}{len(SITE["brands"])} 大品牌比較</li><li>{ic("check")}台南到府服務</li></ul>
    </div>
    <div class="hero-tiles">
      {hero_tiles()}
      <div class="ht-svc"><span class="ht-svc-title">清洗與檢測服務</span>
        <a href="/services/tank-cleaning.html">{ic("tank")}水塔清洗</a>
        <a href="/services/pipe-cleaning.html">{ic("pipe")}管路清洗</a>
        <a href="/services/water-test.html">{ic("test")}水質檢測</a>
      </div>
    </div>
  </div>
</section>

<section class="sec sec-pains"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">常見困擾</span><h2>你家也有這些用水問題嗎？</h2></div>
  <div class="pains">{pains_html}</div>
</div></section>

<section class="sec sec-flow"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">全屋用水路徑</span><h2>水從水塔流到你的杯子，每一段都需要照顧</h2><p>點選每個階段，看看可以怎麼改善。</p></div>
  <div class="flow" data-flow-root>
    <ol class="flow-track">{nodes}</ol>
    <div class="flow-detail" aria-live="polite"></div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head row"><div><span class="eyebrow">產品分類</span><h2>依用途挑選淨水設備</h2></div><a class="link" href="/products/">看全部品牌商品 {ic("arrow")}</a></div>
  <div class="cats">{cats}</div>
</div></section>

<section class="sec sec-soft"><div class="wrap">
  <div class="sec-head row"><div><span class="eyebrow">熱門機型</span><h2>常被詢問的推薦機型</h2></div><a class="link" href="/products/">更多機型 {ic("arrow")}</a></div>
  <div class="p-grid feat">{"".join(product_card(p) for p in feat)}</div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head row"><div><span class="eyebrow">服務項目</span><h2>安裝、清洗、檢測、保養一次到位</h2></div><a class="link" href="/services/">所有服務 {ic("arrow")}</a></div>
  <div class="s-grid">{"".join(service_card(s) for s in SERVICES)}</div>
</div></section>

<section class="sec sec-dark"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">服務流程</span><h2>從諮詢到完工，每一步都清楚</h2></div>
  <ol class="process">{proc_html}</ol>
</div></section>

<section class="sec" id="finder"><div class="wrap finder-wrap">
  <div class="finder-copy"><span class="eyebrow">互動選購</span><h2>3 步驟，找出適合你家的淨水方案</h2><p>回答三個問題，立即看到建議組合；結果可以直接傳到 LINE，讓我們幫你進一步評估。</p></div>
  {QUIZ}
</div></section>

<section class="sec sec-soft"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">為什麼選擇{e(SITE["short"])}</span><h2>把每一分錢花在真正需要的地方</h2></div>
  <div class="whys">{why_html}</div>
</div></section>
{trust}
<section class="sec"><div class="wrap narrow">
  <div class="sec-head"><span class="eyebrow">常見問題</span><h2>選購前最常被問的問題</h2></div>
  {faq_html(SITE["faqs"][:5])}
  <p class="center"><a class="link" href="/faq.html">看全部常見問題 {ic("arrow")}</a></p>
</div></section>
{cta_band()}'''
    page('/', f'{SITE["short"]}｜台南淨水器安裝・水塔清洗・水管清洗・軟水設備', SITE['description'], body, active='/',
         ld=[faq_ld(SITE['faqs'][:5])], og_image=hero_p['image'], full_title=True)

def build_products():
    chips_c = '<button type="button" class="fchip on" data-f="cat" data-v="">全部</button>' + ''.join(
        f'<button type="button" class="fchip" data-f="cat" data-v="{c["key"]}">{e(c["short"])}</button>' for c in SITE['categories'])
    chips_b = '<button type="button" class="fchip on" data-f="brand" data-v="">全部品牌</button>' + ''.join(
        f'<button type="button" class="fchip" data-f="brand" data-v="{b["key"]}">{e(b["name"])}</button>' for b in SITE['brands'])
    order = {c['key']: i for i, c in enumerate(SITE['categories'])}
    items = sorted(PRODUCTS, key=lambda p: order[p['cat']])
    body = f'''<section class="page-hero"><div class="wrap">
  <span class="eyebrow">品牌商品</span><h1>淨水設備與濾心耗材</h1>
  <p>依用途或品牌篩選。產品頁有完整規格、安裝條件與對應濾心，詢價請加 LINE。</p>
</div></section>
<section class="sec sec-tight"><div class="wrap" data-catalog>
  <div class="filters"><div class="frow" role="group" aria-label="依用途篩選">{chips_c}</div><div class="frow" role="group" aria-label="依品牌篩選">{chips_b}</div></div>
  <p class="result-count" aria-live="polite"></p>
  <div class="p-grid">{"".join(product_card(p) for p in items)}</div>
  <div class="empty" hidden><p>這個分類的產品整理中，歡迎加 LINE 詢問。</p><a class="btn btn-line" href="{e(line_href())}" data-line>{ic("line")}<span>LINE 詢問</span></a></div>
</div></section>
{cta_band()}'''
    page('/products/', '淨水設備型錄：直輸 RO、淨熱一體機、全戶淨水、全戶軟水、廚下加熱器', '台南淨水設備型錄：直輸 RO、淨熱一體機、廚下加熱器、全戶淨水、全戶軟水與濾心耗材，含規格、安裝條件與建議售價。',
         body, active='/products/', crumbs=[(None, '品牌商品')])
    for p in PRODUCTS:
        build_product(p)

def gallery_html(p):
    g = [x for x in (p.get('gallery') or []) if os.path.exists(os.path.join(ROOT, x['src']))]
    if not g:
        d = os.path.join(ROOT, 'assets', 'catalog', 'detail', p['id'])
        if os.path.isdir(d):
            files = sorted(f for f in os.listdir(d) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')))
            g = [{'src': f'assets/catalog/detail/{p["id"]}/{f}', 'alt': f'{p["name"]} 產品介紹圖 {i+1}'} for i, f in enumerate(files)]
    p['_gallery'] = g
    if not g:
        return ''
    imgs = ''.join(f'<img src="{a(x["src"])}" alt="{e(x.get("alt") or p["name"])}" loading="lazy" decoding="async">' for x in g)
    return f'''<section class="pd-gallery" id="intro"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">產品介紹</span><h2>{e(p["name"])}</h2></div>
  <div class="gallery-stack">{imgs}</div>
  <p class="note center">產品介紹圖片來源：{e(BRANDS[p["brand"]]["name"])} 原廠資料。</p>
</div></section>'''

def build_product(p):
    gal = gallery_html(p)
    c = CATS[p['cat']]
    b = BRANDS[p['brand']]
    specs = ''.join(f'<tr><th>{e(k)}</th><td>{e(v)}</td></tr>' for k, v in p['specs'])
    points = ''.join(f'<li>{ic("check")}{e(x)}</li>' for x in p['points'])
    install = ''.join(f'<li>{e(x)}</li>' for x in c['install'])
    rel_block = ''
    if p.get('filterInfo'):
        rows = ''.join(f'<tr><td>{e(f["model"])}</td><td>{e(f["interval"])}</td></tr>' for f in p['filterInfo'])
        rel_block = f'''<section class="pd-sec"><h2>{ic("filter")}濾心與更換週期</h2>
  <div class="table-wrap"><table class="tbl"><thead><tr><th>濾心／說明</th><th>建議更換</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="note">更換週期依原廠說明，實際會受水質與用水量影響。年度耗材費用可加 LINE 詢問。</p></section>'''
    elif p['filters']:
        fl = [PBY[i] for i in p['filters'] if i in PBY]
        rows = ''.join(f'<tr><td><a href="/products/{f["id"]}.html">{e(f["name"])}</a></td><td>{e(f["model"])}</td><td>{e(f.get("interval") or "依原廠指示與用水量")}</td></tr>' for f in fl)
        rel_block = f'''<section class="pd-sec"><h2>{ic("filter")}對應濾心與更換週期</h2>
  <div class="table-wrap"><table class="tbl"><thead><tr><th>濾心</th><th>型號</th><th>建議更換</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="note">濾心費用與實際更換時間會依水質與用水量不同，購買前可加 LINE 詢問年度耗材費用。</p></section>'''
    elif p['fits']:
        ml = [PBY[i] for i in p['fits'] if i in PBY]
        rel_block = f'''<section class="pd-sec"><h2>{ic("ro")}適用機型</h2><ul class="fit-list">''' + ''.join(
            f'<li><a href="/products/{m["id"]}.html">{e(m["name"])}</a></li>' for m in ml) + '</ul></section>'
    same = [x for x in PRODUCTS if x['cat'] == p['cat'] and x['id'] != p['id']][:4]
    src = f'<p class="note">資料來源：<a href="{e(p["source"])}" target="_blank" rel="noopener">{e(p["sourceText"])}</a>。規格依公開資料整理，實際以原廠與現場評估為準。</p>' if p.get('source') else ''
    svc = next((s for s in SERVICES if s.get('category') == p['cat']), None)
    if p['cat'] == 'whole': svc = next(s for s in SERVICES if s['slug'] == 'whole-house')
    if p['cat'] == 'drink': svc = next(s for s in SERVICES if s['slug'] == 'maintenance')
    line_txt = f'您好，我想詢問 {p["name"]}（{p["model"]}）的價格與安裝。'
    body = f'''<section class="pd wrap">
  <div class="pd-media">{img_html(p["image"], p["name"] + " 產品照片", "pd-img", lazy=False)}</div>
  <div class="pd-info">
    <div class="pd-tags"><a class="chip" href="/products/?cat={c["key"]}">{e(c["short"])}</a><a class="chip chip-soft" href="/products/?brand={p["brand"]}">{e(b["name"])}</a>{f'<span class="chip chip-soft">{e(p["label"])}</span>' if p.get("label") else ""}</div>
    <h1>{e(p["name"])}</h1>
    <p class="pd-model">型號 {e(p["model"])}</p>
    <p class="pd-sum">{e(p["summary"])}</p>
    <div class="pd-price">{price_html(p, big=True)}<p>安裝費用依現場管路與施工條件而定，傳照片即可先估價。</p></div>
    <div class="pd-cta"><a class="btn btn-line btn-lg" href="{e(line_href())}" data-line data-line-text="{e(line_txt)}">{ic("line")}<span>LINE 詢價／預約安裝</span></a>
    {f'<a class="btn btn-ghost btn-lg" href="/services/{svc["slug"]}.html">看安裝服務流程</a>' if svc else ''}</div>
    <ul class="pd-points">{points}</ul>
    {'<a class="link pd-more" href="#intro">看完整產品介紹 ' + ic("arrow") + '</a>' if p.get('_gallery') else ''}
  </div>
</section>
{gal}
<div class="wrap pd-body">
  <section class="pd-sec"><h2>{ic("list")}產品規格</h2><div class="table-wrap"><table class="tbl spec"><tbody>{specs}</tbody></table></div>{src}</section>
  <section class="pd-sec"><h2>{ic("house")}安裝前要確認</h2><ul class="install">{install}</ul><p class="note">以上為{e(c["short"])}的一般安裝條件，實際以現場評估為準。</p></section>
  {rel_block}
</div>
{f'<section class="sec sec-soft"><div class="wrap"><div class="sec-head"><h2>同類型產品比較</h2></div><div class="p-grid">' + "".join(product_card(x) for x in same) + '</div></div></section>' if same else ''}
{cta_band('想知道這台適不適合你家？', '傳一張櫥下或安裝位置的照片給我們，幫你確認空間、電源與管路條件。')}'''
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p['name'], "sku": p['model'], "mpn": p['model'],
          "brand": {"@type": "Brand", "name": b['name']}, "description": p['summary'], "category": c['name']}
    if p['image']: ld['image'] = DOMAIN + '/' + p['image']
    if p.get('price'):
        ld['offers'] = {"@type": "Offer", "priceCurrency": "TWD", "price": p['price'], "url": DOMAIN + f'/products/{p["id"]}.html'}
    page(f'/products/{p["id"]}.html', f'{p["name"]}（{p["model"]}）規格與安裝', f'{p["name"]}：{p["summary"]} 台南安裝、規格、對應濾心與建議售價。',
         body, active='/products/', crumbs=[('/products/', '品牌商品'), (f'/products/?cat={c["key"]}', c['short']), (None, p['model'])],
         ld=ld, og_image=p['image'] or None)

def build_services():
    body = f'''<section class="page-hero"><div class="wrap">
  <span class="eyebrow">服務項目</span><h1>台南淨水安裝・水塔與管路清洗</h1>
  <p>{e(SITE["areaNote"])}</p>
</div></section>
<section class="sec sec-tight"><div class="wrap"><div class="s-grid">{"".join(service_card(s) for s in SERVICES)}</div></div></section>
{cta_band()}'''
    page('/services/', '服務項目：水塔清洗、水管清洗、淨水安裝、水質檢測', '台南水塔清洗、自來水管路清洗、直輸 RO 安裝、全戶淨水與軟水安裝、水質檢測與換濾心保養服務。',
         body, active='/services/', crumbs=[(None, '服務項目')])
    for s in SERVICES:
        build_service(s)

def build_service(s):
    pains = ''.join(f'<li>{ic("drop")}{e(x)}</li>' for x in s['pains'])
    hl = ''.join(f'<li>{ic("check")}{e(x)}</li>' for x in s['highlights'])
    steps = ''.join(f'<li><span class="no">{i+1:02d}</span><div><h3>{e(st["t"])}</h3><p>{e(st["d"])}</p></div></li>' for i, st in enumerate(s['steps']))
    rows = ''.join(f'<tr><th>{e(r["type"])}</th><td>{("NT$" + format(r["price"], ",") + " 起") if r.get("price") else "請洽 LINE 估價"}</td><td>{e(r["note"])}</td></tr>' for r in s['pricing'])
    faqs = [SITE['faqs'][i] for i in s.get('faqKeys', [])]
    rel = ''
    if s.get('category'):
        ps = [p for p in PRODUCTS if p['cat'] == s['category']][:4]
        if s['slug'] == 'whole-house':
            ps = [p for p in PRODUCTS if p['cat'] in ('whole', 'softener')][:4]
        if ps:
            rel = f'<section class="sec sec-soft"><div class="wrap"><div class="sec-head row"><h2>相關產品</h2><a class="link" href="/products/?cat={s["category"]}">看更多 {ic("arrow")}</a></div><div class="p-grid">' + ''.join(product_card(p) for p in ps) + '</div></div></section>'
    src = f'<p class="note">參考資料：<a href="{e(s["source"])}" target="_blank" rel="noopener">{e(s["sourceText"])}</a></p>' if s.get('source') else ''
    line_txt = f'您好，我想詢問「{s["name"]}」的估價。'
    body = f'''<section class="svc-hero"><div class="wrap svc-hero-grid">
  <div><span class="eyebrow">{e("、".join(SITE["areas"]))}服務</span><h1>{e(s["title"])}</h1><p class="lead">{e(s["lead"])}</p>
    <div class="hero-cta"><a class="btn btn-line btn-lg" href="{e(line_href())}" data-line data-line-text="{e(line_txt)}">{ic("line")}<span>LINE 傳照片估價</span></a><a class="btn btn-ghost btn-lg" href="#steps">看施工流程</a></div></div>
  <div class="svc-badge">{ic(s["icon"], "ic huge")}</div>
</div></section>
<section class="sec"><div class="wrap two-col">
  <div><h2 class="h-sm">這些情況，建議安排{e(s["name"])}</h2><ul class="pain-list">{pains}</ul></div>
  <div class="hl-box"><h2 class="h-sm">服務重點</h2><ul class="hl-list">{hl}</ul>{src}</div>
</div></section>
<section class="sec sec-soft" id="steps"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">施工流程</span><h2>{e(s["name"])}怎麼進行？</h2></div>
  <ol class="steps">{steps}</ol>
</div></section>
<section class="sec"><div class="wrap narrow">
  <div class="sec-head"><span class="eyebrow">收費方式</span><h2>依房型與現場狀況報價</h2><p>傳照片到 LINE 即可先取得初步估價，到府確認後再施工。</p></div>
  <div class="table-wrap"><table class="tbl price-tbl"><thead><tr><th>類型</th><th>費用</th><th>計價依據</th></tr></thead><tbody>{rows}</tbody></table></div>
</div></section>
{rel}
{f'<section class="sec"><div class="wrap narrow"><div class="sec-head"><h2>常見問題</h2></div>{faq_html(faqs)}</div></section>' if faqs else ''}
{cta_band(f'預約{s["name"]}，先傳照片估價', '告訴我們地址區域、房型與現場照片，我們會回覆初步估價與可安排的時間。')}'''
    ld = {"@context": "https://schema.org", "@type": "Service", "name": s['title'], "serviceType": s['name'], "description": s['lead'],
          "provider": {"@type": "LocalBusiness", "name": SITE['name'], "url": DOMAIN + '/'},
          "areaServed": [{"@type": "City", "name": x} for x in SITE['areas']]}
    lds = [ld] + ([faq_ld(faqs)] if faqs else [])
    page(f'/services/{s["slug"]}.html', s['title'], s['lead'], body, active='/services/',
         crumbs=[('/services/', '服務項目'), (None, s['name'])], ld=lds)

def build_filters():
    machines = [p for p in PRODUCTS if p['filters']]
    rows = ''
    for m in machines:
        for i, fid in enumerate(m['filters']):
            f = PBY[fid]
            th = f'<th rowspan="{len(m["filters"])}"><a href="/products/{m["id"]}.html">{e(m["name"])}</a></th>' if i == 0 else ''
            rows += f'<tr>{th}<td><a href="/products/{f["id"]}.html">{e(f["name"])}</a></td><td>{e(f["model"])}</td><td>{e(f.get("interval") or "依原廠指示")}</td></tr>'
    fl = [p for p in PRODUCTS if p['cat'] == 'filter']
    body = f'''<section class="page-hero"><div class="wrap">
  <span class="eyebrow">濾心專區</span><h1>找對濾心，定期更換</h1>
  <p>從機型找到對應濾心。不確定自己的機型？拍下機身型號標籤傳 LINE，我們幫你確認。</p>
  <div class="hero-cta"><a class="btn btn-line" href="{e(line_href())}" data-line data-line-text="您好，我想確認我家淨水器要用哪一款濾心。">{ic("line")}<span>傳機身照片確認濾心</span></a><a class="btn btn-ghost" href="/services/maintenance.html">到府換濾心服務</a></div>
</div></section>
<section class="sec sec-tight"><div class="wrap">
  <div class="sec-head"><h2>機型對照表</h2></div>
  <div class="table-wrap"><table class="tbl match-tbl"><thead><tr><th>機型</th><th>濾心</th><th>型號</th><th>建議更換</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="note">更換週期依原廠指示，實際會受水質與用水量影響。</p>
</div></section>
<section class="sec sec-soft"><div class="wrap">
  <div class="sec-head"><h2>所有濾心耗材</h2></div>
  <div class="p-grid">{"".join(product_card(p) for p in fl)}</div>
</div></section>
<section class="sec"><div class="wrap remind">
  <div>{ic("care", "ic big")}</div>
  <div><h2>濾心到期，LINE 提醒你</h2><p>加入 LINE 並告訴我們機型與安裝日期，濾心快到期時我們會主動提醒，不用自己記。</p></div>
  <a class="btn btn-line btn-lg" href="{e(line_href())}" data-line data-line-text="您好，我想登記濾心更換提醒，我的機型是：">{ic("line")}<span>登記換濾心提醒</span></a>
</div></section>'''
    page('/filters/', '濾心專區：淨水器濾心對照與更換', '淨水器濾心對照表：依機型查詢對應濾心型號與建議更換週期，台南到府換濾心與 LINE 到期提醒。',
         body, active='/filters/', crumbs=[(None, '濾心專區')])

def build_knowledge():
    cards = ''.join(f'<a class="art-card" href="/knowledge/{x["slug"]}.html"><span class="date">{e(x["date"])}</span><h2>{e(x["title"])}</h2><p>{e(x["desc"])}</p><span class="s-more">閱讀全文 {ic("arrow")}</span></a>' for x in ARTICLES)
    body = f'''<section class="page-hero"><div class="wrap"><span class="eyebrow">水質知識</span><h1>選購與保養前，先看懂這些</h1><p>用簡單的方式整理淨水、軟水與水塔清洗的基本觀念。</p></div></section>
<section class="sec sec-tight"><div class="wrap art-grid">{cards}</div></section>{cta_band()}'''
    page('/knowledge/', '水質知識：淨水器、軟水機與水塔清洗', '淨水器怎麼選、軟水機適合誰、水塔多久洗一次？整理選購與保養前必看的用水知識。',
         body, active='/knowledge/', crumbs=[(None, '水質知識')])
    for x in ARTICLES:
        parts = []
        for blk in x['blocks']:
            if blk[0] == 'p': parts.append(f'<p>{e(blk[1])}</p>')
            elif blk[0] == 'h2': parts.append(f'<h2>{e(blk[1])}</h2>')
            elif blk[0] == 'ul': parts.append('<ul>' + ''.join(f'<li>{e(i)}</li>' for i in blk[1]) + '</ul>')
        src = f'<p class="note">參考資料：<a href="{e(x["source"])}" target="_blank" rel="noopener">{e(x["sourceText"])}</a></p>' if x.get('source') else ''
        others = ''.join(f'<li><a href="/knowledge/{o["slug"]}.html">{e(o["title"])}</a></li>' for o in ARTICLES if o['slug'] != x['slug'])
        body = f'''<article class="article wrap narrow">
  <header><span class="eyebrow">水質知識</span><h1>{e(x["title"])}</h1><p class="date">{e(x["date"])}・{e(SITE["short"])}</p></header>
  <div class="prose">{"".join(parts)}{src}</div>
  <aside class="art-cta"><h2>想直接問我們？</h2><p>傳照片或描述你家的狀況，我們給你具體建議。</p><a class="btn btn-line" href="{e(line_href())}" data-line>{ic("line")}<span>加 LINE 諮詢</span></a></aside>
  <nav class="more-arts"><h2>延伸閱讀</h2><ul>{others}</ul></nav>
</article>'''
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": x['title'], "description": x['desc'], "datePublished": x['date'],
              "author": {"@type": "Organization", "name": SITE['name']}, "publisher": {"@type": "Organization", "name": SITE['name']}}
        page(f'/knowledge/{x["slug"]}.html', x['title'], x['desc'], body, active='/knowledge/',
             crumbs=[('/knowledge/', '水質知識'), (None, x['title'])], ld=ld)

def build_static():
    brands = ''.join(f'<li>{e(b["name"])}</li>' for b in SITE['brands'])
    body = f'''<section class="page-hero"><div class="wrap"><span class="eyebrow">關於我們</span><h1>{e(SITE["name"])}</h1><p class="slogan-lg">{e(SITE.get("slogan",""))}・{e(SITE.get("tagline",""))}</p><p>{e(SITE["description"])}</p></div></section>
<section class="sec sec-tight"><div class="wrap two-col">
  <div class="prose"><h2>我們做什麼</h2>
    <p>{e(SITE["short"])}專注在居家用水的完整解決方案：從水塔、自來水管路的清洗，到全戶淨水、全戶軟水，再到廚房的直輸 RO 與廚下加熱器，以及後續的濾心更換與保養。</p>
    <p>每個家庭的水質、房型與預算都不一樣。我們的做法是先了解你家的狀況，必要時先做水質檢測，再建議真正需要的設備，避免花冤枉錢。</p>
    <h2>我們的原則</h2>
    <ul><li>產品標示建議售價，服務依現場透明報價</li><li>施工前說明流程與內容</li><li>多品牌比較，依需求挑選</li><li>完工後說明使用與保養方式</li></ul>
  </div>
  <div class="hl-box"><h2 class="h-sm">銷售品牌</h2><ul class="brand-list">{brands}</ul>
    <h2 class="h-sm">服務地區</h2><p>{e(SITE["areaNote"])}</p></div>
</div></section>{cta_band()}'''
    page('/about.html', '關於我們', f'{SITE["name"]}：{SITE["description"]}', body, active='/about.html', crumbs=[(None, '關於我們')])

    body = f'''<section class="page-hero"><div class="wrap"><span class="eyebrow">常見問題</span><h1>淨水設備與清洗服務常見問題</h1><p>找不到答案？直接加 LINE 問我們。</p></div></section>
<section class="sec sec-tight"><div class="wrap narrow">{faq_html(SITE["faqs"])}</div></section>{cta_band()}'''
    page('/faq.html', '常見問題', '水塔多久洗一次、廚下加熱器怎麼裝、軟水機要加鹽嗎？淨水設備與清洗服務常見問題。', body,
         active='/faq.html', crumbs=[(None, '常見問題')], ld=faq_ld(SITE['faqs']))

    rows = []
    if C.get('lineId') or C.get('lineUrl'): rows.append(f'<li>{ic("line")}<div><b>LINE</b><a href="{e(line_href())}" data-line>{e(C.get("lineId") or "加入 LINE 好友")}</a></div></li>')
    if C.get('mobile'): rows.append(f'<li>{ic("phone")}<div><b>手機{"（" + e(C["person"]) + "）" if C.get("person") else ""}</b><a href="tel:{tel(C["mobile"])}">{e(C["mobile"])}</a></div></li>')
    if C.get('phone'): rows.append(f'<li>{ic("phone")}<div><b>電話</b><a href="tel:{tel(C["phone"])}">{e(C["phone"])}</a></div></li>')
    if C.get('fax'): rows.append(f'<li>{ic("list")}<div><b>傳真</b><span>{e(C["fax"])}</span></div></li>')
    if C.get('address'): rows.append(f'<li>{ic("pin")}<div><b>地址</b><a href="https://www.google.com/maps/search/?api=1&amp;query={quote(C["address"])}" target="_blank" rel="noopener">{e(C["address"])}</a></div></li>')
    if C.get('hours'): rows.append(f'<li>{ic("list")}<div><b>營業時間</b><span>{e(C["hours"])}</span></div></li>')
    rows.append(f'<li>{ic("pin")}<div><b>服務地區</b><span>{e(SITE["areaNote"])}</span></div></li>')
    pending = '' if (C.get('lineId') or C.get('lineUrl')) else '<p class="notice">LINE 加好友連結準備中，現在請直接來電，或傳簡訊照片到手機。</p>'
    tips = ''.join(f'<li>{ic("check")}{e(t)}</li>' for t in ['您的區域（例如：台南市東區）與房型', '想詢問的設備或服務', '現場照片：櫥下空間、水塔、總進水管或機身型號標籤'])
    body = f'''<section class="page-hero"><div class="wrap"><span class="eyebrow">聯絡我們</span><h1>加 LINE，最快拿到建議與估價</h1><p>傳照片給我們，比電話描述更快更準確。</p></div></section>
<section class="sec sec-tight"><div class="wrap two-col">
  <div class="contact-box">{pending}<ul class="contact-rows">{"".join(rows)}</ul>
    {f'<a class="btn btn-line btn-lg" href="{e(line_href())}" data-line>{ic("line")}<span>加 LINE 免費諮詢</span></a>' if (C.get('lineId') or C.get('lineUrl')) else f'<a class="btn btn-primary btn-lg" href="tel:{tel(C["mobile"])}">{ic("phone")}<span>撥打 {e(C["mobile"])}</span></a>'}</div>
  <div class="hl-box"><h2 class="h-sm">詢問時請提供</h2><ul class="hl-list">{tips}</ul></div>
</div></section>'''
    page('/contact.html', '聯絡我們', f'聯絡{SITE["name"]}：加 LINE 傳照片即可取得淨水設備與清洗服務的初步建議與估價。', body, crumbs=[(None, '聯絡我們')])

    body = f'''<section class="page-hero"><div class="wrap"><span class="eyebrow">互動選購</span><h1>3 步驟找出適合你家的淨水方案</h1><p>回答三個問題，立即看到建議組合，結果可以直接傳到 LINE。</p></div></section>
<section class="sec sec-tight"><div class="wrap narrow">{QUIZ}</div></section>'''
    page('/finder.html', '3 步驟找出適合你家的淨水方案', '回答住宅型態、用水需求與預算三個問題，找出適合的淨水、軟水或清洗方案。', body, crumbs=[(None, '3 步驟找方案')])

    body = f'''<section class="page-hero"><div class="wrap"><span class="eyebrow">404</span><h1>找不到這個頁面</h1><p>頁面可能已移動或更新。</p>
<div class="hero-cta"><a class="btn btn-primary" href="/">回到首頁</a><a class="btn btn-ghost" href="/products/">看品牌商品</a></div></div></section>'''
    page('/404.html', '找不到頁面', '找不到頁面', body)

def build_meta():
    today = datetime.date.today().isoformat()
    urls = ''.join(f'<url><loc>{e(DOMAIN + p)}</loc><lastmod>{today}</lastmod></url>' for p in OUT_PAGES)
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    with open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8') as f:
        if SITE.get('indexable'):
            f.write(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
        else:
            f.write('# 網站建置中，暫不開放搜尋引擎索引（data/site.json 的 indexable 改為 true 即開放）\nUser-agent: *\nDisallow: /\n')

def main():
    for d in ('products', 'services', 'knowledge', 'filters'):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    build_home(); build_products(); build_services(); build_filters(); build_knowledge(); build_static(); build_meta()
    print(f'已產生 {len(OUT_PAGES)} 個頁面（版本 {V}）')

if __name__ == '__main__':
    main()
