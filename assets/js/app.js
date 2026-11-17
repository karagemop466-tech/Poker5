// Filters and the trip-cost calculator. No network calls, no dependencies.
(() => {
  const tables = [...document.querySelectorAll('table[data-table]')];
  const bar = document.querySelector('[data-tools]');
  const q = bar && bar.querySelector('[data-q]');
  const from = bar && bar.querySelector('[data-from]');
  const to = bar && bar.querySelector('[data-to]');
  const onlyConfirmed = bar && bar.querySelector('[data-only-confirmed]');
  const hideCont = bar && bar.querySelector('[data-hide-cont]');
  const changedOnly = bar && bar.querySelector('[data-changed-only]');
  const walk30 = bar && bar.querySelector('[data-walk30]');
  const count = bar && bar.querySelector('[data-count]');
  const norm = (s) => (s || '').toLowerCase().replace(/\s+/g, ' ').trim();

  function apply() {
    const needle = norm(q && q.value);
    const f = from && from.value ? from.value : '';
    const t = to && to.value ? to.value : '';
    let shown = 0, total = 0;
    for (const tb of tables) {
      for (const tr of tb.querySelectorAll('tr[data-status],tr[data-date]')) {
        total++;
        const st = tr.dataset.status || '';
        const d = tr.dataset.date || '';
        let ok = true;
        if (needle && !norm(tr.textContent).includes(needle)) ok = false;
        if (ok && d && (f && d < f)) ok = false;
        if (ok && d && (t && d > t)) ok = false;
        if (ok && onlyConfirmed && onlyConfirmed.checked && st !== 'confirmed-single') ok = false;
        if (ok && hideCont && hideCont.checked && st === 'continuation') ok = false;
        if (ok && changedOnly && changedOnly.checked && tr.dataset.changed !== '1') ok = false;
        if (ok && walk30 && walk30.checked && !(Number(tr.dataset.walk) <= 30)) ok = false;
        tr.hidden = !ok;
        if (ok) shown++;
      }
    }
    if (count) count.textContent = `${shown} of ${total} rows shown`;
  }
  // sortable headers: click to order by that column, click again to reverse
  let sortKey = '';
  for (const tb of tables) {
    for (const head of tb.querySelectorAll('th[data-sort]')) {
      const col = Number(head.dataset.sort);
      head.classList.add('sortable');
      head.addEventListener('click', () => {
        const key = `${tb.dataset.table || ''}#${col}`;
        const dir = sortKey === key ? (head.getAttribute('aria-sort') === 'ascending' ? -1 : 1) : 1;
        for (const o of tb.querySelectorAll('th[data-sort]')) o.removeAttribute('aria-sort');
        head.setAttribute('aria-sort', dir === 1 ? 'ascending' : 'descending');
        sortKey = key;
        const body = [...tb.querySelectorAll('tr[data-status],tr[data-date]')];
        const val = (tr) => { const c = tr.children[col]; return c ? (c.dataset.v !== undefined ? c.dataset.v : c.textContent.trim()) : ''; };
        body.sort((a, b) => {
          const x = val(a), y = val(b);
          const nx = Number(x), ny = Number(y);
          const cmp = (Number.isFinite(nx) && Number.isFinite(ny) && x !== '' && y !== '') ? nx - ny : String(x).localeCompare(String(y), 'en', { numeric: true });
          return cmp * dir;
        });
        const frag = document.createDocumentFragment();
        for (const tr of body) frag.appendChild(tr);
        tb.appendChild(frag);
      });
    }
  }
  if (tables.length) {
  bar && bar.addEventListener('input', apply);
  bar && bar.addEventListener('change', apply);
    apply();
  }

  // ---------- trip calculator ----------
  const calc = document.querySelector('[data-calc]');
  if (!calc) return;
  const list = calc.querySelector('[data-entrylist]');
  const sel = calc.querySelector('[data-entryadd]');
  const num = (el) => (el.value === '' ? null : Number(el.value));
  const money = (n) => '$' + n.toLocaleString('en-US', { maximumFractionDigits: 2 });

  function prefill() {
    [...sel.options].filter((o) => o.dataset.prefill === '1').slice(0, 2).forEach((o) => add(o));
  }
  function add(opt) {
    if (!opt) return;
    const row = document.createElement('div');
    row.className = 'erow';
    row.innerHTML = `<span class="lab">${opt.dataset.label}</span>
      <label>count<input type="number" min="1" value="1"></label>
      <span>$<b class="fee">${Number(opt.value).toLocaleString()}</b> each</span>
      <button type="button" title="remove">×</button>`;
    row.querySelector('button').onclick = () => { row.remove(); recalc(); };
    row.querySelector('input').oninput = recalc;
    row.dataset.fee = opt.value;
    list.appendChild(row);
  }
  sel.onchange = () => { add(sel.options[sel.selectedIndex]); sel.selectedIndex = 0; recalc(); };
  calc.querySelector('[data-add]').onclick = () => { add(sel.options[sel.selectedIndex] || sel.options[0]); recalc(); };
  const cin = calc.querySelector('[data-in]'), cout = calc.querySelector('[data-out]');
  const nights = calc.querySelector('[data-nights]');
  const rate = calc.querySelector('[data-rate]'), fee = calc.querySelector('[data-fee]');
  const tax = calc.querySelector('[data-tax]'), park = calc.querySelector('[data-park]');
  const total = calc.querySelector('[data-total]'), brk = calc.querySelector('[data-break]');
  [cin, cout].forEach((i) => (i.oninput = () => {
    const a = Date.parse(cin.value), b = Date.parse(cout.value);
    if (!Number.isNaN(a) && !Number.isNaN(b) && b > a) nights.value = Math.round((b - a) / 864e5);
    recalc();
  }));
  [nights, rate, fee, tax, park].forEach((i) => (i.oninput = recalc));

  function recalc() {
    let entries = 0, entrySum = 0;
    for (const r of list.querySelectorAll('.erow')) {
      const c = Number(r.querySelector('input').value) || 0;
      entries += c; entrySum += c * Number(r.dataset.fee);
    }
    const n = Number(nights.value) || 0;
    const parts = [];
    let hotel = null, perNight = null;
    const r = num(rate), f = num(fee), tx = num(tax), pk = num(park);
    if (r != null && f != null && tx != null) {
      perNight = r + f + (r * tx) / 100;
      if (pk != null && n) perNight += pk / n;
      hotel = perNight * n;
      parts.push(['room rate / night', money(r)]);
      parts.push(['resort fee / night', money(f)]);
      parts.push([`tax ${tx}% of rate`, money((r * tx) / 100)]);
      if (pk != null) parts.push(['parking / night', money(n ? pk / n : pk)]);
      parts.push(['true cost / night', money(perNight)]);
    }
    const show = (label, v) => `<li><span>${label}</span><b>${v == null ? 'unknown — no official value' : v}</b></li>`;
    brk.innerHTML = [
      show('entries', entries),
      show('entry fees total', entries ? money(entrySum) : null),
      show('nights', n),
      ...parts.map(([label, v]) => show(label, v)),
      hotel == null ? show('hotel total', null) : show('hotel total', money(hotel)),
      `<li><span>formula</span><b>${entries} × entry fee + ${n} × true nightly cost</b></li>`,
    ].join('');
    total.textContent = hotel == null && entries === 0 ? '—' : money((entrySum || 0) + (hotel || 0)) + (hotel == null ? ' + hotel (unknown)' : '');
    if (hotel == null) total.innerHTML = money(entrySum) + ' <span class="sub">+ hotel unknown</span>';
  }
  prefill(); recalc();
})();
