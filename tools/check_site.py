#!/usr/bin/env python3
"""Gate for a hand-written bilingual (VI/EN) static site.

    python3 check_site.py <site-dir> [--banned word,word,...]

Five checks, each able to fail; exit 1 if any does.
  1 tags       - every element closed, nothing left open
  2 links      - every #anchor, every local href AND every local img/media src resolves
  3 pairs      - per parent element, count(lang="vi") == count(lang="en")
  4 orphans    - no Vietnamese text outside every lang subtree (would show in BOTH languages).
                 Opt out deliberately with data-i18n="neutral" on an element whose text is the
                 same in both languages (proper nouns, song titles, names); the count of such
                 blocks is reported so they stay visible instead of silently growing.
  5 banned     - no forbidden keyword (employer names, internal paths) anywhere
  6 format     - the page carries the house-format CSS block (house-format.css next to this script) verbatim;
                 every page has its own <style>, so a site-wide rule exists only if each page repeats it.
                 Pass --no-format to skip (e.g. a site that does not use the block).
Check 3 alone is NOT enough: a duplicated VI/EN pair with no lang attribute passes it.
"""
import argparse, collections, html.parser, os, re, sys

VN = re.compile(r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]', re.I)
VOID = {'meta', 'link', 'img', 'br', 'hr', 'input', 'source'}
SKIP_TEXT = {'script', 'style', 'title'}


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.hrefs = set(), []
        self.stack, self.errs = [], []
        self.pairs = collections.Counter()
        self.orphans, self.nested = [], []
        self.langdepth = self.skip = self.node = 0
        self.langstack = []
        self.neutraldepth = 0
        self.neutralstack = []
        self.neutral_blocks = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if 'id' in d:
            self.ids.add(d['id'])
        if tag == 'a' and 'href' in d:
            self.hrefs.append(d['href'])
        # an <img>/<source>/<video> whose file is missing renders as a broken box and the
        # href-only check never sees it (gap found 2026-10-25)
        if tag in ('img', 'source', 'video', 'audio', 'embed') and d.get('src'):
            self.hrefs.append(d['src'])
        lang = d.get('lang')
        tagged = tag != 'html' and lang in ('vi', 'en')
        if tagged:
            parent = self.stack[-1][1] if self.stack else 'ROOT'
            self.pairs[(parent, lang)] += 1
            if self.langstack and self.langstack[-1][0] != lang:
                self.nested.append(f'<{tag} lang={lang}> nested inside lang={self.langstack[-1][0]}')
        neutral = d.get('data-i18n') == 'neutral'
        if tag in VOID:
            return
        self.node += 1
        self.stack.append((tag, self.node))
        if neutral:
            self.neutraldepth += 1
            self.neutralstack.append(self.node)
            self.neutral_blocks += 1
        if tagged:
            self.langdepth += 1
            self.langstack.append((lang, self.node))
        if tag in SKIP_TEXT:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            t, nid = self.stack.pop()
            if self.neutralstack and self.neutralstack[-1] == nid:
                self.neutralstack.pop()
                self.neutraldepth -= 1
            if self.langstack and self.langstack[-1][1] == nid:
                self.langstack.pop()
                self.langdepth -= 1
            if t in SKIP_TEXT:
                self.skip -= 1
        else:
            self.errs.append(f'stray </{tag}> (open: {[t for t, _ in self.stack[-3:]]})')

    def handle_data(self, data):
        if self.skip or self.langdepth or self.neutraldepth:
            return
        if VN.search(data):
            txt = ' '.join(data.split())[:70]
            if txt:
                self.orphans.append(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('site')
    ap.add_argument('--banned', default='')
    ap.add_argument('--no-format', action='store_true', help='skip check 6 (house-format block)')
    args = ap.parse_args()
    root = os.path.abspath(args.site)
    banned = [w.strip().lower() for w in args.banned.split(',') if w.strip()]
    fmt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'house-format.css')
    fmt_block = None if args.no_format or not os.path.exists(fmt_file) else open(fmt_file, encoding='utf-8').read().strip()

    pages, fails = {}, 0
    for dirpath, _, names in os.walk(root):
        for n in sorted(names):
            if n.endswith('.html'):
                f = os.path.join(dirpath, n)
                p = Page()
                p.feed(open(f, encoding='utf-8').read())
                p.close()
                pages[f] = p

    if not pages:
        print(f'no .html under {root}')
        return 1

    all_ids = {f: p.ids for f, p in pages.items()}
    for f, p in sorted(pages.items()):
        rel = os.path.relpath(f, root)
        bad = []

        if p.errs or p.stack:
            bad += [f'1 tags: {e}' for e in p.errs]
            bad += [f'1 tags: never closed <{t}>' for t, _ in p.stack]

        for h in p.hrefs:
            if h.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                continue
            path, _, anch = h.partition('#')
            if not path:
                if anch not in p.ids:
                    bad.append(f'2 links: #{anch} has no such id on this page')
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(f), path))
            if not os.path.exists(target):
                bad.append(f'2 links: {h} -> missing file')
            # a fragment is an HTML anchor only on an HTML target; on a .pdf it is a PDF
            # open parameter (#toolbar=0&view=FitH) and must not be checked as an id
            elif anch and target.endswith(('.html', '.htm')) \
                    and anch not in all_ids.get(target, set()):
                bad.append(f'2 links: {h} -> no id "{anch}" in that page')

        for parent in {k[0] for k in p.pairs}:
            vi, en = p.pairs[(parent, 'vi')], p.pairs[(parent, 'en')]
            if vi != en:
                bad.append(f'3 pairs: a parent holds {vi} VI block(s) vs {en} EN block(s)'
                           ' -> one language loses content')
        bad += [f'3 pairs: {x}' for x in p.nested]
        bad += [f'4 orphan VI text (shows in BOTH languages): "{t}"' for t in p.orphans]

        low = open(f, encoding='utf-8').read().lower()
        for w in banned:
            # A plain substring test flags "decoherence" for the banned word "cohere"
            # (real false positive, 2026-10-30). For alphanumeric terms require that the
            # neighbouring characters are not letters/digits; path-like terms stay literal.
            if w.replace('_', '').isalnum():
                hit = re.search(r'(?<![a-z0-9])' + re.escape(w) + r'(?![a-z0-9])', low)
            else:
                hit = w in low
            if hit:
                bad.append(f'5 banned: the word "{w}" appears in a public page')

        if fmt_block is not None:
            raw = open(f, encoding='utf-8').read().replace('\r\n', '\n')
            if fmt_block not in raw:
                bad.append('6 format: house-format CSS block missing or edited -> run apply_format.py'
                           if '/* ==== house-format' in raw else
                           '6 format: no house-format CSS block -> run apply_format.py')

        vi_total = sum(v for k, v in p.pairs.items() if k[1] == 'vi')
        if bad:
            fails += 1
            print(f'FAIL {rel}')
            for b in bad[:20]:
                print(f'       {b}')
            if len(bad) > 20:
                print(f'       ... and {len(bad) - 20} more')
        else:
            extra = f', {p.neutral_blocks} neutral' if p.neutral_blocks else ''
            print(f'PASS {rel}  ({vi_total} bilingual pairs{extra})')

    print(f'\n{len(pages) - fails}/{len(pages)} pages PASS')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
