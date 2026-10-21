const D = (() => {
  global.window = {};
  require('C:/Users/rakan/flashcards/data.js');
  return global.window.R3D_DATA;
})();
const glosses = new Set(), types = new Set(), subs = new Set();
let cardCount = 0;
for (const k in D.cards) {
  D.cards[k].forEach(c => {
    cardCount++;
    if (c.ar && c.ar.trim()) glosses.add(c.ar.trim());
    if (c.type) types.add(c.type.trim());
    if (c.sub) subs.add(c.sub.trim());
  });
}
const list = s => [...new Set(s.split('\n').map(x => x.trim()).filter(Boolean))];
console.log('CARDS: ' + cardCount);
console.log('UNIQUE GLOSSES: ' + list('').length);  // placeholder
console.log('UNIQUE TYPES: ' + list('').length);
console.log('UNIQUE SUBS: ' + list('').length);
