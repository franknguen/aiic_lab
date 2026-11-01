#!/usr/bin/env python3
"""Put the house-format CSS block (house-format.css, next to this script) into every page of the site.

    python3 apply_format.py <site-dir>

Every page carries its own <style>, so a site-wide typography rule has to be written into each one. The block is
delimited by its first and last comment lines; a page that already has one gets it REPLACED (so an edit to
house-format.css propagates by re-running this), a page without one gets it inserted just before the first </style>.
Idempotent: a second run changes nothing. check_site.py (check 6) then fails any page whose block differs.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BLOCK = open(os.path.join(HERE, 'house-format.css'), encoding='utf-8').read().strip()
START, END = '/* ==== house-format', '/* ==== /house-format ==== */'
assert BLOCK.startswith(START) and BLOCK.endswith(END), 'house-format.css must begin and end with the marker comments'
RE_BLOCK = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)


def main():
    root = os.path.abspath(sys.argv[1])
    added = replaced = same = 0
    for dirpath, _, names in os.walk(root):
        for n in sorted(names):
            if not n.endswith('.html'):
                continue
            f = os.path.join(dirpath, n)
            s = open(f, encoding='utf-8').read()
            if RE_BLOCK.search(s):
                new = RE_BLOCK.sub(lambda m: BLOCK, s, count=1)
                if new == s:
                    same += 1; continue
                replaced += 1
            else:
                i = s.find('</style>')
                if i < 0:
                    print(f'SKIP {os.path.relpath(f, root)}: no <style>'); continue
                new = s[:i].rstrip('\n') + '\n' + BLOCK + '\n' + s[i:]
                added += 1
            open(f, 'w', encoding='utf-8').write(new)
            print(f'{"added to" if not RE_BLOCK.search(s) else "replaced in"} {os.path.relpath(f, root)}')
    print(f'house-format: {added} added, {replaced} replaced, {same} already current')


if __name__ == '__main__':
    main()
