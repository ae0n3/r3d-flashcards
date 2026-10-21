// verify language persistence + first-visit detection per stored value
const CHROME = 'C:\\Users\\rakan\\AppData\\Local\\hermes\\tools\\chromium-1208\\chrome-win64\\chrome.exe';
const PORT = 9336;
const BASE = 'http://127.0.0.1:8777/';
const { spawn } = require('child_process');
const fs = require('fs'); const path = require('path');
const ud = path.join(process.env.LOCALAPPDATA, 'Temp', 'cdp-audit-profile4');
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
  const out={};
  await nav(BASE);
  const read = () => ev(`(() => ({ lang: R3D.getLang(), h1: document.querySelector('h1').textContent, dir: document.documentElement.dir }))()`);
  out.fresh = await read();                       // fresh profile -> detect en
  for (const l of ['zh','ar','en','es','fr']) {
    await ev(`R3D.LS.set('r3d-lang','${l}')`);  // app's own JSON writer
    await ev(`location.reload()`);                // real reload, not same-URL navigate
    await sleep(300);
    out['stored_'+l] = await read();
  }
  // unknown stored value falls back
  await ev(`R3D.LS.set('r3d-lang','de')`);
  await ev(`location.reload()`);
  await sleep(300);
  out.stored_unknown = await read();
  console.log(JSON.stringify(out,null,2));
  chrome.kill(); process.exit(0);
})().catch(e=>{ console.error('FATAL',e); chrome.kill(); process.exit(1); });
