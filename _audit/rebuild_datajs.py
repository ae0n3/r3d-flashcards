import re, json, io

ROOT = 'C:/Users/rakan/flashcards'

# Read the original data.js from git (has lessons 1-6 without audio)
import subprocess
orig = subprocess.run(['git', 'show', 'HEAD:data.js'], capture_output=True, text=True, cwd=ROOT).stdout

# Extract lessons 1-6 from original
orig_lessons = {}
for n in range(1, 7):
    m = re.search(r'cards\.l%d = \[' % n, orig)
    if not m:
        continue
    br = m.start() + len(m.group(0)) - 1
    depth = 0
    j = br
    while j < len(orig):
        if orig[j] == '[': depth += 1
        elif orig[j] == ']':
            depth -= 1
            if depth == 0: end = j + 1; break
        j += 1
    orig_lessons[n] = json.loads(orig[br:end])

# Extract lessons 7-12 from HTML files (they have correct JSON with audio)
html_lessons = {}
for n in range(7, 13):
    html_file = ROOT + '/lesson%d-flashcards.html' % n
    try:
        s = io.open(html_file, encoding='utf-8').read()
    except:
        continue
    # Find const CARDS = [...];
    m = re.search(r'const CARDS = (\[.*?\]);', s, re.DOTALL)
    if not m:
        continue
    cards = json.loads(m.group(1))
    html_lessons[n] = cards

# Build new data.js
# Start with the original data.js structure but replace the cards arrays
# The original has: D.cards.l1 = [...]; D.cards.l2 = [...]; ... D.cards.l6 = [...];
# We need to add D.cards.l7 = [...]; ... D.cards.l12 = [...];

# Get the lessons array from original
lessons_m = re.search(r'const lessons = \[(.*?)\];', orig, re.DOTALL)
lessons_arr = lessons_m.group(1) if lessons_m else ''

# Build new cards arrays
new_cards = []
for n in range(1, 13):
    if n in orig_lessons:
        new_cards.append('D.cards.l%d = %s;' % (n, json.dumps(orig_lessons[n], ensure_ascii=False)))
    elif n in html_lessons:
        new_cards.append('D.cards.l%d = %s;' % (n, json.dumps(html_lessons[n], ensure_ascii=False)))

# Build the new data.js
# Keep the original structure but replace the cards section
# Find the cards section in original - from 'D.cards.l1' to the end of cards.l6
cards_start = orig.find('D.cards.l1 = [')
# Find the end of cards.l6 array (the last one in original)
cards6_m = re.search(r'cards\.l6 = \[', orig)
if cards6_m:
    br = cards6_m.start() + len(cards6_m.group(0)) - 1
    depth = 0
    j = br
    while j < len(orig):
        if orig[j] == '[': depth += 1
        elif orig[j] == ']':
            depth -= 1
            if depth == 0: end = j + 1; break
        j += 1
    # Find the ';' after the array
    semi = orig.find(';', end)
    if semi != -1:
        cards_end = semi + 1
    else:
        cards_end = end
else:
    cards_end = orig.find('};', cards_start) + 2

new_cards_section = '\n'.join(new_cards)
new_data = orig[:cards_start] + new_cards_section + orig[cards_end:]

# Write the new data.js
io.open(ROOT + '/data.js', 'w', encoding='utf-8', newline='').write(new_data)
print('Rebuilt data.js, size:', len(new_data))
print('Lessons:', list(orig_lessons.keys()) + list(html_lessons.keys()))
