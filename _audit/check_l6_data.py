# -*- coding: utf-8 -*-
"""Inspect l6 grammar cards in data.js — check for Arabic in other languages' trans."""
import json, io

s = io.open('data.js', encoding='utf-8').read()
i = s.find('cards.l6 = [')
b = i + s[i:].index('[')
depth = 0; k = b
while k < len(s):
    if s[k] == '[': depth += 1
    elif s[k] == ']':
        depth -= 1
        if depth == 0: break
    k += 1
cards = json.loads(s[b:k+1])
print('l6 cards in data.js:', len(cards))

def has_arabic(t):
    return any('؀' <= ch <= 'ۿ' for ch in str(t))

leaks = 0
for c in cards:
    if c['cat'] == 'gram':
        print('=' * 50)
        print('FRONT:', c['front'][:40])
        tr = c.get('trans') or {}
        for lang in ('en', 'zh', 'vi', 'id', 'es', 'fr'):
            v = tr.get(lang, '')
            flag = ' <-- ARABIC!' if has_arabic(v) else ''
            print(' ', lang.upper() + ':', str(v)[:90], flag)
        for lang in ('en', 'zh', 'vi', 'id', 'es', 'fr'):
            v = (c.get('trans_type') or {}).get(lang, '')
            if v and has_arabic(v):
                print('  trans_type', lang, 'ARABIC:', v[:60]); leaks += 1
    else:
        # word/sent: check trans values for arabic leaks too
        tr = c.get('trans') or {}
        for lang in ('en', 'zh', 'vi', 'id', 'es', 'fr'):
            v = tr.get(lang, '')
            if v and has_arabic(v):
                leaks += 1
                if leaks <= 8:
                    print('LEAK', c['cat'], c['front'][:25], lang, '=', str(v)[:60])
print('total arabic leaks:', leaks)
