import { events, hotels, lastVerified, roomTax, routes } from './data.mjs';

const eventGrid = document.querySelector('#event-grid');
const emptyState = document.querySelector('#empty-state');
const eventCount = document.querySelector('#event-count');
const searchInput = document.querySelector('#event-search');
const filterButtons = [...document.querySelectorAll('[data-filter]')];
let activeFilter = 'all';
let searchTerm = '';

const statusText = {
  single: 'Single-entry overall verified',
  multi: 'More than one bullet confirmed',
  unknown: 'Entry cap not verified',
  restricted: 'Restricted access',
};

function make(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function makeLink(label, url, className = 'source-link') {
  const link = make('a', className, label);
  link.href = url;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  return link;
}

function addSources(container, sources) {
  if (!sources?.length) return;
  const details = make('details', 'source-details');
  const summary = make('summary', '', `Official sources (${sources.length})`);
  const list = make('div', 'source-links');
  for (const source of sources) list.append(makeLink(source.label, source.url));
  details.append(summary, list);
  container.append(details);
}

function eventCard(event) {
  const card = make('article', `event-card status-${event.status}`);
  card.dataset.status = event.status;

  const top = make('div', 'event-card-top');
  const series = make('span', 'event-series', event.series);
  const status = make('span', `status-badge badge-${event.status}`, statusText[event.status]);
  top.append(series, status);

  const heading = make('div', 'event-card-heading');
  heading.append(make('p', 'event-date', event.date));
  heading.append(make('h3', '', event.title));
  heading.append(make('p', 'event-venue', event.venue));

  const facts = make('dl', 'event-facts');
  const factsData = [
    ['Buy-in', event.buyIn],
    ['Format', event.format],
  ];
  for (const [label, value] of factsData) {
    const row = make('div', 'event-fact');
    row.append(make('dt', '', label), make('dd', '', value));
    facts.append(row);
  }

  const ruleBox = make('div', 'entry-rule');
  ruleBox.append(make('p', 'entry-rule-label', 'Entry rule'), make('p', 'entry-rule-text', event.rule));

  const caveat = make('p', 'event-caveat', event.caveat);
  const footer = make('div', 'event-card-footer');
  footer.append(make('span', 'verified-date', `Checked ${lastVerified}`));
  const sourceWrap = make('div', 'event-sources');
  addSources(sourceWrap, event.sources);
  footer.append(sourceWrap);

  card.append(top, heading, facts, ruleBox, caveat, footer);
  return card;
}

function eventMatches(event) {
  const matchesFilter = activeFilter === 'all' || event.status === activeFilter;
  if (!matchesFilter) return false;
  if (!searchTerm) return true;
  const searchSpace = [
    event.title,
    event.series,
    event.venue,
    event.date,
    event.buyIn,
    event.format,
    event.statusLabel,
    event.rule,
    event.caveat,
  ].join(' ').toLowerCase();
  return searchSpace.includes(searchTerm);
}

function renderEvents() {
  const visible = events
    .filter(eventMatches)
    .sort((a, b) => a.sortDate.localeCompare(b.sortDate) || a.title.localeCompare(b.title));
  eventGrid.replaceChildren(...visible.map(eventCard));
  eventGrid.hidden = visible.length === 0;
  emptyState.hidden = visible.length !== 0;

  if (activeFilter === 'single' && !searchTerm) {
    eventCount.textContent = 'No events meet the single-entry-overall standard';
  } else {
    eventCount.textContent = `Showing ${visible.length} of ${events.length} researched series and routines`;
  }

  const emptyHeading = emptyState.querySelector('h3');
  const emptyCopy = emptyState.querySelector('p:not(.eyebrow)');
  if (activeFilter === 'single' && !searchTerm) {
    emptyHeading.textContent = 'No single-entry-overall event is confirmed.';
    emptyCopy.textContent = 'We only use this label when the current official terms rule out re-entry, rebuys and additional starting-flight or Day 2 entries. A “1Day” schedule label is not enough.';
  } else {
    emptyHeading.textContent = 'No findings match that search.';
    emptyCopy.textContent = 'Try another venue, tournament name or entry-rule term—or reset the filters to see the full research list.';
  }
}

function setFilter(filter) {
  activeFilter = filter;
  for (const button of filterButtons) {
    const selected = button.dataset.filter === filter;
    button.classList.toggle('is-active', selected);
    button.setAttribute('aria-pressed', String(selected));
  }
  renderEvents();
}

filterButtons.forEach((button) => {
  button.addEventListener('click', () => setFilter(button.dataset.filter));
});

searchInput.addEventListener('input', () => {
  searchTerm = searchInput.value.trim().toLowerCase();
  renderEvents();
});

document.querySelector('[data-reset-filters]').addEventListener('click', () => {
  searchInput.value = '';
  searchTerm = '';
  setFilter('all');
  searchInput.focus();
});

function renderStats() {
  const counts = {
    single: events.filter((event) => event.status === 'single').length,
    multi: events.filter((event) => event.status === 'multi').length,
    unknown: events.filter((event) => event.status === 'unknown').length,
    restricted: events.filter((event) => event.status === 'restricted').length,
    all: events.length,
  };
  for (const [key, value] of Object.entries(counts)) {
    document.querySelectorAll(`[data-stat="${key}"], [data-filter-count="${key}"]`).forEach((node) => {
      node.textContent = String(value);
    });
  }
  document.querySelectorAll('[data-last-verified]').forEach((node) => {
    node.textContent = lastVerified;
  });
  document.querySelector('[data-tax-rate]').textContent = roomTax.rate;
}

function renderHotels() {
  const container = document.querySelector('#hotel-grid');
  const cards = hotels.map((hotel) => {
    const card = make('article', 'hotel-card');
    const top = make('div', 'hotel-card-top');
    top.append(make('span', 'hotel-index', hotel.id.toUpperCase()), make('span', 'room-size', hotel.size));
    card.append(top);
    card.append(make('p', 'hotel-room-label', hotel.room));
    card.append(make('h3', '', hotel.name));
    card.append(make('p', 'hotel-detail', hotel.detail));
    const signal = make('div', 'hotel-signal');
    signal.append(make('span', 'signal-mark', '✦'), make('p', '', hotel.signal));
    card.append(signal);
    const sample = make('div', 'hotel-sample');
    sample.append(make('span', 'sample-tag', hotel.sampleTag), make('p', '', hotel.sample));
    card.append(sample);
    const links = make('div', 'hotel-card-links');
    links.append(makeLink(hotel.bookingLabel, hotel.booking, 'hotel-primary-link'));
    addSources(links, hotel.sources);
    card.append(links);
    return card;
  });
  container.replaceChildren(...cards);
}

function renderRoutes() {
  const container = document.querySelector('#routes-grid');
  const cards = routes.map((route) => {
    const card = make('article', 'route-card');
    const path = make('p', 'route-path');
    path.append(make('span', '', route.from), make('span', 'route-arrow', '→'), make('span', '', route.to));
    const detail = make('div', 'route-detail');
    detail.append(make('strong', '', route.distance), make('span', '', route.time));
    card.append(path, detail, make('p', 'route-note', route.note), makeLink(route.source.label, route.source.url, 'route-source'));
    return card;
  });
  container.replaceChildren(...cards);
}

renderStats();
renderHotels();
renderRoutes();
renderEvents();
