/* material.js — live material for a subject page.
   Fetches published resources from the staff library and files each one under its unit, so
   students see updates without a rebuild. No-ops when no API base is configured. */
(function () {
  var box = document.querySelector('[data-material]');
  if (!box) return;
  var api = (box.getAttribute('data-api') || '').replace(/\/+$/, '');
  var code = box.getAttribute('data-code');
  if (!api || !code) return;
  var note = document.getElementById('live-note');
  var LABEL = { notes: 'Notes', paper: 'Question paper', manual: 'Lab manual',
                book: 'Reference book', other: 'Material' };

  function safeUrl(u) {
    return (typeof u === 'string' && /^(https?:\/\/|\/)/.test(u)) ? u : '';
  }
  function esc(s) {
    var d = document.createElement('div');
    d.textContent = (s == null ? '' : String(s));
    return d.innerHTML;
  }
  function item(r) {
    var url = safeUrl(r.url);
    var btn = url
      ? '<a class="open-btn" href="' + esc(url) + '" target="_blank" rel="noopener">Open</a>'
      : '<span class="none">link missing</span>';
    return '<li class="res-item"><span class="res-kind">' + (LABEL[r.type] || 'Material') +
           '</span><span class="res-title">' + esc(r.title) + '</span>' + btn + '</li>';
  }

  fetch(api + '/api/public/library', { headers: { 'Accept': 'application/json' } })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (!data || !data.subjects) return;
      var items = data.subjects[code] || [];
      var byUnit = {}, general = [];
      items.forEach(function (it) {
        if (it.unitSeq) { (byUnit[it.unitSeq] = byUnit[it.unitSeq] || []).push(it); }
        else { general.push(it); }
      });
      box.querySelectorAll('[data-unit]').forEach(function (li) {
        var list = byUnit[li.getAttribute('data-unit')] || [];
        var body = li.querySelector('[data-unit-body]');
        if (body && list.length) {
          body.innerHTML = '<ul class="res-inline">' + list.map(item).join('') + '</ul>';
        }
      });
      var sb = box.querySelector('[data-subject-body]');
      if (sb && general.length) {
        sb.innerHTML = '<ul class="subject-material">' + general.map(item).join('') + '</ul>';
      }
      if (note) {
        var n = items.length;
        note.textContent = n
          ? 'Live — ' + n + ' item' + (n === 1 ? '' : 's') + ' from the staff library, updated as departments publish.'
          : 'No material has been published for this subject yet.';
      }
    })
    .catch(function () { /* not configured or offline: keep the static fallback */ });
})();