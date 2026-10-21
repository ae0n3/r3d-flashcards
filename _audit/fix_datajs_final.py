import re, json

# Read the corrupted data.js
with open('data.js', encoding='utf-8', newline='') as f:
    s = f.read()

# The build script added '];' each time without removing the old one
# So each cards.lN line ends with ']];];];];' instead of '];'
# Fix: for each cards.lN line, find the matching ']' and remove extra ']' after it

lines = s.split('\n')
fixed = 0
for i, line in enumerate(lines):
    if 'D.cards.l' in line and ' = [' in line:
        # Find the matching ']' using bracket depth (ignoring strings)
        in_str = False
        escape = False
        depth = 0
        bracket_pos = None
        for j, ch in enumerate(line):
            if escape:
                escape = False
                continue
            if ch == '\\' and in_str:
                escape = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    bracket_pos = j
                    break
        
        if bracket_pos:
            # Find the matching ']' - everything after it until ';' is extra
            # The line should end with '];'
            semi_pos = line.find(';', bracket_pos)
            if semi_pos != -1:
                # Remove extra ']' between bracket_pos and semi_pos
                between = line[bracket_pos+1:semi_pos]
                if ']' in between:
                    between_fixed = between.replace(']', '')
                    line = line[:bracket_pos+1] + between_fixed + line[semi_pos:]
                    fixed += 1
        lines[i] = line

s = '\n'.join(lines)
with open('data.js', 'w', encoding='utf-8', newline='') as f:
    f.write(s)

print(f'Fixed {fixed} lines')
print(f'Size: {len(s)} bytes')
