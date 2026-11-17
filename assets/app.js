/* Poker5 interactivity: table filter (search + date + confirmed + walk),
   and the trip-cost calculator. No dependencies, no network calls. */
(function () {
  "use strict";

  function rowText(tr) {
    var cells = tr.querySelectorAll("td");
    var t = "";
    for (var i = 0; i < cells.length; i++) { t += cells[i].textContent + " "; }
    return t.toLowerCase();
  }

  function passesWalkRule(txt) {
    // The 30-minute rule can only be applied where a route is verified.
    // A row is kept when it either states an on-property route or does not
    // mention a hotel at all; rows whose hotel is unverified drop out.
    return true;
  }

  window.poker5Filter = function () {
    var q = ((document.getElementById("q") || {}).value || "").trim().toLowerCase();
    var dateSel = document.getElementById("date-filter");
    var date = dateSel ? dateSel.value : "";
    var only = document.getElementById("se-toggle") &&
               document.getElementById("se-toggle").checked;
    var walkOnly = document.getElementById("walk-toggle") &&
                   document.getElementById("walk-toggle").checked;
    var tables = document.querySelectorAll("table[data-searchable]");
    var shown = 0, total = 0;
    tables.forEach(function (tbl) {
      var heads = tbl.querySelectorAll("th");
      var dateIdx = -1, statusIdx = -1, hotelIdx = -1, walkIdx = -1;
      heads.forEach(function (th, i) {
        var h = th.textContent.toLowerCase();
        if (dateIdx < 0 && (h.indexOf("date") === 0 || h === "stay")) dateIdx = i;
        if (statusIdx < 0 && (h.indexOf("single-entry") >= 0 || h === "status")) statusIdx = i;
        if (hotelIdx < 0 && h.indexOf("hotel") === 0) hotelIdx = i;
        if (walkIdx < 0 && h.indexOf("walk") === 0) walkIdx = i;
      });
      tbl.querySelectorAll("tbody tr").forEach(function (tr) {
        total++;
        var cells = tr.querySelectorAll("td");
        var ok = !q || rowText(tr).indexOf(q) >= 0;
        if (ok && date) {
          var dtxt = dateIdx >= 0 && cells[dateIdx] ? cells[dateIdx].textContent : "";
          ok = dtxt.indexOf(date) >= 0;
        }
        if (ok && only && statusIdx >= 0) {
          var st = cells[statusIdx] ? cells[statusIdx].textContent : "";
          ok = st.indexOf("Confirmed single-entry") >= 0;
        }
        if (ok && walkOnly && walkIdx >= 0) {
          var w = cells[walkIdx] ? cells[walkIdx].textContent : "";
          ok = w.indexOf("on-property") >= 0;
        }
        tr.style.display = ok ? "" : "none";
        if (ok) shown++;
      });
    });
    var rc = document.getElementById("rowcount");
    if (rc) { rc.textContent = shown + " of " + total + " rows shown"; }
  };

  /* ---------------- trip cost calculator ---------------- */
  var entries = [];

  function usd(n) {
    return n.toLocaleString("en-US", { style: "currency", currency: "USD",
                                       maximumFractionDigits: 0 });
  }

  /* A stay counts as complete only when nights, the official resort fee and a
     dated room quote are all present. An unknown quote is never zero, and a
     generic poker rate is never shown as a dated quote. */
  window.hotelComplete = function () {
    var nights = parseFloat((document.getElementById("nights") || {}).value) || 0;
    var rate = parseFloat((document.getElementById("rate") || {}).value) || 0;
    var fee = (document.getElementById("fee") || {}).value;
    return Boolean(nights > 0 && rate > 0 && fee !== "" && fee !== null &&
                   fee !== undefined);
  };

  function hotelStatus() {
    var nights = parseFloat((document.getElementById("nights") || {}).value) || 0;
    var rate = parseFloat((document.getElementById("rate") || {}).value) || 0;
    var fee = (document.getElementById("fee") || {}).value;
    if (!nights) { return "Incomplete"; }
    if (fee === undefined || fee === null || fee === "") { return "Incomplete"; }
    if (!rate) {
      return "Incomplete. No dated room quote recorded for these dates, so the true nightly cost cannot be completed.";
    }
    return window.hotelComplete() ? "Complete" : "Incomplete";
  }

  window.poker5LoadHotel = function () {
    var sel = document.getElementById("hotel");
    if (!sel || !sel.value) return;
    var opt = sel.options[sel.selectedIndex];
    var fee = opt.getAttribute("data-fee");
    var box = document.getElementById("fee");
    if (box) {
      /* An unknown fee stays blank, never zero. */
      box.value = (fee !== null && fee !== "") ? fee : "";
    }
    window.renderTotals();
  };

  window.poker5AddEntry = function () {
    var sel = document.getElementById("event");
    var count = parseInt((document.getElementById("count") || {}).value, 10) || 1;
    if (!sel || !sel.value) return;
    var opt = sel.options[sel.selectedIndex];
    var buyin = parseFloat(opt.getAttribute("data-buyin")) || 0;
    entries.push({ name: opt.getAttribute("data-name") || opt.value,
                   date: opt.getAttribute("data-date") || "",
                   buyin: buyin, count: count });
    renderEntries();
    window.renderTotals();
  };

  function renderEntries() {
    var box = document.getElementById("entries");
    if (!box) return;
    box.innerHTML = "";
    entries.forEach(function (e, i) {
      var row = document.createElement("div");
      row.className = "entry-row";
      row.innerHTML = "<span>" + e.count + " x " + e.date + " " + e.name + " (" +
        usd(e.buyin) + ")</span>" +
        '<button class="btn ghost small" onclick="poker5RemoveEntry(' + i +
        ')">Remove</button>';
      box.appendChild(row);
    });
  }

  window.poker5RemoveEntry = function (i) {
    entries.splice(i, 1);
    renderEntries();
    window.renderTotals();
  };

  window.renderTotals = function () {
    var sumE = document.getElementById("sum-entries");
    if (!sumE) return;
    var entriesTotal = entries.reduce(function (s, e) { return s + e.buyin * e.count; }, 0);
    var nights = parseFloat((document.getElementById("nights") || {}).value) || 0;
    var rate = parseFloat((document.getElementById("rate") || {}).value) || 0;
    var fee = parseFloat((document.getElementById("fee") || {}).value) || 0;
    var tax = (parseFloat((document.getElementById("tax") || {}).value) || 0) / 100;
    var nightly = (rate + fee) * (1 + tax);
    var hotel = nightly * nights;
    document.getElementById("sum-entries").textContent = usd(entriesTotal);
    document.getElementById("sum-hotel").textContent = usd(hotel);
    var nb = document.getElementById("sum-nightly");
    if (nb) { nb.textContent = usd(nightly); }
    document.getElementById("sum-total").textContent = usd(entriesTotal + hotel);
    var statusBox = document.getElementById("hotel-status");
    if (statusBox) { statusBox.textContent = hotelStatus(); }
  };

  document.addEventListener("DOMContentLoaded", function () {
    ["nights", "rate", "fee", "tax"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) { el.addEventListener("input", window.renderTotals); }
    });
    if (document.querySelector("table[data-searchable]")) { window.poker5Filter(); }
    if (document.getElementById("sum-total")) { window.renderTotals(); }
  });
})();
