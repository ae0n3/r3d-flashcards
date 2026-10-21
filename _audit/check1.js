const D = (() => {
  global.window = {};
  require('C:/Users/rakan/flashcards/data.js');
  return global.window.R3D_DATA;
})();
const map = JSON.parse(require('fs').readFileSync('C:/Users/rakan/flashcards/_audit/vi_data.json', 'utf8'));
const missing = [];
let known = 0;
for (const k in D.cards) {
  D.cards[k].forEach(c => {
    if (map.trans[c.ar]) known++;
    else missing.push(c.ar);
  });
}
console.log('mapped: ' + known + ' / ' + Object.values(D.cards).reduce((a, x) => a + x.length, 0));
console.log('MISSING (' + missing.length + '):');
console.log(missing.join('\n'));
