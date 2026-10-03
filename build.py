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

Run:  python3 build.py
"""
from pathlib import Path

ROOT = Path(__file__).parent
PAGES = ROOT / "_pages"

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
    ("team", "team.html", "Competitive Team", "Boys & girls"),
    ("parties", "parties.html", "Parties & Open Gym", "Weekends & drop-in"),
    ("about", "about.html", "About", "Coaches & gym"),
    ("contact", "contact.html", "Contact", "Visit or call"),
]


def nav_links(current, mobile=False):
    out = []
    items = NAV if mobile else NAV[:4]
    for key, href, label, sub in items:
        cur = ' aria-current="page"' if key == current else ""
        if mobile:
            out.append(f'<li><a href="{href}"{cur}>{label} <small>{sub}</small></a></li>')
        else:
            out.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "\n          ".join(out)


def head(title, description):
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
  <link rel="stylesheet" href="assets/css/styles.css">
</head>"""


def header(current):
    return f"""
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="index.html" aria-label="NIX Gymnastics home"><img src="assets/img/nix-logo-rev.svg" alt="NIX Gymnastics" width="168" height="57"></a>
    <nav class="nav" aria-label="Main">
      <ul class="nav-list">
          {nav_links(current)}
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
    {nav_links(current, mobile=True)}
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
        <p>Gymnastics, tumbling, ninja and circus classes for boys and girls, from first steps to competitive team. New Ipswich, New Hampshire.</p>
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
          <li><a href="parties.html">Parties &amp; Open Gym</a></li>
          <li><a href="about.html">About NIX</a></li>
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


def build():
    for src in sorted(PAGES.glob("*.html")):
        raw = src.read_text()
        meta_block, body = raw.split("---\n", 1)
        meta = dict(
            line.split(":", 1) for line in meta_block.strip().splitlines()
        )
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        body = (body.replace("{{arrow}}", ARROW)
                    .replace("{{phone}}", PHONE)
                    .replace("{{phone_href}}", PHONE_HREF)
                    .replace("{{email}}", EMAIL)
                    .replace("{{check}}", CHECK_ICON))
        html = (head(meta["title"], meta["description"])
                + header(meta.get("nav", ""))
                + body
                + footer(meta.get("bar", "yes") == "yes"))
        (ROOT / src.name).write_text(html)
        print("built", src.name)


if __name__ == "__main__":
    build()
