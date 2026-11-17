/* Poker5 root-site interactivity: global search, single-entry toggle,
   date filter and the trip-cost calculator. No external dependencies. */
(function () {
  "use strict";

  function visible(tr, query, onlyConfirmed, dateValue) {
    var cells = tr.querySelectorAll("td");
    var text = "";
    for (var i = 0; i < cells.length; i++) text += (cells[i].textContent || "") + " ";
    text = text.toLowerCase();
    if (query && text.indexOf(query) === -1) return false;
    if (dateValue && tr.getAttribute("data-date") !== dateValue) return false;
    if (onlyConfirmed) {
      // the format column also uses .badge, so scan every badge in the row
      var badges = tr.querySelectorAll(".badge"), hit = false;
      for (var j = 0; j < badges.length; j++) {
        if (badges[j].textContent.indexOf("Confirmed single-entry") !== -1) hit = true;
      }
      if (!hit) return false;
    }
    return true;
  }

  window.poker5Filter = function () {
    var q = (document.getElementById("q") || {}).value || "";
    var only = document.getElementById("se-toggle") && document.getElementById("se-toggle").checked;
    var dv = (document.getElementById("date-filter") || {}).value || "";
    q = q.trim().toLowerCase();
    var tables = document.querySelectorAll("table[data-searchable]");
    var anyVisible = false;
    tables.forEach(function (tbl) {
      var rows = tbl.querySelectorAll("tbody tr");
      rows.forEach(function (tr) {
        var show = visible(tr, q, only, dv);
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
    var count = Math.max(1, parseInt(document.getElementById("count").value, 10) || 1);
    if (!sel.value) return;
    var opt = sel.options[sel.selectedIndex];
    var buyin = parseFloat(opt.getAttribute("data-buyin").replace(/[^0-9.]/g, "")) || 0;
    var qualifies = opt.getAttribute("data-qualifies") === "1";
    var name = opt.value;
    entries.push({ name: name, buyin: buyin, count: count, qualifies: qualifies });
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
      var qual = e.qualifies ?
        ' <em class="muted">(\u2265 $300: satisfies the Venetian poker-suite play requirement for one night)</em>' :
        ' <em class="muted">(&lt; $300: does not satisfy the poker-suite play requirement alone)</em>';
      row.innerHTML = "<span>" + e.count + " &times; " + e.name + " (" +
        e.buyin.toLocaleString("en-US", { style: "currency", currency: "USD" }) + ")" + qual + "</span>" +
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
    var nightsInput = document.getElementById("nights").value;
    var rateInput = document.getElementById("rate").value;
    var feeInput = document.getElementById("fee").value;
    var taxInput = document.getElementById("tax").value;
    var nights = nightsInput === "" ? NaN : Number(nightsInput);
    var rate = rateInput === "" ? NaN : Number(rateInput);
    var fee = feeInput === "" ? NaN : Number(feeInput);
    var tax = taxInput === "" ? NaN : Number(taxInput) / 100;
    var hotelComplete = Number.isFinite(nights) && nights > 0 &&
      Number.isFinite(rate) && rate > 0 && Number.isFinite(fee) && fee >= 0 &&
      Number.isFinite(tax) && tax >= 0;
    var hotelTotal = hotelComplete ? (rate + fee) * (1 + tax) * nights : null;
    sumE.textContent = "$" + entriesTotal.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
    sumH.textContent = hotelComplete ? "$" + hotelTotal.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 }) : "Incomplete";
    sumT.textContent = hotelComplete ? "$" + (entriesTotal + hotelTotal).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 }) : "Incomplete";
    var qualBox = document.getElementById("sum-qual");
    if (qualBox) {
      var nightsCovered = 0;
      entries.forEach(function (e) { if (e.qualifies) nightsCovered += e.count; });
      qualBox.textContent = Number.isFinite(nights) ? nightsCovered + " of " + nights + " night(s)" : "Enter nights";
    }
  };

  // Wire hotel select to load logged rate/fee.
  document.addEventListener("DOMContentLoaded", function () {
    var hotel = document.getElementById("hotel");
    if (hotel) {
      hotel.addEventListener("change", function () {
        var opt = hotel.options[hotel.selectedIndex];
        var rateInput = document.getElementById("rate");
        var feeInput = document.getElementById("fee");
        var evidence = document.getElementById("hotel-evidence");
        // A hotel change invalidates the previous hotel's manually entered quote.
        rateInput.value = "";
        feeInput.value = "";
        if (evidence) {
          evidence.textContent = opt.value ? "No dated room quote recorded for " + opt.value + "." :
            "No hotel source selected. A dated room quote is required for a hotel total.";
          var fee = opt.getAttribute("data-fee");
          var source = opt.getAttribute("data-fee-source");
          var date = opt.getAttribute("data-fee-date");
          if (opt.value && fee !== "") {
            feeInput.value = Number(fee).toFixed(2);
            evidence.textContent += " Official resort fee: $" + Number(fee).toFixed(2) +
              " per night" + (date ? " (retrieved " + date + ")" : "") + ". Source: ";
            if (source && /^https:\/\//.test(source)) {
              var a = document.createElement("a");
              a.href = source;
              a.target = "_blank";
              a.rel = "noopener";
              a.textContent = "official fee page";
              evidence.appendChild(a);
            } else {
              evidence.appendChild(document.createTextNode("not recorded"));
            }
          } else if (opt.value) {
            evidence.textContent += " No official fee amount is verified; hotel total remains incomplete.";
          }
        }
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
