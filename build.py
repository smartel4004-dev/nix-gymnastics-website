#!/usr/bin/env python3
"""Assemble the static NIX Gymnastics pages.

Each file in _pages/ starts with a small header block:
    title: Page title
    description: Meta description
    nav: programs | team | parties | about | contact | home
    bar: yes | no          (mobile sticky "Book a free trial" bar)
    ---
followed by the page's <main> content. Shared partials (header, menu,
footer) live in this file so navigation stays identical on every page.

Team meets and results/news live in _data/meets.json and _data/news.json.
The build renders them into pages ({{meets_*}}, {{news_feed}} placeholders)
and writes calendar files to assets/cal/.

Run:  python3 build.py
"""
import json
import re
from datetime import date, timedelta
from html import escape
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).parent
PAGES = ROOT / "_pages"
DATA = ROOT / "_data"
CAL = ROOT / "assets" / "cal"
REG_FORM = "assets/docs/nix-registration-form.pdf"

PHONE = "(603) 878-3051"
PHONE_HREF = "tel:+16038783051"
EMAIL = "obrovin@nixgym.com"
SOCIAL = [
    ("Facebook", "https://www.facebook.com/NIX-GYM-LLC-100731539967950/",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.5V4.4c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.8v2.4H8v3h2.6V21h2.9Z"/></svg>'),
    ("YouTube", "https://www.youtube.com/channel/UCjNNc5FpwyWCU7XXIew-84g",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8ZM10 15V9l5.2 3L10 15Z"/></svg>'),
]

ARROW = '<svg class="arrow" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M3 10h13m-5-5 5 5-5 5" stroke="currentColor" stroke-width="2.2" stroke-linecap="square"/></svg>'
PHONE_ICON = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'
CHECK_ICON = '<svg viewBox="0 0 56 56" fill="none" aria-hidden="true"><circle cx="28" cy="28" r="26" stroke="currentColor" stroke-width="3"/><path d="m17 29 7 7 15-16" stroke="currentColor" stroke-width="3.5" stroke-linecap="square"/></svg>'

NAV = [
    ("programs", "programs.html", "Programs", "Classes by age"),
    ("team", "team.html", "Competitive Team", "Boys & girls", [
        ("team.html", "Team overview", "Training, events and how athletes join"),
        ("meets.html", "Meet calendar", "Upcoming meets, directions, add to calendar"),
        ("meets.html#results", "Results & news", "Scores and team milestones"),
        ("galleries.html", "Photo galleries", "Meet photos by season and team"),
    ]),
    ("parties", "parties.html", "Parties & Open Gym", "Weekends & drop-in"),
    ("about", "about.html", "About", "Coaches & gym"),
    ("contact", "contact.html", "Contact", "Visit or call"),
]


CHEVRON = '<svg viewBox="0 0 12 8" fill="none" aria-hidden="true"><path d="m1 1.5 5 5 5-5" stroke="currentColor" stroke-width="2"/></svg>'


def nav_links(current, page, mobile=False):
    out = []
    items = NAV if mobile else NAV[:4]
    for key, href, label, sub, *children in items:
        children = children[0] if children else []
        cur = ' aria-current="page"' if href == page else ""
        section = " is-section" if key == current else ""
        li = ' class="is-section"' if section else ""
        if mobile:
            subs = "".join(
                f'<li><a href="{h}"{" aria-current=\"page\"" if h == page else ""}>{escape(t)}</a></li>'
                for h, t, _ in children if h != href)
            subs = f'<ul class="menu-sub">{subs}</ul>' if subs else ""
            out.append(f'<li{li}><a href="{href}"{cur}>{label} <small>{sub}</small></a>{subs}</li>')
        elif children:
            links = "\n              ".join(
                f'<li><a href="{h}"{" aria-current=\"page\"" if h == page else ""}>{escape(t)}<small>{escape(d)}</small></a></li>'
                for h, t, d in children)
            out.append(f"""<li class="has-sub{section}" data-subnav>
            <a href="{href}"{cur}>{label}</a>
            <button class="sub-toggle" type="button" aria-expanded="false" aria-controls="sub-{key}">{CHEVRON}<span class="visually-hidden">{label} pages</span></button>
            <div class="sub" id="sub-{key}">
              <ul>
              {links}
              </ul>
            </div>
          </li>""")
        else:
            out.append(f'<li{li}><a href="{href}"{cur}>{label}</a></li>')
    return "\n          ".join(out)


def head(title, description, extra=""):
    full = "NIX Gymnastics" if title == "home" else f"{title} | NIX Gymnastics"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full}</title>
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#0f1512">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,400..900;1,62..125,400..900&family=Hanken+Grotesk:ital,wght@0,400..700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/styles.css">{extra}
</head>"""


def header(current, page):
    return f"""
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="index.html" aria-label="NIX Gymnastics home"><img src="assets/img/nix-logo-rev.svg" alt="NIX Gymnastics" width="168" height="57"></a>
    <nav class="nav" aria-label="Main">
      <ul class="nav-list">
          {nav_links(current, page)}
      </ul>
      <a class="header-phone" href="{PHONE_HREF}">{PHONE}</a>
      <a class="btn btn--tint btn--sm" href="contact.html">Book a free trial</a>
    </nav>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu" data-menu-open>
      Menu <span class="bars" aria-hidden="true"><span></span><span></span></span>
    </button>
  </div>
</header>

<div class="menu" id="menu" role="dialog" aria-modal="true" aria-label="Site menu" aria-hidden="true" inert>
  <div class="menu-top">
    <a class="brand" href="index.html" aria-label="NIX Gymnastics home"><img src="assets/img/nix-logo-rev.svg" alt="NIX Gymnastics" width="140" height="47"></a>
    <button class="menu-toggle menu-close" type="button" data-menu-close style="display:inline-flex">
      Close <span class="bars" aria-hidden="true"><span></span><span></span></span>
    </button>
  </div>
  <ul class="menu-list">
    {nav_links(current, page, mobile=True)}
  </ul>
  <div class="menu-foot">
    <a class="btn btn--tint btn--lg" href="contact.html">Book a free trial class {ARROW}</a>
    <div class="menu-contact">
      <a href="{PHONE_HREF}">{PHONE}</a>
      <span>138 Turnpike Rd, New Ipswich, NH</span>
    </div>
  </div>
</div>
"""


def footer(bar):
    mobile_bar = f"""
<div class="mobile-bar" aria-label="Quick actions">
  <a class="btn btn--tint" href="contact.html">Book a free trial {ARROW}</a>
  <a class="call" href="{PHONE_HREF}" aria-label="Call NIX Gymnastics">{PHONE_ICON} Call</a>
</div>""" if bar else ""
    social = "\n          ".join(
        f'<li><a href="{href}" rel="noopener" target="_blank" aria-label="{name} (opens in a new tab)">{icon}</a></li>'
        for name, href, icon in SOCIAL)
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/img/nix-logo-rev.svg" alt="NIX Gymnastics" width="190" height="64" loading="lazy">
        <p>Gymnastics, tumbling and circus classes for boys and girls, from first steps to competitive team. New Ipswich, New Hampshire.</p>
        <ul class="social" aria-label="NIX Gymnastics on social media">
          {social}
        </ul>
      </div>
      <div>
        <h2>Visit</h2>
        <address>138 Turnpike Rd<br>New Ipswich, NH 03071</address>
        <a href="https://maps.google.com/?q=138+Turnpike+Rd+New+Ipswich+NH+03071" rel="noopener">Get directions</a>
      </div>
      <div>
        <h2>Contact</h2>
        <ul>
          <li><a href="{PHONE_HREF}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="contact.html">Book a free trial</a></li>
        </ul>
      </div>
      <div>
        <h2>Explore</h2>
        <ul>
          <li><a href="programs.html">Programs</a></li>
          <li><a href="team.html">Competitive Team</a></li>
          <li><a href="meets.html">Meets &amp; results</a></li>
          <li><a href="galleries.html">Photo galleries</a></li>
          <li><a href="parties.html">Parties &amp; Open Gym</a></li>
          <li><a href="about.html">About NIX</a></li>
          <li><a href="{REG_FORM}" download="NIX-Gymnastics-registration-form.pdf">Registration form (PDF)</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      <span>&copy; <span data-year>2026</span> NIX Gym, LLC</span>
      <span>Gymnastics for a healthy life.</span>
    </div>
  </div>
</footer>{mobile_bar}
<script src="assets/js/main.js" defer></script>
<script>document.querySelectorAll('[data-year]').forEach(function(e){{e.textContent=new Date().getFullYear()}})</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Team meets, results/news and the registration form

DOC_ICON = '<svg viewBox="0 0 40 48" fill="none" aria-hidden="true"><path d="M3 3h23l11 11v31H3V3Z" stroke="currentColor" stroke-width="3"/><path d="M26 3v11h11" stroke="currentColor" stroke-width="3"/><path d="M11 25h18M11 32h18M11 39h11" stroke="currentColor" stroke-width="3"/></svg>'
SQUAD = {"boys": "Boys' team", "girls": "Girls' team"}


def parse_day(s):
    return date.fromisoformat(s)


def slug(m):
    name = m["name"] if re.search(r"\b20\d\d\b", m["name"]) else f"{m['name']} {m['start'][:4]}"
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_meets():
    meets = json.loads((DATA / "meets.json").read_text())
    for m in meets:
        m["s"], m["e"] = parse_day(m["start"]), parse_day(m["end"])
        m["slug"] = slug(m)
    return sorted(meets, key=lambda m: m["s"])


def season_of(d):
    """Gymnastics seasons run autumn to spring: Dec 2026 and Mar 2027 are both 2026–27."""
    y = d.year if d.month >= 8 else d.year - 1
    return y, f"{y}–{str(y + 1)[2:]}"


def where(m):
    place = ", ".join(x for x in (m["city"], m["state"]) if x)
    return f"{m['venue']}, {place}" if m["venue"] else f"Venue to be announced, {place}"


def maps_url(m):
    q = " ".join(x for x in (m["venue"], m["street"], m["city"], m["state"], m["zip"]) if x)
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(q)


def date_block(m):
    s, e = m["s"], m["e"]
    dw = s.strftime("%a") if s == e else f"{s.strftime('%a')}–{e.strftime('%a')}"
    if s == e:
        days, tail = str(s.day), ""
    elif s.month == e.month:
        days, tail = f"{s.day}–{e.day}", ""
    else:
        days, tail = str(s.day), f" <span class=\"to\">to {e.strftime('%b')} {e.day}</span>"
    return (f'<p class="meet-date"><time datetime="{m["start"]}"><span class="mo">{s.strftime("%b")}</span>'
            f' <span class="dd">{days}</span></time>{tail} <span class="dw">{dw}</span></p>')


def meet_item(m):
    host = (f'<a href="{m["host_url"]}" rel="noopener" target="_blank">Host website<span class="visually-hidden"> for {escape(m["name"])} (opens in a new tab)</span></a>'
            if m["host_url"] else "")
    directions = (f'<a href="{maps_url(m)}" rel="noopener" target="_blank">Directions<span class="visually-hidden"> to {escape(m["venue"])} (opens in a new tab)</span></a>'
                  if m["venue"] else "")
    g = GALLERY_BY_EVENT.get(m["slug"])
    photos = (f'<a class="meet-photos" href="{g["href"]}">Photos ({len(g["photos"])})<span class="visually-hidden"> from {escape(m["name"])}</span></a>'
              if g else "")
    links = [photos, directions, host,
             f'<a href="assets/cal/{m["slug"]}.ics" download>Add to calendar<span class="visually-hidden">: {escape(m["name"])}</span></a>']
    links = "".join(f"<li>{x}</li>" for x in links if x)
    return f"""<li class="meet meet--{m['squad']}" id="{m['slug']}" data-squad="{m['squad']}" data-start="{m['start']}" data-end="{m['end']}">
            {date_block(m)}
            <div class="meet-body">
              <h4 class="meet-name">{escape(m['name'])}</h4>
              <p class="meet-squad">{SQUAD[m['squad']]}</p>
              <p class="meet-where">{escape(where(m))}<span class="meet-host"> · Hosted by {escape(m['host'])}</span></p>
            </div>
            <ul class="meet-links">{links}</ul>
          </li>"""


def render_upcoming(meets):
    groups, order = {}, []
    for m in meets:
        key = m["s"].strftime("%Y-%m")
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(m)
    out = []
    for key in order:
        label = groups[key][0]["s"].strftime("%B %Y")
        items = "\n          ".join(meet_item(m) for m in groups[key])
        out.append(f"""<section class="meet-month" id="m-{key}" aria-labelledby="m-{key}-h">
        <h3 class="meet-month-label" id="m-{key}-h">{label}</h3>
        <ol class="meet-list">
          {items}
        </ol>
      </section>""")
    return "\n      ".join(out)


def render_season_strip(upcoming, season_start):
    counts = {}
    for m in upcoming:
        counts[m["s"].strftime("%Y-%m")] = counts.get(m["s"].strftime("%Y-%m"), 0) + 1
    cells = []
    for i in range(9):  # September to May
        month = date(season_start + (8 + i) // 12, (8 + i) % 12 + 1, 1)
        key, n = month.strftime("%Y-%m"), counts.get(month.strftime("%Y-%m"), 0)
        label = month.strftime("%b")
        if n:
            cells.append(f'<li><a href="#m-{key}" class="has-meets"><span class="mo">{label}</span>'
                         f'<span class="n">{n} meet{"s" if n > 1 else ""}</span></a></li>')
        else:
            cells.append(f'<li><span class="mo">{label}</span><span class="n"><span class="visually-hidden">No meets</span></span></li>')
    return "\n          ".join(cells)


def render_teaser(upcoming):
    rows = []
    for m in upcoming[:5]:
        rows.append(f"""<li class="meet meet--{m['squad']}" data-squad="{m['squad']}" data-start="{m['start']}" data-end="{m['end']}">
            {date_block(m)}
            <div class="meet-body">
              <h3 class="meet-name"><a href="meets.html#{m['slug']}">{escape(m['name'])}</a></h3>
              <p class="meet-squad">{SQUAD[m['squad']]}</p>
              <p class="meet-where">{escape(where(m))}</p>
            </div>
          </li>""")
    return "\n          ".join(rows)


def render_news():
    posts = sorted(json.loads((DATA / "news.json").read_text()), key=lambda p: p["date"], reverse=True)
    out = []
    for p in posts:
        y = p["date"][:4]
        shown = date.fromisoformat(p["date"] + "-01").strftime("%B %Y") if len(p["date"]) == 7 else (
            date.fromisoformat(p["date"]).strftime("%B %-d, %Y") if len(p["date"]) == 10 else y)
        kind = "Result" if p["kind"] == "result" else "News"
        link = (f'<a class="link-arrow" href="{p["link"]["url"]}" rel="noopener" target="_blank">{escape(p["link"]["label"])}{{{{arrow}}}}<span class="visually-hidden"> (opens in a new tab)</span></a>'
                if p.get("link") else "")
        g = GALLERY_BY_EVENT.get(p.get("event", ""))
        if g:
            link += f'<a class="link-arrow" href="{g["href"]}">See the photos ({len(g["photos"])}){{{{arrow}}}}</a>'

        board = ""
        if p.get("scoreboard"):
            sb = p["scoreboard"]
            head = "".join(f'<th scope="col">{escape(e)}</th>' for e in sb["events"])
            body = "".join(
                f'<tr><th scope="row">{escape(r["gymnast"])}<span>{escape(r["level"])}</span></th>'
                + "".join(f'<td>{s}<span>{pl}</span></td>' for s, pl in r["scores"]) + "</tr>"
                for r in sb["rows"])
            board = f"""<details class="scoreboard">
            <summary>Scores and places</summary>
            <div class="table-scroll" tabindex="0" role="region" aria-label="Scores for {escape(p['title'])}">
              <table>
                <caption class="visually-hidden">Scores for {escape(p['title'])}. Each score is followed by the place.</caption>
                <thead><tr><th scope="col">Gymnast</th>{head}</tr></thead>
                <tbody>{body}</tbody>
              </table>
            </div>
          </details>"""
        out.append(f"""<article class="post reveal">
          <p class="post-meta"><time datetime="{p['date']}">{shown}</time><span>{kind}</span></p>
          <div class="post-body">
            <h3 class="h3">{escape(p['title'])}</h3>
            <p>{escape(p['body'])}</p>
            {link}
            {board}
          </div>
        </article>""")
    return "\n        ".join(out)


def ics_text(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def ics_event(m):
    loc = ", ".join(x for x in (m["venue"], m["street"], m["city"], m["state"], m["zip"]) if x)
    desc = f"NIX Gymnastics {SQUAD[m['squad']].lower()} meet. Hosted by {m['host']}. Your coach confirms session and report times."
    lines = ["BEGIN:VEVENT", f"UID:{m['slug']}@nixgym.com", "DTSTAMP:20260101T000000Z",
             f"DTSTART;VALUE=DATE:{m['s'].strftime('%Y%m%d')}",
             f"DTEND;VALUE=DATE:{(m['e'] + timedelta(days=1)).strftime('%Y%m%d')}",
             f"SUMMARY:{ics_text(m['name'])} – NIX {SQUAD[m['squad']].lower()}",
             f"DESCRIPTION:{ics_text(desc)}"]
    if loc:
        lines.append(f"LOCATION:{ics_text(loc)}")
    if m["host_url"]:
        lines.append(f"URL:{m['host_url']}")
    return lines + ["END:VEVENT"]


def write_calendars(meets, upcoming):
    CAL.mkdir(parents=True, exist_ok=True)
    for old in CAL.glob("*.ics"):
        old.unlink()
    wrap = lambda events: "\r\n".join(
        ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//NIX Gymnastics//Team meets//EN",
         "CALSCALE:GREGORIAN", "X-WR-CALNAME:NIX Gymnastics team meets"] + events + ["END:VCALENDAR", ""])
    for m in meets:
        (CAL / f"{m['slug']}.ics").write_text(wrap(ics_event(m)))
    (CAL / "nix-team-meets.ics").write_text(wrap([l for m in upcoming for l in ics_event(m)]))


def registration_block(tone=""):
    kb = round((ROOT / REG_FORM).stat().st_size / 1024)
    return f"""<div class="download{' ' + tone if tone else ''}">
          <span class="download-icon">{DOC_ICON}</span>
          <div class="download-text">
            <h3 class="h4">Registration form</h3>
            <p>Print it, fill it out and bring it to the gym. It covers contact and medical details, our payment policy and the parent waiver.</p>
            <p class="download-meta">PDF · 2 pages · {kb} KB</p>
          </div>
          <a class="btn btn--sm" href="{REG_FORM}" download="NIX-Gymnastics-registration-form.pdf">Download PDF {ARROW}</a>
        </div>"""


# ---------------------------------------------------------------------------
# Photo galleries: one record per gallery in _data/galleries.json, linked to a meet by
# "event". Date, season, team and venue come from the meet, so a gallery is entered once
# and appears on its own page, the gallery index, the meet calendar and linked news posts.

GALLERY_BY_EVENT = {}


def jpeg_size(path):
    """Width and height from a JPEG's SOF marker (no imaging library needed)."""
    data = path.read_bytes()
    i = 2
    while i < len(data):
        marker, length = data[i + 1], int.from_bytes(data[i + 2:i + 4], "big")
        if marker in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
        i += 2 + length
    raise ValueError(f"no size in {path}")


def date_range(s, e):
    if s == e:
        return s.strftime("%B %-d, %Y")
    if s.year != e.year:
        return f"{s.strftime('%B %-d, %Y')} – {e.strftime('%B %-d, %Y')}"
    if s.month == e.month:
        return f"{s.strftime('%B %-d')}–{e.day}, {s.year}"
    return f"{s.strftime('%B %-d')} – {e.strftime('%B %-d')}, {s.year}"


def load_galleries(meets):
    by_slug = {m["slug"]: m for m in meets}
    galleries = json.loads((DATA / "galleries.json").read_text()) if (DATA / "galleries.json").exists() else []
    out = []
    for g in galleries:
        m = by_slug.get(g.get("event", ""))
        if g.get("event") and not m:
            raise SystemExit(f"gallery '{g['id']}' links to unknown meet '{g['event']}'")
        g["meet"] = m
        g["title"] = g.get("title") or (m["name"] if m else g["id"])
        g["s"] = m["s"] if m else parse_day(g["date"])
        g["e"] = m["e"] if m else parse_day(g.get("end", g["date"]))
        g["squad"] = m["squad"] if m else g.get("squad", "")
        g["where"] = where(m) if m and m["venue"] else (g.get("where", "") if not m else "")
        g["season"] = season_of(g["s"])[1]
        g["href"] = f"gallery-{g['id']}.html"
        folder = ROOT / "assets" / "galleries" / g["id"]
        for ph in g["photos"]:
            ph["src"] = f"assets/galleries/{g['id']}/{ph['file']}"
            ph["thumb"] = f"assets/galleries/{g['id']}/sm/{ph['file']}"
            ph["w"], ph["h"] = jpeg_size(folder / ph["file"])
            ph["tw"], ph["th"] = jpeg_size(folder / "sm" / ph["file"])
            if not ph.get("alt"):
                print(f"  warning: {g['id']}/{ph['file']} has no alt text")
        g["cover_photo"] = next((ph for ph in g["photos"] if ph["file"] == g.get("cover")), g["photos"][0])
        out.append(g)
        if m:
            GALLERY_BY_EVENT[m["slug"]] = g
    return sorted(out, key=lambda g: g["s"], reverse=True)


def squad_label(g):
    return SQUAD.get(g["squad"], "Boys' & girls' teams")


def render_gallery_cards(galleries):
    cards = []
    for g in galleries:
        c = g["cover_photo"]
        cards.append(f"""<li class="gcard" data-season="{g['season']}" data-squad="{g['squad'] or 'all'}">
          <a href="{g['href']}">
            <span class="gcard-img img"><img src="{c['thumb']}" alt="" width="{c['tw']}" height="{c['th']}" loading="lazy"></span>
            <span class="gcard-meta">{squad_label(g)} · {g['s'].strftime('%b %Y')}</span>
            <h3 class="gcard-title">{escape(g['title'])}</h3>
            <span class="gcard-count">{len(g['photos'])} photos</span>
          </a>
        </li>""")
    return "\n        ".join(cards)


def render_gallery_filters(galleries):
    seasons = sorted({g["season"] for g in galleries}, reverse=True)
    btns = ['<button class="seg" type="button" data-gfilter="season" data-value="all" aria-pressed="true">All seasons</button>']
    btns += [f'<button class="seg" type="button" data-gfilter="season" data-value="{s}" aria-pressed="false">{s}</button>' for s in seasons]
    return "\n          ".join(btns)


def render_gallery_page(g, galleries):
    m = g["meet"]
    items = "\n        ".join(
        f'<a href="{ph["src"]}" data-pswp-width="{ph["w"]}" data-pswp-height="{ph["h"]}" target="_blank">'
        f'<img src="{ph["thumb"]}" alt="{escape(ph["alt"])}" width="{ph["tw"]}" height="{ph["th"]}" loading="lazy"></a>'
        for ph in g["photos"])
    facts = [f'<div><dt>Team</dt><dd>{squad_label(g)}</dd></div>',
             f'<div><dt>Date</dt><dd>{date_range(g["s"], g["e"])}</dd></div>']
    if g["where"]:
        facts.append(f'<div><dt>Where</dt><dd>{escape(g["where"])}</dd></div>')
    facts.append(f'<div><dt>Photos</dt><dd>{len(g["photos"])}{" · " + escape(g["credit"]) if g.get("credit") else ""}</dd></div>')
    meet_link = f'<a class="link-arrow" href="meets.html#{m["slug"]}">Meet details {ARROW}</a>' if m else ""
    i = galleries.index(g)
    newer, older = (galleries[i - 1] if i > 0 else None), (galleries[i + 1] if i + 1 < len(galleries) else None)
    pager = "".join(
        f'<a class="gallery-pager-link gallery-pager-link--{cls}" href="{x["href"]}"><span class="label">{lab}</span>{escape(x["title"])}</a>'
        for cls, lab, x in (("newer", "Newer gallery", newer), ("older", "Older gallery", older)) if x)
    return f"""<main id="main">

  <header class="page-hero gallery-hero">
    <div class="container">
      <a class="back-link" href="galleries.html"><span aria-hidden="true">←</span> All photo galleries</a>
      <h1 class="h1">{escape(g['title'])}</h1>
      <dl class="gallery-facts">
        {"".join(facts)}
      </dl>
      {meet_link}
    </div>
  </header>

  <section class="section gallery-section" aria-label="Photos" style="padding-top:0">
    <div class="container">
      <p class="visually-hidden">Select a photo to view it larger. Use the arrow keys to move between photos and Escape to close.</p>
      <div class="gallery-grid" id="gallery" data-gallery>
        {items}
      </div>
      <nav class="gallery-pager" aria-label="More galleries">{pager}</nav>
    </div>
  </section>

</main>
"""


def meet_context(today):
    meets = load_meets()
    galleries = load_galleries(meets)
    upcoming = [m for m in meets if m["e"] >= today]
    past = [m for m in meets if m["e"] < today][::-1]
    start, label = season_of(upcoming[0]["s"] if upcoming else today)
    past_season = season_of(past[0]["s"])[1] if past else ""
    write_calendars(meets, upcoming)
    return {
        "{{meets_upcoming}}": render_upcoming(upcoming),
        "{{meets_past}}": "\n          ".join(meet_item(m) for m in past),
        "{{meets_past_count}}": str(len(past)),
        "{{meets_past_season}}": past_season,
        "{{season_label}}": label,
        "{{season_strip}}": render_season_strip(upcoming, start),
        "{{meets_next}}": render_teaser(upcoming),
        "{{news_feed}}": render_news(),
        "{{registration_form}}": registration_block(),
        "{{registration_href}}": REG_FORM,
        "{{gallery_cards}}": render_gallery_cards(galleries),
        "{{gallery_season_filters}}": render_gallery_filters(galleries),
        "{{gallery_count}}": str(len(galleries)),
    }, galleries


def build():
    context, galleries = meet_context(date.today())
    for src in sorted(PAGES.glob("*.html")):
        raw = src.read_text()
        meta_block, body = raw.split("---\n", 1)
        meta = dict(
            line.split(":", 1) for line in meta_block.strip().splitlines()
        )
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        for key, value in context.items():
            body = body.replace(key, value)
        body = (body.replace("{{arrow}}", ARROW)
                    .replace("{{phone}}", PHONE)
                    .replace("{{phone_href}}", PHONE_HREF)
                    .replace("{{email}}", EMAIL)
                    .replace("{{check}}", CHECK_ICON))
        html = (head(meta["title"], meta["description"])
                + header(meta.get("nav", ""), src.name)
                + body
                + footer(meta.get("bar", "yes") == "yes"))
        (ROOT / src.name).write_text(html)
        print("built", src.name)

    for old in ROOT.glob("gallery-*.html"):
        old.unlink()
    pswp_css = '\n  <link rel="stylesheet" href="assets/vendor/photoswipe/photoswipe.css">'
    for g in galleries:
        desc = f"Photos of the NIX Gymnastics {squad_label(g).lower()} at the {g['title']}, {date_range(g['s'], g['e'])}."
        html = (head(f"{g['title']} photos", escape(desc), pswp_css)
                + header("team", "galleries.html")
                + render_gallery_page(g, galleries)
                + footer(True).replace("</body>", '<script type="module" src="assets/js/gallery.js"></script>\n</body>'))
        (ROOT / g["href"]).write_text(html)
        print("built", g["href"])


if __name__ == "__main__":
    build()
