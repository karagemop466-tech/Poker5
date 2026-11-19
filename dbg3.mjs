import { readFileSync } from 'node:fs';
const { JSDOM } = await import('jsdom');
const JS = readFileSync('./assets/app.js','utf8');
function load(rel){const dom=new JSDOM(readFileSync('./'+rel,'utf8'),{runScripts:'outside-only',pretendToBeVisual:true,url:'https://x/'+rel});dom.window.eval(JS);dom.window.document.dispatchEvent(new dom.window.Event('DOMContentLoaded',{bubbles:true}));return dom.window;}
const vis=(d,sel='table.data tbody tr')=>[...d.querySelectorAll(sel)].filter(tr=>tr.parentElement?.tagName==='TBODY'&&tr.style.display!=='none');
for (const rel of ['pages/hotels.html','pages/planner.html']) {
  const w=load(rel), d=w.document;
  console.log('###', rel);
  const tiers=[...new Set([...d.querySelectorAll('[data-tier]')].map(e=>e.getAttribute('data-tier')))];
  console.log('  data-tier values present:', JSON.stringify(tiers));
  const q=d.getElementById('pquality');
  if(q){ const before=vis(d).length; q.value='2'; q.dispatchEvent(new w.Event('change',{bubbles:true}));
    console.log('  shared Luxury-only: before',before,'after',vis(d).length);
    q.value=''; q.dispatchEvent(new w.Event('change',{bubbles:true})); }
  const b=d.getElementById('bfloor');
  if(b){ const before=vis(d).length; b.value='Luxury'; b.dispatchEvent(new w.Event('change',{bubbles:true}));
    console.log('  local bfloor=Luxury: before',before,'after',vis(d).length);
    const lux=vis(d).filter(tr=>/Luxury/.test(tr.children[1]?.textContent||'')).length;
    console.log('    rows whose tier cell says Luxury:', lux);
    b.value=''; b.dispatchEvent(new w.Event('change',{bubbles:true})); }
}
