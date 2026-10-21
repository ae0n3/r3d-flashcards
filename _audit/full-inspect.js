// Full-site error inspection via CDP (bundled Chromium)
const CHROME = 'C:/Users/rakan/AppData/Local/hermes/tools/chromium-1208/chrome-win64/chrome.exe';
const PORT = 9345;
const BASE = 'https://ae0n3.github.io/r3d-flashcards/';
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const userData = path.join(process.env.LOCALAPPDATA, 'Temp', 'cdp-inspect-' + Date.now().toString(36));
fs.mkdirSync(userData, { recursive: true });
const chrome = spawn(CHROME, ['--headless=new','--no-sandbox','--disable-gpu','--no-first-run', '--remote-debugging-port=' + PORT, '--user-data-dir=' + userData, '--mute-audio', 'about:blank'], { stdio: 'ignore' });
const sleep = function(ms) { return new Promise(function(r) { setTimeout(r, ms); }); };

let ws;
let exceptions = [];
let failedReqs = [];
let pageLoads = 0;
const checks = [];
let msgId = 0;
const pending = {};
const handlers = [];

function send(method, params) {
  return new Promise(function(resolve, reject) {
    msgId++;
    pending[msgId] = { resolve: resolve, reject: reject };
    try { ws.send(JSON.stringify({ id: msgId, method: method, params: params })); } catch (e) { reject(e); }
  });
}
async function evalJS(expr) {
  const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error('eval failed: ' + (r.exceptionDetails.exception ? r.exceptionDetails.exception.description : r.exceptionDetails.text));
  return r.result.value;
}
async function getTarget() {
  for (let i = 0; i < 40; i++) {
    try {
      const list = await (await fetch('http://127.0.0.1:' + PORT + '/json/list')).json();
      const page = list.find(function(t) { return t.type === 'page'; });
      if (page) return page.webSocketDebuggerUrl;
    } catch (e) {}
    await sleep(250);
  }
  throw new Error('chrome did not start');
}
async function navigate(url) {
  for (let a = 0; a < 4; a++) {
    const loaded = new Promise(function(res) { handlers.push({ method: 'Page.loadEventFired', fn: res }); });
    await send('Page.navigate', { url: url });
    await loaded;
    await sleep(500);
    const ok = await send('Runtime.evaluate', { expression: '!!(window.R3D || document.querySelector("h1"))', returnByValue: true }).then(function(r) { return r.result.value; }).catch(function() { return false; });
    if (ok) { pageLoads++; return; }
  }
  throw new Error('did not load: ' + url);
}

(async function() {
  ws = new WebSocket(await getTarget());
  await new Promise(function(res, rej) { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = function(ev) {
    const m = JSON.parse(ev.data);
    if (m.id && pending[m.id]) {
      const p = pending[m.id];
      delete pending[m.id];
      if (m.error) { p.reject(new Error(m.error.message)); } else { p.resolve(m.result); }
    } else if (m.method) {
      if (m.method === 'Runtime.exceptionThrown') {
        exceptions.push((m.params.exceptionDetails.exception ? m.params.exceptionDetails.exception.description : '').split('\n')[0]);
      }
      if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) {
        failedReqs.push(m.params.response.status + ' ' + m.params.response.url);
      }
    }
  };
  await send('Runtime.enable');
  await send('Page.enable');
  await send('Network.enable');
  await send('Log.enable');

  const pages = ['/', '/review.html', '/lesson1-flashcards.html', '/lesson2-flashcards.html', '/lesson3-flashcards.html', '/lesson4-flashcards.html', '/lesson5-flashcards.html'];
  for (var pi = 0; pi < pages.length; pi++) {
    try {
      await navigate(BASE + pages[pi]);
      const expr = 'function g(){var r={lang:(window.R3D&&window.R3D.LS?window.R3D.LS.get("r3d-lang"):null),cards:0,transvi:0,lessons:0};if(window.R3D&&window.R3D_DATA){var D=window.R3D_DATA;if(D.lessons)r.lessons=D.lessons.length;if(D.cards)for(var k in D.cards){r.cards+=D.cards[k].length;for(var i=0;i<D.cards[k].length;i++){var c=D.cards[k][i];if(c.trans&&c.trans.vi)r.transvi++;}}}try{var q=JSON.parse(localStorage.getItem("r3d-quiz")||"{}");r.quiz=Object.keys(q).length;}catch(e){}try{var rv=JSON.parse(localStorage.getItem("r3d-review")||"{}");r.review=Object.keys(rv).length;}catch(e){}return r;}g()';
      const state = await evalJS(expr);
      checks.push({ page: pages[pi], state: state });
      console.log('NAV ' + pages[pi] + ' -> OK, lang=' + (state.lang || '?') + ', cards=' + state.cards + ', transvi=' + state.transvi + ', lessons=' + (state.lessons || 0));
    } catch (e) {
      checks.push({ page: pages[pi], error: e.message });
      console.log('NAV ' + pages[pi] + ' -> FAILED: ' + e.message);
    }
  }
  console.log('--- JS exceptions: ' + exceptions.length);
  if (exceptions.length) console.log(exceptions.slice(0, 10).join('\n  '));
  console.log('--- network 4xx/5xx: ' + failedReqs.length);
  if (failedReqs.length) console.log(failedReqs.slice(0, 10).join('\n  '));
  console.log('--- checks:');
  for (var ci = 0; ci < checks.length; ci++) {
    var c = checks[ci];
    if (c.state) console.log('  ' + c.page + ' -> lang=' + (c.state.lang || '?') + ' cards=' + c.state.cards + ' transvi=' + c.state.transvi + ' lessons=' + (c.state.lessons || 0));
    else console.log('  ' + c.page + ' -> ERROR: ' + c.error);
  }
  await chrome.kill();
})();
