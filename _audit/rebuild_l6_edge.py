# -*- coding: utf-8 -*-
"""Regenerate ALL lesson-6 audio (au + ax) with edge-tts 7.3.1 via VPN, re-encode to exact lesson 1-5 format."""
import io, os, re, json, base64, subprocess, sys, time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l6_data import CARDS_L6, TYPE_SUB_TRANS, SUB_L6

ROOT = 'C:/Users/rakan/flashcards'
WORK = os.path.join(os.environ['LOCALAPPDATA'], 'hermes', 'cache', 'scratch', 'l6tts')
os.makedirs(WORK, exist_ok=True)
FFMPEG = 'C:/Users/rakan/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg.exe'
EDGE_PY = os.path.join(ROOT, '_audit', 'edgevenv', 'Scripts', 'python.exe')

def edge_tts(text, out_mp3):
    """edge-tts 7.3.1 -> raw mp3. Returns True on success."""
    for attempt in range(3):
        r = subprocess.run(
            [EDGE_PY, '-c',
             'import edge_tts, asyncio\n'
             'async def m():\n'
             f'    t = edge_tts.Communicate({text!r}, "zh-CN-XiaoxiaoNeural")\n'
             f'    await t.save({out_mp3!r})\n'
             'asyncio.run(m())\n'],
            capture_output=True, timeout=60)
        if r.returncode == 0 and os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
            return True
        time.sleep(2)
    print('EDGE FAIL:', text[:30], r.stderr.decode()[-200:] if r.stderr else '')
    return False

def to_edge_format(src_mp3, dst_mp3):
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error',
                    '-i', src_mp3, '-ar', '24000', '-ac', '1',
                    '-codec:a', 'libmp3lame', '-b:a', '48k',
                    '-write_xing', '0', '-id3v2_version', '0',
                    '-map_metadata', '-1', dst_mp3], check=True)

# ---------- 1) collect texts ----------
jobs = []  # (kind, card_idx, text)
for i, c in enumerate(CARDS_L6):
    jobs.append(('au', i, c[0]))          # front
    if c[4]:                              # ex
        jobs.append(('ax', i, c[4]))

print('total TTS jobs:', len(jobs))
ok = 0; fail = 0
for kind, ci, text in jobs:
    raw = os.path.join(WORK, 'e_%s_%d.mp3' % (kind, ci))
    if not (os.path.exists(raw) and os.path.getsize(raw) > 500):
        if not edge_tts(text, raw):
            fail += 1
            continue
    ok += 1
    if ok % 20 == 0:
        print('  generated', ok, '/', len(jobs))
print('TTS done: ok=%d fail=%d' % (ok, fail))
assert fail == 0, 'some TTS calls failed'

# ---------- 2) re-encode ----------
for kind, ci, text in jobs:
    raw = os.path.join(WORK, 'e_%s_%d.mp3' % (kind, ci))
    dst = os.path.join(WORK, 'ee_%s_%d.mp3' % (kind, ci))
    if not os.path.exists(dst):
        to_edge_format(raw, dst)
print('re-encode done')

def b64(kind, idx):
    with io.open(os.path.join(WORK, 'ee_%s_%d.mp3' % (kind, idx)), 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')

# ---------- 3) rebuild cards ----------
def fix_front(f):
    return f.replace('صفة', '形容词')

cards_html = []
cards_data = []
for i, (front, py, ar, typ, ex, sub, glosses, _at) in enumerate(CARDS_L6):
    cat = 'word' if typ else ('gram' if sub else 'sent')
    front_fixed = fix_front(front)
    ch = {'cat': cat, 'front': front_fixed, 'py': py, 'ar': ar}
    if typ: ch['type'] = typ
    ch['ex'] = ex
    ch['au'] = 'data:audio/mp3;base64,' + b64('au', i)
    if ex:
        ch['ax'] = 'data:audio/mp3;base64,' + b64('ax', i)
    if sub: ch['sub'] = sub
    cards_html.append(ch)
    c = {'cat': cat, 'front': front_fixed, 'py': py, 'ar': ar}
    if typ: c['type'] = typ
    c['ex'] = ex
    if sub: c['sub'] = sub
    trans = {'en': glosses['en'], 'zh': glosses['zh'], 'vi': glosses['vi'],
             'id': glosses['id'], 'es': glosses['es'], 'fr': glosses['fr']}
    c['trans'] = trans
    if typ: c['trans_type'] = TYPE_SUB_TRANS.get(typ, {})
    if sub: c['trans_sub'] = SUB_L6.get(sub, {})
    cards_data.append(c)

print('cards_html:', len(cards_html), '| with ax:', sum(1 for c in cards_html if 'ax' in c))

# ---------- 4) rebuild lesson6 HTML ----------
tpl = io.open(os.path.join(ROOT, 'lesson1-flashcards.html'), encoding='utf-8').read()
tpl = tpl.replace('<title>درس · 田芳去哪儿了 · بطاقات استذكار</title>',
                  '<title>درس · 我比你更喜欢音乐 · بطاقات استذكار</title>')
tpl = tpl.replace('汉语教程 · 第三版 · 第二册上 · <b>第一课</b>',
                  '汉语教程 · 第三版 · 第二册上 · <b>第六课</b>')
tpl = tpl.replace('<h1>田芳去哪儿了</h1>', '<h1>我比你更喜欢音乐</h1>')
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
tpl = tpl.replace("const LESSON_ID = 'l1';", "const LESSON_ID = 'l6';")
io.open(os.path.join(ROOT, 'lesson6-flashcards.html'), 'w', encoding='utf-8').write(tpl)
print('lesson6-flashcards.html written:', len(tpl), 'bytes')

# ---------- 5) update data.js ----------
s = io.open(os.path.join(ROOT, 'data.js'), encoding='utf-8').read()
i = s.find('cards.l6 = [')
b = i + s[i:].index('[')
depth = 0; k = b
while k < len(s):
    if s[k] == '[': depth += 1
    elif s[k] == ']':
        depth -= 1
        if depth == 0: break
    k += 1
l6_arr = json.dumps(cards_data, ensure_ascii=False)
s = s[:b] + l6_arr + s[k+1:]
io.open(os.path.join(ROOT, 'data.js'), 'w', encoding='utf-8').write(s)
print('data.js updated')
print('DONE')
