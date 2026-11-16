(() => {
  const root = document.querySelector("#calendar-root");
  if (!root) return;

  const search = document.querySelector("#event-search");
  const dateFilter = document.querySelector("#date-filter");
  const venueFilter = document.querySelector("#venue-filter");
  const resultCount = document.querySelector("#result-count");
  const totalCount = document.querySelector("[data-total-events]");
  const loadError = document.querySelector("#calendar-error");
  const startCount = document.querySelector("[data-start-count]");

  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  };

  const timeLabel = (value) => {
    const [rawHour, minute] = value.split(":").map(Number);
    const suffix = rawHour < 12 ? "AM" : "PM";
    return `${((rawHour + 11) % 12) + 1}:${String(minute).padStart(2, "0")} ${suffix}`;
  };

  const dateLabel = (value, options = {}) => new Intl.DateTimeFormat("en-US", {
    weekday: options.weekday || "long",
    month: "long",
    day: "numeric",
    year: options.year ? "numeric" : undefined,
    timeZone: "UTC"
  }).format(new Date(`${value}T12:00:00Z`));

  const statusDetails = (status) => {
    const labels = {
      "unverified": ["Entry rule unverified", "pill-amber"],
      "multi-flight": ["Multi-flight · cap unclear", "pill-amber"],
      "re-entry": ["Re-entry confirmed", "pill-coral"],
      "continuation": ["Day 2 / continuation", "pill-blue"],
      "satellite": ["Satellite", "pill-blue"],
      "review": ["Flagged for review", "pill-coral"]
    };
    return labels[status] || [status, ""];
  };

  const createEventCard = (event, sources) => {
    const card = make("article", "event-card");
    const time = make("div", "event-time", timeLabel(event.time));
    const main = make("div", "event-main");
    main.append(make("div", "event-series", `${event.venue} · ${event.series}`));
    main.append(make("h3", "", event.name));
    const [statusLabel, statusClass] = statusDetails(event.status);
    main.append(make("span", `pill ${statusClass}`, statusLabel));
    main.append(make("p", "", event.entryRule || "Entry limit not verified in the official structure reviewed."));
    if (event.notes) main.append(make("p", "", event.notes));

    const facts = make("div", "event-facts");
    const buyIn = make("div", "event-fact");
    buyIn.append(make("span", "meta-label", "Buy-in"));
    buyIn.append(make("strong", "", event.buyIn || (event.status === "continuation" ? "No new buy-in listed" : "Not listed")));
    const guarantee = make("div", "event-fact");
    guarantee.append(make("span", "meta-label", "Guarantee / prize"));
    guarantee.append(make("strong", "", event.guarantee || "Not listed"));
    facts.append(buyIn, guarantee);
    if (event.poolShare) {
      const share = make("div", "event-fact");
      share.append(make("span", "meta-label", "Prize-pool share"));
      share.append(make("strong", "", event.poolShare));
      facts.append(share);
    }

    const links = make("div", "event-links");
    const schedule = sources[event.schedule];
    if (schedule) {
      const link = make("a", "", schedule.label);
      link.href = schedule.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      links.append(link);
    }
    const rules = sources[event.rules];
    if (rules) {
      const link = make("a", "", rules.label);
      link.href = rules.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      links.append(link);
    }
    facts.append(links);
    card.append(time, main, facts);
    return card;
  };

  const load = async () => {
    try {
      const response = await fetch("data/tournaments.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const events = [...data.events].sort((a, b) => `${a.date} ${a.time}`.localeCompare(`${b.date} ${b.time}`));
      if (totalCount) totalCount.textContent = String(events.length);
      if (startCount) startCount.textContent = String(events.length);

      const dates = [...new Set(events.map((event) => event.date))];
      for (const date of dates) {
        const option = make("option", "", dateLabel(date, { weekday: "short" }));
        option.value = date;
        dateFilter.append(option);
      }
      const venues = [...new Set(events.map((event) => event.venue))].sort();
      for (const venue of venues) {
        const option = make("option", "", venue);
        option.value = venue;
        venueFilter.append(option);
      }

      const render = () => {
        const query = search.value.trim().toLowerCase();
        const selectedDate = dateFilter.value;
        const selectedVenue = venueFilter.value;
        const filtered = events.filter((event) => {
          const matchesDate = !selectedDate || event.date === selectedDate;
          const matchesVenue = !selectedVenue || event.venue === selectedVenue;
          const searchable = [event.name, event.series, event.venue, event.buyIn, event.guarantee, event.entryRule, event.notes].join(" ").toLowerCase();
          return matchesDate && matchesVenue && (!query || searchable.includes(query));
        });
        root.replaceChildren();
        resultCount.replaceChildren();
        resultCount.append(make("strong", "", String(filtered.length)), document.createTextNode(` of ${events.length} schedule rows · starts in Las Vegas local time (PST)`));

        if (!filtered.length) {
          root.append(make("div", "no-results", "No events match those filters. Try clearing the search or changing the day."));
          return;
        }
        const byDate = new Map();
        for (const event of filtered) {
          if (!byDate.has(event.date)) byDate.set(event.date, []);
          byDate.get(event.date).push(event);
        }
        for (const [date, dayEvents] of byDate) {
          const group = make("section", "day-group");
          const header = make("div", "day-header");
          const title = make("h2", "", dateLabel(date));
          const note = date === data.window.checkOut ? "Checkout day · events are shown for context" : `${dayEvents.length} listed start${dayEvents.length === 1 ? "" : "s"}`;
          header.append(title, make("small", "", note));
          const list = make("div", "day-events");
          for (const event of dayEvents) list.append(createEventCard(event, data.sources));
          group.append(header, list);
          root.append(group);
        }
      };
      search.addEventListener("input", render);
      dateFilter.addEventListener("change", render);
      venueFilter.addEventListener("change", render);
      render();
    } catch (error) {
      console.error("Could not load tournament data", error);
      loadError.hidden = false;
      loadError.textContent = "The schedule data could not be loaded. Open the dashboard from a web server (not directly as a file) and try again.";
    }
  };

  load();
})();
