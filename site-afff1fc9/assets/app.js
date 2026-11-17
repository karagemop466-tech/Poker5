// afff1fc9: search, date filter, confirmed-only toggle, and trip calculator.
(function () {
  function applyFilters(tableId) {
    var table = document.getElementById(tableId);
    if (!table) return;
    var q = (document.querySelector('[data-search-target="' + tableId + '"]') || {}).value || "";
    q = q.trim().toLowerCase();
    var dateSel = document.querySelector('[data-date-target="' + tableId + '"]');
    var date = dateSel ? dateSel.value : "";
    var tog = document.querySelector('[data-toggle-confirmed="' + tableId + '"]');
    var onlyConfirmed = tog && tog.checked;
    var shown = 0;
    table.querySelectorAll("tbody tr").forEach(function (tr) {
      var ok = true;
      if (q && (tr.getAttribute("data-search") || "").indexOf(q) === -1 && tr.textContent.toLowerCase().indexOf(q) === -1) ok = false;
      if (date && tr.getAttribute("data-date") !== date) ok = false;
      if (onlyConfirmed && tr.getAttribute("data-confirmed") !== "1") ok = false;
      tr.classList.toggle("hide", !ok);
      if (ok) shown++;
    });
    var note = table.parentNode.querySelector(".empty-note");
    if (!note) {
      note = document.createElement("p");
      note.className = "muted empty-note";
      table.parentNode.parentNode.insertBefore(note, table.parentNode.nextSibling);
    }
    note.textContent = shown === 0 && onlyConfirmed
      ? "No row is confirmed single-entry, so nothing matches this toggle. See Analysis for the gates."
      : "Showing " + shown + " row(s).";
  }
  document.querySelectorAll("[data-search-target]").forEach(function (el) {
    el.addEventListener("input", function () { applyFilters(el.getAttribute("data-search-target")); });
  });
  document.querySelectorAll("[data-date-target]").forEach(function (el) {
    el.addEventListener("change", function () { applyFilters(el.getAttribute("data-date-target")); });
  });
  document.querySelectorAll("[data-toggle-confirmed]").forEach(function (el) {
    el.addEventListener("change", function () { applyFilters(el.getAttribute("data-toggle-confirmed")); });
  });

  // Calculator
  var evData = document.getElementById("events-data");
  if (!evData) return;
  var events = JSON.parse(evData.textContent);
  var byId = {};
  events.forEach(function (e) { byId[e.id] = e; });
  var lines = [];
  function money(n) { return "$" + (Math.round(n * 100) / 100).toLocaleString("en-US", { maximumFractionDigits: 2 }); }
  function num(id) { var v = parseFloat(document.getElementById(id).value); return isNaN(v) ? null : v; }
  function render() {
    var tbody = document.querySelector("#evList tbody");
    tbody.innerHTML = "";
    var entryTotal = 0;
    lines.forEach(function (ln, idx) {
      var e = byId[ln.id];
      var sub = e.buy_in * ln.qty;
      entryTotal += sub;
      var tr = document.createElement("tr");
      tr.innerHTML = "<td>" + e.label.replace(/</g, "&lt;") + "</td><td>" + ln.qty + "</td><td>" + money(e.buy_in) +
        "</td><td>" + money(sub) + '</td><td><button type="button" data-rm="' + idx + '">remove</button></td>';
      tbody.appendChild(tr);
    });
    tbody.querySelectorAll("[data-rm]").forEach(function (b) {
      b.addEventListener("click", function () { lines.splice(parseInt(b.getAttribute("data-rm"), 10), 1); render(); });
    });
    var nights = num("nights"), rate = num("rate"), fee = num("fee") || 0, tax = num("tax");
    var trueNight = null;
    if (rate !== null && tax !== null) trueNight = (rate + fee) * (1 + tax / 100);
    document.getElementById("entryTotal").textContent = money(entryTotal);
    document.getElementById("entryTotal2").textContent = money(entryTotal);
    document.getElementById("trueNight").textContent = trueNight === null ? "enter rate" : money(trueNight) + " per night";
    var hotel = null;
    if (nights !== null && trueNight !== null) hotel = nights * trueNight;
    document.getElementById("hotelTotal").textContent = hotel === null ? "enter nights and rate" : money(hotel);
    document.getElementById("hotelTotal2").textContent = money(hotel || 0);
    document.getElementById("grand").textContent = money(entryTotal + (hotel || 0));
  }
  document.getElementById("evAdd").addEventListener("click", function () {
    var id = document.getElementById("evSel").value;
    var qty = parseInt(document.getElementById("evQty").value, 10);
    if (!id || isNaN(qty) || qty < 1) return;
    lines.push({ id: id, qty: qty });
    render();
  });
  ["nights", "rate", "fee", "tax"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", render);
  });
  render();
})();
