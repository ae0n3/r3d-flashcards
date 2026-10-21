# -*- coding: utf-8 -*-
"""Inspect lesson1 vs lesson6 card structure: ax field + translation quality."""
import io, re, json

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
    print('=' * 25, name, '| cards:', len(cards))
    print('  with au:', sum(1 for c in cards if c.get('au')))
    print('  with ax:', sum(1 for c in cards if c.get('ax')))
    print('  with ex:', sum(1 for c in cards if c.get('ex')))
    cats = {}
    for c in cards:
        cats[c['cat']] = cats.get(c['cat'], 0) + 1
    print('  categories:', cats)
    # check grammar cards' translations for non-Arabic content
    for c in cards:
        if c['cat'] == 'gram':
            tr = c.get('trans', {})
            non_ar = {k: v for k, v in tr.items() if k not in ('ar', 'zh') and v}
            # check if any non-ar/zh value looks like Arabic
            import unicodedata
            def has_arabic(t):
                return any('؀' <= ch <= 'ۿ' for ch in t)
            arabic_leak = {k: v[:40] for k, v in non_ar.items() if has_arabic(str(v))}
            if arabic_leak:
                print('  GRAM ARABIC LEAK:', c['front'][:30], '->', arabic_leak)
    # word cards: check trans values
    leaks = 0
    for c in cards:
        if c['cat'] == 'word':
            tr = c.get('trans', {})
            for k, v in tr.items():
                if k != 'ar' and isinstance(v, str) and any('؀' <= ch <= 'ۿ' for ch in v):
                    leaks += 1
                    if leaks <= 5:
                        print('  WORD ARABIC LEAK:', c['front'][:20], k, '=', v[:40])
    print('  word arabic leaks:', leaks)
