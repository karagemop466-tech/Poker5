(() => {
  'use strict';

  const ROOT = document.body.dataset.root || '.';
  const PAGE = document.body.dataset.page || 'dashboard';
  const routeFiles = {
    dashboard: 'index.html',
    tournaments: 'pages/tournaments.html',
    hotels: 'pages/hotels.html',
    analysis: 'pages/analysis.html',
    qa: 'pages/qa.html',
    suggestions: 'pages/suggestions.html',
    review: 'pages/review.html',
    publication: 'pages/publication.html'
  };
  const routeNames = {
    dashboard: 'Dashboard',
    tournaments: 'Tournaments',
    hotels: 'Hotels',
    analysis: 'Analysis',
    qa: 'Q&A',
    suggestions: 'Suggestions',
    review: 'Flagged review',
    publication: 'Publication'
  };
  const urlFor = (key) => `${ROOT}/${routeFiles[key]}`;
  const assetFor = (path) => `${ROOT}/${path}`;

  const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[character]));
  const money = (value, decimals = 0) => value == null ? 'Not published' : new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'USD', minimumFractionDigits: decimals, maximumFractionDigits: decimals
  }).format(value);
  const shortDate = (iso) => {
    if (!iso) return '';
    const [year, month, day] = iso.split('-').map(Number);
    return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(new Date(year, month - 1, day));
  };
  const longDate = (iso) => {
    if (!iso) return '';
    const [year, month, day] = iso.split('-').map(Number);
    return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(year, month - 1, day));
  };

  function renderChrome() {
    const nav = Object.entries(routeNames).map(([key, label]) => {
      const current = PAGE === key ? ' aria-current="page"' : '';
      return `<a href="${escapeHtml(urlFor(key))}"${current}>${escapeHtml(label)}</a>`;
    }).join('');
    const header = document.getElementById('site-header');
    if (header) header.innerHTML = `
      <a class="skip-link" href="#main-content">Skip to content</a>
      <header class="site-header">
        <div class="nav-shell">
          <a class="brand" href="${escapeHtml(urlFor('dashboard'))}" aria-label="Felt & Stay dashboard">
            <span class="brand-mark" aria-hidden="true">♠</span>
            <span><span class="brand-name">Felt &amp; Stay</span><span class="brand-sub">Las Vegas poker planner</span></span>
          </a>
          <nav class="site-nav" aria-label="Main navigation">${nav}</nav>
          <div class="edition-chip">Research snapshot · Nov 16, 2026</div>
        </div>
      </header>`;
    const footer = document.getElementById('site-footer');
    if (footer) footer.innerHTML = `
      <footer class="site-footer">
        <div class="container footer-inner">
          <div>
            <p class="footer-title">Felt &amp; Stay · research first, no guesses.</p>
            <p class="footer-note">Dec 13–20, 2026 is a working research window—not a travel date chosen by the user. Rates and tournament terms can change. Verify directly before booking or registering.</p>
          </div>
          <div class="footer-links">
            <a href="${escapeHtml(assetFor('research/tournaments.md'))}">Tournament notes</a>
            <a href="${escapeHtml(assetFor('research/hotels.md'))}">Hotel notes</a>
            <a href="${escapeHtml(urlFor('publication'))}">Publication process</a>
            <a href="https://karagemop466-tech.github.io/Poker5/">Main Poker5 site ↗</a>
          </div>
        </div>
      </footer>`;
  }

  function pill(status) {
    const labels = {
      'unconfirmed': 'Entry terms unverified',
      'multiple-entry': 'Multiple entry confirmed',
      'conflicting': 'Source conflict',
      'single-entry': 'Strict single-entry confirmed'
    };
    return `<span class="pill ${escapeHtml(status)}">${escapeHtml(labels[status] || status)}</span>`;
  }

  function sourceLinks(sourceIds, sources, compact = true) {
    return (sourceIds || []).map((id) => {
      const source = sources[id];
      if (!source) return '';
      return `<a class="source-chip" href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer" title="${escapeHtml(source.title)}">${compact ? 'Source' : escapeHtml(source.title)} ↗</a>`;
    }).join('');
  }

  function eventDateLabel(event) {
    return event.endDate && event.endDate !== event.date
      ? `${shortDate(event.date)}–${shortDate(event.endDate)}`
      : shortDate(event.date);
  }

  function isInWindow(event, window) {
    const start = event.date;
    const end = event.endDate || event.date;
    return start <= window.end && end >= window.start;
  }

  function eventCard(event, venues, sources, window) {
    const venue = venues[event.venueId]?.name || event.venueId || 'Venue to confirm';
    const startsBefore = event.date < window.start;
    const guarantee = event.guaranteeUsd == null ? '' : `<span><strong>${money(event.guaranteeUsd)}</strong> published guarantee</span>`;
    const overlap = startsBefore ? '<span class="tag">Event overlaps stay dates</span>' : '';
    const notes = (event.notes || []).slice(0, 2).map((note) => `<span class="tag">${escapeHtml(note)}</span>`).join('');
    const breakdown = event.buyInBreakdownUsd
      ? `<p class="note">Prize pool ${money(event.buyInBreakdownUsd.playerPrizePool)} · fees ${money(event.buyInBreakdownUsd.tournamentFee)} · staff ${money(event.buyInBreakdownUsd.pokerStaffServiceCharge)}</p>`
      : '';
    return `<article class="event-card">
      <div class="event-date"><strong>${escapeHtml(shortDate(event.date))}</strong><span>${escapeHtml(event.endDate && event.endDate !== event.date ? `to ${shortDate(event.endDate)}` : 'local date')}</span></div>
      <div>
        <div class="card-title-row"><h3 class="event-title">${escapeHtml(event.title)}</h3>${pill(event.entryStatus)}</div>
        <div class="event-meta">
          <span>${escapeHtml(venue)}</span>
          <span>${escapeHtml(event.time || 'Time not listed')}</span>
          <span>${escapeHtml(event.game || '')}</span>
          <span>Format: ${escapeHtml(event.format || 'not specified')}</span>
          ${guarantee}
        </div>
        <p class="event-rule">${escapeHtml(event.entryRule || 'Entry terms not found in the reviewed official source.')}</p>
        ${breakdown}
        <div class="tag-row">${overlap}${notes}</div>
        <div class="event-sources">${sourceLinks(event.sourceIds, sources)}</div>
      </div>
      <div class="event-side">
        <span class="buy-in">${event.buyInUsd == null ? '—' : money(event.buyInUsd)}</span>
        <span class="buy-in-label">listed buy-in</span>
      </div>
    </article>`;
  }

  function hotelCard(quote, sources) {
    const direct = quote.quoteStatus === 'direct_quote_includes_fees_and_tax';
    const displayed = direct ? quote.quotedTotalUsd : quote.displayedAverageNightUsd;
    const priceLabel = direct ? 'direct quote · 7 nights all-in' : 'displayed average / night · tax excluded';
    const rows = direct
      ? `<div class="price-row"><span>Room subtotal</span><strong>${money(quote.roomSubtotalUsd, 2)}</strong></div>
         <div class="price-row"><span>Resort fees · ${quote.nights} nights</span><strong>${money(quote.resortFeeUsd, 2)}</strong></div>
         <div class="price-row"><span>Taxes shown by hotel</span><strong>${money(quote.taxUsd, 2)}</strong></div>
         <div class="price-row total"><span>Quoted total</span><strong>${money(quote.quotedTotalUsd, 2)}</strong></div>
         <div class="price-row"><span>All-in per night</span><strong>${money(quote.quotedAllInPerNightUsd, 2)}</strong></div>`
      : `<div class="price-row"><span>7-night pre-tax arithmetic</span><strong>${money(quote.preTaxStayCalculationUsd, 2)}</strong></div>
         <div class="price-row"><span>Estimated tax · ${((quote.taxRateUsedForEstimate || 0) * 100).toFixed(2)}%</span><strong>${money(quote.estimatedTaxUsd, 2)}</strong></div>
         <div class="price-row total"><span>Estimated total · not hotel-quoted</span><strong>${money(quote.estimatedAllInStayUsd, 2)}</strong></div>
         <div class="price-row"><span>Tax-inclusive quote from Wynn</span><strong>Not returned</strong></div>`;
    return `<article class="card hotel-card">
      <div class="hotel-top"><div><p class="card-eyebrow">${escapeHtml(quote.nights)} nights · ${escapeHtml(quote.adults)} adult</p><h3 class="hotel-name">${escapeHtml(quote.hotel)}</h3><p class="hotel-room">${escapeHtml(quote.roomType)} · ${escapeHtml(quote.roomSizeSqFt)} sq ft</p></div><span class="hotel-tag">${direct ? 'Quoted' : 'Estimate caveat'}</span></div>
      <div class="hotel-price">${money(displayed, direct ? 2 : 0)}</div><div class="hotel-price-label">${priceLabel}</div>
      <div class="price-breakdown">${rows}</div>
      <p class="note" style="margin:14px 0 0">${escapeHtml(quote.note)}</p>
      <div class="event-sources">${sourceLinks(quote.sourceIds, sources)}</div>
    </article>`;
  }

  function renderDashboard(tournaments, hotels) {
    const window = tournaments.meta.window;
    const events = tournaments.events.filter((event) => isInWindow(event, window));
    const counts = countStatuses(tournaments.events);
    const venetian = hotels.quotes.find((quote) => quote.hotel.includes('Venetian'));
    const hotelCount = hotels.quotes.length;
    const featured = events.slice().sort((a, b) => a.date.localeCompare(b.date)).slice(0, 4);
    return `
      <div class="container page-wrap">
        <section class="hero" aria-labelledby="page-title">
          <div class="hero-grid">
            <div>
              <div class="eyebrow">Research window · not user-selected</div>
              <h1 id="page-title">Plan the stay around the cards, not assumptions.</h1>
              <p class="lede">A source-linked Las Vegas poker and hotel planner. Every entry rule and room total is labeled for what the official evidence actually confirms—and what it does not.</p>
              <div class="hero-note"><span aria-hidden="true">◷</span> ${escapeHtml(window.label)} · working research dates</div>
              <div class="hero-actions"><a class="btn" href="${escapeHtml(urlFor('tournaments'))}">Explore tournaments <span aria-hidden="true">→</span></a><a class="btn btn-secondary" href="${escapeHtml(urlFor('hotels'))}">Compare stay quotes</a></div>
            </div>
            <aside class="hero-card" aria-label="Best available hotel quote">
              <span class="hero-card-label">Best-supported stay quote</span>
              <strong class="hero-card-value">${money(venetian?.quotedTotalUsd, 2)}</strong>
              <p class="hero-card-copy">The Venetian · 7 nights · fees and taxes included in the retrieved quote</p>
              <div class="hero-card-rule"></div>
              <div class="hero-card-small"><span>Wynn nightly display</span><strong>${money(hotels.quotes.find((q) => q.hotel.includes('Wynn'))?.displayedAverageNightUsd)} / night</strong></div>
              <div class="hero-card-small"><span>Wynn final tax total</span><strong>Not returned</strong></div>
            </aside>
          </div>
        </section>

        <section class="stat-grid" aria-label="Research summary">
          <div class="stat-card"><span class="stat-number">${counts['single-entry'] || 0}</span><span class="stat-label">Strict single-entry options confirmed</span></div>
          <div class="stat-card"><span class="stat-number">${counts.unconfirmed || 0}</span><span class="stat-label">Tracked events with entry terms unresolved</span></div>
          <div class="stat-card"><span class="stat-number">${counts['multiple-entry'] || 0}</span><span class="stat-label">Tracked events with re-entry confirmed</span></div>
          <div class="stat-card"><span class="stat-number">${hotelCount}</span><span class="stat-label">Date-specific hotel snapshots reviewed</span></div>
        </section>

        <section class="section">
          <div class="callout danger"><span class="callout-icon" aria-hidden="true">!</span><div><strong>No strict single-entry tournament is verified in this research snapshot.</strong><p>“Not verified” is not the same as “none exist.” The Venetian's one-day sheets do not publish a clear re-entry cap; WPT's Ladies Championship entry rule is also unverified. See the <a href="${escapeHtml(urlFor('review'))}">flagged-review list</a> before planning around an event.</p></div></div>
        </section>

        <section class="section">
          <div class="section-head"><div><div class="section-kicker">On the felt · selected listings</div><h2>What overlaps the working dates</h2></div><a class="text-link" href="${escapeHtml(urlFor('tournaments'))}">Full tracked list</a></div>
          <p class="note">A reviewed subset, not the full 85+ event WPT festival calendar. Tournaments and terms can change.</p>
          <div class="event-list">${featured.map((event) => eventCard(event, tournaments.venuesById, tournaments.sourcesById, window)).join('')}</div>
        </section>

        <section class="section">
          <div class="section-head"><div><div class="section-kicker">Sleep · current snapshot</div><h2>Two direct booking signals, different certainty</h2></div><a class="text-link" href="${escapeHtml(urlFor('hotels'))}">Hotel details</a></div>
          <div class="grid grid-2">${hotels.quotes.map((quote) => hotelCard(quote, hotels.sourcesById)).join('')}</div>
          <div class="callout blue" style="margin-top:14px"><span class="callout-icon" aria-hidden="true">i</span><div><strong>Not an apples-to-apples price ranking.</strong><p>Venetian returned a seven-night total including resort fees and tax. Wynn returned $355 average/night including resort fee but excluding tax; its all-in total is unknown. The $2,817.49 figure is only an estimate.</p></div></div>
        </section>

        <section class="section">
          <div class="section-head"><div><div class="section-kicker">How to use this planner</div><h2>Keep the unknowns visible</h2></div></div>
          <div class="grid grid-3">
            <article class="card"><div class="card-eyebrow">01 · Filter</div><h3>Start with the entry rule</h3><p class="card-copy">Use the tournament list to separate clear re-entry events from event rules that are still unknown. A one-day label alone is not enough.</p><a class="text-link" href="${escapeHtml(urlFor('tournaments'))}">Browse events</a></article>
            <article class="card"><div class="card-eyebrow">02 · Compare</div><h3>Use checkout totals</h3><p class="card-copy">Compare the same dates, occupancy, room class, resort fees, taxes, and cancellation terms—not just a nightly headline rate.</p><a class="text-link" href="${escapeHtml(urlFor('hotels'))}">See hotel evidence</a></article>
            <article class="card"><div class="card-eyebrow">03 · Confirm</div><h3>Ask before you commit</h3><p class="card-copy">Review the open questions and contact the venue for written event-specific terms. Re-check every official schedule before traveling.</p><a class="text-link" href="${escapeHtml(urlFor('suggestions'))}">Next steps</a></article>
          </div>
        </section>
        <p class="note">Tournament source review: ${escapeHtml(tournaments.meta.researchedAt)} · Hotel quote snapshot: ${escapeHtml(hotels.meta.researchedAt)} · Times are Las Vegas local time.</p>
      </div>`;
  }

  function countStatuses(events) {
    return events.reduce((counts, event) => {
      counts[event.entryStatus] = (counts[event.entryStatus] || 0) + 1;
      return counts;
    }, {});
  }

  function renderTournaments(tournaments) {
    const window = tournaments.meta.window;
    const counts = countStatuses(tournaments.events);
    return `<div class="container page-wrap">
      <div class="page-head"><div class="eyebrow">Tournament directory · source reviewed</div><h1 id="page-title">The tournament slate</h1><p class="lede">An event-by-event view of reviewed official schedules and structures. Entry status describes published evidence, not assumptions about what a room may allow.</p></div>
      <div class="callout danger"><span class="callout-icon" aria-hidden="true">!</span><div><strong>${counts['single-entry'] || 0} confirmed strict single-entry events in the reviewed listings.</strong><p>${escapeHtml(tournaments.meta.summary.caveat)} The 25 tracked records are a subset, not a complete tournament calendar.</p></div></div>
      <div class="stat-grid"><div class="stat-card"><span class="stat-number">${tournaments.events.length}</span><span class="stat-label">Tracked schedule records</span></div><div class="stat-card"><span class="stat-number">${counts.unconfirmed || 0}</span><span class="stat-label">Entry terms unverified</span></div><div class="stat-card"><span class="stat-number">${counts['multiple-entry'] || 0}</span><span class="stat-label">Multiple-entry allowed</span></div><div class="stat-card"><span class="stat-number">${counts.conflicting || 0}</span><span class="stat-label">Conflicting source records</span></div></div>
      <div class="filter-panel" role="search" aria-label="Filter tournament listings">
        <div class="field search-field"><label for="event-search">Search event / game</label><input id="event-search" type="search" placeholder="Try ‘bounty’ or ‘WPT’" autocomplete="off"></div>
        <div class="field"><label for="venue-filter">Venue</label><select id="venue-filter"><option value="all">All reviewed venues</option>${tournaments.venues.map((venue) => `<option value="${escapeHtml(venue.id)}">${escapeHtml(venue.name.split('—')[0].trim())}</option>`).join('')}</select></div>
        <div class="field"><label for="status-filter">Entry status</label><select id="status-filter"><option value="all">All terms</option><option value="single-entry">Strict single-entry confirmed</option><option value="multiple-entry">Multiple entry confirmed</option><option value="unconfirmed">Entry terms unverified</option><option value="conflicting">Source conflict</option></select></div>
        <div class="result-count" id="result-count" aria-live="polite"></div>
      </div>
      <div class="event-list" id="event-list" aria-live="polite"></div>
      <section class="section"><div class="section-head"><div><div class="section-kicker">Outside the working dates</div><h2>Worth noting, not stay events</h2></div></div><div class="grid grid-2">${tournaments.outsideWindow.map((event) => `<article class="card"><div class="card-title-row"><h3>${escapeHtml(event.title)}</h3>${pill(event.entryStatus)}</div><p class="card-copy">${escapeHtml(event.dates)} · ${event.buyInUsd == null ? '' : money(event.buyInUsd) + ' buy-in'}</p><p class="card-copy">${escapeHtml(event.entryRule)}</p><p class="note">${escapeHtml(event.note)}</p><div class="event-sources">${sourceLinks(event.sourceIds, tournaments.sourcesById)}</div></article>`).join('')}</div></section>
      <section class="section"><div class="section-head"><div><div class="section-kicker">Method</div><h2>What counts as single-entry here?</h2></div></div><div class="card"><p class="card-copy">${escapeHtml(tournaments.meta.strictSingleEntryDefinition)}</p><p class="card-copy">An event is listed as confirmed multiple-entry only when the reviewed official rules explicitly allow re-entry or additional entries. A missing rule stays “unverified.” If a structure says a player who bags for Day 2 cannot play later flights, that does not tell us whether a player who busts may enter another flight.</p><a class="text-link" href="${escapeHtml(assetFor('research/tournaments.md'))}">Open full source notes</a></div></section>
    </div>`;
  }

  function wireTournamentFilters(tournaments) {
    const list = document.getElementById('event-list');
    if (!list) return;
    const search = document.getElementById('event-search');
    const venue = document.getElementById('venue-filter');
    const status = document.getElementById('status-filter');
    const count = document.getElementById('result-count');
    const window = tournaments.meta.window;
    const render = () => {
      const term = search.value.trim().toLowerCase();
      const matching = tournaments.events.filter((event) => {
        const searchable = [event.title, event.game, event.series, event.entryRule, event.notes?.join(' '), tournaments.venuesById[event.venueId]?.name].join(' ').toLowerCase();
        return (!term || searchable.includes(term)) && (venue.value === 'all' || event.venueId === venue.value) && (status.value === 'all' || event.entryStatus === status.value);
      }).sort((a, b) => a.date.localeCompare(b.date) || (a.time || '').localeCompare(b.time || ''));
      list.innerHTML = matching.length
        ? matching.map((event) => eventCard(event, tournaments.venuesById, tournaments.sourcesById, window)).join('')
        : '<div class="empty-state">No tracked event matches those filters. Try another venue or entry status.</div>';
      count.textContent = `${matching.length} of ${tournaments.events.length} tracked records`;
    };
    [search, venue, status].forEach((control) => control.addEventListener('input', render));
    render();
  }

  function renderHotels(hotels) {
    const compare = hotels.comparison;
    const walk = hotels.walking[0];
    return `<div class="container page-wrap">
      <div class="page-head"><div class="eyebrow">Hotel comparison · direct booking evidence</div><h1 id="page-title">Stay near the action. Price the whole stay.</h1><p class="lede">A matched date/occupancy snapshot for ${escapeHtml(longDate(hotels.meta.window.checkIn))} to ${escapeHtml(longDate(hotels.meta.window.checkOut))}, ${escapeHtml(hotels.meta.window.nights)} nights, ${escapeHtml(hotels.meta.window.adults)} adult. These are research dates only—not a date choice from the user.</p></div>
      <div class="grid grid-2">${hotels.quotes.map((quote) => hotelCard(quote, hotels.sourcesById)).join('')}</div>
      <section class="section"><div class="callout blue"><span class="callout-icon" aria-hidden="true">i</span><div><strong>Price signal only—not an apples-to-apples ranking.</strong><p>${escapeHtml(compare.conclusion)} Wynn did not return a tax-inclusive total. Re-run both booking pages with identical dates, occupancy, room type, and cancel terms before deciding.</p></div></div></section>
      <section class="section"><div class="section-head"><div><div class="section-kicker">The rest of the Strip shortlist</div><h2>Fees are not room quotes</h2></div></div><div class="table-wrap"><table><thead><tr><th>Hotel</th><th>Published resort fee</th><th>Tax-inclusive room quote</th><th>Source</th></tr></thead><tbody>${hotels.otherResortFees.map((item) => `<tr><td><strong>${escapeHtml(item.hotel)}</strong></td><td>${money(item.feeUsdPerNight, 2)} / night${item.taxExtra ? ' + tax' : ''}${item.taxAmountDisplayedUsd ? `<br><span class="note">Displayed fee tax ${money(item.taxAmountDisplayedUsd, 2)}</span>` : ''}</td><td>Not retrieved for these dates</td><td>${sourceLinks(item.sourceIds, hotels.sourcesById)}</td></tr>`).join('')}</tbody></table></div></section>
      <section class="section"><div class="section-head"><div><div class="section-kicker">Walkability · unverified</div><h2>Close on the map, route not official</h2></div></div><div class="grid grid-2"><article class="card"><p class="card-eyebrow">Third-party route estimate</p><h3>${escapeHtml(walk.from)} → ${escapeHtml(walk.to)}</h3><div class="number-display">${walk.distanceFeet.toLocaleString()} ft</div><p class="card-copy" style="margin-top:6px">About ${escapeHtml(walk.estimatedMinutes)} min on foot per a third-party route planner.</p><p class="note">${escapeHtml(walk.note)}</p>${sourceLinks([walk.sourceId], hotels.sourcesById)}</article><article class="card"><p class="card-eyebrow">Official distance check</p><h3>No official walking time found</h3><p class="card-copy">Hotel websites reviewed did not publish an official pedestrian route between Wynn and The Venetian, or a verified walk time from other candidate hotels to the poker room.</p><p class="card-copy">Check accessibility, entrances, construction, weather, and current pedestrian routing before relying on a walk estimate.</p></article></div></section>
      <section class="section"><div class="section-head"><div><div class="section-kicker">Booking checklist</div><h2>Re-run at checkout</h2></div></div><div class="grid grid-3"><div class="card"><h3>Match the search</h3><p class="card-copy">Same dates, occupancy, room class, refundable/nonrefundable terms, and any promotion or membership.</p></div><div class="card"><h3>Compare the actual total</h3><p class="card-copy">Include room subtotal, resort fees, taxes, deposit, and any mandatory charges. Save the quote timestamp.</p></div><div class="card"><h3>Confirm the route</h3><p class="card-copy">Check an official map or current pedestrian route. Do not treat the 11-minute third-party estimate as a guarantee.</p></div></div></section>
      <p class="note">Source-by-source prices, fee terms, and limitations: <a href="${escapeHtml(assetFor('research/hotels.md'))}">hotel research notes</a> and <a href="${escapeHtml(assetFor('data/hotels.json'))}">machine-readable quote data</a>.</p>
    </div>`;
  }

  function renderAnalysis(tournaments, hotels) {
    const counts = countStatuses(tournaments.events);
    const total = tournaments.events.length;
    const bars = [
      ['Strict single-entry confirmed', counts['single-entry'] || 0, 'single-entry'],
      ['Entry terms unverified', counts.unconfirmed || 0, 'unconfirmed'],
      ['Re-entry / multiple entry confirmed', counts['multiple-entry'] || 0, 'multiple-entry'],
      ['Conflicting official listing', counts.conflicting || 0, 'conflicting']
    ];
    const chart = bars.map(([label, value, status]) => `<div class="metric-row"><div class="metric-label">${escapeHtml(label)}</div><div class="metric-track" aria-label="${value} of ${total}"><div class="metric-fill ${status}" style="width:${total ? (value / total) * 100 : 0}%;background:${status === 'unconfirmed' ? '#d3a85e' : status === 'multiple-entry' ? '#c3765c' : status === 'conflicting' ? '#819bb5' : '#2c7850'}"></div></div><div class="metric-value">${value}</div></div>`).join('');
    const ven = hotels.quotes.find((quote) => quote.hotel.includes('Venetian'));
    const wynn = hotels.quotes.find((quote) => quote.hotel.includes('Wynn'));
    return `<div class="container page-wrap">
      <div class="page-head"><div class="eyebrow">Analysis · evidence and limits</div><h1 id="page-title">The signal is clear. The gaps are, too.</h1><p class="lede">A compact read of the tournament and hotel evidence for the working Dec 13–20, 2026 research window.</p></div>
      <section class="grid grid-2">
        <article class="card"><p class="card-eyebrow">Tournament entry status · ${total} tracked records</p><h2 style="font-size:26px">No strict single-entry option is confirmed</h2>${chart}<p class="note">The data is a subset of published event listings, not a complete festival calendar. “Unverified” means the reviewed official source does not answer the question.</p></article>
        <article class="card"><p class="card-eyebrow">Planning implication</p><h2 style="font-size:26px">Treat eligibility as an open question</h2><p class="card-copy">Venetian's reviewed one-day structure sheets do not state an entry cap. Multi-flight rules restrict players who bag for Day 2, but do not clearly settle re-entry after a bust. WPT Ladies Championship re-entry terms were not found in the reviewed materials.</p><div class="card-rule"></div><p class="card-copy"><strong>Confirmed counterexamples:</strong> WPT World Championship allows up to four entries; Super Gold Million allows unlimited re-entry; Bellagio Friday/Sunday structures allow re-entry.</p><a class="text-link" href="${escapeHtml(urlFor('review'))}">Open flagged questions</a></article>
      </section>
      <section class="section"><div class="section-head"><div><div class="section-kicker">Hotel price evidence</div><h2>A quote and a calculation are not the same</h2></div></div><div class="grid grid-3"><article class="card"><p class="card-eyebrow">Venetian · quoted total</p><div class="number-display">${money(ven?.quotedTotalUsd, 2)}</div><p class="card-copy" style="margin-top:8px">7 nights, room + resort fee + tax. The quote's all-in average is ${money(ven?.quotedAllInPerNightUsd, 2)}/night.</p></article><article class="card"><p class="card-eyebrow">Wynn · displayed nightly rate</p><div class="number-display">${money(wynn?.displayedAverageNightUsd)}</div><p class="card-copy" style="margin-top:8px">Per night, includes resort fee, excludes taxes. Hotel did not return a tax-inclusive total.</p></article><article class="card"><p class="card-eyebrow">Wynn · modeled only</p><div class="number-display">${money(wynn?.estimatedAllInStayUsd, 2)}</div><p class="card-copy" style="margin-top:8px">Arithmetic using 13.38% from the cited Clark County guide. Not a booking quote; verify at checkout.</p></article></div></section>
      <section class="section"><div class="callout"><span class="callout-icon" aria-hidden="true">!</span><div><strong>Do not publish a cheapest-hotel claim from this snapshot.</strong><p>One property returned a tax-inclusive total; the other returned a nightly pre-tax display. The estimated difference is a directional calculation, not a confirmed saving.</p></div></div></section>
      <section class="section"><div class="section-head"><div><div class="section-kicker">Three facts that change the plan</div><h2>What the research can support</h2></div></div><div class="grid grid-3"><article class="card"><div class="number-display">0</div><h3 style="margin-top:9px">Verified strict single-entry</h3><p class="card-copy">No reviewed event can be recommended as meeting the strict definition yet.</p></article><article class="card"><div class="number-display">4 max</div><h3 style="margin-top:9px">WPT World Championship entries</h3><p class="card-copy">Three flights plus a separate Day 2 entry under the event-details page; explicitly multiple-entry.</p></article><article class="card"><div class="number-display">0</div><h3 style="margin-top:9px">8 a.m. tournaments verified</h3><p class="card-copy">The earliest reviewed nearby Venetian start was a 9:10 a.m. satellite on Dec 12, outside the assumed dates.</p></article></div></section>
      <p class="note">Full source trails: <a href="${escapeHtml(assetFor('research/tournaments.md'))}">tournament research</a> · <a href="${escapeHtml(assetFor('research/hotels.md'))}">hotel research</a>.</p>
    </div>`;
  }

  function renderQA(tournaments, hotels) {
    const ven = hotels.quotes.find((quote) => quote.hotel.includes('Venetian'));
    const wynn = hotels.quotes.find((quote) => quote.hotel.includes('Wynn'));
    const entries = [
      ['Did I choose Dec 13–20, 2026?', `No. This is a working research window aligned with the WPT World Championship dates. The interface labels it as an assumption; it should not be treated as a travel booking request or date selection.`, null],
      ['Is there a confirmed strict single-entry tournament?', `None is confirmed among the reviewed ${tournaments.events.length} tracked records. Eighteen listings have incomplete entry terms, six explicitly allow multiple entry, and one Bellagio Saturday listing is conflicting. This is not proof no strict single-entry event exists.`, 'tournaments'],
      ['Why is a “1Day” event not considered single-entry?', `A one-day label only describes event duration. It does not state whether a player can re-enter, rebuy, or buy another entry after busting. We need an official event-specific rule that clearly caps total entries at one.`, 'tournaments'],
      ['Can I play the WPT World Championship once?', `It is a multiple-entry event. Official event details set a four-entry maximum: one entry per starting flight plus one separate Day 2 entry. A player who advances to Day 2 cannot enter a later starting flight. The $1 million mystery payout addition is not a guaranteed prize pool.`, 'tournaments'],
      ['Is the WPT Ladies Championship a single-entry option?', `Unknown. The official schedule lists the Dec 13–14 event and buy-in, but re-entry/entry-cap terms were not verified in the reviewed official materials. Ask Wynn for the event-specific written terms.`, 'review'],
      ['Is The Venetian cheaper than Wynn?', `The Venetian returned a $2,420.40 seven-night quote with resort fees and taxes. Wynn displayed $355 per night including resort fee, excluding taxes; it did not return an all-in total. The $2,817.49 figure is an estimate from applying the cited 13.38% tax rate, not a Wynn quote, so a definitive apples-to-apples comparison is not supported.`, 'hotels'],
      ['Are there official walking times between the hotels?', `No official hotel-to-hotel pedestrian route/time was verified. Rome2Rio estimates about ${walkDistance(hotels)} feet / 11 minutes, but it is a third-party route estimate and not guaranteed.`, 'hotels'],
      ['Are there any verified 8:00 a.m. events?', `No. The earliest nearby start found in the reviewed Venetian material is a 9:10 a.m. satellite on Dec 12, which is outside the working stay window.`, 'tournaments'],
      ['How current are these prices and schedules?', `They are a snapshot checked Nov 16, 2026. Schedules, re-entry terms, inventory, taxes, promotions, and prices can change. Recheck the official operator or hotel's live page before committing.`, 'publication']
    ];
    return `<div class="container page-wrap"><div class="page-head"><div class="eyebrow">Q&amp;A · what this snapshot means</div><h1 id="page-title">Straight answers. No hidden assumptions.</h1><p class="lede">The planner is designed to surface what is known, what is not, and the next verification step.</p></div><div class="faq-list">${entries.map(([question, answer, route]) => `<details class="faq"><summary>${escapeHtml(question)}</summary><p class="answer">${escapeHtml(answer)}${route ? ` <a href="${escapeHtml(urlFor(route))}">See ${escapeHtml(routeNames[route])} →</a>` : ''}</p></details>`).join('')}</div><section class="section"><div class="callout blue"><span class="callout-icon" aria-hidden="true">i</span><div><strong>Working dates, not user-selected dates.</strong><p>Research and travel planning should be revised if the user chooses a different date window.</p></div></div></section></div>`;
  }

  function walkDistance(hotels) { return hotels.walking?.[0]?.distanceFeet?.toLocaleString() || '3,160'; }

  function renderSuggestions() {
    return `<div class="container page-wrap"><div class="page-head"><div class="eyebrow">Suggestions · next sensible moves</div><h1 id="page-title">A plan that waits for the missing facts.</h1><p class="lede">These are research actions, not a booked itinerary. The date range is still only a working assumption.</p></div>
      <div class="callout danger"><span class="callout-icon" aria-hidden="true">!</span><div><strong>Recommendation for now: do not select an event on a “single-entry” assumption.</strong><p>No strict single-entry candidate is verified in the reviewed records. First confirm event-specific entry rules, then compare dates and rooms.</p></div></div>
      <section class="section"><div class="section-head"><div><div class="section-kicker">Priority order</div><h2>Resolve the decision blockers</h2></div></div><div class="steps">
        <article class="step"><span class="step-number">1</span><div><h3>Confirm the actual travel dates</h3><p>Dec 13–20, 2026 was selected only as a research window around the WPT World Championship. Re-run the event/hotel search when the user supplies dates.</p></div></article>
        <article class="step"><span class="step-number">2</span><div><h3>Ask Venetian for the exact entry cap</h3><p>For each appealing one-day event, ask whether a player may re-enter/rebuy or buy any extra entry after busting. For multi-flight events, ask whether a busted player may enter another flight. Request the event/date-specific rule in writing.</p></div></article>
        <article class="step"><span class="step-number">3</span><div><h3>Ask Wynn about the Ladies Championship</h3><p>It is the clearest in-window candidate whose entry terms remain unresolved: Dec 13–14, $1,100, $250,000 guarantee. Confirm whether the structure permits any re-entry or additional entry.</p></div></article>
        <article class="step"><span class="step-number">4</span><div><h3>Re-quote hotels on matching terms</h3><p>Get a tax-inclusive Wynn checkout total and rerun Venetian with the same occupancy and cancellation terms. Ask for current official pedestrian/accessibility route information if walking matters.</p></div></article>
        <article class="step"><span class="step-number">5</span><div><h3>Re-check schedule changes before publishing</h3><p>Confirm the WPT full festival schedule, Bellagio Saturday terms, Venetian event structures, and resort fees near the actual travel date. Preserve a timestamp and source URL for every updated claim.</p></div></article>
      </div></section>
      <section class="section"><div class="section-head"><div><div class="section-kicker">If the window remains Dec 13–20</div><h2>Research-first shortlist</h2></div></div><div class="grid grid-3"><article class="card"><span class="pill unconfirmed">Terms unverified</span><h3 style="margin-top:12px">Venetian one-day events</h3><p class="card-copy">Broadest daily choice in the reviewed schedule, but structures do not prove strict single-entry. Ask about re-entry before adding one to a plan.</p></article><article class="card"><span class="pill unconfirmed">Terms unverified</span><h3 style="margin-top:12px">WPT Ladies Championship</h3><p class="card-copy">Dec 13–14, $1,100, $250K guarantee. Only a candidate pending explicit entry terms—not a confirmed single-entry recommendation.</p></article><article class="card"><span class="pill multiple-entry">Multiple entry</span><h3 style="margin-top:12px">WPT headline events</h3><p class="card-copy">World Championship permits up to four entries; Super Gold Million allows unlimited re-entry. Exclude these if a strict one-entry rule is required.</p></article></div></section>
      <p class="note">No tournament registration, hotel booking, or travel selection is made by this planner.</p></div>`;
  }

  function renderReview(tournaments, hotels) {
    const counts = countStatuses(tournaments.events);
    const flags = [
      { level: 'High priority', cls: 'high', title: 'No event is verified strict single-entry', body: `${counts.unconfirmed || 0} records have unverified entry rules. In particular, Venetian one-day structures are silent on re-entry caps, and a multi-flight “no later flight after bagging” rule does not settle what happens after a bust.`, action: 'Ask the room for event/date-specific written terms; do not label unknown records single-entry.', sources: ['tournaments'] },
      { level: 'High priority', cls: 'high', title: 'WPT Ladies Championship entry cap not verified', body: 'The official event listing confirms Dec 13–14, $1,100 and $250,000 guarantee; the reviewed materials did not confirm whether re-entry or additional entries are allowed.', action: 'Contact Wynn tournament operations for the current structure and maximum paid entries.', sources: ['tournaments'] },
      { level: 'High priority', cls: 'high', title: 'Bellagio Saturday terms conflict', body: 'The official poker page lists $1,000, linked flyer title says $1,100, and flyer terms describe a $600 buy-in, $50,000 guarantee and a Sept 13, 2026 Day 2. The flyer is not reliable for Dec 19.', action: 'Exclude the Saturday event from cost/entry recommendations until Bellagio provides current terms.', sources: ['tournaments'] },
      { level: 'Medium', cls: 'medium', title: 'Wynn all-in room total is missing', body: "The direct Wynn page displayed $355 average/night including resort fee, excluding taxes, but did not return a tax-inclusive total. The planner's $2,817.49 figure is a calculation using a cited tax rate, not a hotel quote.", action: 'Re-run Wynn checkout for the same dates, room, occupancy, and cancellation terms as The Venetian.', sources: ['hotels'] },
      { level: 'Medium', cls: 'medium', title: 'Room-tax estimate uses a published 2021 county guide', body: `The ${((hotels.meta.taxEstimateRate || 0) * 100).toFixed(2)}% rate is from the cited Clark County guide, which dates to July 2021. It is a transparent estimate input, not proof the rate/tax base remains applicable in Dec 2026.`, action: 'Verify current lodging tax and taxable fee treatment at booking; keep the Wynn official total blank until quoted.', sources: ['hotels'] },
      { level: 'Medium', cls: 'medium', title: 'Official hotel-to-hotel walking route not verified', body: 'The 3,160-ft / 11-min Wynn–Venetian estimate comes from a third-party route planner, not either hotel. No official pedestrian route/time was found.', action: 'Check a current official map/accessible route and conditions if a walking plan is important.', sources: ['hotels'] },
      { level: 'Medium', cls: 'medium', title: 'WPT record is not the full 85+ event schedule', body: 'The WPT festival spans Nov 27–Dec 21 and advertises 85+ events. The data records the headline events and selected side events whose terms were reviewed; it is not exhaustive.', action: 'Check the live official festival schedule for additions, times, guarantees, and later terms.', sources: ['tournaments'] },
      { level: 'Low', cls: 'medium', title: 'PGT ARIA structure and schedule disagree on start time', body: 'The official PGT schedule lists 3 p.m.; the official structure PDF says noon. The series is Nov 28–Dec 2, outside this working window, but the conflict is retained for future reuse.', action: 'Verify with PGT/ARIA before using the schedule; do not choose one time by inference.', sources: ['tournaments'] },
      { level: 'Low', cls: 'medium', title: 'No official walking time / no 8 a.m. event verified', body: 'No 8 a.m. tournament appears in the reviewed schedule. The earliest reviewed nearby Venetian start (9:10 a.m.) is a Dec 12 satellite outside the working dates.', action: "If early starts matter, recheck all rooms' latest official schedules once travel dates are known.", sources: ['tournaments'] }
    ];
    return `<div class="container page-wrap"><div class="page-head"><div class="eyebrow">Flagged for review · unresolved and conflicting</div><h1 id="page-title">Open questions stay open.</h1><p class="lede">This page collects the facts that should not be guessed. Resolve the high-priority items before making an eligibility recommendation or claiming a hotel is cheaper.</p></div><div class="stat-grid"><div class="stat-card"><span class="stat-number">${counts.unconfirmed || 0}</span><span class="stat-label">Tournament records with unknown terms</span></div><div class="stat-card"><span class="stat-number">${counts.conflicting || 0}</span><span class="stat-label">Conflicting official listing</span></div><div class="stat-card"><span class="stat-number">2</span><span class="stat-label">Hotel prices not directly comparable</span></div><div class="stat-card"><span class="stat-number">1</span><span class="stat-label">Third-party walking estimate only</span></div></div><div class="review-list" style="margin-top:18px">${flags.map((flag) => `<article class="review-item"><span class="review-level ${flag.cls}">${escapeHtml(flag.level)}</span><div><h3>${escapeHtml(flag.title)}</h3><p>${escapeHtml(flag.body)}</p><p class="review-action"><strong>Next step:</strong> ${escapeHtml(flag.action)}</p><div class="event-sources">${flag.sources.map((route) => `<a class="source-chip" href="${escapeHtml(urlFor(route))}">See ${escapeHtml(routeNames[route])} ↗</a>`).join('')}</div></div></article>`).join('')}</div><section class="section"><div class="callout"><span class="callout-icon" aria-hidden="true">✓</span><div><strong>Resolved: WPT World Championship maximum entry count.</strong><p>The official event-detail page explicitly states four entries maximum—one per starting flight plus one Day 2 entry. The event is therefore clearly multiple-entry, not eligible for a strict single-entry plan.</p></div></div></section><p class="note">Source links and dated notes are in the <a href="${escapeHtml(assetFor('research/tournaments.md'))}">tournament research</a> and <a href="${escapeHtml(assetFor('research/hotels.md'))}">hotel research</a> files.</p></div>`;
  }

  function renderPublication(tournaments, hotels) {
    return `<div class="container page-wrap"><div class="page-head"><div class="eyebrow">Publication workflow · versioned evidence</div><h1 id="page-title">Publish only what the sources support.</h1><p class="lede">A small, static research product with an explicit review path. Data remains source-linked, unknown values remain blank, and publication is gated by validation.</p></div>
      <div class="grid grid-3"><article class="card"><p class="card-eyebrow">Research snapshot</p><div class="number-display">Nov 16</div><p class="card-copy" style="margin-top:8px">2026 · source check date</p></article><article class="card"><p class="card-eyebrow">Tournament files</p><div class="number-display">${tournaments.events.length}</div><p class="card-copy" style="margin-top:8px">Tracked event records · not exhaustive</p></article><article class="card"><p class="card-eyebrow">Hotel snapshots</p><div class="number-display">${hotels.quotes.length}</div><p class="card-copy" style="margin-top:8px">Two different price-certainty levels</p></article></div>
      <section class="section"><div class="section-head"><div><div class="section-kicker">Release path</div><h2>From source to live page</h2></div></div><div class="steps">
        <article class="step"><span class="step-number">1</span><div><h3>Capture the official source</h3><p>Use operator/venue/hotel pages first. Record exact URL, checked date, the fact supported, and any contradiction or missing clause.</p></div></article>
        <article class="step"><span class="step-number">2</span><div><h3>Update the research notes and JSON</h3><p>Put source-linked prose in <a href="${escapeHtml(assetFor('research/tournaments.md'))}">research/tournaments.md</a> or <a href="${escapeHtml(assetFor('research/hotels.md'))}">research/hotels.md</a>. Update the corresponding source, event, quote, or flag in <a href="${escapeHtml(assetFor('data/tournaments.json'))}">data/tournaments.json</a> and <a href="${escapeHtml(assetFor('data/hotels.json'))}">data/hotels.json</a>. Leave unsupported prices/caps blank.</p></div></article>
        <article class="step"><span class="step-number">3</span><div><h3>Run local checks</h3><p>The build validates JSON, source IDs, calculated summary counts, required uncertainty fields, internal links, and the static output bundle. See the validation workflow in the repository.</p></div></article>
        <article class="step"><span class="step-number">4</span><div><h3>Review before publishing</h3><p>Update the Flagged Review page and coordination board. Open a pull request only after checks pass; merge only after required CI succeeds. The existing GitHub Pages site is published from the repository root on main; this planner lives in its own subdirectory so it does not overwrite another session's site.</p></div></article>
        <article class="step"><span class="step-number">5</span><div><h3>Verify the live deployment</h3><p>After release, open the Pages URL and test navigation, data loads, source links, mobile layout, and external link validity. Record run/deployment status and timestamp on the board.</p></div></article>
      </div></section>
      <section class="section"><div class="section-head"><div><div class="section-kicker">Current publication caveats</div><h2>These are not bookings or eligibility guarantees</h2></div></div><div class="grid grid-2"><article class="card"><h3>Tournaments</h3><p class="card-copy">${tournaments.meta.summary.headline} ${tournaments.meta.summary.caveat}</p><a class="text-link" href="${escapeHtml(urlFor('review'))}">Open review queue</a></article><article class="card"><h3>Hotels</h3><p class="card-copy">Venetian is a retrieved quote; Wynn's all-in amount is an estimate. The window is not user-selected. Recheck current room terms and fees before any booking.</p><a class="text-link" href="${escapeHtml(urlFor('hotels'))}">See quote details</a></article></div></section>
      <p class="note">Site scope and release ownership: <a href="https://github.com/karagemop466-tech/Poker5/blob/main/COORDINATION.md" target="_blank" rel="noopener noreferrer">coordination board</a>. For a build preview or test result, use the repository workflow/run linked from GitHub.</p></div>`;
  }

  async function init() {
    renderChrome();
    const main = document.getElementById('page-content');
    if (!main) return;
    try {
      const [tournamentResponse, hotelResponse] = await Promise.all([
        fetch(assetFor('data/tournaments.json')),
        fetch(assetFor('data/hotels.json'))
      ]);
      if (!tournamentResponse.ok || !hotelResponse.ok) throw new Error('Could not load the research data files.');
      const tournaments = await tournamentResponse.json();
      const hotels = await hotelResponse.json();
      tournaments.venuesById = Object.fromEntries(tournaments.venues.map((venue) => [venue.id, venue]));
      tournaments.sourcesById = Object.fromEntries(tournaments.sources.map((source) => [source.id, source]));
      hotels.sourcesById = Object.fromEntries(hotels.sources.map((source) => [source.id, source]));
      const renderers = {
        dashboard: () => renderDashboard(tournaments, hotels),
        tournaments: () => renderTournaments(tournaments),
        hotels: () => renderHotels(hotels),
        analysis: () => renderAnalysis(tournaments, hotels),
        qa: () => renderQA(tournaments, hotels),
        suggestions: renderSuggestions,
        review: () => renderReview(tournaments, hotels),
        publication: () => renderPublication(tournaments, hotels)
      };
      main.innerHTML = (renderers[PAGE] || renderers.dashboard)();
      if (PAGE === 'tournaments') wireTournamentFilters(tournaments);
      document.title = `${routeNames[PAGE] || 'Dashboard'} · Felt & Stay`;
    } catch (error) {
      main.innerHTML = `<div class="container page-wrap"><div class="callout danger"><span class="callout-icon" aria-hidden="true">!</span><div><strong>Research data could not be loaded.</strong><p>${escapeHtml(error.message || 'Please reload the page.')}</p></div></div></div>`;
    }
  }

  init();
})();
