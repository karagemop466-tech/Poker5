/* Poker5 — site behavior */

document.addEventListener('DOMContentLoaded', function () {
  initMobileNav();
  initSortableTables();
  initFilter();
  setActiveNav();
  console.log('Poker5 site initialized');
});

/* Mobile nav toggle */
function initMobileNav() {
  const nav = document.querySelector('nav');
  if (!nav) return;
  const btn = document.createElement('button');
  btn.className = 'nav-toggle';
  btn.innerHTML = '&#9776;';
  btn.setAttribute('aria-label', 'Menu');
  btn.style.cssText = 'display:none;border:none;background:none;font-size:1.5rem;cursor:pointer;color:var(--ink);padding:0 12px;';
  nav.insertAdjacentElement('beforebegin', btn);
  btn.addEventListener('click', function () {
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!expanded));
    nav.style.display = expanded ? '' : 'flex';
    nav.style.flexDirection = 'column';
    nav.style.position = 'absolute';
    nav.style.top = 'var(--header-height)';
    nav.style.left = '0';
    nav.style.right = '0';
    nav.style.background = 'var(--surface)';
    nav.style.borderBottom = '1px solid var(--line)';
  });
  const mq = window.matchMedia('(min-width: 721px)');
  mq.addEventListener('change', function (e) {
    if (e.matches) { nav.style.display = ''; btn.style.display = 'none'; }
    else { btn.style.display = ''; }
  });
  if (!mq.matches) btn.style.display = '';
}

/* Make tables sortable (click header) and searchable */
function initSortableTables() {
  document.querySelectorAll('table').forEach(function (table) {
    const headers = table.querySelectorAll('th');
    headers.forEach(function (th, idx) {
      th.style.cursor = 'pointer';
      th.title = 'Sort';
      th.addEventListener('click', function () {
        sortTable(table, idx);
        document.querySelectorAll('table th').forEach(function (h) { h.classList.remove('sort-asc','sort-desc'); });
        th.classList.add(table._lastDir === 'asc' ? 'sort-desc' : 'sort-asc');
      });
    });
  });
}

function sortTable(table, colIdx) {
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const dir = table._lastDir !== 'asc' ? 'asc' : 'desc';
  table._lastDir = dir;
  const numeric = /^[\d$,.]+$/;
  rows.sort(function (a, b) {
    const av = a.children[colIdx] ? a.children[colIdx].innerText.trim() : '';
    const bv = b.children[colIdx] ? b.children[colIdx].innerText.trim() : '';
    const an = numeric.test(av.replace(/[$,]/g, '')) ? parseFloat(av.replace(/[$,]/g, '')) : av;
    const bn = numeric.test(bv.replace(/[$,]/g, '')) ? parseFloat(bv.replace(/[$,]/g, '')) : bv;
    if (an < bn) return dir === 'asc' ? -1 : 1;
    if (an > bn) return dir === 'asc' ? 1 : -1;
    return 0;
  });
  rows.forEach(function (r) { tbody.appendChild(r); });
}

/* Simple text filter for tables with a .filter-input sibling */
function initFilter() {
  document.querySelectorAll('.filter-input').forEach(function (input) {
    const targetId = input.getAttribute('data-target');
    const table = document.getElementById(targetId);
    if (!table) return;
    const tbody = table.querySelector('tbody');
    const rows = tbody ? tbody.querySelectorAll('tr') : [];
    input.addEventListener('input', function () {
      const q = input.value.toLowerCase();
      rows.forEach(function (row) {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
      });
    });
  });
}

/* Highlight active nav item based on filename */
function setActiveNav() {
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.navbar li a').forEach(function (a) {
    const href = a.getAttribute('href');
    if (href === page) a.classList.add('active');
  });
}

/* Accessible: expose sort status for screen readers */
window.addEventListener('load', function () {
  document.querySelectorAll('table th').forEach(function (th) {
    th.setAttribute('role', 'button');
    th.setAttribute('aria-sort', 'none');
  });
});