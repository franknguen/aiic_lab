# AIIC Lab — website

Website of the **AI & Intelligent Communication (AIIC) Lab.**, Prof. Sunghwan Kim,
Department of Artificial Intelligence and Information Technology, Sejong University (Seoul, Korea).

Static HTML, no framework, no build step: open `index.html` and it runs. Bilingual **English / Vietnamese**,
switched with the **EN | VI** buttons in the header (English is the default; the choice is remembered in the
browser). The content is a complete transcription of the lab's previous site on Google Sites
(<https://sites.google.com/site/nodoubt09/lab-information>) as of 1 Nov 2026, laid out in the house style of
[ChiU·SoC](https://github.com/franknguen/frank.github.io).

## Layout

```
index.html                         home: lab intro · research fields · current members · publications · join us · contact
pages/next-generation-communications.html   research field (NOMA / RSMA / RIS / massive MIMO)
pages/dna-storage.html             research field (ECC, constrained codes and LDPC for DNA storage)
pages/members.html                 professor · Ph.D. students · MS students · alumni (doctors, masters)
pages/journal-papers.html          158 international journal papers, by year    (generated)
pages/conference-papers.html       36 international conference papers, by year  (generated)
pages/application.html             benefits · application website · English-certificate rule · department
tools/publications.json            the publication data (numbered as on the original site)
tools/build_publications.py        regenerates the two publication pages and the home-page stats / latest-5
tools/check_site.py                the gate: tags, links, bilingual pairs, orphan text, banned words, house format
tools/house-format.css             the typography block every page carries verbatim
tools/apply_format.py              inserts / refreshes that block on every page
```

Each page is self-contained (its own `<style>`), so there is nothing to compile and any page can be opened alone.

## Editing

### Text

Every sentence a reader reads exists twice, tagged with `lang`:

```html
<p lang="en">The English version…</p>
<p lang="vi">Bản tiếng Việt…</p>
<span lang="en">short</span><span lang="vi">ngắn</span>
```

CSS shows only the selected language. Rules:

- each `lang="en"` block needs exactly one `lang="vi"` twin under the same parent, or the text vanishes in one language;
- language-neutral content (names, dates, citations, e-mail addresses, CV lines) is left **untagged**;
- a Vietnamese string outside every `lang` block is an error (it would show in both languages) — the gate catches it.

### Members

`pages/members.html` holds one `<div class="card">` per person: a role line, the name, the CV lines, then research /
hobby / e-mail / links. Copy a card to add a member; move the card between the *Ph.D. students*, *MS students*,
*Alumni — doctors* and *Alumni — masters* groups when someone graduates. The four current students also appear as
short cards on `index.html` (section *Members*) — update both.

**Photos.** The previous site's photos cannot be downloaded by a script, so cards show initials. To add a photo, save
it as `assets/members/<first-last>.jpg` (square, ~400 px) and replace the card's
`<div class="avatar" aria-hidden="true">XY</div>` with
`<img class="avatar" src="../assets/members/<first-last>.jpg" alt="<Name>">`
(the `.avatar` class already sizes and rounds it). The gate checks that the file exists.

### Publications

Do **not** edit the lists in the HTML by hand. Add the entry to `tools/publications.json` — two arrays, `journal` and
`conference`, each a list of `[number, citation]` with the numbering of the original site (newest = highest) — then:

```bash
python3 tools/build_publications.py          # rewrites the generated blocks in place
python3 tools/build_publications.py --check  # CI-style: exit 1 if a page is stale
```

It regenerates the year-grouped lists in both publication pages, the five newest journal papers and the counters on
the home page. Everything outside the `<!-- PUBS -->`, `<!-- LATEST -->` and `<!-- STATS -->` markers is untouched.
The year of an entry is the last four-digit year in its citation.

### Research figures

The figures of the two research pages (massive-MIMO system and results, DNA-storage comparison, LLR system model
and reading cost) are linked to the original pages rather than copied, for the same reason as the photos. To host
them, put the images in `assets/figures/` and replace the `.figure-note` box with
`<figure><img src="../assets/figures/<name>.png" alt="…"><figcaption>…</figcaption></figure>`.

## Checking before publishing

```bash
python3 tools/apply_format.py .                       # house typography block on every page (idempotent)
python3 tools/build_publications.py --check           # publication pages match the data
python3 tools/check_site.py . --banned '/home/frank'  # 7/7 pages PASS expected
```

`check_site.py` fails (exit 1) on an unclosed tag, a dead `#anchor` or local file, an unequal number of EN/VI
blocks under one parent, Vietnamese text outside every `lang` block, a banned word (use it for internal paths and
anything that must never reach the public page), or a page whose house-format block differs from
`tools/house-format.css`. It was proved on 1 Nov 2026 by seeding five such defects on a copy: 5/5 caught.

To change the typography site-wide, edit `tools/house-format.css`, run `apply_format.py`, run the gate.

## Publishing

GitHub Pages from the `main` branch, root folder. No action is needed beyond pushing: there are no dependencies
and no build. External fonts (Inter) load from Google Fonts; the page falls back to Arial offline.

## Differences from the Google Sites original

- Same content, reorganised: one home page with sections, detail pages for the two research fields, one members
  page with all groups, two publication pages grouped by year with the original numbering kept.
- Added: a Vietnamese edition of every sentence, a short "in plain words" paragraph on each research page, a
  practical "what to put in your first email" note on the application page (marked as added), the year span and
  counters.
- Fixed obvious typos of the original (certificate, candidates, Click here, design; the duplicated author in
  conference paper [34]; glued author names in journal paper [153]; "Kyounggi" → Kyonggi University).
- Two alumni entries whose current position on the original was unclear or named a private employer are written
  generically ("Post-Doc", "Digital IC / SoC design engineer, Korea", "Researcher in a Korean company").
- Photos and figures: linked, not copied (see above).
