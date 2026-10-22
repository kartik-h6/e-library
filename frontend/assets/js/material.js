/* material.js — live material for a subject page.
   Fetches published resources from the staff library so students see updates without a
   rebuild. No-ops when no API base is configured, leaving the static fallback in place. */
(function () {
  var box = document.querySelector('[data-material]');
  if (!box) return;
  var api = (box.getAttribute('data-api') || '').replace(/\/+$/, '');
  var code = box.getAttribute('data-code');
  if (!api || !code) return;
  var note = document.getElementById('live-note');

  function safeUrl(u) {
    return (typeof u === 'string' && /^(https?:\/\/|\/)/.test(u)) ? u : '';
  }
  function esc(s) {
    var d = document.createElement('div');
    d.textContent = (s == null ? '' : String(s));
    return d.innerHTML;
  }

  fetch(api + '/api/public/library', { headers: { 'Accept': 'application/json' } })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (!data || !data.subjects) return;
      var items = data.subjects[code] || [];
      var byKind = {};
      items.forEach(function (it) { (byKind[it.type] = byKind[it.type] || []).push(it); });
      box.querySelectorAll('[data-kind]').forEach(function (col) {
        var list = byKind[col.getAttribute('data-kind')] || [];
        var count = col.querySelector('[data-count]');
        if (count) count.textContent = list.length;
        var body = col.querySelector('.res-body');
        if (!body) return;
        if (list.length) {
          body.innerHTML = '<ul class="res-list">' + list.map(function (r) {
            var url = safeUrl(r.url);
            var link = url ? ' <a href="' + esc(url) + '" target="_blank" rel="noopener">Open</a>' : '';
            return '<li><span>' + esc(r.title) + '</span>' + link + '</li>';
          }).join('') + '</ul>';
        }
      });
      if (note) {
        note.textContent = items.length
          ? 'Live from the staff library — ' + items.length + ' item(s), updated as staff publish.'
          : 'No published material for this subject yet.';
      }
    })
    .catch(function () { /* not configured or offline: keep the static fallback */ });
})();