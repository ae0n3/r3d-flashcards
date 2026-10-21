# -*- coding: utf-8 -*-
import io, json, re, sys

ROOT = 'C:/Users/rakan/flashcards'
CARD_FILES = [
    (7,  'l7_data.py',  '我们那儿的冬天跟北京一样冷'),
    (8,  'l8_data.py',  '冬天快要到了'),
]

def last_assignment(s, N):
    """Return (start_of_bracket, end_of_array_exclusive) for cards.lN array."""
    # Find the last 'cards.lN = [' occurrence
    pat = 'cards.l%d = [' % N
    i = s.rfind(pat)
    if i == -1:
        # try any cards.lN (in case next lesson was already added)
        i = s.rfind('cards.l')
        if i == -1:
            return None
    # i points at 'cards.lN = [', bracket is at i+13
    bracket = i + len(pat) - 1  # index of '['
    depth = 0
    j = bracket
    while j < len(s):
        if s[j] == '[':
            depth += 1
        elif s[j] == ']':
            depth -= 1
            if depth == 0:
                return bracket, j + 1  # end is after ']'
        j += 1
    return None

for N, data_file, title in CARD_FILES:
    print('=' * 15, 'lesson %d' % N, '=' * 15)
    s = io.open(ROOT + '/data.js', encoding='utf-8', newline='').read()
    mod = __import__(data_file.replace('.py', ''))
    cards = getattr(mod, 'CARDS_L%d' % N)
    new_data = json.dumps(cards, ensure_ascii=False)
    res = last_assignment(s, N)
    if res is None:
        # fallback: no existing cards.lN, append at end
        s += '\ncards.l%d = ' % N + new_data + ';\n'
        print('  appended (no existing)')
    else:
        b, e = res
        m_no = re.search(r'cards\.l(\d+) = \[', s[:b])
        num = m_no.group(1) if m_no else '?'
        # Replace: keep prefix up to 'cards.lNUM = [', then new data, then '];'
        prefix = s[:b]
        s = prefix + new_data + '];' + s[e:]
        # append the new lesson registration
        li = s.find('const lessons = [')
        le = s.find('];', li)
        # insert after the last lesson entry (l(N-1))
        if N > 7:
            prev = 'l' + str(N-1)
            m2 = re.search(r'\{\s*id:\s*\'%s\',' % prev, s)
            if m2:
                ep = s.find('},', m2.end())
                if ep == -1: ep = le
                s = s[:ep] + ',\n    { id: \'l%d\', num: \'第%s课\', title: \'%s\', file: \'lesson%d-flashcards.html?v=1\' }' % (N, {7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}.get(N,str(N)), title, N) + s[ep:]
        print('  replaced cards.l%s array, appended cards.l%d' % (num, N))
    io.open(ROOT + '/data.js', 'w', encoding='utf-8', newline='').write(s)
    print('  size:', len(s))

print('DONE')
