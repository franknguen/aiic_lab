# AIIC Lab — website

Website of the **AI & Intelligent Communication (AIIC) Lab**, Prof. Sunghwan Kim,
Department of Artificial Intelligence and Information Technology, Sejong University (Seoul, Korea).

Static HTML in English, no framework, no build step: open `index.html` and it runs. Each page carries its own
`<style>`, so any page can be opened alone.

## Layout

```
index.html                         home: lab intro · research fields · current members · publications · join us · contact
pages/next-generation-communications.html   research field (NOMA / RSMA / RIS / massive MIMO)
pages/dna-storage.html             research field (ECC, constrained codes and LDPC for DNA storage)
pages/members.html                 professor · Ph.D. students · MS students · alumni (doctors, masters)
pages/journal-papers.html          158 international journal papers, by year    (generated)
pages/conference-papers.html       36 international conference papers, by year  (generated)
pages/application.html             benefits · application website · English-certificate rule · department
assets/members/                    member photos  <first-last>.jpg   (see "Photos and figures")
assets/figures/                    research figures <name>.png
tools/publications.json            the publication data (numbered newest = highest)
tools/build_publications.py        regenerates the two publication pages and the home-page stats / latest-5
tools/add_photos.py                puts photos and figures into the pages once the files exist
tools/check_site.py                the gate: tags, links, stray non-English text, banned words, house format
tools/house-format.css             the typography block every page carries verbatim
tools/apply_format.py              inserts / refreshes that block on every page
```

## Editing

### Members

`pages/members.html` holds one `<div class="card">` per person: a role line, the name, the CV lines, then
research / hobby / e-mail / links. Copy a card to add a member; move the card between the *Ph.D. students*,
*MS students*, *Alumni — doctors* and *Alumni — masters* groups when someone graduates. The professor and the
current students also appear as short cards on `index.html` (section *Members*) — update both.

### Photos and figures

Every member card has a photo slot and every research page has figure slots. Until a file exists, the card shows
the person's initials and the figure slot is an invisible HTML comment, so the site is always complete.

1. Save each photo as `assets/members/<first-last>.jpg` (portrait, about 400×500 px). The exact file name
   expected for every slot is printed by:

   ```bash
   python3 tools/add_photos.py --list
   ```

2. Save research figures as `assets/figures/<name>.png` (1000–1280 px wide), names from the same listing:
   `massive-mimo-four-cell`, `massive-mimo-power`, `massive-mimo-sum-rate`, `dna-storage-comparison`,
   `dna-ldpc-system-model`, `dna-ldpc-reading-cost`.
3. Run

   ```bash
   python3 tools/add_photos.py
   ```

   It replaces each slot whose file is present with an `<img>` (photo: 96×120 rounded, top-aligned crop;
   figure: full width with its caption) and leaves the others untouched. Safe to run again at any time.

A new member card gets its slot by copying this line and changing the file name and initials:

```html
<div class="avatar" aria-hidden="true" data-photo="assets/members/first-last.jpg">FL</div>
```

A new figure gets its slot with a comment, placed where the figure should appear:

```html
<!-- FIGURE: assets/figures/my-figure.png | Caption shown under the figure -->
```

### Publications

Do **not** edit the lists in the HTML by hand. Add the entry to `tools/publications.json` — two arrays, `journal`
and `conference`, each a list of `[number, citation]` with the lab's running numbering (newest = highest) — then:

```bash
python3 tools/build_publications.py          # rewrites the generated blocks in place
python3 tools/build_publications.py --check  # exit 1 if a page is stale
```

It regenerates the year-grouped lists in both publication pages, the five newest journal papers and the counters
on the home page. Everything outside the `<!-- PUBS -->`, `<!-- LATEST -->` and `<!-- STATS -->` markers is
untouched. The year of an entry is the last four-digit year in its citation; Prof. Kim's name is highlighted.

### Text

Plain HTML. Prose is justified on every page by the house-format block; link rows and tables stay left-aligned.
To change the typography site-wide, edit `tools/house-format.css`, run `tools/apply_format.py .`, run the gate.

## Checking before publishing

```bash
python3 tools/apply_format.py .                       # house typography block on every page (idempotent)
python3 tools/build_publications.py --check           # publication pages match the data
python3 tools/add_photos.py --list                    # which photo / figure files are still missing
python3 tools/check_site.py . --banned '/home/frank'  # 7/7 pages PASS expected
```

`check_site.py` fails (exit 1) on an unclosed tag, a dead `#anchor`, a missing local file or image, stray
Vietnamese text, a banned word (use it for internal paths and anything that must never reach the public page),
or a page whose house-format block differs from `tools/house-format.css`.

## Publishing

GitHub Pages from the `main` branch, root folder. Nothing to build: push and it is live. The Inter font loads
from Google Fonts and falls back to Arial offline.
