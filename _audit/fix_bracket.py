import sys
s = open('data.js', encoding='utf-8', newline='').read()
lines = s.split('\n')
line = lines[27]
bs = chr(92)
q = chr(34)
in_str = False
escape = False
depth = 0
bracket_pos = None
for i, ch in enumerate(line):
    if escape:
        escape = False
        continue
    if ch == bs and in_str:
        escape = True
        continue
    if ch == q:
        in_str = not in_str
        continue
    if in_str:
        continue
    if ch == '[':
        depth += 1
    elif ch == ']':
        depth -= 1
        if depth == 0:
            bracket_pos = i
            break
print('Matching ] at:', bracket_pos)
print('After:', repr(line[bracket_pos:bracket_pos+20]))
last_semi = line.rfind(';')
new_line = line[:bracket_pos+1] + line[last_semi:]
lines[27] = new_line
print('New ending:', repr(new_line[-30:]))
open('data.js', 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('Written')
