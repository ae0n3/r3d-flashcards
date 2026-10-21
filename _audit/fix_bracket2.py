import re, json

s = open('data.js', encoding='utf-8', newline='').read()

# Fix: each cards.lN line has extra '];' appended from multiple build runs
# We need to find the matching ']' for each array and remove extra ']' after it

lines = s.split('\n')
fixed_lines = []
for line in lines:
    if 'D.cards.l' in line and ' = [' in line:
        # Find the matching ']' using bracket depth (ignoring strings)
        in_str = False
        escape = False
        depth = 0
        bracket_pos = None
        for i, ch in enumerate(line):
            if escape:
                escape = False
                continue
            if ch == chr(92) and in_str:
                escape = True
                continue
            if ch == chr(34):
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
        
        if bracket_pos:
            # Find the last '];' or just ';' after bracket_pos
            rest = line[bracket_pos+1:]
            # Remove extra ']' characters before the final ';'
            # The rest should be just ';' or ';  ' etc.
            # Find the first ';' 
            semi_pos = rest.find(';')
            if semi_pos != -1:
                # Check if there are extra ']' between bracket_pos and semi_pos
                between = rest[:semi_pos]
                if ']' in between:
                    # Remove all ']' from between
                    new_between = between.replace(']', '')
                    line = line[:bracket_pos+1] + new_between + rest[semi_pos:]
                    print('Fixed line, removed extra ]')
        fixed_lines.append(line)
    else:
        fixed_lines.append(line)

s = '\n'.join(fixed_lines)
open('data.js', 'w', encoding='utf-8', newline='').write(s)
print('Done, size:', len(s))
