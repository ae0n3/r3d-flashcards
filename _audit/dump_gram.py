# -*- coding: utf-8 -*-
"""Dump full grammar card JSON from lesson1 and lesson6 HTML."""
import json, io

def extract_cards(path):
    s = io.open(path, encoding='utf-8').read()
    start = s.find('const CARDS = ')
    st = start + len('const CARDS = ')
    depth = 0; i = st; in_str = False
    while i < len(s):
        ch = s[i]
        if in_str:
            if ch == '\\':
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
    return json.loads(s[st:i+1])

for name in ('lesson1-flashcards.html', 'lesson6-flashcards.html'):
    cards = extract_cards(name)
    grams = [c for c in cards if c['cat'] == 'gram']
    print('=' * 30, name, '| gram cards:', len(grams))
    c = grams[0]
    c2 = dict(c)
    for key in list(c2.keys()):
        if c2[key] and str(c2[key]).startswith('data:audio'):
            c2[key] = c2[key][:40] + '...'
    print(json.dumps(c2, ensure_ascii=False, indent=1)[:1500])
    print()
