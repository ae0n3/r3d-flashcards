// debug: why does reload not pick up stored lang?
const CHROME = 'C:\\Users\\rakan\\AppData\\Local\\hermes\\tools\\chromium-1208\\chrome-win64\\chrome.exe';
const PORT = 9337;
const BASE = 'http://127.0.0.1:8777/';
const { spawn } = require('child_process');
const fs = require('fs'); const path = require('path');
const ud = path.join(process.env.LOCALAPPDATA, 'Temp', 'cdp-audit-profile5');
fs.mkdirSync(ud, { recursive: true });
const chrome = spawn(CHROME, ['--headless=new','--disable-gpu','--no-first-run',`--remote-debugging-port=${PORT}`,`--user-data-dir=${ud}`,'--mute-audio','about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function getTarget(){ for(let i=0;i<40;i++){ try{ const l=await(await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); const p=l.find(t=>t.type==='page'); if(p) return p.webSocketDebuggerUrl; }catch(e){} await sleep(250);} throw new Error('no chrome'); }
let msgId=0; const pending=new Map(); let ws;
function send(m,p={}){ return new Promise((res,rej)=>{ const id=++msgId; pending.set(id,{resolve:res,reject:rej}); ws.send(JSON.stringify({id,method:m,params:p})); }); }
async function ev(e){ const r=await send('Runtime.evaluate',{expression:e,awaitPromise:true,returnByValue:true}); if(r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text); return r.result.value; }
const handlers=[];
async function nav(url){ const p=new Promise(res=>handlers.push({method:'Page.loadEventFired',fn:res})); await send('Page.navigate',{url}); await p; await sleep(250); }
(async()=>{
  ws=new WebSocket(await getTarget());
  await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
  ws.onmessage=ev=>{ const m=JSON.parse(ev.data); if(m.id&&pending.has(m.id)){ const p=pending.get(m.id); pending.delete(m.id); m.error?p.reject(new Error(m.error.message)):p.resolve(m.result);} else if(m.method){ handlers.forEach(h=>{if(h.method===m.method)h.fn(m.params);}); } };
  await send('Runtime.enable'); await send('Page.enable');
  await nav(BASE);
  console.log('1 fresh:', JSON.stringify(await ev(`(() => ({ stored: localStorage.getItem('r3d-lang'), lang: R3D.getLang(), h1: document.querySelector('h1').textContent }))()`)));
  console.log('2 set zh:', JSON.stringify(await ev(`(() => { localStorage.setItem('r3d-lang','zh'); return localStorage.getItem('r3d-lang'); })()`)));
  await ev(`location.reload()`);
  await sleep(600);
  console.log('3 after reload:', JSON.stringify(await ev(`(() => ({ stored: localStorage.getItem('r3d-lang'), lang: R3D.getLang(), h1: document.querySelector('h1').textContent, navType: (performance.getEntriesByType('navigation')[0]||{}).type }))()`)));
  // try a hard navigate to a different URL then back
  await nav(BASE + 'review.html');
  await nav(BASE);
  await sleep(300);
  console.log('4 after nav away/back:', JSON.stringify(await ev(`(() => ({ stored: localStorage.getItem('r3d-lang'), lang: R3D.getLang(), h1: document.querySelector('h1').textContent }))()`)));
  // force reload with cache bypass
  await send('Network.enable');
  await ev(`location.reload(true)`);
  await sleep(600);
  console.log('5 after hard reload:', JSON.stringify(await ev(`(() => ({ stored: localStorage.getItem('r3d-lang'), lang: R3D.getLang(), h1: document.querySelector('h1').textContent }))()`)));
  chrome.kill(); process.exit(0);
})().catch(e=>{ console.error('FATAL',e); chrome.kill(); process.exit(1); });
