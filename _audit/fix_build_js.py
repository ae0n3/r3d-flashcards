# -*- coding: utf-8 -*-
import re
p = '_audit/build_lesson.py'
s = open(p, encoding='utf-8').read()

OLD = s[s.find('# ---------- 4) update data.js'):s.find("print('data.js updated')")]

NEW = '''# ---------- 4) update data.js ----------
s = io.open(os.path.join(ROOT, 'data.js'), encoding='utf-8').read()
# 4a) Find the LAST cards.lN array (one-line JSON, nested {} inside trans dict)
# and append the new lesson's cards immediately after it
import re
# Find the last assignment of the form cards.lM = [
m = re.search(r'cards\.l(\d+) = \[', s)
if not m:
    print('WARNING: no cards.lN assignment found')
    s += '\ncards.l%d = ' % N + json.dumps(cards_data, ensure_ascii=False) + ';'
else:
    last_line_start = s.rfind('\n', 0, m.start()) + 1
    bracket = m.start() + len(m.group(0)) - 1  # index of '['
    depth = 0; j = bracket
    while j < len(s):
        if s[j] == '[': depth += 1
        elif s[j] == ']':
            depth -= 1
            if depth == 0: break
        j += 1
    end = j + 1  # position right after ']'
    # Replace the array content: cards.lM = [OLD] -> cards.lM = [NEW]
    s = s[:bracket] + json.dumps(cards_data, ensure_ascii=False) + '];' + s[end:]
    # 4b) register the lesson in the lessons array
    li = s.find('const lessons = [')
    le = s.find('];', li)
    prev = 'l%d' % (N-1)
    m2 = re.search(r"\{ id: '%s'," % prev, s)
    if m2:
        ep = s.find(',}', m2.end())
        if ep == -1: ep = le
        num_cn = {7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}.get(N, str(N))
        s = s[:ep] + ',\n    { id: \'l%d\', num: \'第%s课\', title: \'%s\', file: \'%s?v=1\' }' % (N, num_cn, TITLE_CN, HTML_FILE) + s[ep:]
        print('lessons registry updated')
    io.open(os.path.join(ROOT, 'data.js'), 'w', encoding='utf-8').write(s)
    print('data.js updated (added lesson %d)' % N)

print('DONE')

'''
s = s.replace(OLD, NEW)
open(p, 'w', encoding='utf-8').write(s)
print('build_lesson.py fixed')
