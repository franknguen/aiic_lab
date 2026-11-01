#!/usr/bin/env python3
"""Put member photos and research figures into the pages once the image files exist.

    python3 tools/add_photos.py            # replace every slot whose file is present
    python3 tools/add_photos.py --list     # show every slot and whether its file exists

Two kinds of slot are written into the HTML by hand (or by the first-build generator):

  <div class="avatar" aria-hidden="true" data-photo="assets/members/<slug>.jpg">XY</div>
      -> <img class="avatar" src="<root>assets/members/<slug>.jpg" alt="<Name>">     when the file exists
  <!-- FIGURE: assets/figures/<name>.png | <caption> -->
      -> <figure><img src="<root>assets/figures/<name>.png" alt="<caption>"><figcaption><caption></figcaption></figure>

Paths in the slots are relative to the repo root; the script prefixes "../" for pages under pages/.
A slot whose file is missing is left as it is (initials stay visible, the figure comment stays invisible),
so the site is always complete. Idempotent: a slot already replaced is not touched.
The extension in the slot is only a suggestion: a file with the same base name and any of
.jpg .jpeg .png .webp .gif is accepted, and the <img> points at the file that exists.
Photo guidance: portrait, about 400x500 px; figures: 1000-1280 px wide.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ['index.html'] + sorted('pages/' + f for f in os.listdir(os.path.join(ROOT, 'pages')) if f.endswith('.html'))
EXTS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']


def find_file(rel):
    """Return the repo-relative path of an existing file with rel's base name and any accepted extension, or None."""
    base = os.path.splitext(rel)[0]
    for ext in [os.path.splitext(rel)[1]] + EXTS:
        if ext and os.path.exists(os.path.join(ROOT, base + ext)):
            return base + ext
    return None


AVATAR = re.compile(r'<div class="avatar" aria-hidden="true" data-photo="([^"]+)">([^<]*)</div>')
FIGURE = re.compile(r'<!-- FIGURE: ([^|]+?) \| (.*?) -->')
NAME = re.compile(r'<h3>([^<]*)</h3>')


def main(list_only=False):
    total = done = 0
    for rel in PAGES:
        path = os.path.join(ROOT, rel)
        s = open(path, encoding='utf-8').read()
        prefix = '../' if rel.startswith('pages/') else ''
        changed = 0

        def avatar(m):
            nonlocal changed
            f, initials = m.group(1), m.group(2)
            found = find_file(f)
            if list_only:
                print(f'{"ok     " if found else "missing"} {f}  ({rel})' + (f'  -> {found}' if found and found != f else ''))
                return m.group(0)
            if not found:
                return m.group(0)
            f = found
            n = NAME.search(s[m.end():m.end() + 400])
            alt = n.group(1) if n else initials
            changed += 1
            return f'<img class="avatar" src="{prefix}{f}" alt="{alt}">'

        def figure(m):
            nonlocal changed
            f, cap = m.group(1).strip(), m.group(2).strip()
            found = find_file(f)
            if list_only:
                print(f'{"ok     " if found else "missing"} {f}  ({rel})' + (f'  -> {found}' if found and found != f else ''))
                return m.group(0)
            if not found:
                return m.group(0)
            f = found
            changed += 1
            return f'<figure><img src="{prefix}{f}" alt="{cap}" loading="lazy"><figcaption>{cap}</figcaption></figure>'

        total += len(AVATAR.findall(s)) + len(FIGURE.findall(s))
        new = FIGURE.sub(figure, AVATAR.sub(avatar, s))
        if changed and not list_only:
            open(path, 'w', encoding='utf-8').write(new)
            print(f'{rel}: {changed} slot(s) filled')
        done += changed
    if not list_only:
        print(f'{done} filled, {total - done} slot(s) still waiting for a file')


if __name__ == '__main__':
    main('--list' in sys.argv[1:])
