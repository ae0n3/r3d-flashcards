# -*- coding: utf-8 -*-
"""Fix the backslash comparison line in rebuild_l6.py to use chr(92)."""
import io, ast

p = '_audit/rebuild_l6.py'
lines = io.open(p, encoding='utf-8').readlines()
BS = chr(92)  # backslash
fixed = 0
for i, l in enumerate(lines):
    if 'ch ==' in l and BS in l:
        lines[i] = '        if ch == chr(92):\n'
        fixed += 1
        print('fixed line', i + 1)
io.open(p, 'w', encoding='utf-8').writelines(lines)
ast.parse(io.open(p, encoding='utf-8').read())
print('syntax OK | fixed', fixed, 'lines')
