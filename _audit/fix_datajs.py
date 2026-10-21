# -*- coding: utf-8 -*-
"""Fix the data.js update logic in build_lesson.py and rebuild."""
import io, json, re, subprocess, sys

ROOT = 'C:/Users/rakan/flashcards'
CARD_FILES = [
    (7,  'l7_data.py',  '我们那儿的冬天跟北京一样冷'),
    (8,  'l8_data.py',  '冬天快要到了'),
]

for N, data_file, title in CARD_FILES:
    print('=' * 20, 'lesson', N, '=' * 20)
    # 1) reload data.js fresh
    s = io.open(ROOT + '/data.js', encoding='utf-8', newline='').read()
    # 2) import the card data
    sys.path.insert(0, ROOT + '/_audit')
    mod = __import__(data_file.replace('.py',''))
    cards = mod.CARDS_L7 if N==7 else mod.CARDS_L8
    new_data = json.dumps(cards, ensure_ascii=False)
    # 3) find the last cards.lM = [ ... ]; one-line array
    m = re.search(r'cards\.l\d+ = \[(?:[^{}]|\{[^{}]*\})*\];', s)
    if not m:
        print('FAIL: no cards.lN array found')
        continue
    # The array is on one line: cards.lM = [ ... ];
    # Replace the array content
    prefix = s[:m.start()]
    # s[m.start():m.end()] is 'cards.lM = [OLD...]'
    # We want to keep 'cards.lM = ' and replace the array content
    # Find the ';' that closes the array (after the '[')
    semi = s.find('];', m.end())
    if semi == -1:
        print('FAIL: no closing ]; ')
        continue
    new_line = 'cards.l' + str(N) + ' = ' + new_data + ';'
    s = prefix + 'cards.l' + str(N) + ' = ' + new_data + '];' + '\n' + new_line + ';' + s[semi+2:]
    # 4b) register the lesson in the lessons array
    li = s.find("const lessons = [")
    le = s.find('];', li)
    import re
    # find the previous lesson entry
    prev_id = 'l' + str(N-1)
    m2 = re.search(r'\{\s*id:\s*\'%s\',' % prev_id, s)
    if m2:
        # find the end of that entry (next }, or the end of the array)
        # append new entry after the previous
        end_prev = s.find('},', m2.end())
        if end_prev == -1:
            end_prev = le
        s = s[:end_prev] + ',\n    { id: \'l%d\', num: \'第%s课\', title: \'%s\', file: \'lesson%d-flashcards.html?v=1\' }' % (N, {7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}.get(N,str(N)), title, N) + s[end_prev:]
        print('  lessons registry updated')
    io.open(ROOT + '/data.js', 'w', encoding='utf-8', newline='').write(s)
    print('  data.js updated')

print('DONE')
