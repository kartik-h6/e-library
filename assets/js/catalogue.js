/* catalogue.js — loads and caches the public catalogue */
window.Catalogue = (function(){
  var cache=null, inflight=null;
  function root(){ return document.body.getAttribute('data-root') || ''; }
  function load(){
    if(cache) return Promise.resolve(cache);
    if(inflight) return inflight;
    inflight = fetch(root()+'data/catalogue.json',{cache:'no-cache'})
      .then(function(r){ if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
      .then(function(j){ cache=j; return j; });
    return inflight;
  }
  return { load: load, root: root };
})();