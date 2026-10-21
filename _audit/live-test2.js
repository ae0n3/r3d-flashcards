// Focused CDP re-test: identify 404 URL, test filter chips, quiz retry, keyboard nav
const CHROME = 'C:\\Users\\rakan\\AppData\\Local\\hermes\\tools\\chromium-1208\\chrome-win64\\chrome.exe';
const PORT = 9334;
const BASE = 'https://ae0n3.github.io/r3d-flashcards/';
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const userData = path.join(process.env.LOCALAPPDATA, 'Temp', 'cdp-audit-profile2');
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
async function navigate(url) {
  const loaded = new Promise(res => {
    const h = () => res();
    handlers.push({ method: 'Page.loadEventFired', fn: h });
  });
  await send('Page.navigate', { url });
  await loaded; await sleep(300);
}
const handlers = [];
(async () => {
  ws = new WebSocket(await getTarget());
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  const failedRequests = [];
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result);
    } else if (m.method) {
      handlers.forEach(h => { if (h.method === m.method) h.fn(m.params); });
      if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) {
        failedRequests.push(m.params.response.status + ' ' + m.params.response.url);
      }
      if (m.method === 'Runtime.exceptionThrown') {
        console.log('PAGE EXCEPTION:', (m.params.exceptionDetails.exception?.description || '').split('\n')[0]);
      }
    }
  };
  await send('Runtime.enable'); await send('Page.enable'); await send('Network.enable');
  const out = {};

  // fresh profile => first visit, detected lang = en (headless default)
  await navigate(BASE);
  out.firstVisit = await evalJS(`(() => ({
    detectedLang: R3D.getLang(),
    h1: document.querySelector('h1').textContent,          // hardcoded Arabic in HTML
    navBtn: document.querySelector('.navbtn').textContent, // hardcoded Arabic
    masteredLine: document.getElementById('mstLine').textContent // rendered by JS
  }))()`);

  // ---- lesson: filter chips ----
  await navigate(BASE + 'lesson1-flashcards.html');
  out.chips = await evalJS(`(() => {
    const chips = [...document.querySelectorAll('.chip')];
    const before = document.getElementById('cnt').textContent;
    chips[3].click(); // grammar
    const gram = document.getElementById('cnt').textContent;
    const gramTag = document.getElementById('tagf').textContent;
    chips[0].click(); // all
    return { before, gram, gramTag, backToAll: document.getElementById('cnt').textContent };
  })()`);

  // ---- lesson: keyboard nav ----
  await evalJS(`document.dispatchEvent(new KeyboardEvent('keydown', {key:'ArrowRight'}))`);
  await sleep(250);
  out.keyboard = await evalJS(`document.getElementById('cnt').textContent`);

  // ---- quiz retry flow ----
  for (let i = 0; i < 45; i++) {
    await evalJS(`document.getElementById('next').click()`);
    await sleep(20);
    if (await evalJS(`document.getElementById('quizTool').style.display`) === '') break;
  }
  await evalJS(`document.getElementById('quizTool').click()`);
  await sleep(300);
  await evalJS(`document.querySelector('#quizSec .qchoice').click()`);
  await sleep(1700);
  out.quizSecondQ = await evalJS(`R3D.Quiz.cur`);
  // finish quiz fast: answer all
  for (let i = 0; i < 70; i++) {
    if (await evalJS(`R3D.Quiz.cur >= R3D.Quiz.qs.length`)) break;
    await evalJS(`document.querySelector('#quizSec .qchoice').click()`);
    await sleep(1650);
  }
  out.quizFinishShown = await evalJS(`(() => {
    const t = document.getElementById('quizSec').innerText;
    return t.includes(R3D.t('quiz.resultTitle'));
  })()`);
  // click "again"
  out.preRetry = await evalJS(`(() => ({
    cur: R3D.Quiz.cur, qs: R3D.Quiz.qs.length,
    btns: [...document.querySelectorAll('#quizSec .qbtn')].map(b => b.textContent),
    text: document.getElementById('quizSec').innerText.slice(0, 120)
  }))()`);
  console.log('DEBUG quizFinishShown=', JSON.stringify(out.quizFinishShown), 'preRetry=', JSON.stringify(out.preRetry));
  try {
    await evalJS(`[...document.querySelectorAll('#quizSec .qbtn')].find(b => b.textContent.includes('🔁')).click()`);
  } catch (e) { out.retryClickError = String(e.message).slice(0, 80); }
  await sleep(400);
  out.quizRetry = await evalJS(`(() => ({ cur: R3D.Quiz.cur, visible: !document.getElementById('quizSec').hidden }))()`);
  // close quiz
  await evalJS(`[...document.querySelectorAll('#quizSec .qbtn')].find(b => b.textContent.length < 6).click()`);
  await sleep(200);
  out.quizClosed = await evalJS(`document.getElementById('quizSec').hidden`);

  out.failedRequests = failedRequests;
  console.log(JSON.stringify(out, null, 2));
  chrome.kill(); process.exit(0);
})().catch(e => { console.error('FATAL', e); chrome.kill(); process.exit(1); });
