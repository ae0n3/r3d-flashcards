# -*- coding: utf-8 -*-
"""Regenerate lesson-6 audio to match edge-tts format exactly: MPEG2 L3, 24kHz, 48kbps CBR, mono, no ID3."""
import io, os, re, json, base64, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'hermes', 'cache', 'scratch', 'l6tts')
FFMPEG = 'C:/Users/rakan/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg.exe'

# count existing wavs
wavs = sorted([f for f in os.listdir(WORK) if re.match(r'out_\d+\.wav$', f)],
              key=lambda x: int(re.search(r'\d+', x).group()))
n = len(wavs)
print('wav files found:', n)
assert n == 58, 'expected 58 wav files, found %d' % n

# ffmpeg -> mp3 with edge-tts format: 24kHz / 48kbps CBR / mono / no ID3 / no Xing
for i in range(n):
    w = os.path.join(WORK, 'out_%d.wav' % i)
    m = os.path.join(WORK, 'new_%d.mp3' % i)
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error',
                    '-i', w,
                    '-ar', '24000', '-ac', '1',
                    '-codec:a', 'libmp3lame', '-b:a', '48k',
                    '-write_xing', '0', '-id3v2_version', '0',
                    '-map_metadata', '-1',
                    m], check=True)
print('converted', n, 'files')

# patch lesson6-flashcards.html: replace au data URIs only
path = os.path.join(ROOT, 'lesson6-flashcards.html')
s = io.open(path, encoding='utf-8').read()
m = re.search(r'const CARDS = (\[.*\]);', s, re.S)
assert m, 'CARDS not found'
cards = json.loads(m.group(1))
print('cards in file:', len(cards))

changed = 0
for i, c in enumerate(cards):
    if 'au' not in c:
        continue
    with io.open(os.path.join(WORK, 'new_%d.mp3' % i), 'rb') as f:
        newau = 'data:audio/mp3;base64,' + base64.b64encode(f.read()).decode('ascii')
    if c['au'] != newau:
        c['au'] = newau
        changed += 1

new_cards_js = 'const CARDS = ' + json.dumps(cards, ensure_ascii=False, separators=(',', ':'))
s = s[:m.start()] + new_cards_js + s[m.end():]
io.open(path, 'w', encoding='utf-8').write(s)
print('au fields replaced:', changed, '| file size:', len(s))
