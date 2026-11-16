// Simple client-side row filter for every table that has a filter box.
document.querySelectorAll("input.filter").forEach(function (box) {
  var table = document.getElementById(box.dataset.target);
  if (!table) return;
  box.addEventListener("input", function () {
    var q = box.value.toLowerCase();
    table.querySelectorAll("tbody tr").forEach(function (tr) {
      tr.style.display = tr.textContent.toLowerCase().indexOf(q) === -1 ? "none" : "";
    });
  });
});
