/* Poker5 - client-side filtering and calculators (root site, session ea99006a;
   extended by 6bc143b9: unified search across every table on a page, date
   selector, confirmed single-entry toggle, <=30-minute walk filter, hotel
   budget/quality filters). No dependencies, no network calls. */
function qsa(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function norm(s){return (s||'').toLowerCase();}

var poker5Bound=false;
function initFilters(){
  if(poker5Bound) return; poker5Bound=true;
  var q=document.getElementById('q'), from=document.getElementById('dfrom'),
      to=document.getElementById('dto'), ven=document.getElementById('fvenue'),
      se=document.getElementById('fse'), mu=document.getElementById('fsemulti'),
      en=document.getElementById('fentry'), walk=document.getElementById('walkfilter'),
      budget=document.getElementById('pbudget'), quality=document.getElementById('pquality'),
      cnt=document.getElementById('count'), empty=document.getElementById('empty');
  var tables=qsa('table.data');
  var TIER_RANK={"Deluxe":1,"Luxury":2};
  function apply(){
    var needle=norm(q?q.value:''), f=from?from.value:'', t2=to?to.value:'',
        v=ven?ven.value:'', s=se?se.checked:false,
        m2=mu?mu.checked:false, e=en?en.checked:false,
        w=walk?walk.checked:false,
        b=budget&&budget.value!==''?parseFloat(budget.value):null,
        pmin=quality?parseInt(quality.value||'0',10):0,
        shown=0,total=0;
    tables.forEach(function(t){
      qsa('tbody tr',t).forEach(function(tr){
        total++;
        var d=tr.getAttribute('data-date')||'';
        var rule=tr.getAttribute('data-rule')||'';
        var kind=tr.getAttribute('data-kind')||'';
        var ok=true;
        if(needle){
          var txt=tr.getAttribute('data-search');
          txt=norm(txt!==null&&txt!==undefined?txt:tr.textContent);
          if(txt.indexOf(needle)<0) ok=false;
        }
        if(ok&&f&&d&&d<f) ok=false;
        if(ok&&t2&&d&&d>t2) ok=false;
        if(ok&&v&&tr.getAttribute('data-venue')!==v) ok=false;
        if(ok && s && tr.getAttribute('data-rule')!=='confirmed_single') ok=false;
        if(ok&&m2&&rule==='multi') ok=false;
        if(ok&&e&&kind&&kind!=='entry') ok=false;
        if(ok&&w){
          /* Hide only pairs that are known to exceed 30 minutes. Rows with no
             verified minutes stay visible and stay marked unverified. */
          var m=tr.getAttribute('data-min');
          if(m!==null&&m!==''&&!isNaN(parseFloat(m))&&parseFloat(m)>30) ok=false;
        }
        if(ok&&pmin&&tr.getAttribute('data-tier')!==null){
          if((TIER_RANK[tr.getAttribute('data-tier')]||0)<pmin) ok=false;
        }
        if(ok&&b!==null&&tr.getAttribute('data-cost')!==null&&tr.getAttribute('data-cost')!==''){
          var c=parseFloat(tr.getAttribute('data-cost'));
          if(!isNaN(c)&&c>b) ok=false;
        }
        tr.style.display=ok?'':'none'; if(ok) shown++;
      });
    });
    if(cnt) cnt.textContent=shown+' of '+total+' rows';
    if(empty) empty.hidden=!(shown===0&&total>0);
  }
  if(q) q.addEventListener('input',apply);
  [from,to].forEach(function(el){if(el) el.addEventListener('change',apply);});
  if(ven) ven.addEventListener('change',apply);
  [se,mu,en,walk].forEach(function(el){if(el) el.addEventListener('change',apply);});
  [budget,quality].forEach(function(el){if(el){el.addEventListener('input',apply);el.addEventListener('change',apply);}});
  var rst=document.getElementById('reset');
  if(rst) rst.addEventListener('click',function(){
    if(q)q.value=''; if(from)from.value=''; if(to)to.value=''; if(ven)ven.value='';
    if(se)se.checked=false; if(mu)mu.checked=false; if(en)en.checked=false;
    if(walk)walk.checked=false; if(budget)budget.value=''; if(quality)quality.value='';
    apply();});
  /* click-to-sort per table */
  tables.forEach(function(t){
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
  });
  apply();
}
/* backwards-compatible name used by inline page scripts */
function initTable(){initFilters();}

/* ---- hotel true nightly cost + dated rate log ---- */
var RATE_KEY='poker5.ratelog.v1';
function num(el){var v=parseFloat((el&&el.value||'').replace(/[^0-9.\-]/g,''));return isNaN(v)?0:v;}
function rateLog(){try{return JSON.parse(localStorage.getItem(RATE_KEY)||'[]');}catch(e){return [];}}
function saveRateLog(l){try{localStorage.setItem(RATE_KEY,JSON.stringify(l));}catch(e){}}
function renderRateLog(){
  var box=document.getElementById('ratelog'); if(!box) return;
  var l=rateLog();
  if(!l.length){box.innerHTML='<p class="muted sm">No dated quotes recorded in this browser yet. Add one above and it is stored here only. The researched, source-linked captures are in the table above.</p>';return;}
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
      if(walk.checked && m!=='' && m!==null && parseFloat(m)>30) tr.style.display='none';
      else tr.style.display='';
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
  initFilters(); initHotels(); initPlanner(); initSuggestions();
});
