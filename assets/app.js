/* Poker5 - client-side filtering and calculators (root site, session ea99006a;
   extended by 6bc143b9: unified search across every table on a page, date
   selector, confirmed single-entry toggle, <=30-minute walk filter, hotel
   budget/quality filters). No dependencies, no network calls. */
function qsa(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function norm(s){return (s||'').toLowerCase();}

function searchText(tr){
  /* Searchable text of a row. Folded evidence blocks are skipped on purpose: they are full of
     negated excerpts ("no re-entry sentence appears"), so searching 're-entry' must not match a
     row merely because the sentence denying it is attached to it. */
  var cached=tr.getAttribute('data-search');
  if(cached!==null && cached!=='') return cached;
  var t='';
  for(var i=0;i<tr.children.length;i++){
    var td=tr.children[i], bits=[];
    for(var j=0;j<td.childNodes.length;j++){
      var n=td.childNodes[j];
      if(n.nodeType===1 && n.hasAttribute && n.hasAttribute('data-no-search')) continue;
      bits.push(n.textContent);
    }
    t+=' '+bits.join(' ');
  }
  return t.toLowerCase();
}

/* One ordering for every quality floor on the site, shared with the builder through P5_TIER_ORDER so a
   select's value and a row's rank cannot drift apart. It used to be {"Deluxe":1,"Luxury":2} looked up on
   a NAME by the itemized panel and on a NUMBER by the page-wide bar, so "Luxury only" hid the Luxury rows
   in the shortlist (their attribute read "2", not a key in that map) while leaving unranked rows visible,
   and "Luxury or Upscale" in the panel hid the Luxury hotels outright because it compared the tier for
   equality. A row whose tier is not verified is never hidden by a floor - the same rule the 30-minute walk
   filter uses for a row with no verified walking time. */
var P5_TIER_ORDER=["Budget","Mid-scale","Upscale","Upper upscale","Deluxe","Luxury"];
function tierRank(tr){
  var v=tr.getAttribute('data-tier-rank');
  if(v!==null&&v!==''&&!isNaN(parseInt(v,10))) return parseInt(v,10);
  var n=tr.getAttribute('data-tier');
  if(n===null||n==='') return null;
  for(var i=0;i<P5_TIER_ORDER.length;i++){ if(P5_TIER_ORDER[i].toLowerCase()===String(n).toLowerCase()) return i; }
  return null;
}

var poker5Bound=false;
function initFilters(){
  if(poker5Bound) return; poker5Bound=true;
  var q=document.getElementById('q'), from=document.getElementById('dfrom'),
      to=document.getElementById('dto'), ven=document.getElementById('fvenue'),
      se=document.getElementById('fse'), mu=document.getElementById('fsemulti'),
      en=document.getElementById('fentry'), walk=document.getElementById('walkfilter'),
      budget=document.getElementById('pbudget'), quality=document.getElementById('pquality'),
      day=document.getElementById('fday'), rule=document.getElementById('frule'),
      rank=document.getElementById('frank'), chg=document.getElementById('fchanged'),
      cnt=document.getElementById('count'), empty=document.getElementById('empty');
  var tables=qsa('table.data');
  function apply(){
    var needle=norm(q?q.value:''), f=from?from.value:'', t2=to?to.value:'',
        v=ven?ven.value:'', s=se?se.checked:false,
        m2=mu?mu.checked:false, e=en?en.checked:false,
        w=walk?walk.checked:false,
        b=budget&&budget.value!==''?parseFloat(budget.value):null,
        pmin=quality?parseInt(quality.value||'0',10):0,
        dy=day?day.value:'', rl=rule?rule.value:'',
        rk=rank&&rank.checked, cg=chg&&chg.checked,
        shown=0,total=0;
    tables.forEach(function(t){
      if(t.hasAttribute('data-owned')) return;   /* owned by its own bar, which reads these too */
      qsa('tbody tr',t).forEach(function(tr){
        total++;
        var d=tr.getAttribute('data-date')||'';
        var rule=tr.getAttribute('data-rule')||'';
        var kind=tr.getAttribute('data-kind')||'';
        var ok=true;
        if(needle){
          var txt=tr.getAttribute('data-search');
          txt=norm(txt!==null&&txt!==undefined?txt:searchText(tr));
          if(txt.indexOf(needle)<0) ok=false;
        }
        if(ok&&f&&d&&d<f) ok=false;
        if(ok&&t2&&d&&d>t2) ok=false;
        if(ok&&dy&&d&&d!==dy) ok=false;
        if(ok&&v&&tr.getAttribute('data-venue')!==v) ok=false;
        if(ok&&rl&&rule&&rule!==rl) ok=false;
        if(ok && s && tr.getAttribute('data-rule')!=='confirmed_single') ok=false;
        if(ok&&m2&&rule==='multi') ok=false;
        if(ok&&e&&kind&&kind!=='entry') ok=false;
        if(ok&&rk&&tr.getAttribute('data-rankable')!=='1') ok=false;
        if(ok&&cg&&tr.getAttribute('data-changed')!=='1') ok=false;
        if(ok&&w){
          /* Hide only pairs that are known to exceed 30 minutes. Rows with no
             verified minutes stay visible and stay marked unverified. */
          var m=tr.getAttribute('data-min');
          if(m!==null&&m!==''&&!isNaN(parseFloat(m))&&parseFloat(m)>30) ok=false;
        }
        if(ok&&pmin){ var tk=tierRank(tr); if(tk!==null&&tk<pmin) ok=false; }
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
  /* date and select controls fire 'change' when a value is picked and 'input' while one is typed: a
     reader who types a date instead of picking it used to see the table stay unfiltered until they
     clicked elsewhere, so both events are bound. */
  [from,to,day,rule].forEach(function(el){if(el){el.addEventListener('change',apply);el.addEventListener('input',apply);}});
  if(ven) ven.addEventListener('change',apply);
  [se,mu,en,walk,rank,chg].forEach(function(el){if(el) el.addEventListener('change',apply);});
  [budget,quality].forEach(function(el){if(el){el.addEventListener('input',apply);el.addEventListener('change',apply);}});
  var rst=document.getElementById('reset');
  if(rst) rst.addEventListener('click',function(){
    if(q)q.value=''; if(from)from.value=''; if(to)to.value=''; if(ven)ven.value='';
    if(day)day.value=''; if(rule)rule.value='';
    if(se)se.checked=false; if(mu)mu.checked=false; if(en)en.checked=false;
    if(rank)rank.checked=false; if(chg)chg.checked=false;
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

/* ---- day schedule: the bar above the cards filters CARDS, not a table ---- */
function initDays(){
  var nav=document.getElementById('daynav'); if(!nav) return;
  var cards=qsa('.daycard');
  var q=document.getElementById('q'), from=document.getElementById('dfrom'), to=document.getElementById('dto'),
      ven=document.getElementById('fvenue'), rule=document.getElementById('frule'),
      se=document.getElementById('fse'), rank=document.getElementById('frank'),
      chg=document.getElementById('fchanged'), win=document.getElementById('winonly');
  var picked='';
  function apply(){
    var needle=norm(q?q.value:''), f=from?from.value:'', t2=to?to.value:'',
        v=ven?ven.value:'', rl=rule?rule.value:'', s=se&&se.checked,
        rk=rank&&rank.checked, cg=chg&&chg.checked, only=win&&win.checked, shown=0;
    cards.forEach(function(c){
      var d=c.getAttribute('data-date')||'';
      var ok=true;
      if(only && c.getAttribute('data-outside')) ok=false;
      if(ok && picked && d!==picked) ok=false;
      if(ok && f && d<f) ok=false;
      if(ok && t2 && d>t2) ok=false;
      var rows=0;
      qsa('tbody tr',c).forEach(function(tr){
        var rok=true;
        if(needle && norm(tr.getAttribute('data-search')||'').indexOf(needle)<0) rok=false;
        if(rok && v && tr.getAttribute('data-venue')!==v) rok=false;
        if(rok && rl && tr.getAttribute('data-rule')!==rl) rok=false;
        if(rok && s && tr.getAttribute('data-rule')!=='confirmed_single') rok=false;
        if(rok && rk && tr.getAttribute('data-rankable')!=='1') rok=false;
        if(rok && cg && tr.getAttribute('data-changed')!=='1') rok=false;
        tr.style.display=rok?'':'none'; if(rok) rows++;
      });
      if(ok && (needle||v||rl||s||rk||cg) && rows===0) ok=false;
      c.style.display=ok?'':'none'; if(ok) shown++;
    });
    qsa('[data-day]',nav).forEach(function(bt){
      bt.className='btn tiny'+((bt.getAttribute('data-day')||'')===picked?' active':'');});
    var cnt=document.getElementById('count');
    if(cnt) cnt.textContent=shown+' of '+cards.length+' days';
  }
  nav.addEventListener('click',function(e){
    var bt=e.target.closest?e.target.closest('[data-day]'):null; if(!bt) return;
    picked=bt.getAttribute('data-day')||'';
    var dp=document.getElementById('fday'); if(dp) dp.value=picked;
    apply();});
  var dp=document.getElementById('fday');
  if(dp) dp.addEventListener('change',function(){picked=dp.value; apply();});
  [q,from,to,ven,rule,se,rank,chg,win].forEach(function(el){
    if(el) el.addEventListener(el.type==='search'||el.type==='text'?'input':'change',apply);});
  apply();
}

/* ---- hotels: the brief's budget ceiling and quality floor, applied to the itemized table ---- */
function initHotels2(){
  var ceil=document.getElementById('bceil'), fl=document.getElementById('bfloor'),
      tbl=document.getElementById('hitems'), sel=document.getElementById('hsearch'),
      out=document.getElementById('bcost');
  if(!tbl) return;
  /* This table has its own bar (ceiling, floor, hotel) and the page's shared bar above it (search,
     ceiling, floor). Both wrote style.display to the same rows, so whichever ran last undid the other:
     typing in the search box silently revealed the rows the ceiling had hidden, because the shared
     filter found no data-cost on them and set every row visible. Now one function owns these rows and
     reads BOTH bars - the stricter ceiling wins, the higher floor wins, and the shared search box
     filters this table like every other table on the page. */
  var gq=document.getElementById('q'), gb=document.getElementById('pbudget'),
      gf=document.getElementById('pquality');
  function num(el){ if(!el) return NaN;
    var v=parseFloat(String(el.value||'').replace(/[^0-9.\-]/g,'')); return isNaN(v)?NaN:v; }
  function floorLabel(){
    var el=(fl&&fl.value!=='')?fl:gf;
    if(!el||el.selectedIndex<0||!el.options[el.selectedIndex]) return '';
    return el.options[el.selectedIndex].text;
  }
  function apply(){
    var cs=[num(ceil),num(gb)].filter(function(x){return !isNaN(x);});
    var c=cs.length?Math.min.apply(null,cs):NaN, fs=[];
    if(fl&&fl.value!=='') fs.push(parseInt(fl.value,10));
    if(gf&&gf.value!=='') fs.push(parseInt(gf.value,10));
    var fmin=fs.length?Math.max.apply(null,fs):-1, w=sel?sel.value:'', n=0;
    var needle=gq?norm(gq.value):'';
    var all=qsa('tbody tr',tbl);
    all.forEach(function(tr){
      var ok=true, v=tr.getAttribute('data-ceil')||'';
      if(w && norm(tr.children[0].textContent).indexOf(norm(w))<0) ok=false;
      if(ok && needle && norm(tr.textContent).indexOf(needle)<0) ok=false;
      if(ok && fmin>=0){ var tk=tierRank(tr); if(tk!==null&&tk<fmin) ok=false; }
      /* a hotel with no official rate can never be proven inside a budget: when a ceiling is set it
         is hidden, never assumed to fit */
      if(ok && !isNaN(c)){ if(v===''){ ok=false; } else if(parseFloat(v)>c){ ok=false; } }
      tr.style.display=ok?'':'none'; if(ok) n++;
    });
    if(out) out.textContent=n+' of '+all.length+' hotels match'+(isNaN(c)?'':' a ceiling of $'+c.toFixed(2))+
      (fmin>=0?' against the quality floor "'+floorLabel()+'"':'')+'. Hotels with no official nightly '+
      'rate cannot be proven inside a ceiling, so they are hidden while one is set. The bar at the top '+
      'of the page sets the same two limits, and the stricter of the two always wins.';
  }
  [ceil,sel,gq,gb].forEach(function(el){if(el) el.addEventListener('input',apply);});
  [fl,gf].forEach(function(el){if(el) el.addEventListener('change',apply);});
  apply();
}

/* ---- trip planner ---- */
/* status chips on the requirements page: they drive the page's own search box, so no
   query-string link is needed and the site's link checker stays honest. */
function initQueryChips(){
  qsa('[data-q]').forEach(function(b){
    b.addEventListener('click',function(){
      var q=document.getElementById('q'); if(!q) return;
      q.value=b.getAttribute('data-q')||'';
      q.dispatchEvent(new Event('input',{bubbles:true}));
      q.focus();
    });
  });
}

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
    /* Parking and the mandatory stay fees come from the official pages, so they are added here
       instead of being left for a reader to remember. If the hotel figure in use already includes
       the stay (a dated checkout capture), parking is the only thing added on top. */
    var panel=document.getElementById('pcalc');
    var parkBox=document.getElementById('ppark');
    var perNight=function(k){return panel&&panel.getAttribute('data-'+k)?Number(panel.getAttribute('data-'+k)):0;};
    var quote=document.getElementById('pquote');
    var opt=quote&&quote.selectedIndex>=0?quote.options[quote.selectedIndex]:null;
    var includesStay=!!(opt&&opt.getAttribute('data-includes')==='1');
    var parkOn=!!(parkBox&&parkBox.checked);
    var perNightPark=parkOn?perNight('park'):0;
    var feeTaxed=perNight('fee')*(1+perNight('tax')/100);
    var knownNight=feeTaxed+perNightPark;
    var hotelComplete=Number.isFinite(hotel)&&hotel>0&&Number.isFinite(nights)&&nights>0;
    var nightsN=Number.isFinite(nights)&&nights>0?nights:NaN;
    var hotelTotal=hotelComplete?(hotel+perNightPark)*nightsN:null;
    var tripComplete=hotelComplete&&entries>0&&!hasInvalidBuyin;
    var grandTotal=tripComplete?buy+hotelTotal:null;
    var srcNote=opt&&opt.value!=='manual'?' <span class="muted sm">from '+(opt.getAttribute('data-label')||'')+'</span>':'';
    if(out) out.innerHTML='<div>Selected entries: <b>'+entries+'</b> &nbsp; Buy-ins total: <b>$'+buy.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2})+'</b></div>'+
      '<div>Hotel: '+(Number.isFinite(nights)?nights:'—')+' night(s) &times; '+(hotelComplete?'$'+hotel.toFixed(2)+' true cost / night'+srcNote:'<span class="blank">true nightly cost not confirmed</span>')+
      (hotelComplete&&parkOn?' + parking $'+perNightPark.toFixed(2)+'/night':'')+
      ' = <b>'+(hotelComplete?'$'+hotelTotal.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2}):'Incomplete')+'</b></div>'+
      (includesStay?'<div class="muted sm">The hotel figure in use already includes the room, the resort fee and the tax for the stay it was captured for'+(parkOn?', so only parking is added on top':'. Nothing is added on top')+'.</div>':'')+
      (!includesStay&&hotelComplete?'<div class="muted sm">This hotel figure is a room-rate component only: add the resort fee and tax (or use the dated capture) before treating it as the whole nightly cost.</div>':'')+
      '<div class="big">Estimated trip cost: '+(grandTotal===null?'Incomplete':'$'+grandTotal.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2})+(opt&&opt.getAttribute('data-datematched')==='0'?' <span class="pill pill-warn">not date-matched to your window</span>':''))+'</div>'+
      (grandTotal===null&&Number.isFinite(nightsN)?'<div>Mandatory stay cost that IS verified: $'+knownNight.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})+' / night &times; '+nightsN+' = <b>$'+(knownNight*nightsN).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})+'</b> <span class="muted sm">resort fee + '+perNight('tax')+'% tax'+(parkOn?' + parking':'')+'; the room rate is the only missing term</span></div>':'')+
      '<div class="muted sm">Formula: selected entries &times; their listed buy-ins + nights &times; true hotel cost. One buy-in is counted per selected event. The candidate events below do not have confirmed single-entry caps.</div>'+
      (opt&&opt.value==='capture'?'<p class="warnbox">Not date-matched: the auto capture is an itemized total for the dates printed in the dated log, not for your window. It is shown so the scale of the hotel side is visible; it is not a quote for your stay.</p>':'')+
      (hotelComplete?'':'<p class="warnbox">Incomplete. No date-specific room quote is currently recorded; the calculator shows the verified mandatory stay cost, and the trip total closes only when a dated nightly total is recorded in the hotel rate log.</p>')+
      (entries===0?'<p class="muted sm">Select at least one event to include its buy-in in the estimate.</p>':'')+
      (hasInvalidBuyin?'<p class="warnbox">A selected event has no valid buy-in. The trip total cannot be completed.</p>':'');
  }
  box.addEventListener('change',total);
  var pq=document.getElementById('pquote');
  if(pq) pq.addEventListener('change',function(){
    var o=pq.options[pq.selectedIndex], f=document.getElementById('ptrue');
    var v=o.getAttribute('data-pernight');
    if(f){ if(v&&v!=='null'){f.value=v;f.readOnly=true;} else {f.value='';f.readOnly=false;} }
    total();
  });
  var pb=document.getElementById('ppark'); if(pb) pb.addEventListener('change',total);
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
  /* landing-page search hands its term over as ?q=...; pre-fill the page's search box and filter */
  try{ var qp=new URLSearchParams(location.search).get('q'); var qb=document.getElementById('q');
    if(qp && qb){ qb.value=qp; qb.dispatchEvent(new Event('input')); } }catch(e){}
  initFilters(); initHotels(); initHotels2(); initDays(); initPlanner(); initSuggestions(); initQueryChips();
});
