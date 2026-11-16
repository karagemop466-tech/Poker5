import { events, hotels, lastVerified, roomTax, routes } from './data.mjs';

function make(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function link(label, url) {
  const anchor = make('a', 'ledger-link', label);
  anchor.href = url;
  anchor.target = '_blank';
  anchor.rel = 'noopener noreferrer';
  return anchor;
}

function renderEventSources() {
  const container = document.querySelector('#source-events');
  const nodes = [...events]
    .sort((a, b) => a.sortDate.localeCompare(b.sortDate) || a.title.localeCompare(b.title))
    .map((event) => {
      const card = make('article', `ledger-card ledger-event status-${event.status}`);
      const header = make('div', 'ledger-card-heading');
      const headingText = make('div');
      headingText.append(make('p', 'ledger-card-date', `${event.date} · ${event.venue}`));
      headingText.append(make('h3', '', event.title));
      header.append(headingText, make('span', `status-badge badge-${event.status}`, event.statusLabel));
      card.append(header);
      card.append(make('p', 'ledger-card-detail', event.rule));
      card.append(make('p', 'ledger-caveat', event.caveat));
      const list = make('ul', 'ledger-source-list');
      for (const source of event.sources) {
        const item = make('li');
        item.append(link(source.label, source.url));
        list.append(item);
      }
      card.append(list);
      return card;
    });
  container.replaceChildren(...nodes);
}

function renderHotelSources() {
  const container = document.querySelector('#source-hotels');
  const nodes = hotels.map((hotel) => {
    const card = make('article', 'ledger-card ledger-hotel');
    const header = make('div', 'ledger-card-heading');
    const title = make('div');
    title.append(make('p', 'ledger-card-date', `${hotel.room} · ${hotel.size}`));
    title.append(make('h3', '', hotel.name));
    header.append(title);
    card.append(header, make('p', 'ledger-card-detail', hotel.sample), make('p', 'ledger-caveat', hotel.signal));
    const list = make('ul', 'ledger-source-list');
    for (const source of hotel.sources) {
      const item = make('li');
      item.append(link(source.label, source.url));
      list.append(item);
    }
    card.append(list);
    return card;
  });
  container.replaceChildren(...nodes);
}

function renderRouteSources() {
  const container = document.querySelector('#source-routes');
  const nodes = routes.map((route) => {
    const card = make('article', 'route-card');
    const path = make('p', 'route-path');
    path.append(make('span', '', route.from), make('span', 'route-arrow', '→'), make('span', '', route.to));
    const detail = make('div', 'route-detail');
    detail.append(make('strong', '', route.distance), make('span', '', route.time));
    card.append(path, detail, make('p', 'route-note', route.note), link(route.source.label, route.source.url));
    return card;
  });
  container.replaceChildren(...nodes);
}

document.querySelectorAll('[data-last-verified]').forEach((node) => {
  node.textContent = lastVerified;
});
document.querySelectorAll('[data-tax-rate]').forEach((node) => {
  node.textContent = roomTax.rate;
});
renderEventSources();
renderHotelSources();
renderRouteSources();
