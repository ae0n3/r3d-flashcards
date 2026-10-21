import io, os, json, re, subprocess, glob

ROOT = 'C:/Users/rakan/flashcards'

# Load the .py data files for lessons 7-12
sys_path = ROOT + '/_audit'
import importlib
lessons = {}

# Load l1-l6 from git HEAD data.js (they have trans + audio)
import subprocess
orig = subprocess.run(['git', 'show', 'HEAD:data.js'], capture_output=True, text=True, cwd=ROOT).stdout

for n in range(1, 7):
    m = re.search(r'cards\.l%d = \[' % n, orig)
    if not m: continue
    br = m.start() + len(m.group(0)) - 1
    depth = 0; j = br
    while j < len(orig):
        if orig[j] == '[': depth += 1
        elif orig[j] == ']':
            depth -= 1
            if depth == 0: end = j + 1; break
        j += 1
    cards = json.loads(orig[br:end])
    lessons[n] = cards
    print('l%d from git: %d cards, has trans: %s, has au: %s' % (n, len(cards), 'trans' in cards[0], 'au' in cards[0]))

# Load l7-l12 from .py files (they have glosses + we need to add audio from existing data.js)
# First, load current data.js to get audio for l7-l12
cur = io.open(ROOT + '/data.js', encoding='utf-8', newline='').read()
for n in range(7, 13):
    m = re.search(r'cards\.l%d = \[' % n, cur)
    if not m: continue
    br = m.start() + len(m.group(0)) - 1
    depth = 0; j = br
    while j < len(cur):
        if cur[j] == '[': depth += 1
        elif cur[j] == ']':
            depth -= 1
            if depth == 0: end = j + 1; break
        j += 1
    cur_cards = json.loads(cur[br:end])

    # Load from .py
    mod_name = 'l%d_data' % n
    import sys
    sys.path.insert(0, ROOT + '/_audit')
    if mod_name in sys.modules: del sys.modules[mod_name]
    mod = importlib.import_module(mod_name)
    CARDS = getattr(mod, 'CARDS_L%d' % n)
    TYPE_SUB_TRANS = getattr(mod, 'TYPE_SUB_TRANS', {})
    SUB_TRANS = getattr(mod, 'SUB_L%d' % n, {})

    cards = []
    for i, c in enumerate(CARDS):
        front, py, ar, typ, ex, sub, glosses = c[0], c[1], c[2], c[3], c[4], c[5], c[6]
        cat = 'word' if typ else ('gram' if sub else 'sent')
        ch = {'cat': cat, 'front': front, 'py': py, 'ar': ar}
        if typ: ch['type'] = typ
        ch['ex'] = ex
        if sub: ch['sub'] = sub
        ch['trans'] = glosses
        if typ and typ in TYPE_SUB_TRANS:
            ch['trans_type'] = TYPE_SUB_TRANS[typ]
        if sub and sub in SUB_TRANS:
            ch['trans_sub'] = SUB_TRANS[sub]
        # Add audio from current data.js
        if i < len(cur_cards):
            if 'au' in cur_cards[i]: ch['au'] = cur_cards[i]['au']
            if 'ax' in cur_cards[i]: ch['ax'] = cur_cards[i]['ax']
        cards.append(ch)

    lessons[n] = cards
    print('l%d from py: %d cards, has trans: %s, has au: %s, has ax: %s' % (
        n, len(cards), 'trans' in cards[0], 'au' in cards[0], 'ax' in cards[0]))

# Build new data.js - preserve original structure, replace all cards arrays
lines = orig.split('\n')
# Find where cards section starts and ends
cards_start = orig.find('D.cards.l1 = [')
# Find the IIFE end
iife_end = orig.rfind('})();')
if iife_end == -1:
    iife_end = orig.rfind('})(') + 4

# Build new cards section
new_cards = []
for n in range(1, 13):
    if n in lessons:
        new_cards.append('D.cards.l%d = %s;' % (n, json.dumps(lessons[n], ensure_ascii=False)))

new_cards_section = '\n'.join(new_cards)
new_data = orig[:cards_start] + new_cards_section + orig[iife_end:]

io.open(ROOT + '/data.js', 'w', encoding='utf-8', newline='').write(new_data)
print('\nRebuilt data.js, size:', len(new_data))
print('Lessons:', sorted(lessons.keys()))
