/* search.js — client-side search over published catalogue metadata */
window.Search = (function(){
  function esc(s){ return String(s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];}); }
  function subjectUrl(sem, sub){
    return window.Catalogue.root()+'semester-'+sem.number+'/'+sub.slug+'/';
  }
  function render(items, q){
    var box=document.getElementById('results'); var count=document.getElementById('result-count');
    count.textContent = items.length + (items.length===1?' result':' results');
    if(!items.length){
      box.innerHTML='<div class="empty"><p>No matches for <b>'+esc(q)+'</b>.</p><p class="meta">Try a subject name, a course code like <b>BP102T</b>, or a topic such as <b>pharmacology</b>.</p></div>';
      return;
    }
    box.innerHTML=items.map(function(it){
      var s=it.subject, sem=it.semester;
      return '<a class="card" href="'+subjectUrl(sem,s)+'">'+
        '<div class="code">'+esc(s.code)+' &middot; '+esc(sem.label)+'</div>'+
        '<div class="title">'+esc(s.title)+'</div>'+
        '<div class="sub">'+esc(it.typeLabel)+(s.units&&s.units.length?(' &middot; '+s.units.length+' units'):'')+'</div></a>';
    }).join('');
  }
  function init(){
    var input=document.getElementById('q'); if(!input) return;
    window.Catalogue.load().then(function(cat){
      var idx=[];
      cat.semesters.forEach(function(sem){
        sem.subjects.forEach(function(s){
          idx.push({semester:sem, subject:s, typeLabel:(s.type.charAt(0).toUpperCase()+s.type.slice(1)),
            hay:[s.code,s.title,sem.label,(s.options||[]).join(' '),(s.units||[]).join(' ')].join(' ').toLowerCase()});
        });
      });
      function run(){
        var q=(input.value||'').trim().toLowerCase();
        if(!q){ render([], ''); return; }
        render(idx.filter(function(it){return it.hay.indexOf(q)>=0;}), q);
      }
      input.addEventListener('input', run); run();
    }).catch(function(e){
      document.getElementById('results').innerHTML='<div class="empty">Could not load the catalogue. '+esc(e.message)+'</div>';
    });
  }
  return { init: init };
})();