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
const NL = String.fromCharCode(10);
const dedupe = arr => [...new Set(arr.map(x => x.trim()).filter(Boolean))];
console.log('CARDS: ' + cardCount);
const gl = dedupe([...glosses]);
console.log('UNIQUE GLOSSES: ' + gl.length);
console.log(gl.join(String.fromCharCode(10)));
const ty = dedupe([...types]);
console.log('UNIQUE TYPES: ' + ty.length);
console.log(ty.join(String.fromCharCode(10)));
const su = dedupe([...subs]);
console.log('UNIQUE SUBS: ' + su.length);
console.log(su.join(String.fromCharCode(10)));
