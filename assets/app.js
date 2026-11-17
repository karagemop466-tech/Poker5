/* Poker5 root-site interactivity: global search, single-entry toggle,
   date filter and the trip-cost calculator. No external dependencies. */
(function () {
  "use strict";

  function visible(tr, query, onlyConfirmed) {
    var cells = tr.querySelectorAll("td");
    var text = "";
    for (var i = 0; i < cells.length; i++) text += (cells[i].textContent || "") + " ";
    text = text.toLowerCase();
    if (query && text.indexOf(query) === -1) return false;
    if (onlyConfirmed) {
      var badge = tr.querySelector(".badge");
      if (!badge || badge.textContent.indexOf("Confirmed single-entry") === -1) return false;
    }
    return true;
  }

  window.poker5Filter = function () {
    var q = (document.getElementById("q") || {}).value || "";
    var only = document.getElementById("se-toggle") && document.getElementById("se-toggle").checked;
    q = q.trim().toLowerCase();
    var tables = document.querySelectorAll("table[data-searchable]");
    var anyVisible = false;
    tables.forEach(function (tbl) {
      var rows = tbl.querySelectorAll("tbody tr");
      rows.forEach(function (tr) {
        var show = visible(tr, q, only);
        tr.style.display = show ? "" : "none";
        if (show) anyVisible = true;
      });
    });
    return anyVisible;
  };

  // Trip-cost calculator state.
  var entries = [];
  window.poker5AddEntry = function () {
    var sel = document.getElementById("event");
    var count = parseInt(document.getElementById("count").value, 10) || 1;
    if (!sel.value) return;
    var opt = sel.options[sel.selectedIndex];
    var buyin = parseFloat(opt.getAttribute("data-buyin").replace(/[^0-9.]/g, "")) || 0;
    var name = opt.value;
    entries.push({ name: name, buyin: buyin, count: count });
    renderEntries();
    renderTotals();
  };

  function renderEntries() {
    var box = document.getElementById("entries");
    if (!box) return;
    box.innerHTML = "";
    entries.forEach(function (e, i) {
      var row = document.createElement("div");
      row.className = "entry-row";
      row.innerHTML = "<span>" + e.count + " &times; " + e.name + " (" +
        e.buyin.toLocaleString("en-US", { style: "currency", currency: "USD" }) + ")</span>" +
        "<button class=\"btn ghost small\" onclick=\"poker5RemoveEntry(" + i + ")\">Remove</button>";
      box.appendChild(row);
    });
  }
  window.poker5RemoveEntry = function (i) {
    entries.splice(i, 1);
    renderEntries();
    renderTotals();
  };

  window.renderTotals = function () {
    var sumE = document.getElementById("sum-entries");
    var sumH = document.getElementById("sum-hotel");
    var sumT = document.getElementById("sum-total");
    if (!sumE) return;
    var entriesTotal = entries.reduce(function (s, e) { return s + e.buyin * e.count; }, 0);
    var nights = parseFloat(document.getElementById("nights").value) || 0;
    var rate = parseFloat(document.getElementById("rate").value) || 0;
    var fee = parseFloat(document.getElementById("fee").value) || 0;
    var tax = (parseFloat(document.getElementById("tax").value) || 0) / 100;
    var trueNightly = (rate + fee) * (1 + tax);
    var hotelTotal = trueNightly * nights;
    sumE.textContent = "$" + entriesTotal.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
    sumH.textContent = "$" + hotelTotal.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
    sumT.textContent = "$" + (entriesTotal + hotelTotal).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  };

  // Wire hotel select to load logged rate/fee.
  document.addEventListener("DOMContentLoaded", function () {
    var hotel = document.getElementById("hotel");
    if (hotel) {
      hotel.addEventListener("change", function () {
        var opt = hotel.options[hotel.selectedIndex];
        if (!opt.value) return;
        var rate = opt.getAttribute("data-rate");
        var fee = opt.getAttribute("data-fee");
        if (rate !== "") document.getElementById("rate").value = parseFloat(rate).toFixed(0);
        if (fee !== "") document.getElementById("fee").value = parseFloat(fee).toFixed(0);
        renderTotals();
      });
    }
    ["nights", "rate", "fee", "tax", "count"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener("input", renderTotals);
    });
    renderTotals();
  });
})();
