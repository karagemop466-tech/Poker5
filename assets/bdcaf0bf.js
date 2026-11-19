
/* Poker5 bdcaf0bf: table filters, day plan, rate log, trip calculator. No server, no manual data entry. */
(function(){
var F=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));};

function state(){try{return JSON.parse(localStorage.getItem('p5.state')||'{}');}catch(e){return {};}}
function saveState(o){var s=state();Object.keys(o).forEach(function(k){s[k]=o[k];});try{localStorage.setItem('p5.state',JSON.stringify(s));}catch(e){}}

/* ---- generic table filtering + sorting + expandable rule fields ---- */
function wireTable(t){
  var bar=document.querySelector('.filters[data-for="'+t.id+'"]');
  // a table's own rows only: the expandable rule fields live in a sibling <tr class="rulesrow">
  var rows=F('tbody tr[data-search]', t).filter(function(tr){return !tr.classList.contains('rulesrow');});
  if(!rows.length) rows=F('tbody tr:not(.rulesrow)', t);
  var inp=function(n){return bar?bar.querySelector('[data-f="'+n+'"]'):null;};
  var q=inp('search'),from=inp('from'),to=inp('to'),ven=inp('venue'),single=inp('single'),
      chg=inp('changed'),reset=inp('reset'),cnt=bar?bar.querySelector('.count'):null;
  var extraF=F('.filters[data-for="'+t.id+'"] [data-col]');
  if(t.dataset.syncdates==='1'&&from&&!from.value&&state().from){from.value=state().from;}
  if(t.dataset.syncdates==='1'&&to&&!to.value&&state().to){to.value=state().to;}
  var sAttr=t.getAttribute('data-single')||'rule';
  var sVals=t.getAttribute('data-single-values')||'explicit_one_entry|no_reentry_language';
  function apply(){
    var n=(q?q.value:'').toLowerCase().trim(), f=from?from.value:'', t2=to?to.value:'',
        v=ven?ven.value:'', s=single&&single.checked, c=chg&&chg.checked, shown=0;
    rows.forEach(function(tr){
      var d=tr.getAttribute('data-date')||'', ok=true;
      if(n&&(tr.getAttribute('data-search')||'').indexOf(n)<0) ok=false;
      if(ok&&f&&d&&d<f) ok=false;
      if(ok&&t2&&d&&d>t2) ok=false;
      if(ok&&v&&tr.getAttribute('data-venue')!==v) ok=false;
      if(ok&&s&&!(new RegExp('^(?:'+sVals+')$')).test(tr.getAttribute('data-'+sAttr)||'')) ok=false;
      if(ok&&c&&tr.getAttribute('data-changed')!=='1') ok=false;
      if(ok){extraF.forEach(function(el){
        var col=el.getAttribute('data-col'), want=el.checked?el.getAttribute('data-yes'):'*';
        var have=tr.getAttribute('data-'+col)||'';
        if(want!=='*'&&have!==want) ok=false;
      });}
      tr.style.display=ok?'':'none';
      var nxt=tr.nextElementSibling;
      if(nxt&&nxt.classList.contains('rulesrow')){
        nxt.style.display=ok&&nxt.classList.contains('open')?'table-row':'none';
        if(!ok) nxt.classList.remove('open');
      }
      if(ok) shown++;
    });
    if(cnt) cnt.textContent=shown+' of '+rows.length+' rows';
  }
  [q].concat([]).forEach(function(el){if(el) el.addEventListener('input',apply);});
  [from,to,ven].forEach(function(el){if(el) el.addEventListener('change',function(){
    if(el===from&&t.dataset.syncdates==='1') saveState({from:from.value});
    if(el===to&&t.dataset.syncdates==='1') saveState({to:to.value});
    apply();});});
  [single,chg].concat(extraF).forEach(function(el){if(el) el.addEventListener('change',apply);});
  var trip=bar?bar.querySelector('[data-f="trip"]'):null;
  if(trip&&from&&to) trip.addEventListener('click',function(){
    from.value=t.getAttribute('data-trip-from')||''; to.value=t.getAttribute('data-trip-to')||''; apply();});
  if(reset) reset.addEventListener('click',function(){
    [q,from,to,ven].forEach(function(el){if(el) el.value='';});
    [single,chg].concat(extraF).forEach(function(el){if(el) el.checked=false;});
    apply();});
  F('thead th',t).forEach(function(th,i){
    th.addEventListener('click',function(){
      var tb=t.tBodies[0], arr=F('tbody tr:not(.rulesrow)',tb).filter(function(r){return r.style.display!=='none';});
      var asc=th.getAttribute('data-asc')!=='1';
      F('thead th',t).forEach(function(o){o.removeAttribute('data-asc');});
      th.setAttribute('data-asc',asc?'1':'0');
      arr.sort(function(a,b){
        var ra=cell(a,i), rb=cell(b,i);
        var ka=ra&&ra.getAttribute('data-order'), kb=rb&&rb.getAttribute('data-order');
        var va=ka!==null&&ka!==''?ka:(ra?ra.textContent.trim():''), vb=kb!==null&&kb!==''?kb:(rb?rb.textContent.trim():'');
        var na=parseFloat(String(va).replace(/[^0-9.\-]/g,'')), nb=parseFloat(String(vb).replace(/[^0-9.\-]/g,''));
        var cmp=(!isNaN(na)&&!isNaN(nb))?na-nb:String(va).localeCompare(String(vb));
        return asc?cmp:-cmp;});
      arr.forEach(function(r){var nx=r.nextElementSibling;tb.appendChild(r);
        if(nx&&nx.classList.contains('rulesrow')) tb.appendChild(nx);});});});
  F('details.rules',t).forEach(function(d){d.addEventListener('toggle',function(){
    var tr=d.closest('tr'); if(!tr) return;
    tr.classList.toggle('open', d.open);
    tr.style.display=d.open?'table-row':'none';});});
  apply();
  function cell(tr,i){var c=tr.children[Math.min(i,tr.children.length-1)];return c;}
}

/* ---- dated rate log (browser-local, compare like-for-like) ---- */
var RK='p5.rates.v1';
function rl(){try{return JSON.parse(localStorage.getItem(RK)||'[]');}catch(e){return [];}}
function wr(l){try{localStorage.setItem(RK,JSON.stringify(l));}catch(e){}}
function renderRates(){
  var box=document.getElementById('ratelog'); if(!box) return;
  var l=rl(), h;
  if(!l.length){box.innerHTML='<p class="muted sm">No booking quote recorded in this browser yet. The official '
    +'booking engines need a live date search, and this site stores nothing on a server: run the hotel\u2019s own '
    +'booking link, then log the checkout total here so nights and totals can be compared like-for-like.</p>';return;}
  h='<div class="tablewrap"><table class="grid"><thead><tr><th>Logged</th><th>Hotel</th><th>Dates</th>'
   +'<th class="num">Checkout total</th><th class="num">Nights</th><th class="num">Nightly avg</th>'
   +'<th class="num">Resort fee /night</th><th class="num">Tax %</th><th class="num">True /night</th>'
   +'<th class="num">Stay true total</th><th>Rate stamp</th><th></th></tr></thead><tbody>';
  l.slice().reverse().forEach(function(r,i){
    var nights=r.nights||1, avg=r.total/nights, fee=r.fee||0, tax=(r.tax||13.38)/100;
    var tr_=avg+fee, trueNight=tr_*(1+tax), trueStay=trueNight*nights;
    h+='<tr><td class="nowrap">'+r.ts+'</td><td>'+esc(r.hotel)+'</td><td class="nowrap">'+esc(r.checkin)+' \u2192 '
      +esc(r.checkout)+'</td><td class="num">$'+r.total.toFixed(2)+'</td><td class="num">'+nights+'</td>'
      +'<td class="num">$'+avg.toFixed(2)+'</td><td class="num">$'+fee.toFixed(2)+'</td><td class="num">'+(tax*100).toFixed(2)
      +'%</td><td class="num">$'+trueNight.toFixed(2)+'</td><td class="num"><b>$'+trueStay.toFixed(2)+'</b></td>'
      +'<td class="nowrap">'+esc(r.stamp||'')+'</td><td><button class="btn ghost" data-del="'+(l.length-1-i)+'">remove</button></td></tr>';});
  h+='</tbody></table></div>';box.innerHTML=h;
  F('[data-del]',box).forEach(function(b){b.addEventListener('click',function(){
    var l2=rl();l2.splice(parseInt(b.getAttribute('data-del'),10),1);wr(l2);renderRates();});});
}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function initRateForm(){
  var f=document.getElementById('rateform'); if(!f) return;
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var g=function(id){var el=document.getElementById(id);return el?el.value.trim():'';};
    var tot=parseFloat(g('r_total')), nights=parseInt(g('r_nights'),10);
    if(!(tot>0)||!(nights>0)){document.getElementById('r_err').textContent='A checkout total and a positive number of nights are both required - the log refuses an average built on nothing.';return;}
    var l=rl();l.push({ts:new Date().toISOString().slice(0,16).replace('T',' ')+'Z',hotel:g('r_hotel'),
      checkin:g('r_in'),checkout:g('r_out'),total:tot,nights:nights,fee:parseFloat(g('r_fee'))||0,
      tax:parseFloat(g('r_tax'))||13.38,parking:parseFloat(g('r_park'))||0,stamp:g('r_stamp'),
      link:g('r_link')});wr(l);f.reset();document.getElementById('r_err').textContent='';renderRates();});
}

/* ---- trip cost calculator: entries x buy-ins + nights x true hotel cost ---- */
function initTrip(){
  var box=document.getElementById('picks'), out=document.getElementById('ptotal'), cfgEl=document.getElementById('cfg');
  if(!box||!cfgEl) return;
  var cfg=JSON.parse(cfgEl.textContent);
  var sel={};
  function num2(v){return (v===''||v==null||isNaN(+v))?null:+v;}
  function calc(){
    var hotel=cfg.hotels[document.getElementById('t_hotel').value]||{};
    var entries=0, buyins=0, badBuyin=false, pool=0, fees=0;
    F('input[data-buyin]',box).forEach(function(c){
      if(!c.checked) return;
      var b=num2(c.getAttribute('data-buyin'));
      if(b===null||b<=0){badBuyin=true;return;}
      entries++; buyins+=b;
      pool+=num2(c.getAttribute('data-pool'))||0; fees+=(b-(num2(c.getAttribute('data-pool'))||0));
    });
    var nights=num2(document.getElementById('t_nights').value);
    var mode=document.getElementById('t_mode').value;
    var rateInput=document.getElementById('t_rate');
    var rate=num2(rateInput.value);
    var fee=num2(hotel.fee), tax=num2(hotel.tax);
    var parking=0;
    if(hotel.parking_free_if_playing){parking=0;}
    else if(num2(hotel.parking)!=null){var p=num2(hotel.parking);var pk=document.getElementById('t_park');parking=(pk&&pk.checked)?p*nights:0;}
    var hotelNight=null, hotelTotal=null, note='';
    if(mode==='quote'&&rate!=null&&nights&&fee!=null&&tax!=null){hotelNight=(rate+fee)*(1+tax/100);hotelTotal=hotelNight*nights;}
    else if(mode==='floor'&&hotel.floor!=null&&nights&&fee!=null&&tax!=null){rate=hotel.floor;hotelNight=(rate+fee)*(1+tax/100);hotelTotal=hotelNight*nights;
      note='estimate at the property\u2019s own published rate floor - not a dated quote';}
    else if(mode==='log'){var l=rl();if(l.length){var r=l[l.length-1];hotelNight=(r.total/r.nights+(r.fee||0))*(1+(r.tax||13.38)/100);hotelTotal=hotelNight*r.nights;nights=r.nights;
      rate=r.total/r.nights;fee=r.fee||0;note='from the last dated log entry in this browser ('+r.ts+')';}}
    var complete=entries>0&&!badBuyin&&hotelTotal!=null&&nights>0;
    var lines='';
    lines+='<div>Entries: <b>'+entries+'</b> \u00d7 listed buy-ins = <b>$'+buyins.toLocaleString()+'</b> '+
      '<span class="sm">(of which $'+fees.toLocaleString(undefined,{maximumFractionDigits:0})+' is the house fee and $'+pool.toLocaleString(undefined,{maximumFractionDigits:0})+' goes to the prize pool)</span></div>';
    lines+='<div>Hotel: '+(nights||'\u2014')+' night(s) \u00d7 true cost / night '+
      (hotelNight==null?'<span class="blank">not completed</span>':'<b>$'+hotelNight.toFixed(2)+'</b> '+
       '<span class="sm">(rate $'+rate.toFixed(2)+' + mandatory fee $'+fee.toFixed(2)+') \u00d7 (1+'+tax+'/100)</span>')+
      ' = '+(hotelTotal==null?'<span class="blank">Incomplete</span>':'<b>$'+hotelTotal.toLocaleString(undefined,{maximumFractionDigits:0})+'</b>')+'</div>';
    lines+='<div>Parking: '+(parking?'<b>$'+parking.toLocaleString(undefined,{maximumFractionDigits:0})+'</b>':'$0 '
      +'<span class="sm">'+(hotel.parking_free_if_playing?'free self-parking applies to a player with 3 h+ of play (official rule)':'not added by default')+'</span>')+'</div>';
    lines+='<div class="big">Estimated trip cost: '+(complete?'$'+(buyins+hotelTotal+parking).toLocaleString(undefined,{maximumFractionDigits:0}):'Incomplete')+'</div>';
    if(note) lines+='<div class="sm">'+esc(note)+'</div>';
    if(badBuyin) lines+='<div class="badbox sm">A selected event has no published buy-in, so the total cannot be completed.</div>';
    else if(!complete) lines+='<div class="warnbox sm">Incomplete on purpose: the hotel leg needs a dated room quote '
      +'(or the rate-floor mode switched on), a positive night count and a mandatory fee that an official page states. '
      +'Nothing is filled in with a guess. Pick an event list above, or switch the mode selector.</div>';
    else lines+='<div class="goodbox sm">Complete under the published formula. Reconfirm the schedule, the room quote and the cancellation deadline before any non-refundable payment.</div>';
    out.innerHTML=lines;
    var days=new Set(F('input[data-buyin]:checked',box).map(function(c){return c.getAttribute('data-date');}));
    var perday=document.getElementById('t_days'); if(perday) perday.textContent=days.size+' of the days in the window carry a selected event';
  }
  box.addEventListener('change',calc);
  F('#tripform input,#tripform select').forEach(function(el){el.addEventListener('input',calc);el.addEventListener('change',calc);});
  var btn=document.getElementById('t_auto');
  if(btn) btn.addEventListener('click',function(){
    F('input[data-primary="1"]',box).forEach(function(c){c.checked=true;});calc();});
  calc();
}

document.addEventListener('DOMContentLoaded',function(){
  F('table.grid').forEach(wireTable);
  renderRates();initRateForm();initTrip();
  var link=document.getElementById('sharewin');
  if(link) link.addEventListener('click',function(e){e.preventDefault();
    var s=state();document.getElementById('winout').textContent='from='+ (s.from||'') +' to='+(s.to||'');});
});
})();
