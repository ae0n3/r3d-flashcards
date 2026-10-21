# -*- coding: utf-8 -*-
"""Build Lesson 6 (l6): TTS audio via SAPI Huihui + ffmpeg -> lesson HTML + data.js update."""
import io, os, re, json, base64, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l6_data import CARDS_L6, TYPE_SUB_TRANS, SUB_L6

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'hermes', 'cache', 'scratch', 'l6tts')
os.makedirs(WORK, exist_ok=True)

# ---------- 1) audio texts ----------
texts = [c[7] for c in CARDS_L6]
with io.open(os.path.join(WORK, 'texts.txt'), 'w', encoding='utf-8') as f:
    for t in texts:
        f.write(t.replace('\n', ' ') + '\n')
print('cards:', len(CARDS_L6), '| audio texts:', len(texts))

# ---------- 2) SAPI batch TTS ----------
ps = os.path.join(WORK, 'tts.ps1')
with io.open(ps, 'w', encoding='utf-8') as f:
    f.write("""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Huihui Desktop')
$lines = Get-Content '%s' -Encoding UTF8
$i = 0
foreach ($t in $lines) {
  if ($t.Trim().Length -gt 0) {
    $out = Join-Path '%s' ("out_" + $i + ".wav")
    $synth.SetOutputToWaveFile($out)
    $synth.Speak($t.Trim())
  }
  $i++
}
$synth.Dispose()
Write-Output "TTS_DONE $i"
""" % (os.path.join(WORK, 'texts.txt'), WORK))
if not all(os.path.exists(os.path.join(WORK, 'out_%d.wav' % i)) for i in range(len(texts))):
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps], capture_output=True, text=True, timeout=400)
else:
    print('audio already generated, skipping TTS')
print('ps1 done')

# ---------- 3) ffmpeg wav -> mp3 ----------
FFMPEG = 'C:/Users/rakan/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg.exe'
for i in range(len(texts)):
    w = os.path.join(WORK, 'out_%d.wav' % i)
    m = os.path.join(WORK, 'out_%d.mp3' % i)
    if os.path.exists(w):
        subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', w, '-codec:a', 'libmp3lame', '-b:a', '24k', m], check=True)

def b64(idx):
    m = os.path.join(WORK, 'out_%d.mp3' % idx)
    with io.open(m, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')

# ---------- 4) build CARDS (lesson HTML: includes au) + data.js cards ----------
cards_html = []
cards_data = []
for i, (front, py, ar, typ, ex, sub, glosses, _at) in enumerate(CARDS_L6):
    cat = 'word' if typ else ('gram' if sub else 'sent')
    aub64 = b64(i)
    # lesson HTML card (with au)
    ch = {'cat': cat, 'front': front, 'py': py, 'ar': ar}
    if typ: ch['type'] = typ
    ch['ex'] = ex
    ch['au'] = 'data:audio/mp3;base64,' + aub64
    if sub: ch['sub'] = sub
    cards_html.append(ch)
    # data.js card (trans + trans_type + trans_sub, no au)
    c = {'cat': cat, 'front': front, 'py': py, 'ar': ar}
    if typ: c['type'] = typ
    c['ex'] = ex
    if sub: c['sub'] = sub
    trans = {'en': glosses['en'], 'zh': glosses['zh'], 'vi': glosses['vi'], 'id': glosses['id'], 'es': glosses['es'], 'fr': glosses['fr']}
    c['trans'] = trans
    if typ:
        c['trans_type'] = TYPE_SUB_TRANS.get(typ, {})
    if sub:
        c['trans_sub'] = SUB_L6.get(sub, {})
    cards_data.append(c)

CARDS_JS = 'const CARDS = ' + json.dumps(cards_html, ensure_ascii=False, separators=(',', ':'))
# NOTE: original file uses JSON-ish object with double-quoted keys; match that.

print('cards_html:', len(cards_html), '| cards_data:', len(cards_data))

# ---------- 5) build lesson6-flashcards.html from lesson1 template ----------
tpl = io.open(os.path.join(ROOT, 'lesson1-flashcards.html'), encoding='utf-8').read()
# replace title
tpl = tpl.replace('<title>درس · 田芳去哪儿了 · بطاقات استذكار</title>',
                  '<title>درس · 我比你更喜欢音乐 · بطاقات استذكار</title>')
# replace lesson header
tpl = tpl.replace('汉语教程 · 第三版 · 第二册上 · <b>第一课</b>',
                  '汉语教程 · 第三版 · 第二册上 · <b>第六课</b>')
tpl = tpl.replace('<h1>田芳去哪儿了</h1>', '<h1>我比你更喜欢音乐</h1>')
# replace CARDS array (the single line starting with 'const CARDS = [')
tpl = re.sub(r'const CARDS = \[.*?\];', lambda m: CARDS_JS + ';', tpl, count=1, flags=re.S)
# replace LESSON_ID
tpl = tpl.replace("const LESSON_ID = 'l1';", "const LESSON_ID = 'l6';")
# cache-bump common.js v7 -> v8 (this file and all others later)
tpl = tpl.replace('common.js?v=7', 'common.js?v=8')
io.open(os.path.join(ROOT, 'lesson6-flashcards.html'), 'w', encoding='utf-8').write(tpl)
print('lesson6-flashcards.html written:', len(tpl), 'bytes')

# ---------- 6) patch data.js: add cards.l6 + lessons entry ----------
s = io.open(os.path.join(ROOT, 'data.js'), encoding='utf-8').read()
# 6a) append cards.l6 after the last cards.l5 = [...];
l5_start = s.find('cards.l5 = [')
b = l5_start + s[l5_start:].index('[')
depth = 0; i = b
while i < len(s):
    if s[i] == '[': depth += 1
    elif s[i] == ']':
        depth -= 1
        if depth == 0: break
    i += 1
end = i + 1 + 1  # include '];'
l6_arr = json.dumps(cards_data, ensure_ascii=False)
l6_line = '\ncards.l6 = ' + l6_arr + ';'
# insert right after the l5 statement's ';'
semi = s.index(';', i)
s = s[:semi+1] + l6_line + s[semi+1:]
# 6b) register lesson in lessons array
old_le = "{ id: 'l5', num: '第五课', title: '我来了两个多月了', file: 'lesson5-flashcards.html' }"
new_le = old_le + ",\n    { id: 'l6', num: '第六课', title: '我比你更喜欢音乐', file: 'lesson6-flashcards.html' }"
if old_le in s:
    s = s.replace(old_le, new_le)
    print('lessons registry updated')
else:
    print('WARNING: lesson registry anchor not found')
io.open(os.path.join(ROOT, 'data.js'), 'w', encoding='utf-8').write(s)
print('data.js updated')

# ---------- 7) bump cache-bust on all pages ----------
import glob
for f in glob.glob(os.path.join(ROOT, '*.html')):
    t = io.open(f, encoding='utf-8').read()
    if 'common.js?v=7' in t:
        t = t.replace('common.js?v=7', 'common.js?v=8')
        io.open(f, 'w', encoding='utf-8').write(t)
        print('bumped:', os.path.basename(f))
