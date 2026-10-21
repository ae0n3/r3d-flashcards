# -*- coding: utf-8 -*-
"""Regenerate lesson-6 audio (au + ax) via Google TTS, re-encoded to edge-tts format.
Also fixes grammar card fronts (صفة -> 形容词)."""
import io, os, re, json, base64, subprocess, sys, time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l6_data import CARDS_L6, TYPE_SUB_TRANS, SUB_L6

ROOT = 'C:/Users/rakan/flashcards'
WORK = os.path.join(os.environ['LOCALAPPDATA'], 'hermes', 'cache', 'scratch', 'l6tts')
os.makedirs(WORK, exist_ok=True)
FFMPEG = 'C:/Users/rakan/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg.exe'
CURL = 'curl'

def google_tts(text, out_mp3):
    """Google translate TTS -> mp3. Returns True on success."""
    q = urllib.parse.quote(text)
    url = 'https://translate.google.com/translate_tts?ie=UTF-8&q=%s&tl=zh-CN&client=tw-ob' % q
    for attempt in range(3):
        r = subprocess.run([CURL, '-s', '--max-time', '20', '-o', out_mp3, url],
                           capture_output=True)
        if r.returncode == 0 and os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
            return True
        time.sleep(1)
    return False

def to_edge_format(src_mp3, dst_mp3):
    """Re-encode to edge-tts format: 24kHz, 48kbps CBR, mono, LAME, no ID3."""
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error',
                    '-i', src_mp3,
                    '-ar', '24000', '-ac', '1',
                    '-codec:a', 'libmp3lame', '-b:a', '48k',
                    '-write_xing', '0', '-id3v2_version', '0',
                    '-map_metadata', '-1',
                    dst_mp3], check=True)

# ---------- 1) generate au (front) + ax (ex), indexed by card ----------
jobs = []  # (kind, card_idx, text)
for i, c in enumerate(CARDS_L6):
    jobs.append(('au', i, c[0]))         # front
    if c[4]:                            # ex
        jobs.append(('ax', i, c[4]))

print('total TTS jobs:', len(jobs))
ok = 0
fail = 0
for kind, ci, text in jobs:
    raw = os.path.join(WORK, 'g_%s_%d.mp3' % (kind, ci))
    if not (os.path.exists(raw) and os.path.getsize(raw) > 500):
        if not google_tts(text, raw):
            print('FAIL', kind, ci, text[:30])
            fail += 1
            continue
    ok += 1
    if ok % 20 == 0:
        print('  generated', ok, '/', len(jobs))
print('TTS done: ok=%d fail=%d' % (ok, fail))
assert fail == 0, 'some TTS calls failed'

# ---------- 2) re-encode to edge format ----------
for kind, ci, text in jobs:
    raw = os.path.join(WORK, 'g_%s_%d.mp3' % (kind, ci))
    dst = os.path.join(WORK, 'ge_%s_%d.mp3' % (kind, ci))
    if not os.path.exists(dst):
        to_edge_format(raw, dst)
print('re-encode done')

def b64(kind, idx):
    with io.open(os.path.join(WORK, 'ge_%s_%d.mp3' % (kind, idx)), 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')

# ---------- 3) build cards (fix grammar fronts) ----------
def fix_front(f):
    return f.replace('صفة', '形容词')

cards_html = []
cards_data = []
for i, (front, py, ar, typ, ex, sub, glosses, _at) in enumerate(CARDS_L6):
    cat = 'word' if typ else ('gram' if sub else 'sent')
    front_fixed = fix_front(front)
    au_b64 = b64('au', i)
    ch = {'cat': cat, 'front': front_fixed, 'py': py, 'ar': ar}
    if typ: ch['type'] = typ
    ch['ex'] = ex
    ch['au'] = 'data:audio/mp3;base64,' + au_b64
    if ex:
        ax_b64 = b64('ax', i)
        ch['ax'] = 'data:audio/mp3;base64,' + ax_b64
    if sub: ch['sub'] = sub
    cards_html.append(ch)
    # data.js card
    c = {'cat': cat, 'front': front_fixed, 'py': py, 'ar': ar}
    if typ: c['type'] = typ
    c['ex'] = ex
    if sub: c['sub'] = sub
    trans = {'en': glosses['en'], 'zh': glosses['zh'], 'vi': glosses['vi'],
             'id': glosses['id'], 'es': glosses['es'], 'fr': glosses['fr']}
    c['trans'] = trans
    if typ:
        c['trans_type'] = TYPE_SUB_TRANS.get(typ, {})
    if sub:
        c['trans_sub'] = SUB_L6.get(sub, {})
    cards_data.append(c)

print('cards_html:', len(cards_html), '| with ax:', sum(1 for c in cards_html if 'ax' in c))
print('cards_data:', len(cards_data))

# ---------- 4) rebuild lesson6-flashcards.html ----------
tpl = io.open(os.path.join(ROOT, 'lesson1-flashcards.html'), encoding='utf-8').read()
tpl = tpl.replace('<title>درس · 田芳去哪儿了 · بطاقات استذكار</title>',
                  '<title>درس · 我比你更喜欢音乐 · بطاقات استذكار</title>')
tpl = tpl.replace('汉语教程 · 第三版 · 第二册上 · <b>第一课</b>',
                  '汉语教程 · 第三版 · 第二册上 · <b>第六课</b>')
tpl = tpl.replace('<h1>田芳去哪儿了</h1>', '<h1>我比你更喜欢音乐</h1>')
CARDS_JS = 'const CARDS = ' + json.dumps(cards_html, ensure_ascii=False, separators=(',', ':'))
print('CARDS_JS len:', len(CARDS_JS), '| first front in JS:', cards_html[0]['front'])
# replace the CARDS array with a deterministic bracket-depth scan (no regex backslash issues)
ci = tpl.find('const CARDS = ')
cs = ci + len('const CARDS = ')
depth = 0; i = cs; in_str = False
while i < len(tpl):
    ch = tpl[i]
    if in_str:
        if ch == chr(92):
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
print('scanned CARDS end at', i, '| char there:', repr(tpl[i]) if i < len(tpl) else 'EOF')
tpl = tpl[:ci] + CARDS_JS + ';' + tpl[i+2:]
print('after replace, has 喂:', '喂' in tpl, '| has 变化:', '变化' in tpl, '| tpl len:', len(tpl))
tpl = tpl.replace("const LESSON_ID = 'l1';", "const LESSON_ID = 'l6';")
io.open(os.path.join(ROOT, 'lesson6-flashcards.html'), 'w', encoding='utf-8').write(tpl)
print('lesson6-flashcards.html written:', len(tpl), 'bytes')

# ---------- 5) update data.js cards.l6 ----------
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
