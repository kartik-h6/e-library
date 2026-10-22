/* navigation.js — mobile menu, active link, back buttons */
window.Nav = (function(){
  function init(){
    var toggle=document.querySelector('.nav-toggle'), nav=document.getElementById('site-nav');
    if(toggle&&nav){ toggle.addEventListener('click',function(){
      var open=nav.getAttribute('data-open')==='true';
      nav.setAttribute('data-open', open?'false':'true');
      toggle.setAttribute('aria-expanded', open?'false':'true');
    }); }
    document.querySelectorAll('[data-back]').forEach(function(b){
      b.addEventListener('click',function(e){ e.preventDefault(); if(history.length>1){history.back();} else {location.href=window.Catalogue.root()+'index.html';} });
    });
    var here=location.pathname.replace(/index\.html$/,'');
    document.querySelectorAll('.site-nav a').forEach(function(a){
      var href=a.getAttribute('href')||'';
      var norm=href.replace(/index\.html$/,'').replace(/^\.\.\//g,'');
      if(norm && here.endsWith(norm)){ a.setAttribute('aria-current','page'); }
    });
  }
  return { init: init };
})();