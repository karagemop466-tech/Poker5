// dashboard-6d1e0039 - filters, search and trip calculator
(function(){
  function each(t,fn){Array.prototype.forEach.call(document.querySelectorAll(t),fn)}

  // ---- generic filters: search + date + single + venue + walking
  var q = document.getElementById('q');
  var df = document.getElementById('dateFilter');
  var so = document.getElementById('singleOnly');
  var vf = document.getElementById('venueFilter');

  each('table.grid tbody tr', function(tr){ if(tr.dataset.date && df){
    if(!df.querySelector('option[value="'+tr.dataset.date+'"]')){
      var o=document.createElement('option');o.value=tr.dataset.date;
      o.textContent=tr.dataset.date;df.appendChild(o);
    }}});
  each('table.grid tbody tr', function(tr){ if(tr.dataset.venue && vf){
    if(!vf.querySelector('option[value="'+tr.dataset.venue+'"]')){
      var o=document.createElement('option');o.value=tr.dataset.venue;
      o.textContent=tr.dataset.venue;vf.appendChild(o);
    }}});
  function sortOpts(sel){ if(!sel) return;
    var opts=Array.prototype.slice.call(sel.options).slice(1)
      .sort(function(a,b){return a.value<b.value?-1:1});
    var cur=sel.value; while(sel.options.length>1) sel.remove(1);
    opts.forEach(function(o){sel.appendChild(o)}); sel.value=cur || ''; }
  sortOpts(df); sortOpts(vf);

  function apply(){
    var term=(q&&q.value||'').trim().toLowerCase();
    var day=df&&df.value, one=so&&so.checked, ven=vf&&vf.value;
    var shown=0, total=0;
    each('table.grid tbody tr', function(tr){
      if(!tr.dataset.text && !tr.dataset.date && !tr.dataset.venue) return;
      total++;
      var ok=true;
      if(term && (tr.dataset.text||'').indexOf(term)===-1) ok=false;
      if(ok && day && tr.dataset.date!==day) ok=false;
      if(ok && one && tr.dataset.single!=='yes') ok=false;
      if(ok && ven && tr.dataset.venue!==ven) ok=false;
      tr.style.display = ok?'':'none';
      if(ok) shown++;
    });
    each('#rowcount', function(el){ el.textContent = shown+' of '+total+' rows'; });
    var note=document.getElementById('calcNote'); // untouched
  }
  [q,df,so,vf].forEach(function(el){ if(el){ el.addEventListener('input',apply); el.addEventListener('change',apply);} });
  var walk=document.getElementById('walkOnly');
  function applyWalk(){
    if(!walk) return;
    var rows=document.querySelectorAll('table[data-table="routes"] tbody tr'), shown=0;
    Array.prototype.forEach.call(rows,function(tr){
      var ok = !walk.checked || tr.dataset.within==='1';
      tr.style.display = ok?'':'none'; if(ok) shown++;
    });
    each('#rowcount',function(el){el.textContent=shown+' of '+rows.length+' rows';});
  }
  if(walk){ walk.addEventListener('change',applyWalk); applyWalk(); }
  if(document.querySelector('table.grid tbody tr[data-text]')) apply();

  // ---- trip cost calculator
  var list=document.getElementById('entryList');
  if(!list) return;
  var entries=[];
  var pick=document.getElementById('evPick');
  var hotel=document.getElementById('hotelPick');
  var nights=document.getElementById('nights');
  var note=document.getElementById('calcNote');

  function money(v){ return v===null||v===undefined||isNaN(v) ? null :
      '$'+Number(v).toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:0}); }
  function money2(v){ return v===null||isNaN(v)? null :
      '$'+Number(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}); }

  function render(){
    var tb=list.querySelector('tbody'); tb.innerHTML='';
    entries.forEach(function(en,i){
      var tr=document.createElement('tr');
      tr.innerHTML='<td>'+en.label+'</td><td class="num">'+money(en.buy)+
        '</td><td class="num">'+(en.gtd?money(en.gtd):'<span class="blank">blank</span>')+
        '</td><td><button class="btn ghost" data-i="'+i+'">remove</button></td>';
      tb.appendChild(tr);
    });
    tb.querySelectorAll('button[data-i]').forEach(function(b){
      b.addEventListener('click',function(){ entries.splice(+b.dataset.i,1); render(); });
    });
    var buyins=entries.reduce(function(s,e){return s+e.buy;},0);
    var o=hotel.options[hotel.selectedIndex];
    var total=o&&o.dataset.total?Number(o.dataset.total):null;
    var nn=nights.value?Number(nights.value):0;
    var perNight = total? total/Number(o.dataset.nights||7) : null;
    document.getElementById('tEntries').textContent=entries.length;
    document.getElementById('tBuyins').textContent=money(buyins)||'$0';
    document.getElementById('tNight').textContent= perNight? money2(perNight) : '—';
    var hotelTotal = perNight && nn ? perNight*nn : null;
    document.getElementById('tHotel').textContent= hotelTotal? money2(hotelTotal) : '—';
    document.getElementById('tTotal').textContent= hotelTotal? money2(buyins+hotelTotal) : '—';
    if(!total){
      note.textContent='This hotel has no published checkout total on this site, so the hotel part '+
        'and the trip total stay blank rather than being estimated. See Hotels → “What is '+
        'verifiable and what is not”.';
    } else if(nn!==Number(o.dataset.nights)){ note.textContent='Note: the quoted total covers '+o.dataset.nights+
        ' nights. You asked for '+nn+', so the per-night figure is applied to your number of nights — '+
        'the hotel may price a different length of stay differently.';
    } else { note.textContent='Hotel cost = the dated 7-night quote ÷ 7, so it includes room, resort fee and tax.'; }
  }
  document.getElementById('addEv').addEventListener('click',function(){
    var o=pick.options[pick.selectedIndex]; if(!o) return;
    var g=o.getAttribute('data-gtd');
    entries.push({label:o.getAttribute('data-label')||o.textContent, buy:Number(o.value),
      gtd:g?Number(g):null});
    render();
  });
  document.getElementById('clearEv').addEventListener('click',function(){entries=[];render();});
  hotel.addEventListener('change',render); nights.addEventListener('input',render);
  render();
})();
