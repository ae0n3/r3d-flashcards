# -*- coding: utf-8 -*-
"""Generic lesson builder: build lesson N flashcards + data.js.
Usage: python build_lesson.py <N> <data_file.py>
Example: python build_lesson.py 7 l7_data.py
"""
import io, os, re, json, base64, subprocess, sys, time

ROOT = 'C:/Users/rakan/flashcards'
WORK = os.path.join(os.environ['LOCALAPPDATA'], 'hermes', 'cache', 'scratch', 'l6tts')
os.makedirs(WORK, exist_ok=True)
FFMPEG = 'C:/Users/rakan/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg.exe'
EDGE_PY = os.path.join(ROOT, '_audit', 'edgevenv', 'Scripts', 'python.exe')

N = int(sys.argv[1])
DATA_FILE = sys.argv[2]
LESSON_ID = 'l%d' % N
HTML_FILE = 'lesson%d-flashcards.html' % N
TITLE_CN = sys.argv[3] if len(sys.argv) > 3 else ''

sys.path.insert(0, os.path.join(ROOT, '_audit'))
mod = __import__(os.path.splitext(os.path.basename(DATA_FILE))[0])
CARDS = getattr(mod, 'CARDS_L%d' % N)
TYPE_SUB_TRANS = getattr(mod, 'TYPE_SUB_TRANS', {})
SUB_TRANS = getattr(mod, 'SUB_L%d' % N, {})

print('lesson %d: %d cards' % (N, len(CARDS)))

# ---------- 1) edge-tts audio ----------
def edge_tts(text, out_mp3):
    for attempt in range(3):
        r = subprocess.run(
            [EDGE_PY, '-c',
             'import edge_tts, asyncio\n'
             'async def m():\n'
             '    t = edge_tts.Communicate(%r, "zh-CN-XiaoxiaoNeural")\n'
             '    await t.save(%r)\n'
             'asyncio.run(m())\n' % (text, out_mp3)],
            capture_output=True, timeout=60)
        if r.returncode == 0 and os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
            return True
        time.sleep(2)
    print('EDGE FAIL:', text[:30])
    return False

def to_edge_format(src_mp3, dst_mp3):
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error',
                    '-i', src_mp3, '-ar', '24000', '-ac', '1',
                    '-codec:a', 'libmp3lame', '-b:a', '48k',
                    '-write_xing', '0', '-id3v2_version', '0',
                    '-map_metadata', '-1', dst_mp3], check=True)

jobs = []
for i, c in enumerate(CARDS):
    jobs.append(('au', i, c[0]))
    if c[4]:  # ex
        jobs.append(('ax', i, c[4]))

print('TTS jobs:', len(jobs))
ok = 0; fail = 0
for kind, ci, text in jobs:
    raw = os.path.join(WORK, 'L%d_%s_%d.mp3' % (N, kind, ci))
    if not (os.path.exists(raw) and os.path.getsize(raw) > 500):
        if not edge_tts(text, raw):
            fail += 1; continue
    ok += 1
    if ok % 20 == 0:
        print('  generated', ok, '/', len(jobs))
print('TTS done: ok=%d fail=%d' % (ok, fail))
assert fail == 0, 'some TTS failed'

for kind, ci, text in jobs:
    raw = os.path.join(WORK, 'L%d_%s_%d.mp3' % (N, kind, ci))
    dst = os.path.join(WORK, 'L%d_e%s_%d.mp3' % (N, kind, ci))
    if not os.path.exists(dst):
        to_edge_format(raw, dst)
print('re-encode done')

def b64(kind, idx):
    with io.open(os.path.join(WORK, 'L%d_e%s_%d.mp3' % (N, kind, idx)), 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')

# ---------- 2) build cards ----------
cards_html = []
cards_data = []
for i, c in enumerate(CARDS):
    front, py, ar, typ, ex, sub, glosses = c[0], c[1], c[2], c[3], c[4], c[5], c[6]
    cat = 'word' if typ else ('gram' if sub else 'sent')
    ch = {'cat': cat, 'front': front, 'py': py, 'ar': ar}
    if typ: ch['type'] = typ
    ch['ex'] = ex
    ch['au'] = 'data:audio/mp3;base64,' + b64('au', i)
    if ex:
        ch['ax'] = 'data:audio/mp3;base64,' + b64('ax', i)
    if sub: ch['sub'] = sub
    cards_html.append(ch)
    d = {'cat': cat, 'front': front, 'py': py, 'ar': ar}
    if typ: d['type'] = typ
    d['ex'] = ex
    if sub: d['sub'] = sub
    d['trans'] = glosses
    if typ and typ in TYPE_SUB_TRANS:
        d['trans_type'] = TYPE_SUB_TRANS[typ]
    if sub and sub in SUB_TRANS:
        d['trans_sub'] = SUB_TRANS[sub]
    d['au'] = 'data:audio/mp3;base64,' + b64('au', i)
    if ex:
        d['ax'] = 'data:audio/mp3;base64,' + b64('ax', i)
    cards_data.append(d)

print('cards_html:', len(cards_html), '| with ax:', sum(1 for c in cards_html if 'ax' in c))

# ---------- 3) rebuild HTML ----------
tpl = io.open(os.path.join(ROOT, 'lesson1-flashcards.html'), encoding='utf-8').read()
tpl = tpl.replace('<title>درس · 田芳去哪儿了 · بطاقات استذكار</title>',
                  '<title>درس · %s · بطاقات استذكار</title>' % TITLE_CN)
tpl = tpl.replace('汉语教程 · 第三版 · 第二册上 · <b>第一课</b>',
                  '汉语教程 · 第三版 · 第二册上 · <b>第%s课</b>' % {7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}.get(N, str(N)))
tpl = tpl.replace('<h1>田芳去哪儿了</h1>', '<h1>%s</h1>' % TITLE_CN)
CARDS_JS = 'const CARDS = ' + json.dumps(cards_html, ensure_ascii=False, separators=(',', ':'))
ci = tpl.find('const CARDS = ')
cs = ci + len('const CARDS = ')
depth = 0; i = cs; in_str = False
while i < len(tpl):
    ch = tpl[i]
    if in_str:
        if ch == '\\': i += 1
        elif ch == '"': in_str = False
    else:
        if ch == '"': in_str = True
        elif ch == '[': depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0: break
    i += 1
tpl = tpl[:ci] + CARDS_JS + ';' + tpl[i+2:]
tpl = tpl.replace("const LESSON_ID = 'l1';", "const LESSON_ID = '%s';" % LESSON_ID)
io.open(os.path.join(ROOT, HTML_FILE), 'w', encoding='utf-8').write(tpl)
print('HTML written:', len(tpl), 'bytes')

# ---------- 4) update data.js ----------
s = io.open(os.path.join(ROOT, 'data.js'), encoding='utf-8').read()
# 4a) Replace the last cards.lM array (one-line JSON) and append the new
# lesson's cards immediately after the OLD array (keep OLD, add NEW after)
import re
m = re.search(r'cards\.l(\d+) = \[', s)
if not m:
    print('WARNING: no cards.lN assignment in data.js')
    s += '\ncards.l%d = ' % N + json.dumps(cards_data, ensure_ascii=False) + ';'
else:
    prev_num = m.group(1)                       # previous lesson (e.g. l6)
    prefix = 'cards.l%s = [' % prev_num
    idx = s.rfind(prefix)                       # start of 'cards.lM = ['
    br = idx + len(prefix) - 1                  # index of '['
    depth = 0; j = br
    while j < len(s):
        if s[j] == '[': depth += 1
        elif s[j] == ']':
            depth -= 1
            if depth == 0:
                end = j + 1                     # right after ']'
                break
        j += 1
    else:
        print('WARNING: array not closed')
        s += '\ncards.l%d = ' % N + json.dumps(cards_data, ensure_ascii=False) + ';'
    new_data = json.dumps(cards_data, ensure_ascii=False)
    # Keep the old array (cards.lM = [OLD]) and insert the new lesson after it
    s = s[:end] + '\ncards.l%d = ' % N + new_data + ';' + s[end:]
    # 4b) register the lesson in the lessons array
    li = s.find('const lessons = [')
    le = s.find('];', li)
    m2 = re.search(r"\{ id: 'l%s'," % (N-1), s)
    if m2:
        ep = s.find(',}', m2.end())
        if ep == -1: ep = le
        num_cn = {7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}.get(N, str(N))
        s = s[:ep] + ',\n    { id: \'l%d\', num: \'第%s课\', title: \'%s\', file: \'%s?v=1\' }' % (N, num_cn, TITLE_CN, HTML_FILE) + s[ep:]
        print('lessons registry updated')
    io.open(os.path.join(ROOT, 'data.js'), 'w', encoding='utf-8').write(s)
    print('data.js updated (lesson %d)' % N)
print('DONE')

print('DONE')

print('data.js updated')
print('DONE')
