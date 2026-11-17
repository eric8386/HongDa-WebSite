/* 鴻達淨水 — site interactions */
(function () {
  var SITE = window.SITE || {};

  /* LINE links: prefill message when an official account ID is set */
  function lineLink(text) {
    if (SITE.lineId) {
      return 'https://line.me/R/oaMessage/' + encodeURIComponent(SITE.lineId) + '/?' + encodeURIComponent(text || '');
    }
    return SITE.lineUrl || '/contact.html';
  }
  document.querySelectorAll('[data-line-text]').forEach(function (el) {
    if (SITE.lineId) el.href = lineLink(el.getAttribute('data-line-text'));
  });

  /* mobile nav */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* homepage water-path diagram */
  document.querySelectorAll('[data-flow-root]').forEach(function (root) {
    var nodes = root.querySelectorAll('.flow-node');
    var detail = root.querySelector('.flow-detail');
    function show(i) {
      nodes.forEach(function (n, j) {
        n.classList.toggle('on', i === j);
        n.setAttribute('aria-pressed', i === j ? 'true' : 'false');
      });
      var tpl = nodes[i].parentNode.querySelector('template');
      detail.innerHTML = tpl.innerHTML;
    }
    nodes.forEach(function (n, i) { n.addEventListener('click', function () { show(i); }); });
    show(0);
  });

  /* product catalog filters (state kept in URL) */
  document.querySelectorAll('[data-catalog]').forEach(function (root) {
    var params = new URLSearchParams(location.search);
    var state = { cat: params.get('cat') || '', brand: params.get('brand') || '' };
    var cards = root.querySelectorAll('.p-card');
    var count = root.querySelector('.result-count');
    var empty = root.querySelector('.empty');
    function apply() {
      var n = 0;
      cards.forEach(function (c) {
        var ok = (!state.cat || c.dataset.cat === state.cat) && (!state.brand || c.dataset.brand === state.brand);
        c.hidden = !ok;
        if (ok) n++;
      });
      root.querySelectorAll('.fchip').forEach(function (b) {
        b.classList.toggle('on', state[b.dataset.f] === b.dataset.v);
        b.setAttribute('aria-pressed', state[b.dataset.f] === b.dataset.v ? 'true' : 'false');
      });
      count.textContent = '共 ' + n + ' 項產品';
      empty.hidden = n > 0;
      var q = new URLSearchParams();
      if (state.cat) q.set('cat', state.cat);
      if (state.brand) q.set('brand', state.brand);
      var qs = q.toString();
      history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
    }
    root.querySelectorAll('.fchip').forEach(function (b) {
      b.addEventListener('click', function () { state[b.dataset.f] = b.dataset.v; apply(); });
    });
    apply();
  });

  /* 3-step finder quiz */
  var LABEL = {
    home: { apt: '公寓／大樓', house: '透天／獨棟' },
    need: { drink: '想直接生飲', scale: '水垢、洗澡用水', tank: '水塔、水管髒污', all: '全屋一次規劃' },
    budget: { low: '2 萬以內', mid: '2～6 萬', high: '6 萬以上', unsure: '還不確定' }
  };
  var R = {
    heater: { t: '廚下加熱器', d: '接在淨水設備後，熱水、冰水即開即用', h: '/products/under-sink-heater/' },
    ro: { t: '直輸 RO 淨水器', d: '過濾精度最高的生飲方案，需電源與排水', h: '/products/ro/' },
    whole: { t: '全戶前置過濾', d: '總進水端攔截泥沙鐵鏽，保護全屋設備', h: '/products/whole-house/' },
    soft: { t: '全戶軟水機', d: '降低硬度，減少熱水器與衛浴水垢', h: '/products/water-softener/' },
    tank: { t: '水塔清洗', d: '建議至少每半年清洗一次', h: '/services/tank-cleaning.html' },
    pipe: { t: '自來水管路清洗', d: '清除管內鏽垢與沉積物', h: '/services/pipe-cleaning.html' },
    test: { t: '先做水質檢測', d: '量測硬度等指標，再決定需要哪種設備', h: '/services/water-test.html' }
  };
  function recommend(a) {
    var out = [];
    if (a.need === 'drink') out = a.budget === 'low' ? [R.ro, R.test] : [R.ro, R.heater];
    else if (a.need === 'scale') out = a.budget === 'low' ? [R.test, R.whole] : [R.soft, R.whole, R.test];
    else if (a.need === 'tank') out = a.home === 'house' ? [R.tank, R.pipe, R.whole] : [R.tank, R.pipe];
    else out = a.budget === 'low' ? [R.test, R.ro, R.tank]
      : a.home === 'house' ? [R.whole, R.soft, R.ro, R.tank] : [R.ro, R.whole, R.tank];
    if (a.budget === 'unsure' && out.indexOf(R.test) < 0) out.push(R.test);
    return out;
  }
  document.querySelectorAll('[data-quiz]').forEach(function (quiz) {
    var steps = quiz.querySelectorAll('.q-step');
    var marks = quiz.querySelectorAll('.quiz-steps li');
    var prev = quiz.querySelector('[data-prev]');
    var form = quiz.querySelector('.quiz-form');
    var result = quiz.querySelector('.q-result');
    var cur = 0;
    function go(i) {
      cur = i;
      steps.forEach(function (s, j) { s.classList.toggle('on', j === i); });
      marks.forEach(function (m, j) { m.classList.toggle('on', j <= i); });
      prev.hidden = i === 0;
    }
    function answers() {
      var a = {};
      ['home', 'need', 'budget'].forEach(function (k) {
        var el = form.querySelector('input[name="' + k + '"]:checked');
        a[k] = el ? el.value : '';
      });
      return a;
    }
    function finish() {
      var a = answers();
      var recs = recommend(a);
      var sum = LABEL.home[a.home] + '・' + LABEL.need[a.need] + '・預算' + LABEL.budget[a.budget];
      var msg = '您好，我用網站 3 步驟測驗：' + sum + '。想請你們幫我評估適合的方案。';
      var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
      result.innerHTML =
        '<h3>建議你可以先看這些方案</h3><p class="q-sum">' + esc(sum) + '</p><ul class="q-recs">' +
        recs.map(function (r) {
          return '<li><a href="' + r.h + '"><span><b>' + esc(r.t) + '</b><small>' + esc(r.d) + '</small></span>' +
            '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a></li>';
        }).join('') +
        '</ul><div class="q-actions"><a class="btn btn-line" href="' + esc(lineLink(msg)) + '">把結果傳到 LINE 請專人評估</a>' +
        '<button type="button" class="btn btn-ghost" data-restart>重新測驗</button></div>';
      form.hidden = true;
      quiz.querySelector('.quiz-steps').hidden = true;
      result.hidden = false;
      result.querySelector('[data-restart]').addEventListener('click', function () {
        form.reset(); form.hidden = false; result.hidden = true; quiz.querySelector('.quiz-steps').hidden = false; go(0);
      });
    }
    form.addEventListener('change', function (ev) {
      if (ev.target.type !== 'radio') return;
      setTimeout(function () { if (cur < steps.length - 1) go(cur + 1); else finish(); }, 180);
    });
    prev.addEventListener('click', function () { if (cur > 0) go(cur - 1); });
    go(0);
  });
})();
