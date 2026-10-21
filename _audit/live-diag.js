// diagnose: why is R3D undefined on the live site?
const CHROME = 'C:\\Users\\rakan\\AppData\\Local\\hermes\\tools\\chromium-1208\\chrome-win64\\chrome.exe';
const PORT = 9339;
const BASE = 'https://ae0n3.github.io/r3d-flashcards/';
const { spawn } = require('child_process');
const fs = require('fs'); const path = require('path');
const ud = path.join(process.env.LOCALAPPDATA, 'Temp', 'cdp-audit-profile7');
fs.mkdirSync(ud, { recursive: true });
const chrome = spawn(CHROME, ['--headless=new','--disable-gpu','--no-first-run',`--remote-debugging-port=${PORT}`,`--user-data-dir=${ud}`,'--mute-audio','about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function getTarget(){ for(let i=0;i<40;i++){ try{ const l=await(await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); const p=l.find(t=>t.type==='page'); if(p) return p.webSocketDebuggerUrl; }catch(e){} await sleep(250);} throw new Error('no chrome'); }
let msgId=0; const pending=new Map(); let ws;
function send(m,p={}){ return new Promise((res,rej)=>{ const id=++msgId; pending.set(id,{resolve:res,reject:rej}); ws.send(JSON.stringify({id,method:m,params:p})); }); }
async function ev(e){ const r=await send('Runtime.evaluate',{expression:e,awaitPromise:true,returnByValue:true}); if(r.exceptionDetails) return {ERR: r.exceptionDetails.exception?.description||r.exceptionDetails.text}; return r.result.value; }
const handlers=[]; const netFails=[]; const exceptions=[];
(async()=>{
  ws=new WebSocket(await getTarget());
  await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
  ws.onmessage=ev=>{ const m=JSON.parse(ev.data); if(m.id&&pending.has(m.id)){ const p=pending.get(m.id); pending.delete(m.id); m.error?p.reject(new Error(m.error.message)):p.resolve(m.result);} else if(m.method){ handlers.forEach(h=>{if(h.method===m.method)h.fn(m.params);});
    if(m.method==='Network.loadingFailed') netFails.push(m.params.errorText+' '+m.params.type);
    if(m.method==='Runtime.exceptionThrown') exceptions.push((m.params.exceptionDetails.exception?.description||'').split('\n')[0]);
  } };
  await send('Runtime.enable'); await send('Page.enable'); await send('Network.enable');
  const loaded=new Promise(res=>handlers.push({method:'Page.loadEventFired',fn:res}));
  await send('Page.navigate',{url:BASE});
  await loaded; await sleep(1200);
  console.log('readyState:', await ev('document.readyState'));
  console.log('h1:', await ev("document.querySelector('h1')?.textContent"));
  console.log('scripts:', JSON.stringify(await ev("[...document.scripts].map(s => s.src || s.getAttribute('src'))")));
  console.log('R3D?', await ev('typeof window.R3D'));
  console.log('R3D_DATA?', await ev('typeof window.R3D_DATA'));
  console.log('resources:', JSON.stringify((await ev("performance.getEntriesByType('resource').map(r => r.name.split('/').pop() + ':' + Math.round(r.duration))"))));
  console.log('netFails:', JSON.stringify(netFails));
  console.log('exceptions:', JSON.stringify(exceptions));
  // try fetching common.js from the page itself
  console.log('fetch test:', await ev("(async () => { try { const r = await fetch('common.js?v=5&diag=1'); const t = await r.text(); return r.status + ' len=' + t.length + ' head=' + t.slice(0,60); } catch(e) { return 'FETCH_ERR ' + e.message; } })()"));
  chrome.kill(); process.exit(0);
})().catch(e=>{ console.error('FATAL',e); chrome.kill(); process.exit(1); });
