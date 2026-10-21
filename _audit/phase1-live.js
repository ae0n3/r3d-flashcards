// Phase-1 verification: applyI18n fix + favicon, full flow sanity, via CDP
const CHROME = 'C:\\Users\\rakan\\AppData\\Local\\hermes\\tools\\chromium-1208\\chrome-win64\\chrome.exe';
const PORT = 9338;
const BASE = 'https://ae0n3.github.io/r3d-flashcards/';
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const userData = path.join(process.env.LOCALAPPDATA, 'Temp', 'cdp-audit-profile6');
fs.mkdirSync(userData, { recursive: true });
const chrome = spawn(CHROME, ['--headless=new','--disable-gpu','--no-first-run',`--remote-debugging-port=${PORT}`,`--user-data-dir=${userData}`,'--mute-audio','about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function getTarget() {
  for (let i = 0; i < 40; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      const page = list.find(t => t.type === 'page');
      if (page) return page.webSocketDebuggerUrl;
    } catch (e) {}
    await sleep(250);
  }
  throw new Error('chrome did not start');
}
let msgId = 0; const pending = new Map(); let ws;
const exceptions = []; const failedReqs = [];
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId; pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evalJS(expression) {
  const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error('eval failed: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
  return r.result.value;
}
const handlers = [];
async function navigate(url) {
  for (let a = 0; a < 4; a++) {
    const loaded = new Promise(res => handlers.push({ method: 'Page.loadEventFired', fn: res }));
    await send('Page.navigate', { url });
    await loaded; await sleep(400);
    const ok = await send('Runtime.evaluate', { expression: '!!(window.R3D || document.querySelector("h1"))', returnByValue: true }).then(r => r.result.value).catch(() => false);
    if (ok) return;
  }
}
(async () => {
  ws = new WebSocket(await getTarget());
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result);
    } else if (m.method) {
      handlers.forEach(h => { if (h.method === m.method) h.fn(m.params); });
      if (m.method === 'Runtime.exceptionThrown') exceptions.push((m.params.exceptionDetails.exception?.description || '').split('\n')[0]);
      if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) failedReqs.push(m.params.response.status + ' ' + m.params.response.url);
    }
  };
  await send('Runtime.enable'); await send('Page.enable'); await send('Network.enable'); await send('Log.enable');
  const out = {};

  // fresh profile: first visit, headless locale = en-US
  await navigate(BASE);
  out.firstVisit = await evalJS(`(() => ({
    lang: R3D.getLang(),
    h1: document.querySelector('h1').textContent,            // now English (fix #1)
    sub: document.querySelector('.sub').textContent,
    dir: document.documentElement.dir,                        // now ltr (fix #1)
    masteredLine: document.getElementById('mstLine').textContent
  }))()`);

  // first-visit with Arabic device: force zh then ar detection paths
  await evalJS(`localStorage.setItem('r3d-lang','zh')`);
  await navigate(BASE);
  await sleep(200);
  out.zhVisit = await evalJS(`(() => ({ h1: document.querySelector('h1').textContent, dir: document.documentElement.dir }))()`);
  await evalJS(`localStorage.setItem('r3d-lang','ar')`);
  await navigate(BASE);
  await sleep(200);
  out.arVisit = await evalJS(`(() => ({ h1: document.querySelector('h1').textContent, dir: document.documentElement.dir }))()`);

  // ---- lesson flow ----
  await navigate(BASE + 'lesson1-flashcards.html');
  await evalJS(`document.getElementById('dunno').click()`);
  await sleep(450);
  out.lesson = await evalJS(`(() => ({
    reviewCount: R3D.reviewCount(),
    marks: R3D.Marks.load('l1')
  }))()`);
  for (let i = 0; i < 45; i++) {
    await evalJS(`document.getElementById('next').click()`);
    await sleep(20);
    if (await evalJS(`document.getElementById('quizTool').style.display`) === '') break;
  }
  await evalJS(`document.getElementById('quizTool').click()`);
  await sleep(300);
  out.quizStart = await evalJS(`!document.getElementById('quizSec').hidden && R3D.Quiz.qs.length`);
  for (let i = 0; i < 70; i++) {
    if (await evalJS(`R3D.Quiz.cur >= R3D.Quiz.qs.length`)) break;
    await evalJS(`document.querySelector('#quizSec .qchoice').click()`);
    await sleep(1650);
  }
  out.quizFinish = await evalJS(`(() => ({ done: R3D.Quiz.cur >= R3D.Quiz.qs.length, stored: !!R3D.LS.get('r3d-quiz').l1 }))()`);

  // ---- review flow + audio lazy fetch ----
  await navigate(BASE + 'review.html');
  await sleep(500);
  out.review = await evalJS(`(() => ({ count: R3D.reviewCount(), card: document.getElementById('rbig').textContent }))()`);
  out.audio = await evalJS(`(async () => {
    const before = performance.getEntriesByType('resource').filter(r => r.name.includes('lesson')).length;
    document.getElementById('rspk').click();
    await new Promise(r => setTimeout(r, 2000));
    const after = performance.getEntriesByType('resource').filter(r => r.name.includes('lesson')).length;
    return after > before;
  })()`);

  // ---- every page loaded clean? ----
  for (const p of ['index.html','review.html','lesson1-flashcards.html','lesson2-flashcards.html','lesson3-flashcards.html','lesson4-flashcards.html','lesson5-flashcards.html']) {
    await navigate(BASE + p);
    await sleep(150);
  }

  out.exceptions = exceptions;
  out.failedRequests = failedReqs;
  console.log(JSON.stringify(out, null, 2));
  chrome.kill(); process.exit(0);
})().catch(e => { console.error('FATAL', e); chrome.kill(); process.exit(1); });
