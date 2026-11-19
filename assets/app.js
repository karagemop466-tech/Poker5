
/* Poker5 - session ea99006a. Client-side filtering and calculators. */
function qsa(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function norm(s){return (s||'').toLowerCase();}

function initTable(id){
  var t=document.getElementById(id); if(!t) return;
  var rows=qsa('tbody tr',t);
  var q=document.getElementById('q'), from=document.getElementById('dfrom'),
      to=document.getElementById('dto'), ven=document.getElementById('fvenue'),
      se=document.getElementById('fse'), en=document.getElementById('fentry'),
      cnt=document.getElementById('count'), empty=document.getElementById('empty');
  function apply(){
    var needle=norm(q?q.value:''), f=from?from.value:'', t2=to?to.value:'',
        v=ven?ven.value:'', s=se?se.checked:false, e=en?en.checked:false, shown=0;
    rows.forEach(function(tr){
      var d=tr.getAttribute('data-date')||'';
      var ok=true;
      if(needle && norm(tr.getAttribute('data-search')).indexOf(needle)<0) ok=false;
      if(ok && f && d && d<f) ok=false;
      if(ok && t2 && d && d>t2) ok=false;
      if(ok && v && tr.getAttribute('data-venue')!==v) ok=false;
      if(ok && s && tr.getAttribute('data-rule')!=='unknown' && tr.getAttribute('data-rule')!=='confirmed_single') ok=false;
      if(ok && e && tr.getAttribute('data-kind')!=='entry') ok=false;
      tr.style.display=ok?'':'none'; if(ok) shown++;
    });
    if(cnt) cnt.textContent=shown+' of '+rows.length+' rows';
    if(empty) empty.hidden=!(shown===0);
  }
  if(q) q.addEventListener('input',apply);
  [from,to].forEach(function(el){if(el) el.addEventListener('change',apply);});
  if(ven) ven.addEventListener('change',apply);
  [se,en].forEach(function(el){if(el) el.addEventListener('change',apply);});
  var rst=document.getElementById('reset');
  if(rst) rst.addEventListener('click',function(){
    if(q)q.value=''; if(from)from.value=''; if(to)to.value=''; if(ven)ven.value='';
    if(se)se.checked=false; if(en)en.checked=false; apply();});
  qsa('thead th',t).forEach(function(th,i){
    th.addEventListener('click',function(){
      var tb=t.tBodies[0], arr=qsa('tr',tb);
      var asc=th.getAttribute('data-asc')!=='1';
      qsa('thead th',t).forEach(function(o){o.removeAttribute('data-asc');});
      th.setAttribute('data-asc',asc?'1':'0');
      arr.sort(function(a,b){
        var A=a.children[i]||a.children[a.children.length-1],
            B=b.children[i]||b.children[b.children.length-1];
        var ka=A.getAttribute('data-order'); var kb=B.getAttribute('data-order');
        var va=ka!==null?ka:A.textContent.trim(), vb=kb!==null?kb:B.textContent.trim();
        var na=parseFloat(String(va).replace(/[^0-9.\-]/g,'')), nb=parseFloat(String(vb).replace(/[^0-9.\-]/g,''));
        var cmp=(!isNaN(na)&&!isNaN(nb))?na-nb:String(va).localeCompare(String(vb));
        return asc?cmp:-cmp;});
      arr.forEach(function(r){tb.appendChild(r);});});});
  apply();
}

/* ---- hotel true nightly cost + dated rate log ---- */
var RATE_KEY='poker5.ratelog.v1';
function num(el){var v=parseFloat((el&&el.value||'').replace(/[^0-9.\-]/g,''));return isNaN(v)?0:v;}
function rateLog(){try{return JSON.parse(localStorage.getItem(RATE_KEY)||'[]');}catch(e){return [];}}
function saveRateLog(l){try{localStorage.setItem(RATE_KEY,JSON.stringify(l));}catch(e){}}
function renderRateLog(){
  var box=document.getElementById('ratelog'); if(!box) return;
  var l=rateLog();
  if(!l.length){box.innerHTML='<p class="muted sm">No dated quotes recorded yet. Add one above and it is stored in this browser only.</p>';return;}
  var h='<table class="data"><thead><tr><th>Recorded</th><th>Hotel</th><th>Dates</th><th class="num">Rate/night</th><th class="num">Resort fee</th><th class="num">Tax %</th><th class="num">True /night</th><th class="num">Stay total</th><th>Source</th><th></th></tr></thead><tbody>';
  l.slice().reverse().forEach(function(r,i){
    h+='<tr><td class="nowrap">'+r.ts+'</td><td>'+r.hotel+'</td><td class="nowrap">'+r.dates+'</td>'+
       '<td class="num">$'+r.rate.toFixed(2)+'</td><td class="num">$'+r.fee.toFixed(2)+'</td>'+
       '<td class="num">'+r.tax.toFixed(2)+'%</td><td class="num">$'+r.truenight.toFixed(2)+'</td>'+
       '<td class="num">$'+r.total.toFixed(2)+'</td>'+
       '<td>'+(r.src?'<a class="src" href="'+r.src+'" target="_blank" rel="noopener">booking link</a>':'<span class="blank">-</span>')+'</td>'+
       '<td><button class="btn tiny ghost" data-del="'+i+'">remove</button></td></tr>';
  });
  h+='</tbody></table>'; box.innerHTML=h;
  qsa('[data-del]',box).forEach(function(b){b.addEventListener('click',function(){
    var l=rateLog(); var idx=l.length-1-parseInt(b.getAttribute('data-del'),10);
    l.splice(idx,1); saveRateLog(l); renderRateLog();});});
}
function initHotels(){
  var f=document.getElementById('hcalc'); if(!f) return;
  function calc(){
    var rate=num(document.getElementById('hrate')), fee=num(document.getElementById('hfee')),
        tax=num(document.getElementById('htax')), nights=num(document.getElementById('hnights'))||1;
    var taxable=rate+fee, t=taxable*(1+tax/100);
    var el=document.getElementById('hres');
    if(el) el.innerHTML='<div><span class="muted">Nightly: rate $'+rate.toFixed(2)+' + resort fee $'+fee.toFixed(2)+
      ' = $'+taxable.toFixed(2)+'; tax at '+tax.toFixed(2)+'% = $'+(taxable*tax/100).toFixed(2)+'</span></div>'+
      '<div class="big">True cost per night: $'+t.toFixed(2)+'</div>'+
      '<div class="muted">'+nights+' night(s): $'+(t*nights).toFixed(2)+'</div>';
    return {rate:rate,fee:fee,tax:tax,nights:nights,truenight:t,total:t*nights};
  }
  ['hrate','hfee','htax','hnights'].forEach(function(id){var e=document.getElementById(id); if(e) e.addEventListener('input',calc);});
  calc();
  var save=document.getElementById('hsave');
  if(save) save.addEventListener('click',function(){
    var r=calc(); if(!r.rate) {alert('Enter the nightly rate you saw on the official booking link.');return;}
    var l=rateLog();
    l.push({ts:new Date().toISOString().slice(0,16).replace('T',' ')+'Z',
      hotel:document.getElementById('hhotel').value,
      dates:(document.getElementById('hin').value||'?')+' to '+(document.getElementById('hout').value||'?'),
      rate:r.rate,fee:r.fee,tax:r.tax,nights:r.nights,truenight:r.truenight,total:r.total,
      src:document.getElementById('hsrc').value||''});
    saveRateLog(l); renderRateLog();});
  renderRateLog();
  var walk=document.getElementById('walkfilter');
  if(walk) walk.addEventListener('change',function(){
    qsa('#routetable tbody tr').forEach(function(tr){
      var m=tr.getAttribute('data-min');
      tr.style.display=(walk.checked && (m===''||m===null))?'':'';
      if(walk.checked && m!==''){ if(parseFloat(m)>30) tr.style.display='none'; }
    });});
  var rec=document.getElementById('walkrecord');
  if(rec) rec.addEventListener('click',function(){
    var mins=parseFloat(document.getElementById('walkmins').value);
    if(isNaN(mins)){alert('Enter the number of minutes you measured.');return;}
    var key='poker5.walk.'+document.getElementById('walkpair').value;
    try{localStorage.setItem(key,JSON.stringify({minutes:mins,at:new Date().toISOString()}));}catch(e){}
    var tr=document.querySelector('#routetable tr[data-pair="'+document.getElementById('walkpair').value+'"]');
    if(tr){tr.setAttribute('data-min',mins); tr.children[3].innerHTML='<b>'+mins+' min</b><br><span class="muted sm">you measured this</span>';}
  });
}

/* ---- trip planner ---- */
function initPlanner(){
  var box=document.getElementById('picks'); if(!box) return;
  var out=document.getElementById('ptotal');
  function total(){
    var buy=0,entries=0,hasInvalidBuyin=false;
    qsa('input[type=checkbox][data-buyin]',box).forEach(function(c){
      if(!c.checked) return;
      var b=Number(c.getAttribute('data-buyin'));
      if(!Number.isFinite(b)||b<=0){hasInvalidBuyin=true;return;}
      buy+=b; entries++;
    });
    var rateField=document.getElementById('ptrue');
    var nightsField=document.getElementById('pnights');
    var hotel=rateField&&rateField.value.trim()!==''?Number(rateField.value):NaN;
    var nights=nightsField&&nightsField.value.trim()!==''?Number(nightsField.value):NaN;
    var hotelComplete=Number.isFinite(hotel)&&hotel>0&&Number.isFinite(nights)&&nights>0;
    var tripComplete=hotelComplete&&entries>0&&!hasInvalidBuyin;
    var hotelTotal=hotelComplete?hotel*nights:null;
    var grandTotal=tripComplete?buy+hotelTotal:null;
    if(out) out.innerHTML='<div>Selected entries: <b>'+entries+'</b> &nbsp; Buy-ins total: <b>$'+buy.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2})+'</b></div>'+
      '<div>Hotel: '+(Number.isFinite(nights)?nights:'—')+' night(s) &times; '+(hotelComplete?'$'+hotel.toFixed(2)+' true cost / night':'<span class="blank">true nightly cost not confirmed</span>')+
      ' = <b>'+(hotelComplete?'$'+hotelTotal.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2}):'Incomplete')+'</b></div>'+
      '<div class="big">Estimated trip cost: '+(grandTotal===null?'Incomplete':'$'+grandTotal.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2}))+'</div>'+
      '<div class="muted sm">Formula: selected entries &times; their listed buy-ins + nights &times; true hotel cost. One buy-in is counted per selected event. The candidate events below do not have confirmed single-entry caps.</div>'+
      (hotelComplete?'':'<p class="warnbox">Incomplete. No date-specific room quote is currently recorded; enter a verified true nightly total from the hotel rate log before treating the trip total as complete.</p>')+
      (entries===0?'<p class="muted sm">Select at least one event to include its buy-in in the estimate.</p>':'')+
      (hasInvalidBuyin?'<p class="warnbox">A selected event has no valid buy-in. The trip total cannot be completed.</p>':'');
  }
  box.addEventListener('change',total);
  ['ptrue','pnights'].forEach(function(id){var e=document.getElementById(id); if(e) e.addEventListener('input',total);});
  total();
}

/* ---- suggestions: choose a path ---- */
function initSuggestions(){
  var box=document.getElementById('sug'); if(!box) return;
  var out=document.getElementById('spicked');
  function render(){
    var c=qsa('input[type=radio]:checked',box);
    if(!out) return;
    if(!c.length){out.innerHTML='<p class="muted">Pick one option per suggestion to build your change list.</p>';return;}
    out.innerHTML='<h3>Your chosen path</h3><ol class="clean">'+c.map(function(r){
      return '<li><b>'+r.getAttribute('data-title')+'</b>: '+r.getAttribute('data-label')+'</li>';}).join('')+'</ol>'+
      '<p class="muted sm">Nothing on this site changes until you ask for it. Copy this list into a request.</p>';
  }
  box.addEventListener('change',render); render();
}

document.addEventListener('DOMContentLoaded',function(){
  initHotels(); initPlanner(); initSuggestions();
});
