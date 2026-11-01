#!/usr/bin/env python3
"""Regenerate the publication lists of the AIIC Lab site from tools/publications.json.

    python3 tools/build_publications.py            # rewrite the generated blocks in place
    python3 tools/build_publications.py --check    # exit 1 if any page is out of date

publications.json holds two arrays, "journal" and "conference", each a list of
[number, citation] pairs numbered exactly as on the original lab site (newest = highest).
To add a paper: append [N+1, "Authors, \"Title,\" venue, vol., pp., Mon. YYYY."] to the
matching array and run this script. It rewrites, in place, the text between

    <!-- PUBS:START ... -->   ...   <!-- PUBS:END -->      in pages/journal-papers.html
                                                           and pages/conference-papers.html
    <!-- LATEST:START -->     ...   <!-- LATEST:END -->    in index.html (five newest journal papers)
    <!-- STATS:START -->      ...   <!-- STATS:END -->     in index.html (paper counts and year span)

Everything outside the markers is hand-written HTML and is left alone.
The year of an entry is the last 4-digit year in its citation. Prof. Kim's name is highlighted.
Run tools/check_site.py afterwards.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'tools', 'publications.json')
PI = 'Sunghwan Kim'


def bi(en, vi):
    return f'<span lang="en">{en}</span><span lang="vi">{vi}</span>'


def year_of(t):
    y = re.findall(r'(?:19|20)\d\d', t)
    return int(y[-1]) if y else 0


def entry_li(n, t):
    t = t.replace('\u201c', '"').replace('\u201d', '"')
    m = re.match(r'^(.*?)"(.*?)"\s*,?\s*(.*)$', t)
    if m:
        authors, title, rest = (html.escape(x.strip()) for x in m.groups())
        body = f'{authors.rstrip(",")}, <span class="t">"{title.rstrip(",")},"</span> {rest}'
    else:
        body = html.escape(t)
    body = body.replace(PI, f'<span class="pi">{PI}</span>')
    return f'<li><span class="n">[{n}]</span>{body}</li>'


def list_html(items):
    items = sorted(items, key=lambda x: (-year_of(x[1]), -x[0]))
    out, cur = [], None
    for n, t in items:
        y = year_of(t)
        if y != cur:
            if cur is not None:
                out.append('</ol>')
            out.append(f'<h2 class="pub-year" id="y{y}">{y}</h2><ol class="pub-list">')
            cur = y
        out.append(entry_li(n, t))
    out.append('</ol>')
    return '\n'.join(out)


def replace_block(page, start_pat, end_tag, new_inner):
    s = open(page, encoding='utf-8').read()
    m = re.search(start_pat, s)
    if not m:
        sys.exit(f'{page}: marker {start_pat!r} not found')
    e = s.index(end_tag, m.end())
    new = s[:m.end()] + '\n' + new_inner + '\n' + s[e:]
    return s, new


def main(check=False):
    d = json.load(open(DATA, encoding='utf-8'))
    J, C = d['journal'], d['conference']
    for arr, name in ((J, 'journal'), (C, 'conference')):
        nums = [n for n, _ in arr]
        if len(set(nums)) != len(nums):
            sys.exit(f'{name}: duplicate numbers {sorted(n for n in set(nums) if nums.count(n) > 1)}')
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if missing:
            print(f'warning: {name} numbering has gaps: {missing}')
    latest = sorted(J, key=lambda x: -x[0])[:5]
    y0 = min(year_of(t) for _, t in J + C)
    y1 = max(year_of(t) for _, t in J + C)
    stats = (f'  <div class="stat"><b>{len(J)}</b><span>{bi("international journal papers", "bài báo tạp chí quốc tế")}</span></div>\n'
             f'  <div class="stat"><b>{len(C)}</b><span>{bi("international conference papers", "bài báo hội nghị quốc tế")}</span></div>\n'
             f'  <div class="stat"><b>{y0}–{y1}</b><span>{bi("years covered", "giai đoạn")}</span></div>')
    jobs = [
        (os.path.join(ROOT, 'pages', 'journal-papers.html'), r'<!-- PUBS:START[^>]*-->', '<!-- PUBS:END -->', list_html(J)),
        (os.path.join(ROOT, 'pages', 'conference-papers.html'), r'<!-- PUBS:START[^>]*-->', '<!-- PUBS:END -->', list_html(C)),
        (os.path.join(ROOT, 'index.html'), r'<!-- LATEST:START -->', '<!-- LATEST:END -->',
         '<ol class="pub-list">\n' + '\n'.join(entry_li(n, t) for n, t in latest) + '\n</ol>'),
        (os.path.join(ROOT, 'index.html'), r'<!-- STATS:START -->', '<!-- STATS:END -->', stats),
    ]
    stale = 0
    for page, sp, et, inner in jobs:
        old, new = replace_block(page, sp, et, inner)
        if old != new:
            stale += 1
            if check:
                print(f'OUT OF DATE: {os.path.relpath(page, ROOT)}')
            else:
                open(page, 'w', encoding='utf-8').write(new)
                print(f'updated  {os.path.relpath(page, ROOT)}')
        else:
            print(f'current  {os.path.relpath(page, ROOT)}')
    print(f'{len(J)} journal + {len(C)} conference papers, {y0}-{y1}')
    if check and stale:
        sys.exit(1)


if __name__ == '__main__':
    main(check='--check' in sys.argv[1:])
