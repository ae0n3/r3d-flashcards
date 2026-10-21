// Live-site functional test via CDP on bundled Chromium (headless)
const CHROME = 'C:\\Users\\rakan\\AppData\\Local\\hermes\\tools\\chromium-1208\\chrome-win64\\chrome.exe';
const PORT = 9333;
const BASE = 'https://ae0n3.github.io/r3d-flashcards/';

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const userData = path.join(process.env.LOCALAPPDATA, 'Temp', 'cdp-audit-profile');
fs.mkdirSync(userData, { recursive: true });

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${userData}`,
  '--disable-extensions', '--mute-audio', 'about:blank'
], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));
async function getTarget() {
  for (let i = 0; i < 40; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      const list = await res.json();
      const page = list.find(t => t.type === 'page');
      if (page) return page.webSocketDebuggerUrl;
    } catch (e) { /* retry */ }
    await sleep(250);
  }
  throw new Error('chrome did not start');
}

let msgId = 0;
const pending = new Map();
const events = [];
let ws;

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function evalJS(expression) {
  const r = await send('Runtime.evaluate', {
    expression, awaitPromise: true, returnByValue: true
  });
  if (r.exceptionDetails) {
    const d = r.exceptionDetails;
    throw new Error('page eval failed: ' + (d.exception?.description || d.text));
  }
  return r.result.value;
}

async function navigate(url) {
  const loaded = new Promise(res => {
    const h = ev => {
      if (ev.method === 'Page.loadEventFired') { events.splice(events.indexOf(h), 1); res(); }
    };
    events.push(h);
  });
  await send('Page.navigate', { url });
  await loaded;
  await sleep(300);
}

(async () => {
  const wsUrl = await getTarget();
  ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result);
    } else if (m.method) {
      events.forEach(h => h(m));
      if (m.method === 'Runtime.exceptionThrown') {
        console.log('PAGE EXCEPTION:', JSON.stringify(m.params.exceptionDetails?.exception?.description || m.params.exceptionDetails?.text).slice(0, 300));
      }
      if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') {
        console.log('CONSOLE ERROR:', m.params.entry.text.slice(0, 300));
      }
      if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) {
        console.log('CONSOLE', m.params.type.toUpperCase() + ':', m.params.args.map(a => a.value || a.description || '').join(' ').slice(0, 300));
      }
    }
  };
  await send('Runtime.enable');
  await send('Page.enable');
  await send('Log.enable');

  const out = {};

  // ---------- INDEX ----------
  await navigate(BASE);
  out.index = await evalJS(`(() => ({
    title: document.title,
    lessons: document.querySelectorAll('.lesson').length,
    badge: document.getElementById('revBadge').textContent,
    mastered: document.getElementById('mstLine').textContent,
    lang: R3D.getLang()
  }))()`);

  // language switch to English
  await evalJS(`(() => { const s = document.getElementById('langSel'); s.value='en'; s.dispatchEvent(new Event('change')); })()`);
  await sleep(250);
  out.afterEnSwitch = await evalJS(`(() => ({
    h1: document.querySelector('h1').textContent,
    dir: document.documentElement.dir,
    sub: document.querySelector('.sub').textContent
  }))()`);
  // back to Arabic
  await evalJS(`(() => { const s = document.getElementById('langSel'); s.value='ar'; s.dispatchEvent(new Event('change')); })()`);
  await sleep(200);

  // ---------- LESSON 1 ----------
  await navigate(BASE + 'lesson1-flashcards.html');
  out.lesson = await evalJS(`(() => ({
    cnt: document.getElementById('cnt').textContent,
    front: document.getElementById('big').textContent,
    chips: document.querySelectorAll('.chip').length
  }))()`);

  // flip card
  await evalJS(`document.getElementById('card').click()`);
  await sleep(350);
  out.flip = await evalJS(`document.getElementById('card').classList.contains('flipped')`);
  await evalJS(`document.getElementById('card').click()`);
  await sleep(200);

  // mark card 0 as dunno -> enters review set
  await evalJS(`document.getElementById('dunno').click()`);
  await sleep(450);
  out.afterDunno = await evalJS(`(() => ({
    reviewCount: R3D.reviewCount(),
    marks: R3D.Marks.load('l1')
  }))()`);

  // mark next card know
  await evalJS(`document.getElementById('know').click()`);
  await sleep(450);
  out.afterKnow = await evalJS(`R3D.Marks.load('l1')`);

  // walk to the end to unlock quiz
  for (let i = 0; i < 45; i++) {
    await evalJS(`document.getElementById('next').click()`);
    await sleep(25);
    const un = await evalJS(`document.getElementById('quizTool').style.display`);
    if (un === '') break;
  }
  out.quizUnlocked = await evalJS(`document.getElementById('quizTool').style.display`);

  // start quiz, answer everything (click first choice each time)
  await evalJS(`document.getElementById('quizTool').click()`);
  await sleep(400);
  out.quiz = await evalJS(`(() => ({
    visible: !document.getElementById('quizSec').hidden,
    qs: R3D.Quiz.qs.length,
    firstPrompt: (document.querySelector('#quizSec .qprompt')||{}).textContent
  }))()`);
  for (let i = 0; i < 70; i++) {
    const done = await evalJS(`!R3D.Quiz.qs.length || R3D.Quiz.cur >= R3D.Quiz.qs.length`);
    if (done) break;
    await evalJS(`document.querySelector('#quizSec .qchoice').click()`);
    await sleep(1650);
  }
  out.quizResult = await evalJS(`(() => ({
    finished: R3D.Quiz.cur >= R3D.Quiz.qs.length,
    stored: R3D.LS.get('r3d-quiz'),
    reviewCount: R3D.reviewCount()
  }))()`);

  // ---------- REVIEW ----------
  await navigate(BASE + 'review.html');
  await sleep(600);
  out.review = await evalJS(`(() => ({
    count: R3D.reviewCount(),
    card: document.getElementById('rbig').textContent,
    empty: document.getElementById('rempty').classList.contains('show')
  }))()`);
  if (out.review.count > 0) {
    // answer know twice -> mastered
    await evalJS(`document.getElementById('rknow').click()`);
    await sleep(750);
    await evalJS(`document.getElementById('rknow').click()`);
    await sleep(950);
    out.reviewAfterMaster = await evalJS(`(() => ({
      mastered: R3D.masteredCount(),
      remaining: R3D.reviewCount()
    }))()`);
  }
  // audio path: press speaker on a remaining item if any
  out.audioTest = await evalJS(`(async () => {
    const n = R3D.reviewCount();
    if (!n) return 'no items to test audio';
    const before = performance.getEntriesByType('resource').filter(r => r.name.includes('lesson')).length;
    document.getElementById('rspk').click();
    await new Promise(r => setTimeout(r, 2500));
    const after = performance.getEntriesByType('resource').filter(r => r.name.includes('lesson')).length;
    return { fetchedLessonFile: after > before, cache: Object.keys(R3D._lessonCache || {}) };
  })()`);

  // ---------- cross-page state ----------
  await navigate(BASE);
  await sleep(400);
  out.indexAfter = await evalJS(`(() => ({
    badge: document.getElementById('revBadge').textContent,
    mastered: document.getElementById('mstLine').textContent,
    l1progress: document.querySelector('.lesson .pbar i').style.width,
    l1quiz: document.querySelectorAll('.lesson .meta span')[1].textContent
  }))()`);

  console.log(JSON.stringify(out, null, 2));
  chrome.kill();
  process.exit(0);
})().catch(e => { console.error('FATAL', e); chrome.kill(); process.exit(1); });
