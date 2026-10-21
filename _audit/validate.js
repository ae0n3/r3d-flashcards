// Validate data.js + cross-check each lesson file's inline CARDS against R3D_DATA
const fs = require('fs');
const path = require('path');

// load data.js as global
global.window = {};
eval(fs.readFileSync('data.js', 'utf8'));
const D = global.window.R3D_DATA;
if (!D) { console.log('FAIL: R3D_DATA missing'); process.exit(1); }

console.log('books:', JSON.stringify(D.books));
console.log('lessons:', JSON.stringify(D.lessons.map(l => ({id: l.id, file: l.file, num: l.num}))));

const issues = [];
const seenFronts = {}; // per-lesson dupes
for (const key in D.cards) {
  const arr = D.cards[key];
  console.log(`cards[${key}]: ${arr.length}`);
  const fronts = {};
  arr.forEach((c, i) => {
    for (const f of ['cat','front','py','ar']) {
      if (c[f] === undefined) issues.push(`${key}[${i}] missing field '${f}': front=${c.front}`);
    }
    if (!['word','sent','gram'].includes(c.cat)) issues.push(`${key}[${i}] bad cat '${c.cat}' (${c.front})`);
    if (c.front in fronts) issues.push(`${key} duplicate front '${c.front}' at idx ${fronts[c.front]} and ${i}`);
    fronts[c.front] = i;
    if (c.trans) {
      for (const l of ['en','es','fr','zh']) {
        if (!c.trans[l]) issues.push(`${key}[${i}] (${c.front}) trans missing '${l}'`);
      }
      if (c.trans.ar) issues.push(`${key}[${i}] (${c.front}) trans should NOT contain ar`);
    } else {
      issues.push(`${key}[${i}] (${c.front}) missing trans`);
    }
    if (c.type && !c.trans_type) issues.push(`${key}[${i}] (${c.front}) missing trans_type`);
    if (c.sub && !c.trans_sub) issues.push(`${key}[${i}] (${c.front}) missing trans_sub`);
    if (c.type && c.trans_type) for (const l of ['en','es','fr','zh']) if (!c.trans_type[l]) issues.push(`${key}[${i}] (${c.front}) trans_type missing '${l}'`);
    if (c.sub && c.trans_sub) for (const l of ['en','es','fr','zh']) if (!c.trans_sub[l]) issues.push(`${key}[${i}] (${c.front}) trans_sub missing '${l}'`);
  });
}
// lesson files: file field exists on disk
for (const l of D.lessons) {
  if (!fs.existsSync(l.file)) issues.push(`lesson file missing on disk: ${l.file}`);
}

// cross-check inline CARDS in each lesson file vs data.js
for (const key in D.cards) {
  const meta = D.lessons.find(l => l.id === key);
  const f = meta ? meta.file : key + '-flashcards.html';
  if (!fs.existsSync(f)) { issues.push(`lesson file not found: ${f}`); continue; }
  const html = fs.readFileSync(f, 'utf8');
  const m = html.match(/const CARDS = (\[[\s\S]*?\]);/);
  if (!m) { issues.push(`${f}: CARDS array not found by regex`); continue; }
  let inline;
  try { inline = eval('(' + m[1] + ')'); } catch (e) { issues.push(`${f}: CARDS parse error: ${e.message}`); continue; }
  if (inline.length !== D.cards[key].length) issues.push(`${f}: inline count ${inline.length} != data.js count ${D.cards[key].length}`);
  const n = Math.min(inline.length, D.cards[key].length);
  for (let i = 0; i < n; i++) {
    const a = inline[i], b = D.cards[key][i];
    for (const fld of ['cat','front','py','ar','type','sub','ex']) {
      if ((a[fld] || '') !== (b[fld] || '')) issues.push(`${f}[${i}] field '${fld}' mismatch: inline="${a[fld]}" data="${b[fld]}"`);
    }
    // audio presence
    if (!a.au) issues.push(`${f}[${i}] (${a.front}) has no audio`);
  }
  // any `]);` or `];` inside the audio/string area that could break the review-page lazy regex?
  // check the FIRST occurrence position of `]);` vs end of array
  const firstIdx = html.indexOf(']);');
  const arrEnd = html.indexOf(m[1]) + m[1].length; // approx end of captured array
  if (firstIdx < arrEnd - 3) { /* matched early inside? recompute */ }
  const after = html.indexOf(']);');
  // find actual end: last `];` before line 180
  // simpler: ensure regex match ends at the line where `const LESSON_ID` follows
  const tail = html.slice(html.indexOf(m[1]) + m[1].length, html.indexOf(m[1]) + m[1].length + 40);
  if (!/^\s*\n/.test(tail)) issues.push(`${f}: CARDS regex may be cutting early, tail="${tail.slice(0,30)}"`);
}

console.log('\n=== ISSUES (' + issues.length + ') ===');
issues.slice(0, 60).forEach(i => console.log('- ' + i));
if (issues.length > 60) console.log(`... and ${issues.length - 60} more`);
