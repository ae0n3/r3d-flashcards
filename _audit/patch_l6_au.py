# -*- coding: utf-8 -*-
"""Replace lesson-6 `au` fields with new 24kHz/48kbps/no-ID3 MP3s (edge-tts format)."""
import io, os, re, json, base64

ROOT = 'C:/Users/rakan/flashcards'
WORK = os.path.join(os.environ['LOCALAPPDATA'], 'hermes', 'cache', 'scratch', 'l6tts')
path = os.path.join(ROOT, 'lesson6-flashcards.html')
s = io.open(path, encoding='utf-8').read()

start = s.find('const CARDS = ')
st = start + len('const CARDS = ')
depth = 0
i = st
in_str = False
while i < len(s):
    ch = s[i]
    if in_str:
        if ch == '\\':
            i += 1
        elif ch == '"':
            in_str = False
    else:
        if ch == '"':
            in_str = True
        elif ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                break
    i += 1
end = i + 1
cards = json.loads(s[st:end])
print('cards:', len(cards))

changed = 0
for idx, c in enumerate(cards):
    if 'au' not in c:
        continue
    with io.open(os.path.join(WORK, 'new_%d.mp3' % idx), 'rb') as f:
        newau = 'data:audio/mp3;base64,' + base64.b64encode(f.read()).decode('ascii')
    if c['au'] != newau:
        c['au'] = newau
        changed += 1

new_cards_js = 'const CARDS = ' + json.dumps(cards, ensure_ascii=False, separators=(',', ':'))
s = s[:start] + new_cards_js + s[end:]
io.open(path, 'w', encoding='utf-8').write(s)
print('au replaced:', changed, '| file size:', len(s))
