# NIX Gymnastics — website

Static site: HTML, one stylesheet, one small vanilla JS file. No framework or build tooling beyond a tiny Python script that shares the header, menu and footer across pages.

## Run it

```bash
cd site && python3 build.py          # rebuild pages from _pages/
python3 -m http.server 8417 --directory site
```

Edit page content in `_pages/*.html`, never the generated `*.html` files in `site/`. Shared header, menu, footer and phone/email live in `build.py`.

## Sitemap

| Page | Purpose |
|---|---|
| `index.html` | Hero, age-based program finder, why NIX (Coach Nikolai), team teaser, parties/open gym, free-trial steps |
| `programs.html` | Every class with ages, what kids learn and schedule; sticky index (side rail on desktop, scrolling tabs on mobile) |
| `team.html` | Competitive team for boys and girls: events, training hours, how athletes join, results |
| `parties.html` | Birthday parties (how it runs, good to know) + Open Gym |
| `about.html` | Coach Nikolai, Coach Charles, facility, community |
| `contact.html` | The single inquiry form (free trial / team evaluation / birthday party / question) + contact details |

**Primary action everywhere:** "Book a free trial class" → `contact.html`. Links can preselect the form: `contact.html?type=team`, `?type=party`, `?program=ninja` (values match the program `<select>`).

## Design system (in `assets/css/styles.css`)

- **Type:** Archivo (variable width; headlines at 62% width, uppercase) + Hanken Grotesk for body text. One italic "leap" word per headline (`.leap`) echoes the leaping figure in the logo.
- **Color:** ink `#0f1512`, NIX green `#1d7f57` (from the logo), deep green `#146142` for text on light, green tint `#69d3a8` (logo hue, lighter) only on dark surfaces, warm paper `#f4f2ec`. All text pairs meet WCAG AA.
- **Motif:** the leap diagonal is used for section cuts (`.cut-top`, `.cut-bottom`), the corner notch on buttons and images (`.img--notch`) and a single tint speed line in the hero.
- **Components:** `.btn` (+ `--tint`, `--white`, `--ink`, `--lg`, `--sm`), `.link-arrow` for secondary actions, `.checks`, `.schedule`, `.facts`, `.steps`, `.path`, `.timeline`.
- **Motion:** fade-up reveals, a gentle hero image settle, a finder hover preview (mouse/trackpad only). Everything is disabled under `prefers-reduced-motion`.
- **Breakpoints:** 1100 / 1000 / 960 (nav → menu) / 860 / 760 (phone layouts + sticky action bar) / 600.

## Before launch — please confirm

These are assumptions or old content from the current site that should be checked:

1. **Free trial offer.** The whole site promises a free first class.
2. **Ages not stated on the current site:** Moms & Tots (walking to 3), Tumbling (7+), Circus Studio (6+), Self-Defense (7+).
3. **Schedules** come from the current site and may be out of date: Recreational (the Wednesday class had no age group, so it's omitted), Team summer hours, Moms & Tots Saturday 10:00, Open Gym Mon/Fri 7–8 pm. Ninja, Circus and Self-Defense say "call for current times".
4. **Circus Studio and Self-Defense descriptions** were written from research into comparable kids' programs. Confirm they match what NIX actually teaches.
5. **Hours block** on the contact page is inferred from class times.
6. **Form delivery:** the form currently shows a success message without sending anything. Connect it to a form service or email handler (see the comment in `assets/js/main.js`).
7. **Photography gaps:** all photos are from one girls' meet. Photos of boys' gymnastics, preschoolers, Ninja, parties and Circus would strengthen those sections. Circus and Self-Defense use the NIX mark as a placeholder thumbnail on mobile.
8. **Open Gym waiver:** the current site links a waiver download. Add the file and link it from `parties.html#open-gym`.
