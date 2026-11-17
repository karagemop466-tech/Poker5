(() => {
  'use strict';

  const body = document.body;
  const ROOT = body.dataset.root || '.';
  const PAGE = body.dataset.page || 'home';
  const VENUE_ID = body.dataset.venue || '';
  const routeFiles = {
    home: 'index.html', tournaments: 'tournaments.html', hotels: 'hotels.html',
    venues: 'venues.html', sources: 'sources.html', method: 'method.html'
  };
  const routeNames = {
    home: 'Overview', tournaments: 'Schedule', hotels: 'Hotels & budget',
    venues: 'Venues', sources: 'Sources', method: 'Method & limits'
  };
  const href = (route) => `${ROOT}/${routeFiles[route] || routeFiles.home}`;
  const venueHref = (id) => `${ROOT}/venues/${encodeURIComponent(id)}.html`;
  const dataFiles = { events: 'tournaments', hotels: 'hotels', venues: 'venues', 'source-ledger': 'source-ledger' };
  const assetData = (name) => `${ROOT}/data/${dataFiles[name] || name}.json`;
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
  const money = (value, digits = 0) => value == null || value === '' ? 'Unknown' : new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'USD', minimumFractionDigits: digits, maximumFractionDigits: digits
  }).format(Number(value));
  const dates = (iso) => {
    if (!iso) return 'Date not listed';
    const [y, m, d] = iso.split('-').map(Number);
    return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(y, m - 1, d));
  };
  const dateShort = (iso) => {
    if (!iso) return '—';
    const [y, m, d] = iso.split('-').map(Number);
    return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(new Date(y, m - 1, d));
  };
  const clock = (value) => {
    if (!value) return 'Time not stated';
    const raw = String(value).trim();
    const match = raw.match(/^(\d{1,2}):(\d{2})$/);
    if (!match) return raw;
    let hours = Number(match[1]);
    const minutes = match[2];
    const suffix = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    return `${hours}:${minutes} ${suffix}`;
  };
  const compactStatus = (status) => ({
    'unconfirmed': 'Entry terms unknown',
    'multiple-entry': 'Multiple entry confirmed',
    'conflicting': 'Official sources conflict',
    'continuation': 'Continuation only',
    'single-entry': 'Single-entry confirmed'
  }[status] || status || 'Entry terms unknown');
  const statusClass = (status) => ({
    'unconfirmed': 'unknown', 'multiple-entry': 'multiple', 'conflicting': 'conflict',
    'continuation': 'continuation', 'single-entry': 'confirmed'
  }[status] || 'unknown');

  let tournaments;
  let hotels;
  let venues;
  let sourceMap;
  let venueMap;
  const selectedEventIds = new Set();

  function renderHeader() {
    const links = Object.entries(routeNames).map(([key, label]) => {
      const current = PAGE === key || (PAGE === 'venue' && key === 'venues');
      return `<a href="${esc(href(key))}"${current ? ' aria-current="page"' : ''}>${esc(label)}</a>`;
    }).join('');
    const header = document.getElementById('site-header');
    if (!header) return;
    header.innerHTML = `<a class="skip-link" href="#main">Skip to content</a>
      <header class="site-header"><div class="nav-shell">
        <a class="brand" href="${esc(href('home'))}" aria-label="Poker5 planner overview"><span class="brand-mark" aria-hidden="true">♠</span><span><b>Poker5</b><small>OFFICIAL-SOURCE TRIP PLANNER</small></span></a>
        <nav class="site-nav" aria-label="Main navigation">${links}</nav>
      </div></header>`;
  }

  function renderFooter() {
    const footer = document.getElementById('site-footer');
    if (!footer) return;
    footer.innerHTML = `<footer class="site-footer"><div class="container footer-inner">
      <div><strong>Research snapshot checked Nov 17, 2026.</strong><p>Dec 13–20, 2026 is a working window, not travel dates selected by the user. Poker and hotel terms change; confirm directly before booking or registering. Not affiliated with a casino, hotel or tour operator.</p></div>
      <div class="footer-links"><a href="${esc(href('sources'))}">Official-source ledger</a><a href="${esc(href('method'))}">Entry-rule standard</a><a href="${esc(`${ROOT}/../index.html`)}">Main Poker5 site</a></div>
    </div></footer>`;
  }

  function sourceLinks(ids, compact = false) {
    return (ids || []).map((id) => {
      const source = sourceMap[id];
      if (!source) return '';
      let label = source.title;
      if (compact) {
        const sheet = id.match(/^venetian-structure-(\d{2})$/);
        if (sheet) label = `DSE sheet ${Number(sheet[1])}`;
        else if (id.includes('schedule')) label = 'Schedule';
        else if (id.includes('structure')) label = 'Structure / rules';
        else if (id.includes('booking') || id.includes('rate-snapshot')) label = 'Booking / rate';
        else if (id.includes('fee')) label = 'Fee policy';
        else if (id.includes('parking')) label = 'Parking policy';
        else if (id.includes('contact') || id.includes('address')) label = 'Official address';
        else label = source.title.length > 30 ? `${source.title.slice(0, 27)}…` : source.title;
      }
      return `<a class="source-link" href="${esc(source.url)}" target="_blank" rel="noopener noreferrer" aria-label="${esc(source.title)}" title="${esc(source.title)}">${esc(label)} ↗</a>`;
    }).join('');
  }

  function entryValue(fact, label) {
    if (!fact || typeof fact !== 'object') return 'Unknown — not stated in the reviewed source.';
    let value = fact.value;
    let summary = '';
    if (fact.status === 'unknown') summary = 'Unknown';
    else if (fact.status === 'allowed') summary = 'Allowed';
    else if (fact.status === 'capped') summary = 'Capped';
    else if (fact.status === 'not-applicable') summary = 'Not applicable';
    else if (fact.status === 'published') summary = 'Published';
    else if (fact.status === 'conflicting') summary = 'Conflict';
    else summary = fact.status || 'Not stated';
    if (value !== undefined && value !== null && value !== '') {
      if (typeof value === 'number') {
        const countFact = label === 'Total entry cap' || label === 'Re-entry';
        summary += ` · ${countFact ? `${value} ${value === 1 ? 'entry' : 'entries'}` : money(value)}`;
      } else if (typeof value === 'string') summary += ` · ${value}`;
      else if (typeof value === 'object') {
        const detail = [];
        if (value.amountUsd != null) detail.push(money(value.amountUsd));
        if (value.chips != null) detail.push(`${Number(value.chips).toLocaleString('en-US')} chips`);
        if (value.timing) detail.push(value.timing);
        if (detail.length) summary += ` · ${detail.join(', ')}`;
      }
    }
    const note = fact.note || '';
    return `<strong>${esc(summary)}</strong>${note ? `<span>${esc(note)}</span>` : ''}`;
  }

  function feeBreakdown(event) {
    const b = event.buyInBreakdownUsd;
    if (!b) return '<p class="unknown-copy">Fee split not stated in the reviewed official source.</p>';
    const parts = [
      ['Player prize pool', b.playerPrizePoolUsd ?? b.prizePoolUsd],
      ['Tournament fee', b.tournamentFeeUsd],
      ['House fee', b.houseFeeUsd],
      ['Poker staff service charge', b.pokerStaffServiceChargeUsd]
    ].filter(([, value]) => value !== undefined && value !== null);
    const rows = parts.map(([label, value]) => `<div class="fee-line"><span>${esc(label)}</span><b>${money(value)}</b></div>`).join('');
    const discount = b.earlyDiscountUsd == null ? '' : `<div class="fee-line discount"><span>Eligible pre-start fee discount</span><b>−${money(b.earlyDiscountUsd)}</b></div><p class="micro-note">${esc(b.earlyDiscountNote || '')}</p>`;
    const note = b.note ? `<p class="micro-note">${esc(b.note)}</p>` : '';
    return `${rows || '<p class="unknown-copy">Breakdown components not specified.</p>'}${discount}${note}`;
  }

  function eventCard(event, options = {}) {
    const venue = venueMap[event.venueId];
    const status = event.entryStatus || 'unconfirmed';
    const isContinuation = event.recordType === 'continuation';
    const dateLabel = event.endDate && event.endDate !== event.date ? `${dateShort(event.date)}–${dateShort(event.endDate)}` : dateShort(event.date);
    const scheduleBadge = event.windowRole === 'recurring-schedule' ? '<span class="tag tag-warn">Recurring pattern · verify date</span>' : '';
    const continuationBadge = isContinuation ? '<span class="tag tag-neutral">No fresh entry</span>' : '';
    const canSelect = !isContinuation && event.recordType === 'entry' && event.buyInUsd != null;
    const select = options.showSelect && canSelect
      ? `<label class="budget-check"><input class="event-budget-check" type="checkbox" data-event-id="${esc(event.id)}" ${selectedEventIds.has(event.id) ? 'checked' : ''}><span>Count one listed buy-in</span></label>` : '';
    const guarantee = event.guaranteeUsd == null ? '' : `<span class="meta-pill">${money(event.guaranteeUsd)} ${event.guaranteeType === 'bounty-inclusive' ? 'bounty-inclusive guarantee' : 'published guarantee'}</span>`;
    const statusLabel = `<span class="status-pill ${statusClass(status)}">${esc(compactStatus(status))}</span>`;
    const notes = (event.notes || []).map((note) => `<li>${esc(note)}</li>`).join('');
    const sources = sourceLinks(event.sourceIds, true);
    const eventLink = venue ? `<a class="venue-inline" href="${esc(venueHref(venue.id))}">${esc(venue.property)} ↗</a>` : esc(event.venueId || 'Venue not verified');
    const timeNote = event.timeNote ? `<span class="time-note">${esc(event.timeNote)}</span>` : '';
    const timeBadge = event.time ? `<span>${esc(clock(event.time))} local</span>` : `<span>Time not published</span>`;
    const specialFee = event.optionalStaffGratuity
      ? `<p class="gratuity-note"><b>Optional staff gratuity, not an add-on:</b> ${money(event.optionalStaffGratuity.amountUsd)} for ${Number(event.optionalStaffGratuity.chips).toLocaleString('en-US')} chips. ${esc(event.optionalStaffGratuity.note || '')}</p>` : '';
    const facts = [
      ['Total entry cap', event.totalEntryCap], ['Re-entry', event.reEntry],
      ['Rebuy', event.rebuy], ['Add-on', event.addOn]
    ].map(([label, fact]) => `<div class="fact"><dt>${esc(label)}</dt><dd>${entryValue(fact, label)}</dd></div>`).join('');
    const late = event.lateRegistration || { status: 'unknown', note: 'Not stated.' };
    const feeUnknown = !event.buyInBreakdownUsd;
    const guaranteeNote = event.guaranteeNote ? `<p class="micro-note">${esc(event.guaranteeNote)}</p>` : '';
    const details = `<details class="event-details"><summary>Entry rules, fees & citations</summary>
      <dl class="fact-grid">${facts}<div class="fact"><dt>Late registration</dt><dd>${entryValue(late, 'Late registration')}</dd></div></dl>
      <div class="detail-columns"><section><h4>Buy-in fee components</h4>${feeBreakdown(event)}${specialFee}</section>
      <section><h4>Guarantee</h4>${event.guaranteeUsd == null ? `<p class="unknown-copy">${esc(event.guaranteeNote || 'No guarantee was established in the reviewed event-specific source.')}</p>` : `<p>${money(event.guaranteeUsd)}${event.guaranteeType === 'bounty-inclusive' ? ' · includes bounty awards per the structure sheet' : ''}</p>${guaranteeNote}`}
      ${event.multiFlightRestriction ? `<p class="callout-mini"><b>Bagging restriction:</b> ${esc(event.multiFlightRestriction.note)}</p>` : ''}</section></div>
      ${notes ? `<ul class="event-notes">${notes}</ul>` : ''}<div class="source-row">${sources || '<span class="unknown-copy">No linked official source record.</span>'}</div>
    </details>`;
    return `<article class="event-card ${isContinuation ? 'is-continuation' : ''}" data-event-card="${esc(event.id)}">
      <div class="event-date"><b>${esc(dateLabel)}</b><span>${esc(event.eventNumber || event.series || '')}</span></div>
      <div class="event-main"><div class="event-heading"><h3>${esc(event.title)}</h3>${statusLabel}</div>
        <div class="event-meta"><span>${eventLink}</span>${timeBadge}<span>${esc(event.game || 'Game not specified')}</span>${event.format ? `<span>${esc(event.format)}</span>` : ''}${event.buyInUsd == null ? '' : `<b class="buyin-chip">Buy-in ${money(event.buyInUsd)}</b>`}${guarantee}</div>
        ${timeNote ? `<p class="time-note">${timeNote}</p>` : ''}
        ${event.scheduleBasis ? `<p class="schedule-basis">${esc(event.scheduleBasis)}</p>` : ''}
        ${(event.notes || []).length && options.compactNotes ? `<p class="event-brief">${esc(event.notes[0])}</p>` : ''}
        <div class="event-actions">${details}${scheduleBadge}${continuationBadge}${select}</div>
      </div>
    </article>`;
  }

  function statusCounts(events) {
    const counts = {};
    for (const event of events) counts[event.entryStatus] = (counts[event.entryStatus] || 0) + 1;
    return counts;
  }

  function eventPool(start, end) {
    return tournaments.events.filter((event) => {
      const eventEnd = event.endDate || event.date;
      return event.date <= end && eventEnd >= start;
    });
  }

  function renderEventFilters({ mount, full = true, limit = 0, budget = false }) {
    const metaWindow = tournaments.meta.window;
    const root = document.getElementById(mount);
    if (!root) return;
    const venuesOptions = venues.venues.map((v) => `<option value="${esc(v.id)}">${esc(v.property)}</option>`).join('');
    root.innerHTML = `<div class="filter-panel">
      <div class="filter-grid">
        <label>From <input type="date" data-filter="from" value="${esc(metaWindow.start)}"></label>
        <label>Through <input type="date" data-filter="to" value="${esc(metaWindow.end)}"></label>
        <label>Venue <select data-filter="venue"><option value="">All venues</option>${venuesOptions}</select></label>
        <label>Entry status <select data-filter="status"><option value="">All statuses</option><option value="unconfirmed">Entry terms unknown</option><option value="multiple-entry">Multiple entry confirmed</option><option value="conflicting">Official source conflict</option><option value="continuation">Continuation only</option></select></label>
        <label class="search-field">Search <input type="search" data-filter="query" placeholder="Event, game, flight…"></label>
      </div>
      <label class="check-line"><input type="checkbox" data-filter="continuations"> Include continuation / restart rows</label>
      <div class="filter-summary" aria-live="polite"></div>
    </div><div class="event-list" data-event-results></div>`;
    const controls = [...root.querySelectorAll('[data-filter]')];
    const list = root.querySelector('[data-event-results]');
    const summary = root.querySelector('.filter-summary');
    const apply = () => {
      const val = (key) => root.querySelector(`[data-filter="${key}"]`)?.value || '';
      const from = val('from') || '0000-01-01';
      const to = val('to') || '9999-12-31';
      const venue = val('venue');
      const status = val('status');
      const query = val('query').trim().toLocaleLowerCase();
      const includeContinuations = root.querySelector('[data-filter="continuations"]')?.checked || status === 'continuation';
      let filtered = tournaments.events.filter((event) => {
        const eventEnd = event.endDate || event.date;
        if (event.date > to || eventEnd < from) return false;
        if (venue && event.venueId !== venue) return false;
        if (status && event.entryStatus !== status) return false;
        if (event.recordType === 'continuation' && !includeContinuations && !status) return false;
        if (query) {
          const venueName = venueMap[event.venueId]?.property || '';
          const haystack = [event.title, event.series, event.eventNumber, event.game, event.format, venueName, ...(event.notes || [])].join(' ').toLocaleLowerCase();
          if (!haystack.includes(query)) return false;
        }
        return true;
      }).sort((a, b) => a.date.localeCompare(b.date) || (a.time || '99:99').localeCompare(b.time || '99:99') || a.venueId.localeCompare(b.venueId));
      const total = filtered.length;
      if (limit && total > limit) filtered = filtered.slice(0, limit);
      summary.textContent = `${total} matching row${total === 1 ? '' : 's'}${limit && total > limit ? ` · showing ${limit}` : ''}. All times are venue-local; start times only.`;
      list.innerHTML = filtered.length ? filtered.map((e) => eventCard(e, { showSelect: budget, compactNotes: !full })).join('') : '<p class="empty-state">No rows match those filters. Widen the date window or clear a filter.</p>';
      list.querySelectorAll('.event-budget-check').forEach((box) => box.addEventListener('change', () => {
        if (box.checked) selectedEventIds.add(box.dataset.eventId);
        else selectedEventIds.delete(box.dataset.eventId);
        updateCalculator();
      }));
    };
    controls.forEach((control) => control.addEventListener('input', apply));
    apply();
  }

  function renderHome() {
    const count = statusCounts(tournaments.events);
    const entryCount = tournaments.events.filter((e) => e.recordType === 'entry').length;
    const venRows = tournaments.meta.scheduleCoverage?.venetianDatedEntryRows || 17;
    const vQuote = hotels.quotes.find((q) => q.id.startsWith('venetian-'));
    const wQuote = hotels.quotes.find((q) => q.id.startsWith('wynn-'));
    return `<div class="container page-wrap">
      <section class="hero hero-home"><div class="hero-copy"><p class="eyebrow">Research snapshot · November 17, 2026</p><h1>Plan the poker trip.<br><em>Keep the unknowns visible.</em></h1><p class="lede">A date-filterable Las Vegas tournament planner, hotel comparison and trip-cost tool built from official sources. Rules, prices and gaps are shown separately—nothing is filled in from silence.</p><div class="hero-actions"><a class="button button-gold" href="${esc(href('tournaments'))}">Open the schedule <span>↗</span></a><a class="button button-outline" href="${esc(href('hotels'))}">Compare hotels & budget</a></div><p class="window-note"><span class="dot"></span><span><b>Dec 13–20, 2026 working window</b><br>Not dates selected by the user. Start times only; durations and seat availability are not confirmed.</span></p></div>
        <aside class="hero-quote"><div class="quote-top"><span>Direct booking snapshot</span><b>7 NIGHTS</b></div><div class="quote-name">The Venetian</div><div class="quote-total">${money(vQuote?.displayedTotalUsd, 2)}</div><p>Estimated stay total with fees and tax shown on the booking page. Availability warning; reconfirm the suite.</p><hr><div class="quote-small"><span>Wynn room display</span><b>${money(wQuote?.displayedAverageNightUsd)} / night</b></div><div class="quote-small"><span>Wynn all-in price</span><b>Not hotel-quoted</b></div><a href="${esc(href('hotels'))}">See what each number means ↗</a></aside>
      </section>
      <section class="metric-grid" aria-label="Research counts"><article><b>${entryCount}</b><span>dated entry rows tracked</span></article><article><b>0</b><span>strict single-entry rules verified</span></article><article><b>${venRows}</b><span>Venetian entry rows matched to official sheets</span></article><article><b>${venues.venues.length}</b><span>venue guides with source and map links</span></article></section>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Entry-rule standard</p><h2>No guesswork about re-entry.</h2></div><a class="text-link" href="${esc(href('method'))}">How labels work ↗</a></div><div class="callout callout-amber"><b>0 strict single-entry events are verified in this reviewed subset.</b><p>A “1Day” label, a missing re-entry rule, or a ban on later flights after bagging does not establish a total entry limit. Unknown terms stay unknown.</p></div><div class="metric-inline"><span><b>${count['multiple-entry'] || 0}</b> rows with multiple-entry/re-entry terms</span><span><b>${count.unconfirmed || 0}</b> rows with entry terms unknown</span><span><b>${count.conflicting || 0}</b> source conflict</span></div></section>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Selected listings</p><h2>What is on the board</h2><p>Search the reviewed subset across the working dates. This is not a complete Las Vegas or full WPT festival calendar.</p></div><a class="text-link" href="${esc(href('tournaments'))}">All filters & all rows ↗</a></div><div id="home-events"></div></section>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Trip budget</p><h2>Price the parts you know.</h2><p>The calculator distinguishes a date-matched booking snapshot from a user-entered estimate. It never auto-adds unknown re-entries or add-ons.</p></div><a class="text-link" href="${esc(href('hotels'))}">Hotel snapshot details ↗</a></div>${calculatorMarkup()}</section>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Property directory</p><h2>Follow the official links to the room.</h2></div><a class="text-link" href="${esc(href('venues'))}">All venue pages ↗</a></div><div class="venue-grid">${venues.venues.map(venueCard).join('')}</div></section>
      <section class="source-banner"><div><p class="eyebrow">Every listing has a source trail</p><h2>${Object.keys(sourceMap).length} official sources. 37 Venetian structure sheets.</h2><p>Each entry links to the official schedule or rule sheet; current hotel quotes and older policy pages carry their own date and uncertainty notes.</p></div><a class="button button-dark" href="${esc(href('sources'))}">Open the source ledger ↗</a></section>
    </div>`;
  }

  function venueCard(venue) {
    const eventCount = tournaments.events.filter((e) => e.venueId === venue.id).length;
    return `<a class="venue-card" href="${esc(venueHref(venue.id))}"><span class="venue-index">${String(venue.id).toUpperCase()}</span><h3>${esc(venue.property)}</h3><p>${esc(venue.room)}</p><small>${eventCount} tracked planner rows · ${esc(venue.coverage)}</small><span class="arrow">↗</span></a>`;
  }

  function renderVenues() {
    return `<div class="container page-wrap"><header class="page-title"><p class="eyebrow">Property directory</p><h1>Venue pages &amp; map routes.</h1><p class="lede">Official venue addresses and poker-room links, with route links opened in Google Maps. No walking time or seat-to-room distance is asserted here.</p></header><div class="venue-grid venue-grid-large">${venues.venues.map(venueCard).join('')}</div><div class="callout callout-blue"><b>Route links are for map planning only.</b><p>Google Maps may propose a route, but its walking time is not a verified measurement. Same-property routes do not show the internal walk from hotel room to poker table.</p></div></div>`;
  }

  function renderTournaments() {
    return `<div class="container page-wrap"><header class="page-title"><p class="eyebrow">Las Vegas · venue-local schedule</p><h1>Events, flights &amp; continuation days.</h1><p class="lede">Use the dates, venue, status and search filters to explore the reviewed subset. Every event keeps total entry cap, re-entry, rebuy, add-on, late registration and fees as separate facts.</p></header><div class="scope-strip"><b>Research window:</b> ${esc(tournaments.meta.window.label)} · working dates, not user-selected · <b>Coverage:</b> selected official listings, not a complete citywide calendar.</div><div id="schedule-events"></div><div class="callout callout-amber"><b>Unknown is not “no.”</b><p>Read the event detail for field-by-field unknowns, conflicting rules, fee components and primary citations.</p></div></div>`;
  }

  function sourceUrl(id) { return sourceMap[id]?.url || '#'; }
  function routeUrl(from, to) {
    const params = new URLSearchParams({ api: '1', origin: from, destination: to, travelmode: 'walking' });
    return `https://www.google.com/maps/dir/?${params.toString()}`;
  }
  function mapSearchUrl(address) {
    const params = new URLSearchParams({ api: '1', query: address });
    return `https://www.google.com/maps/search/?${params.toString()}`;
  }

  function renderVenuePage(id) {
    const venue = venueMap[id];
    if (!venue) return `<div class="container page-wrap"><h1>Venue not found</h1><a href="${esc(href('venues'))}">Return to venues</a></div>`;
    const ownHotel = hotels.properties.find((h) => h.id === venue.hotelId);
    const venueEvents = tournaments.events.filter((e) => e.venueId === id);
    const routeCards = hotels.properties.map((hotel) => {
      const same = hotel.id === venue.hotelId;
      const addressKnown = Boolean(hotel.address);
      const url = !addressKnown ? '' : (same ? mapSearchUrl(venue.address) : routeUrl(hotel.address, venue.address));
      const link = addressKnown ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${same ? 'Open property map' : 'Walking directions'} ↗</a>` : '<small>Property address not verified; no route link.</small>';
      return `<article class="route-card"><b>${esc(hotel.name)}</b><span>${esc(hotel.address || 'Address not verified')}</span>${link}${same && addressKnown ? '<small>Same property; internal room-to-table route is unknown.</small>' : addressKnown ? '<small>Route and travel time are not independently verified.</small>' : ''}</article>`;
    }).join('');
    return `<div class="container page-wrap"><header class="page-title"><p class="eyebrow">Venue guide · ${esc(venue.room)}</p><h1>${esc(venue.property)}</h1><p class="lede">${esc(venue.coverage)}</p></header>
      <section class="venue-hero"><div><p class="eyebrow">Official property details</p><h2>${esc(venue.room)}</h2><address>${esc(venue.address)}</address><p>${esc(venue.hostRelation)}</p><div class="hero-actions"><a class="button button-gold" href="${esc(venue.website)}" target="_blank" rel="noopener noreferrer">Property website ↗</a><a class="button button-light" href="${esc(venue.pokerUrl)}" target="_blank" rel="noopener noreferrer">Poker schedule / room ↗</a><a class="button button-light" href="${esc(mapSearchUrl(venue.address))}" target="_blank" rel="noopener noreferrer">Map pin ↗</a></div></div><div class="venue-status"><b>${venueEvents.length}</b><span>planner rows</span><p>${ownHotel ? `Hotel booking: <a href="${esc(sourceUrl(venue.bookingSourceId))}" target="_blank" rel="noopener noreferrer">official link ↗</a>` : 'No same-property hotel record.'}</p></div></section>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Local program</p><h2>Tracked listings at this venue</h2></div></div><div class="event-list">${venueEvents.map((event) => eventCard(event, { compactNotes: false })).join('') || '<p class="empty-state">No dated event row in this planner window.</p>'}</div></section>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Routes</p><h2>From hotel pins to this venue</h2><p>Map links open in a separate tab. Addresses are property-level only; internal room locations and actual walking times are unknown.</p></div></div><div class="route-grid">${routeCards}</div></section>
      <section class="content-section"><h2>Source links</h2><div class="source-row">${sourceLinks(venue.sourceIds)}</div></section></div>`;
  }

  function renderHotels() {
    const quoteCards = hotels.quotes.map((q) => {
      const isV = q.id.startsWith('venetian-');
      const property = hotels.properties.find((p) => p.id === q.propertyId);
      const total = isV ? q.displayedTotalUsd : q.estimatedAllInStayUsd;
      const mainLabel = isV ? 'Displayed stay estimate · includes tax and resort fees' : 'Arithmetic estimate · not a hotel-quoted total';
      return `<article class="quote-card"><div class="quote-head"><div><span class="eyebrow">${esc(q.checkIn)} → ${esc(q.checkOut)} · ${q.nights} nights · ${q.adults} adult</span><h3>${esc(q.hotel)}</h3><p>${esc(q.roomType)}</p></div><span class="status-pill ${isV ? 'multiple' : 'unknown'}">${isV ? 'Availability not confirmed' : 'Tax-inclusive total unknown'}</span></div><div class="quote-total-line"><div><small>${mainLabel}</small><strong>${money(total, 2)}</strong></div><a class="button button-dark" href="${esc(sourceUrl(property?.bookingSourceId))}" target="_blank" rel="noopener noreferrer">Official booking ↗</a></div><dl class="quote-breakdown">${isV ? `<div><dt>Room subtotal</dt><dd>${money(q.roomSubtotalUsd, 2)}</dd></div><div><dt>Resort fee</dt><dd>${money(q.resortFeeUsd, 2)}</dd></div><div><dt>Displayed tax</dt><dd>${money(q.taxUsd, 2)}</dd></div>` : `<div><dt>Displayed average / night</dt><dd>${money(q.displayedAverageNightUsd, 2)}</dd></div><div><dt>Rate includes resort fee</dt><dd>Yes</dd></div><div><dt>Hotel-returned total with tax</dt><dd>Not returned</dd></div><div><dt>Estimated tax assumption</dt><dd>${(q.taxRateUsedForEstimate * 100).toFixed(2)}% · 2021 county guide</dd></div>`}</dl><p class="quote-note">${esc(q.note)}</p><div class="source-row">${sourceLinks(q.sourceIds, true)}</div></article>`;
    }).join('');
    const propertyRows = hotels.properties.map((p) => {
      const fee = p.fee?.amountUsdPerNight == null ? 'Unknown / not verified' : `${money(p.fee.amountUsdPerNight, 2)} per night ${p.fee.tax ? `· ${esc(p.fee.tax)}` : ''}`;
      const status = p.fee?.status || 'not-verified';
      return `<article class="hotel-property"><div><h3>${esc(p.name)}</h3><address>${esc(p.address || 'Address not verified')}</address><p>${esc(p.note)}</p><div class="source-row">${p.addressSourceId ? sourceLinks([p.addressSourceId], true) : ''}</div></div><div class="hotel-fee"><small>Resort fee</small><b>${fee}</b><span>${esc(status.replaceAll('-', ' '))}</span><div class="source-row">${sourceLinks(p.fee?.sourceIds || [], true)}</div></div><div class="hotel-links"><a href="${esc(sourceUrl(p.bookingSourceId))}" target="_blank" rel="noopener noreferrer">Book direct ↗</a><a href="${esc(p.website)}" target="_blank" rel="noopener noreferrer">Property ↗</a></div></article>`;
    }).join('');
    const parking = (hotels.parking || []).map((p) => {
      const property = hotels.properties.find((h) => h.id === p.propertyId);
      return `<article class="parking-card"><b>${esc(property?.name || p.propertyId)}</b><p>${esc(p.summary)}</p><div class="source-row">${sourceLinks(p.sourceIds, true)}</div></article>`;
    }).join('');
    const promo = hotels.venetianPokerSuiteOffer;
    return `<div class="container page-wrap"><header class="page-title"><p class="eyebrow">Hotels · snapshot separate from the Dec 2–9 dashboard</p><h1>Room rates, resort fees &amp; trip budget.</h1><p class="lede">This comparison uses the Dec 13–20 snapshot only. One Venetian result is a booking-page estimate; Wynn did not return a tax-inclusive total. The remaining properties have fee or booking links, not matched date quotes.</p></header>
      <div class="callout callout-amber"><b>Do not rank these as apples-to-apples prices.</b><p>Dates and occupancy are a working example (one adult, seven nights), not user-selected booking details. Confirm the exact room, availability, cancellation terms and total at checkout.</p></div>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Direct snapshots · Nov 17, 2026</p><h2>Only two date-specific rate signals</h2></div></div><div class="quote-grid">${quoteCards}</div></section>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Cost model</p><h2>Build a trip total without hiding assumptions.</h2><p>Matched snapshots are shown as snapshots. Changing dates never reprices a booking; use editable estimates when no matching quote exists.</p></div></div>${calculatorMarkup()}</section>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Official property pages</p><h2>Resort fees and booking links</h2></div></div><div class="hotel-list">${propertyRows}</div></section>
      <section class="content-section"><div class="section-heading"><div><p class="eyebrow">Parking</p><h2>Room-to-room details still need confirmation.</h2></div></div><div class="parking-grid">${parking}</div></section>
      <section class="content-section promo-card"><div><p class="eyebrow">Separate promotional rate · not a matched quote</p><h2>${esc(promo.label)}</h2><p>Rates from ${money(promo.rateFromUsd[0])} to ${money(promo.rateFromUsd[1])}; tower mapping unclear. Qualification requires ${esc(promo.qualifyingPlay)} This is not included in the calculator's default room total.</p><div class="source-row">${sourceLinks(promo.sourceIds, true)}</div></div><a href="${esc(sourceUrl('venetian-poker-suite-rates'))}" class="button button-dark" target="_blank" rel="noopener noreferrer">Check offer terms ↗</a></section>
      </div>`;
  }

  function renderVenueDirectory() { return renderVenues(); }

  function renderSources() {
    const list = [...(tournaments.sources || [])].sort((a, b) => a.publisher.localeCompare(b.publisher) || a.title.localeCompare(b.title));
    const monitored = list.filter((s) => s.monitor).length;
    return `<div class="container page-wrap"><header class="page-title"><p class="eyebrow">Official-source ledger</p><h1>Research you can trace.</h1><p class="lede">Every source record has a publisher, URL, check date and scope note. Scheduled monitoring checks source availability and expected fact markers; it does not automatically approve a changed rule or price.</p></header><div class="metric-inline"><span><b>${list.length}</b> ledger records</span><span><b>${list.filter((s) => s.kind === 'pdf').length}</b> PDFs</span><span><b>${monitored}</b> monitored official URLs</span></div><div class="filter-panel source-filter"><label>Filter sources <input type="search" id="source-query" placeholder="Search title, publisher, note, ID"></label><label>Type <select id="source-kind"><option value="">All types</option><option value="webpage">Web pages</option><option value="pdf">PDFs</option></select></label></div><div id="source-list" class="source-list"></div></div>`;
  }

  function initSources() {
    const query = document.getElementById('source-query');
    const kind = document.getElementById('source-kind');
    const list = document.getElementById('source-list');
    if (!list) return;
    const render = () => {
      const q = query.value.trim().toLowerCase();
      const k = kind.value;
      const filtered = (tournaments.sources || []).filter((s) => {
        if (k && s.kind !== k) return false;
        return !q || [s.id, s.title, s.publisher, s.notes, s.url].join(' ').toLowerCase().includes(q);
      });
      list.innerHTML = filtered.map((s) => `<article class="source-record"><div class="source-record-top"><span class="tag tag-neutral">${esc(s.kind || 'webpage')}</span><span class="source-id">${esc(s.id)}</span><span class="source-checked">Checked ${esc(s.checkedAt || 'date not recorded')}</span></div><h3><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)} ↗</a></h3><p class="source-publisher">${esc(s.publisher)}</p><p>${esc(s.notes || 'No additional source note.')}</p><div class="source-record-bottom"><code>${esc(s.url)}</code>${s.monitor ? `<span class="monitor-tag">Monitor: ${esc(s.monitor.mode)}${s.monitor.markers?.length ? ` · ${s.monitor.markers.length} markers` : ''}${s.monitor.compareNormalizedText ? ' · text fingerprint' : ''}</span>` : '<span class="tag tag-neutral">No automated marker</span>'}</div></article>`).join('') || '<p class="empty-state">No matching sources.</p>';
    };
    query.addEventListener('input', render); kind.addEventListener('change', render); render();
  }

  function renderMethod() {
    const stats = tournaments.meta.summaryCounts || statusCounts(tournaments.events);
    return `<div class="container page-wrap"><header class="page-title"><p class="eyebrow">Read before planning</p><h1>What this planner means—and what it does not.</h1><p class="lede">Strict entry classification, schedule coverage, date snapshots, unknowns and the source-monitor process.</p></header>
      <section class="method-grid"><article class="method-card"><span>01</span><h2>Single-entry means one total paid entry.</h2><p>A row is called strict single-entry only when a current official, event-specific source clearly limits total paid entries to one and closes off re-entry, rebuy or another extra-entry path. A “1Day” label or silence is not evidence.</p></article><article class="method-card"><span>02</span><h2>Entry paths stay separate.</h2><p>Total entry cap, re-entry, rebuy, add-on and late registration are separate fields. Unknown means the reviewed official material does not settle that fact. An optional staff gratuity is not silently re-labeled as an add-on.</p></article><article class="method-card"><span>03</span><h2>Bagging is not busting.</h2><p>A multi-flight rule barring a player who bags for Day 2 from entering later flights does not prove whether a player who busts can try again, nor does it establish an overall entry maximum.</p></article><article class="method-card"><span>04</span><h2>Schedule scope is explicit.</h2><p>The dataset is a selected official-source subset for a working Dec 13–20, 2026 window. It is not a complete Las Vegas calendar or full WPT festival calendar. Caesars and Horseshoe rows project recurring official start times; they are not seat confirmations.</p></article></section>
      <section class="content-section"><h2>Coverage in this snapshot</h2><div class="metric-inline"><span><b>${tournaments.events.length}</b> dated planner rows</span><span><b>${stats.unconfirmed || 0}</b> entry terms unknown</span><span><b>${stats['multiple-entry'] || 0}</b> multiple-entry records</span><span><b>${stats.conflicting || 0}</b> official-source conflict</span></div><p>All 17 Venetian dated entry rows from the Dec 13–20 schedule window are matched on event date, event number, flight, time, buy-in, guarantee and structure sheet. The four restart rows and other WPT continuation listings are kept separate from new entries.</p><p>All 37 numbered Venetian structure PDFs linked by the official DSE IV schedule are cataloged in the source ledger and summarized in <a href="../data/final/structure-notes.md">the row-by-row structure notes</a>.</p></section>
      <section class="content-section"><h2>Hotel snapshot rules</h2><ul class="method-list"><li>The hotel example uses Dec 13–20, 2026, one adult, seven nights, as a research snapshot only—not user-selected trip dates.</li><li>Venetian's displayed total has a capacity/availability warning and is not an availability confirmation.</li><li>Wynn's $355 average/night includes resort fee but excludes tax. $2,817.49 is a separate estimate using an older 13.38% County tax guide, not a hotel-quoted all-in total.</li><li>The Dec 2–9 dashboard remains separate; its hotel prices are not used here.</li><li>Google Maps links are route lookups, not verified distances or walking-time claims. Internal hotel-to-table routes are unknown.</li></ul></section>
      <section class="content-section"><h2>Automated monitoring</h2><p>The weekly GitHub Actions workflow rechecks monitored official URLs, minimum response size and selected fact markers; it also compares normalized extracted text for 44 static PDFs (including the 37 Venetian sheets) with the last successful baseline. A missing marker, text change or unavailable page creates a report for human review; it cannot decide whether a revised rule is valid or change planner data automatically. Reports are attached to workflow runs.</p><p><a href="${esc(href('sources'))}">Browse the source ledger ↗</a> · <a href="https://github.com/karagemop466-tech/Poker5/blob/main/.github/workflows/source-monitor-a9d1e02d.yml" target="_blank" rel="noopener noreferrer">Monitoring workflow ↗</a></p></section>
      <section class="callout callout-blue"><b>Safety and freshness.</b><p>Prices, schedules, eligibility, fees, parking and hotel availability can change. Verify current terms directly. This planner is informational, is not affiliated with a casino or hotel, and is not a recommendation to gamble.</p></section></div>`;
  }

  function calculatorMarkup() {
    const options = hotels.properties.map((p, index) => `<option value="${esc(p.id)}"${index === 0 ? ' selected' : ''}>${esc(p.name)}</option>`).join('');
    return `<div class="calculator" id="trip-calculator"><div class="calculator-head"><div><p class="eyebrow">Editable estimate · no booking made</p><h3>Trip-cost calculator</h3><p>Matched snapshot when dates fit; otherwise enter your room rate. Re-entries and add-ons stay out unless you add them manually.</p></div><span class="tag tag-neutral">USD</span></div>
      <div class="calc-controls"><label>Check in <input id="trip-in" type="date" value="${esc(hotels.meta.window.checkIn)}"></label><label>Check out <input id="trip-out" type="date" value="${esc(hotels.meta.window.checkOut)}"></label><label>Hotel <select id="trip-hotel">${options}</select></label><label>Adults <input id="trip-adults" type="number" min="1" step="1" value="${hotels.meta.window.adults}"></label><label>Rooms <input id="trip-rooms" type="number" min="1" step="1" value="1"></label></div>
      <p class="calc-snapshot-note" id="calc-snapshot-note" aria-live="polite"></p>
      <div class="calc-body"><div class="calc-inputs"><h4>If no exact hotel total matches</h4><p class="micro-note">Enter a per-room nightly room rate and fee. These fields are estimates you control. Tax defaults to a historical guide, not a current confirmed tax quote. ${sourceMap[hotels.meta.taxEstimateSourceId] ? `<a href="${esc(sourceMap[hotels.meta.taxEstimateSourceId].url)}" target="_blank" rel="noopener noreferrer">Open the 2021 County guide ↗</a>` : ''}</p><div class="calc-number-grid"><label>Room rate / night / room <input id="trip-rate" type="number" min="0" step="0.01" placeholder="Enter rate"></label><label>Resort fee / night / room <input id="trip-fee" type="number" min="0" step="0.01" placeholder="Unknown"></label><label>Tax assumption (%) <input id="trip-tax" type="number" min="0" step="0.01" value="${(hotels.meta.taxEstimateRate * 100).toFixed(2)}"></label><label>Other hotel charges <input id="trip-hotel-other" type="number" min="0" step="0.01" value="0"></label></div>
        <h4>Other trip spending (manual)</h4><div class="calc-number-grid"><label>Transport / parking <input id="trip-transport" type="number" min="0" step="0.01" value="0"></label><label>Meals / incidentals <input id="trip-meals" type="number" min="0" step="0.01" value="0"></label><label>Re-entries / add-ons <input id="trip-extras" type="number" min="0" step="0.01" value="0"></label></div>
        <details class="event-picker"><summary>Choose tournament entries to include <span id="selected-count">0 selected</span></summary><p class="micro-note">Each checked row adds one published buy-in only. Re-entry, rebuy and optional add-on spend is excluded unless entered above. Select only the flights you plan to enter.</p><div id="budget-event-list" class="budget-event-list"></div></details></div>
        <aside class="calc-result"><span class="result-kicker">Known + entered estimate</span><strong id="calc-total">—</strong><div id="calc-confidence" class="result-confidence">Hotel and optional spending may be unknown.</div><hr><div class="result-row"><span>Hotel</span><b id="calc-hotel">Unknown</b></div><div class="result-row"><span>Selected buy-ins</span><b id="calc-buyins">$0</b></div><div class="result-row"><span>Other entered costs</span><b id="calc-other">$0</b></div><p class="micro-note">Not a booking quote. This total excludes any cost not entered or explicitly included in a matched snapshot.</p><a id="calc-booking" href="#" target="_blank" rel="noopener noreferrer" hidden>Open selected hotel's official booking link ↗</a></aside></div></div>`;
  }

  function daysBetween(start, end) {
    if (!start || !end) return 0;
    const a = new Date(`${start}T00:00:00Z`);
    const b = new Date(`${end}T00:00:00Z`);
    return Math.max(0, Math.round((b - a) / 86400000));
  }
  function numericInput(id) {
    const value = document.getElementById(id)?.value;
    return value === '' || value == null ? null : Number(value);
  }
  function updateCalculator() {
    const inEl = document.getElementById('trip-in');
    if (!inEl) return;
    const checkin = inEl.value;
    const checkout = document.getElementById('trip-out').value;
    const nights = daysBetween(checkin, checkout);
    const hotelId = document.getElementById('trip-hotel').value;
    const adults = Number(document.getElementById('trip-adults').value) || 1;
    const rooms = Number(document.getElementById('trip-rooms').value) || 1;
    const hotel = hotels.properties.find((h) => h.id === hotelId);
    const quote = hotels.quotes.find((q) => q.propertyId === hotelId && q.checkIn === checkin && q.checkOut === checkout && q.adults === adults && rooms === 1);
    const snapshotNote = document.getElementById('calc-snapshot-note');
    const rate = numericInput('trip-rate');
    const fee = numericInput('trip-fee');
    const tax = numericInput('trip-tax');
    const otherHotel = numericInput('trip-hotel-other') || 0;
    let hotelAmount = null;
    let hotelLabel = 'Unknown';
    let confidence = '';
    let noteText = '';
    if (!nights) {
      noteText = 'Enter a check-in date earlier than check-out. No hotel total can be calculated.';
    } else if (quote?.quoteStatus === 'direct_booking_page_estimate_includes_fees_and_tax') {
      hotelAmount = Number(quote.displayedTotalUsd) + otherHotel;
      hotelLabel = money(hotelAmount, 2);
      confidence = 'Direct booking-page estimate; availability not confirmed.';
      noteText = `Exact date and occupancy match the ${dates(quote.checkIn)}–${dates(quote.checkOut)} Venetian page snapshot. It showed an estimated total including listed tax and resort fee, but a room-capacity warning. The snapshot is not repriced.`;
    } else if (quote?.quoteStatus === 'direct_nightly_rate_tax_excluded_total_not_returned') {
      hotelAmount = Number(quote.estimatedAllInStayUsd) + otherHotel;
      hotelLabel = money(hotelAmount, 2);
      confidence = 'Modelled tax estimate, not a hotel-quoted total.';
      noteText = `Exact date and occupancy match Wynn's $${quote.displayedAverageNightUsd} average-night display (resort fee included, tax excluded). ${money(quote.estimatedAllInStayUsd, 2)} uses the older ${(quote.taxRateUsedForEstimate * 100).toFixed(2)}% tax guide; Wynn did not return an all-in quote. Do not add a resort fee again.`;
    } else if (rate != null) {
      const feeValue = fee ?? 0;
      const taxMultiplier = tax == null ? 1 : 1 + Math.max(0, tax) / 100;
      hotelAmount = ((Math.max(0, rate) + Math.max(0, feeValue)) * nights * rooms * taxMultiplier) + otherHotel;
      hotelLabel = money(hotelAmount, 2);
      confidence = 'User-entered room and fee estimate; not a booking quote.';
      noteText = `Estimate: (room rate + entered fee) × ${nights} nights × ${rooms} room${rooms === 1 ? '' : 's'}, plus the entered tax assumption. Verify the fee/tax base at checkout.`;
    } else {
      confidence = 'Hotel total unknown; enter a room rate to estimate.';
      noteText = `No date-matched all-in quote for ${hotel?.name || 'this hotel'} and the selected dates. Published fee details may still be shown; nightly room rate and current total are unknown.`;
    }
    snapshotNote.textContent = noteText;
    const eventStart = checkin || tournaments.meta.window.start;
    const eventEnd = checkout || tournaments.meta.window.end;
    const selectedEvents = tournaments.events.filter((e) => selectedEventIds.has(e.id) && e.date <= eventEnd && (e.endDate || e.date) >= eventStart && e.buyInUsd != null && e.recordType === 'entry');
    const buyins = selectedEvents.reduce((sum, e) => sum + Number(e.buyInUsd), 0);
    const transport = numericInput('trip-transport') || 0;
    const meals = numericInput('trip-meals') || 0;
    const extras = numericInput('trip-extras') || 0;
    const other = transport + meals + extras;
    const knownTotal = (hotelAmount ?? 0) + buyins + other;
    const shownTotal = (hotelAmount == null && buyins === 0 && other === 0) ? '—' : money(knownTotal, 2);
    document.getElementById('calc-total').textContent = shownTotal;
    document.getElementById('calc-hotel').textContent = hotelLabel;
    document.getElementById('calc-buyins').textContent = money(buyins, 2);
    document.getElementById('calc-other').textContent = money(other, 2);
    document.getElementById('calc-confidence').textContent = confidence;
    document.getElementById('selected-count').textContent = `${selectedEvents.length} selected · ${money(buyins, 2)}`;
    const bookingLink = document.getElementById('calc-booking');
    if (hotel?.bookingSourceId && sourceMap[hotel.bookingSourceId]) {
      bookingLink.href = sourceMap[hotel.bookingSourceId].url;
      bookingLink.hidden = false;
    } else bookingLink.hidden = true;
  }

  function initCalculator() {
    const root = document.getElementById('trip-calculator');
    if (!root) return;
    const hotelSelect = document.getElementById('trip-hotel');
    const updateProperty = () => {
      const hotel = hotels.properties.find((h) => h.id === hotelSelect.value);
      const feeInput = document.getElementById('trip-fee');
      const fee = hotel?.fee;
      if (fee?.amountUsdPerNight != null && ['officially-published', 'official-page-covers-resort', 'official-Wynn-terms-cover-resort'].includes(fee.status)) {
        feeInput.value = fee.amountUsdPerNight;
        feeInput.placeholder = 'Officially published fee';
      } else {
        feeInput.value = '';
        feeInput.placeholder = fee?.status === 'prior-official-booking-snapshot-not-rechecked' ? 'Prior snapshot only' : 'Unknown';
      }
      updateCalculator();
    };
    const list = document.getElementById('budget-event-list');
    const renderBudgetEvents = () => {
      const start = document.getElementById('trip-in').value || tournaments.meta.window.start;
      const end = document.getElementById('trip-out').value || tournaments.meta.window.end;
      const pool = tournaments.events.filter((e) => e.recordType === 'entry' && e.buyInUsd != null && e.date <= end && (e.endDate || e.date) >= start)
        .sort((a, b) => a.date.localeCompare(b.date) || (a.time || '99:99').localeCompare(b.time || '99:99'));
      list.innerHTML = pool.map((e) => `<label class="budget-row"><input class="event-budget-check" type="checkbox" data-event-id="${esc(e.id)}" ${selectedEventIds.has(e.id) ? 'checked' : ''}><span><b>${esc(dateShort(e.date))} · ${esc(clock(e.time))}</b><small>${esc(e.title)} · ${esc(venueMap[e.venueId]?.property || e.venueId)}</small></span><strong>${money(e.buyInUsd)}</strong></label>`).join('') || '<p class="empty-state">No published buy-ins in this date range.</p>';
      list.querySelectorAll('.event-budget-check').forEach((box) => box.addEventListener('change', () => {
        if (box.checked) selectedEventIds.add(box.dataset.eventId); else selectedEventIds.delete(box.dataset.eventId);
        updateCalculator();
      }));
      updateCalculator();
    };
    hotelSelect.addEventListener('change', () => {
      document.getElementById('trip-rate').value = '';
      updateProperty();
    });
    ['trip-in', 'trip-out', 'trip-adults', 'trip-rooms'].forEach((id) => document.getElementById(id).addEventListener('change', () => { renderBudgetEvents(); updateCalculator(); }));
    ['trip-rate', 'trip-fee', 'trip-tax', 'trip-hotel-other', 'trip-transport', 'trip-meals', 'trip-extras'].forEach((id) => document.getElementById(id).addEventListener('input', updateCalculator));
    updateProperty(); renderBudgetEvents();
  }

  function showPage() {
    const content = document.getElementById('page-content');
    if (!content) return;
    if (PAGE === 'home') { content.innerHTML = renderHome(); renderEventFilters({ mount: 'home-events', full: false, limit: 5 }); initCalculator(); }
    else if (PAGE === 'tournaments') { content.innerHTML = renderTournaments(); renderEventFilters({ mount: 'schedule-events', full: true }); }
    else if (PAGE === 'hotels') { content.innerHTML = renderHotels(); initCalculator(); }
    else if (PAGE === 'venues') content.innerHTML = renderVenueDirectory();
    else if (PAGE === 'venue') content.innerHTML = renderVenuePage(VENUE_ID);
    else if (PAGE === 'sources') { content.innerHTML = renderSources(); initSources(); }
    else if (PAGE === 'method') content.innerHTML = renderMethod();
    else content.innerHTML = renderHome();
  }

  async function init() {
    renderHeader(); renderFooter();
    const target = document.getElementById('page-content');
    try {
      const [t, h, v, ledger] = await Promise.all(['events', 'hotels', 'venues', 'source-ledger'].map((name) => fetch(assetData(name)).then((r) => {
        if (!r.ok) throw new Error(`${name} data returned HTTP ${r.status}`);
        return r.json();
      })));
      tournaments = t; hotels = h; venues = v;
      tournaments.sources = ledger.sources || [];
      sourceMap = Object.fromEntries(tournaments.sources.map((s) => [s.id, s]));
      venueMap = Object.fromEntries(venues.venues.map((venue) => [venue.id, venue]));
      showPage();
    } catch (error) {
      if (target) target.innerHTML = `<div class="container page-wrap"><div class="callout callout-amber"><b>Planner data could not be loaded.</b><p>${esc(error.message)}. Open this site through a web server (not as a local file) and try again.</p></div></div>`;
    }
  }

  init();
})();
