import { readFileSync } from 'node:fs';
const { JSDOM } = await import('jsdom');
const JS = readFileSync('./assets/app.js','utf8');
function load(rel){const dom=new JSDOM(readFileSync('./'+rel,'utf8'),{runScripts:'outside-only',pretendToBeVisual:true,url:'https://karagemop466-tech.github.io/Poker5/'+rel});dom.window.eval(JS);dom.window.document.dispatchEvent(new dom.window.Event('DOMContentLoaded',{bubbles:true}));return dom.window;}
const w = load('pages/tournaments.html'); const d = w.document;
const from=d.getElementById('dfrom'), to=d.getElementById('dto');
from.value='2026-12-06'; to.value='2026-12-12';
from.dispatchEvent(new w.Event('input',{bubbles:true})); to.dispatchEvent(new w.Event('input',{bubbles:true}));
const bad=[...d.querySelectorAll('table.data tbody tr')].filter(tr=>tr.parentElement?.tagName==='TBODY'&&tr.style.display!=='none'&&(tr.getAttribute('data-date')||'')&&tr.getAttribute('data-date')<'2026-12-06');
console.log('leaked rows:', bad.length);
for (const tr of bad.slice(0,3)) {
  const t = tr.closest('table');
  console.log('  table id='+(t.id||'(none)')+' cls='+t.className+' | row data-date='+tr.getAttribute('data-date'));
  console.log('  parent chain:', (()=>{let s=[],e=tr;while(e&&e.tagName!=='BODY'){s.push(e.tagName+(e.id?'#'+e.id:'')+(e.className?'.'+String(e.className).split(' ')[0]:''));e=e.parentElement;}return s.slice(0,6).join(' < ');})());
}
console.log('count text:', d.getElementById('count').textContent);
