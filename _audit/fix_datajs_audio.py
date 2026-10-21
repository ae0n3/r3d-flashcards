# -*- coding: utf-8 -*-
"""Fix data.js: add au/ax audio data URIs to cards for lessons l7..l12.
The audio files already exist in the WORK dir. This script only updates
data.js so the app can load the audio for all lessons."""
import io, os, sys, json, re, base64, subprocess, time

ROOT = 'C:/Users/rakan/flashcards'
WORK = os.path.join(os.environ['LOCALAPPDATA'], 'hermes', 'cache', 'scratch', 'l6tts')
FFMPEG = 'C:/Users/rakan/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg.exe'
EDGE_PY = os.path.join(ROOT, '_audit', 'edgevenv', 'Scripts', 'python.exe')

# Lessons to update
LESSONS = [(7, 'l7_data.py'), (8, 'l8_data.py'), (9, 'l9_data.py'),
           (10, 'l10_data.py'), (11, 'l11_data.py'), (12, 'l12_data.py')]

def edge_tts(text, out_mp3):
    for _ in range(3):
        r = subprocess.run([EDGE_PY, '-c',
            'import edge_tts, asyncio\n'
            'async def m():\n'
            '    t = edge_tts.Communicate(%r, "zh-CN-XiaoxiaoNeural")\n'
            '    await t.save(%r)\n'
            'asyncio.run(m())\n' % (text, out_mp3)],
            capture_output=True, timeout=60)
        if r.returncode == 0 and os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
            return True
        time.sleep(2)
    return False

def ensure_audio(N, kind, idx, text):
    """Ensure the edge-format audio file exists for the given card."""
    src = os.path.join(WORK, 'L%d_%s_%d.mp3' % (N, kind, idx))
    dst = os.path.join(WORK, 'L%d_e%s_%d.mp3' % (N, kind, idx))
    if not (os.path.exists(dst) and os.path.getsize(dst) > 500):
        if not os.path.exists(src) or os.path.getsize(src) < 500:
            edge_tts(text, src)
        subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', src,
                        '-ar', '24000', '-ac', '1', '-codec:a', 'libmp3lame',
                        '-b:a', '48k', '-write_xing', '0', '-id3v2_version', '0',
                        '-map_metadata', '-1', dst], check=True)
    return 'data:audio/mp3;base64,' + base64.b64encode(open(dst, 'rb').read()).decode('ascii')

import subprocess, time

for N, data_file in LESSONS:
    print('=== lesson %d' % N)
    s = io.open(ROOT + '/data.js', encoding='utf-8', newline='').read()
    # import the data file
    sys.path.insert(0, ROOT + '/_audit')
    mod = __import__(data_file.replace('.py', ''))
    CARDS = getattr(mod, 'CARDS_L%d' % N)
    # find the last cards.lN array
    m = re.search(r'cards\.l%d = \[' % N, s)
    if not m:
        print('  WARNING: no cards.l%d found' % N)
        continue
    br = m.start() + len(m.group(0)) - 1  # index of '['
    depth = 0; j = br
    while j < len(s):
        if s[j] == '[': depth += 1
        elif s[j] == ']':
            depth -= 1
            if depth == 0: end = j + 1; break
        j += 1
    else:
        print('  WARNING: bracket not closed')
        continue
    # build the cards_data with au/ax
    cards_data = []
    for i, c in enumerate(CARDS):
        front, py, ar, typ, ex, sub, glosses = c[0], c[1], c[2], c[3], c[4], c[5], c[6]
        cat = 'word' if typ else ('gram' if sub else 'sent')
        d = {'cat': cat, 'front': front, 'py': py, 'ar': ar}
        if typ: d['type'] = typ
        d['ex'] = ex
        if sub: d['sub'] = sub
        d['trans'] = glosses
        if typ and typ in getattr(mod, 'TYPE_SUB_TRANS', {}): d['trans_type'] = mod.TYPE_SUB_TRANS[typ]
        if sub and sub in getattr(mod, 'SUB_L%d' % N, {}): d['trans_sub'] = getattr(mod, 'SUB_L%d' % N)[sub]
        d['au'] = ensure_audio(N, 'au', i, front)
        if ex: d['ax'] = ensure_audio(N, 'ax', i, ex)
        cards_data.append(d)
    new_data = json.dumps(cards_data, ensure_ascii=False)
    s = s[:br] + new_data + '];' + s[end:]
    io.open(ROOT + '/data.js', 'w', encoding='utf-8', newline='').write(s)
    print('  data.js updated, cards:', len(cards_data))
print('ALL DONE')
