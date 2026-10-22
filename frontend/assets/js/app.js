/* app.js — page bootstrap */
document.addEventListener('DOMContentLoaded', function(){
  var y=document.getElementById('year'); if(y){ y.textContent=new Date().getFullYear(); }
  if(window.Nav) window.Nav.init();
  if(document.getElementById('q') && window.Search) window.Search.init();
});