#!/usr/bin/env python3
"""Builds the static site from _build/games.json and _build/privacy/*.html.

Run from anywhere:  python _build/build.py
Needs Pillow (reads screenshot sizes). Folders starting with "_" are not published by GitHub Pages.
"""
import hashlib
import html
import json
import re
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / '_build'
BASE = 'https://yclsoftware-hash.github.io'
STUDIO = 'Fun Games & Funny Games'
EMAIL = 'funfunnygames1@gmail.com'
DEV_URL = 'https://play.google.com/store/apps/dev?id=6015396465325869230'

esc = html.escape

# Feather-style line icons (MIT), 24x24 viewBox.
ICONS = {
    'arrow': '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    'menu': '<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>',
    'mail': '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
    'file': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    'smartphone': '<rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
    'offline': '<line x1="1" y1="1" x2="23" y2="23"/><path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/><path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"/><path d="M10.71 5.05A16 16 0 0 1 22.58 9"/><path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/>',
    'globe': '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    'pointer': '<path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z"/><path d="M13 13l6 6"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    'check': '<polyline points="20 6 9 17 4 12"/>',
    'layers': '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    'pen': '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>',
    'award': '<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>',
    'star': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    'zap': '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    'compass': '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
    'users': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'smile': '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>',
    'heart': '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
    'plus': '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>',
    'divide': '<circle cx="12" cy="6" r="2"/><line x1="5" y1="12" x2="19" y2="12"/><circle cx="12" cy="18" r="2"/>',
    'trending': '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    'refresh': '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
    'map': '<polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/>',
    'crosshair': '<circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/>',
    'eye': '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    'wind': '<path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/>',
    'volume': '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>',
}
PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5 3.9v16.2c0 .8.9 1.3 1.6.9l13.3-8.1c.6-.4.6-1.3 0-1.7L6.6 3c-.7-.4-1.6.1-1.6.9z"/></svg>'


def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def game_url(g):
    return f"/funfunnygames/{g['folder']}/"


def privacy_url(g):
    return game_url(g) + 'privacy.html'


def play_url(g):
    return f"https://play.google.com/store/apps/details?id={g['package']}" if g['live'] else None


def icon_src(g):
    return f"/assets/icons/{g['slug']}.png"


def shots(g):
    """[(src, width, height)] for assets/img/<slug>/shot-N.jpg, in order."""
    files = sorted((ROOT / 'assets/img' / g['slug']).glob('shot-*.jpg'), key=lambda p: int(p.stem.split('-')[1]))
    out = []
    for p in files:
        with Image.open(p) as im:
            out.append((f"/assets/img/{g['slug']}/{p.name}", im.width, im.height))
    return out


def theme_style(g):
    t = g['theme']
    return f"--accent:{t['accent']};--accent-soft:{t['soft']};--game-grad:{t['grad']};--cta-grad:{t['cta']}"


def store_button(url, light=False):
    cls = 'store-btn light' if light else 'store-btn'
    return (f'<a class="{cls}" href="{esc(url)}">{PLAY}'
            '<span><small>Get it on</small><strong>Google Play</strong></span></a>')


SOON_BADGE = f'<span class="store-btn soon">{PLAY}<span><small>Coming soon to</small><strong>Google Play</strong></span></span>'


def css_href():
    digest = hashlib.sha1((ROOT / 'assets/css/site.css').read_bytes()).hexdigest()[:8]
    return f'/assets/css/site.css?v={digest}'


def head(title, desc, path, image):
    url = BASE + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(STUDIO)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/logo.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/fredoka-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/plus-jakarta-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{css_href()}">
</head>'''


def header(current=''):
    links = [('/#games', 'Games', 'games'), ('/#about', 'About', 'about'), ('/#contact', 'Contact', 'contact')]
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if k == current else ""}>{t}</a>' for h, t, k in links)
    menu = ''.join(f'<a href="{h}">{t}</a>' for h, t, _ in links)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container">
    <a class="brand" href="/" aria-label="{esc(STUDIO)} home"><img src="/assets/logo.svg" alt="" width="38" height="38"><span>{esc(STUDIO)}</span></a>
    <nav class="nav" aria-label="Main">{nav}</nav>
    <a class="btn btn-dark btn-sm nav-cta" href="{DEV_URL}">{PLAY}Google Play</a>
    <details class="menu">
      <summary aria-label="Open menu">{icon('menu')}</summary>
      <div class="menu-panel">{menu}<a class="btn btn-dark btn-sm" href="{DEV_URL}">{PLAY}Google Play</a></div>
    </details>
  </div>
</header>'''


def footer(games):
    game_links = ''.join(f'<li><a href="{game_url(g)}">{esc(g["name"])}</a></li>' for g in games)
    privacy_links = ''.join(f'<li><a href="{privacy_url(g)}">{esc(g["name"])}</a></li>' for g in games)
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="/"><img src="/assets/logo.svg" alt="" width="38" height="38"><span>{esc(STUDIO)}</span></a>
        <p>Small, bright and easy-to-learn games for Android.</p>
      </div>
      <div><h4>Games</h4><ul>{game_links}</ul></div>
      <div><h4>Privacy policies</h4><ul>{privacy_links}</ul></div>
      <div><h4>Studio</h4><ul>
        <li><a href="/#about">About us</a></li>
        <li><a href="{DEV_URL}">All games on Google Play</a></li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {date.today().year} {esc(STUDIO)}. All rights reserved.</span>
      <span>Google Play is a trademark of Google LLC.</span>
    </div>
  </div>
</footer>'''


def page(games, title, desc, path, image, main, style='', current=''):
    body_attr = f' style="{style}"' if style else ''
    return f'''{head(title, desc, path, image)}
<body{body_attr}>
{header(current)}
<main id="main">
{main}
</main>
{footer(games)}
</body>
</html>
'''


def section_head(kicker, title, text='', center=False):
    cls = 'section-head center' if center else 'section-head'
    p = f'<p>{esc(text)}</p>' if text else ''
    return f'<div class="{cls}"><span class="kicker">{esc(kicker)}</span><h2>{esc(title)}</h2>{p}</div>'


# ---------- Home ----------

def media(g):
    s = shots(g)
    if s[0][1] < s[0][2]:  # portrait
        imgs = ''.join(f'<img src="{src}" alt="" width="{w}" height="{h}" loading="lazy">' for src, w, h in s[:3])
        return f'<div class="feature-media fan">{imgs}</div>'
    src, w, h = s[0]
    return f'<div class="feature-media land"><img src="{src}" alt="" width="{w}" height="{h}" style="aspect-ratio:{w}/{h}" loading="lazy"></div>'


def live_card(g):
    return f'''<article class="feature-card" style="{theme_style(g)}">
  {media(g)}
  <div class="feature-body">
    <div class="app-row">
      <img src="{icon_src(g)}" alt="{esc(g['name'])} icon" width="68" height="68">
      <div><h3><a href="{game_url(g)}">{esc(g['name'])}</a></h3><div class="genre">{esc(g['genre'])}</div></div>
    </div>
    <p>{esc(g['short'])}</p>
    <div class="card-actions">
      {store_button(play_url(g))}
      <a class="text-link" href="{game_url(g)}">Learn more {icon('arrow')}</a>
    </div>
    <div class="card-foot">{icon('file')}<a href="{privacy_url(g)}">Privacy policy</a></div>
  </div>
</article>'''


def soon_card(g):
    return f'''<article class="game-card" style="{theme_style(g)}">
  <img src="{icon_src(g)}" alt="{esc(g['name'])} icon" width="72" height="72" loading="lazy">
  <div>
    <h3><a href="{game_url(g)}">{esc(g['title'])}</a></h3>
    <div class="meta">{esc(g['genre'])}</div>
    <span class="chip chip-soon">Coming soon</span>
  </div>
  <p>{esc(g['short'])}</p>
  <a class="text-link" href="{game_url(g)}">Learn more {icon('arrow')}</a>
</article>'''


def build_home(games):
    live = [g for g in games if g['live']]
    soon = [g for g in games if not g['live']]
    cloud = ''.join(f'<figure><img src="{icon_src(g)}" alt="{esc(g["name"])}" width="256" height="256"></figure>' for g in games)
    stack = ''.join(f'<img src="{icon_src(g)}" alt="" width="32" height="32">' for g in live)
    live_names = ' and '.join(g['name'] for g in live)
    main = f'''<section class="hero">
  <div class="container hero-grid">
    <div>
      <span class="eyebrow"><i>{icon('smile')}</i>Independent mobile game studio</span>
      <h1>Small games,<br><span class="grad-text">big smiles.</span></h1>
      <p class="lead">We make bright, easy-to-learn games for Android: physics puzzles, sky-high arcade action, maze races and learning games for kids.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#games">Explore our games {icon('arrow')}</a>
        {store_button(DEV_URL)}
      </div>
      <div class="hero-note"><span class="stack">{stack}</span>{esc(live_names)} are live on Google Play</div>
    </div>
    <div class="icon-cloud" aria-hidden="true">{cloud}</div>
  </div>
</section>

<section class="section" id="games">
  <div class="container">
    {section_head('Now on Google Play', 'Play our latest games', 'Free to download on Android phones and tablets.')}
    <div class="showcase">
      {''.join(live_card(g) for g in live)}
    </div>
  </div>
</section>

<section class="section section-white" id="coming-soon">
  <div class="container">
    {section_head('Coming soon', 'More games on the way', 'These games are getting ready for Google Play. Store links will appear here as soon as they are live.')}
    <div class="game-grid">
      {''.join(soon_card(g) for g in soon)}
    </div>
  </div>
</section>

<section class="section" id="about">
  <div class="container about">
    {section_head('About us', 'Fun first, then everything else', f'{STUDIO} is a small independent studio. We build games you can understand in seconds and keep coming back to: clear rules, short levels and plenty of personality.')}
    <div class="values">
      <div class="value"><div class="ico violet">{icon('pointer')}</div><h3>Easy to pick up</h3><p>Simple controls and short levels you can play in a coffee break.</p></div>
      <div class="value"><div class="ico pink">{icon('users')}</div><h3>For every age</h3><p>Friendly games that kids and grown-ups can enjoy together.</p></div>
      <div class="value"><div class="ico amber">{icon('offline')}</div><h3>Play anywhere</h3><p>{esc(live_names)} both work without an internet connection.</p></div>
      <div class="value"><div class="ico sky">{icon('globe')}</div><h3>Made for the world</h3><p>Our store pages are translated into dozens of languages.</p></div>
    </div>
  </div>
</section>

<section class="section pt-0" id="contact">
  <div class="container">
    <div class="cta-band">
      <div><h2>Questions or feedback?</h2><p>Get in touch for support, ideas or privacy requests.</p></div>
      <div class="cta-actions"><a class="btn btn-white" href="mailto:{EMAIL}">{icon('mail')}{EMAIL}</a></div>
    </div>
  </div>
</section>'''
    desc = f'{STUDIO} makes bright, easy-to-learn games for Android: ' + ', '.join(g['name'] for g in games) + '.'
    return page(games, f'{STUDIO} | Casual games for Android', desc, '/', '/assets/img/draw-rescue/feature.jpg', main, current='')


# ---------- Game page ----------

def hero_art(g):
    s = shots(g)
    front, back = s[0], s[1] if len(s) > 1 else s[0]
    alt = esc(g['name']) + ' screenshot'
    if front[1] < front[2]:
        return (f'<div class="phones" aria-hidden="true">'
                f'<div class="phone back"><img src="{back[0]}" alt="" width="{back[1]}" height="{back[2]}"></div>'
                f'<div class="phone front"><img src="{front[0]}" alt="{alt}" width="{front[1]}" height="{front[2]}"></div></div>')
    return (f'<div class="devices" aria-hidden="true">'
            f'<div class="device back" style="aspect-ratio:{back[1]}/{back[2]}"><img src="{back[0]}" alt="" width="{back[1]}" height="{back[2]}"></div>'
            f'<div class="device front" style="aspect-ratio:{front[1]}/{front[2]}"><img src="{front[0]}" alt="{alt}" width="{front[1]}" height="{front[2]}"></div></div>')


def render_section(sec):
    t = sec['type']
    head_html = section_head(sec['kicker'], sec['title'], sec.get('text', ''))
    if t == 'steps':
        items = ''.join(f'<div class="step"><div class="num">{i}</div><h3>{esc(a)}</h3><p>{esc(b)}</p></div>'
                        for i, (a, b) in enumerate(sec['items'], 1))
        body = f'<div class="steps" style="--n:{len(sec["items"])}">{items}</div>'
    elif t == 'features':
        items = ''.join(f'<div class="feature"><div class="ico">{icon(i)}</div><h3>{esc(a)}</h3><p>{esc(b)}</p></div>'
                        for i, a, b in sec['items'])
        cls = 'features three' if sec.get('cols') == 3 else 'features'
        body = f'<div class="{cls}">{items}</div>'
    elif t == 'perks':
        items = ''.join(f'<div class="perk">{icon(i)}<div><strong>{esc(a)}</strong><span>{esc(b)}</span></div></div>'
                        for i, a, b in sec['items'])
        body = f'<div class="perks">{items}</div>'
    else:
        raise ValueError(t)
    note = f'<p class="note">{esc(sec["note"])}</p>' if sec.get('note') else ''
    return f'<section class="section"><div class="container">{head_html}{body}{note}</div></section>'


def build_game(games, g):
    s = shots(g)
    orient = 'portrait' if s[0][1] < s[0][2] else 'landscape'
    alts = g.get('shotAlts') or []
    strip = ''.join(
        f'<img src="{src}" alt="{esc(alts[i] if i < len(alts) else g["name"] + " screenshot " + str(i + 1))}" '
        f'width="{w}" height="{h}" loading="lazy">' for i, (src, w, h) in enumerate(s))
    chips = ''.join(f'<span class="chip">{icon(i)}{esc(t)}</span>' for i, t in g['chips'])
    if g['live']:
        cta_btn = store_button(play_url(g))
        cta_band = f'''<div class="cta-band">
      <div><h2>{esc(g['cta'])}</h2><p>Download {esc(g['name'])} free on Google Play.</p></div>
      <div class="cta-actions">{store_button(play_url(g), light=True)}</div>
    </div>'''
    else:
        cta_btn = SOON_BADGE
        others = ''.join(f'<a class="btn btn-white" href="{game_url(o)}">Try {esc(o["name"])}</a>' for o in games if o['live'])
        cta_band = f'''<div class="cta-band">
      <div><h2>Coming soon to Google Play</h2><p>{esc(g['name'])} is getting ready for release. Until then, try our games that are already live.</p></div>
      <div class="cta-actions">{others}</div>
    </div>'''
    more = ''.join(
        f'<a class="mini" href="{game_url(o)}"><img src="{icon_src(o)}" alt="" width="48" height="48" loading="lazy">'
        f'<span><strong>{esc(o["name"])}</strong><span>{"On Google Play" if o["live"] else "Coming soon"}</span></span></a>'
        for o in games if o is not g)
    main = f'''<section class="game-hero">
  <div class="container">
    <ol class="breadcrumb"><li><a href="/">Home</a></li><li><a href="/#games">Games</a></li><li>{esc(g['name'])}</li></ol>
    <div class="game-hero-grid">
      <div>
        <div class="app-head">
          <img src="{icon_src(g)}" alt="{esc(g['name'])} icon" width="108" height="108">
          <div><h1>{esc(g['name'])}</h1><div class="genre">{esc(g['genre'])}</div></div>
        </div>
        <p class="tagline">{esc(g['tagline'])}</p>
        <p class="lead">{esc(g['intro'])}</p>
        <div class="chips">{chips}</div>
        <div class="hero-cta">
          {cta_btn}
          <a class="btn btn-ghost" href="{privacy_url(g)}">{icon('file')}Privacy policy</a>
        </div>
      </div>
      {hero_art(g)}
    </div>
  </div>
</section>

<section class="section section-white">
  <div class="container">
    {section_head('Screenshots', 'See it in action')}
    <div class="shots {orient}">{strip}</div>
  </div>
</section>

{''.join(render_section(sec) for sec in g['sections'])}

<section class="section pt-0">
  <div class="container">
    {cta_band}
    <div class="more">
      <h2>More from {esc(STUDIO)}</h2>
      <div class="mini-grid">{more}</div>
    </div>
  </div>
</section>'''
    status = 'Available on Google Play' if g['live'] else 'Coming soon to Google Play'
    desc = f"{g['title']}: {g['short']} {status}."
    return page(games, f"{g['title']} | {STUDIO}", desc, game_url(g), f"/assets/img/{g['slug']}/feature.jpg",
                main, style=theme_style(g))


# ---------- Privacy page ----------

def plain_text(fragment):
    t = re.sub(r'<[^>]+>', ' ', fragment)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def legal_html(raw):
    """Turn the generator's <strong>/<br> layout into h2 sections without changing any wording."""
    t = re.sub(r'<!--.*?-->', '', raw, flags=re.S).strip()
    t = re.sub(r'^<strong>Privacy Policy</strong>', '', t)
    headings = []

    def to_h2(m):
        title = m.group(1)
        hid = slugify(html.unescape(title))
        headings.append((hid, title))
        return f'\n<h2 id="{hid}">{title}</h2>'

    t = re.sub(r'<br>\s*<strong>([^<]+)</strong>', to_h2, t)
    t = re.sub(r'<br>', '\n', t)
    t = re.sub(r'<p>\s*</p>', '', t)
    t = re.sub(r'\n{2,}', '\n', t).strip()
    # Wording must match the source exactly (only the page title moves into the hero).
    if plain_text(raw) != ('Privacy Policy ' + plain_text(t)):
        raise SystemExit('privacy text changed during conversion')
    return t, headings


def build_privacy(games, g):
    raw = (SRC / 'privacy' / f"{g['folder']}.html").read_text(encoding='utf-8')
    body, headings = legal_html(raw)
    toc = ''.join(f'<li><a href="#{hid}">{title}</a></li>' for hid, title in headings)
    main = f'''<section class="doc-hero">
  <div class="container">
    <ol class="breadcrumb"><li><a href="/">Home</a></li><li><a href="{game_url(g)}">{esc(g['name'])}</a></li><li>Privacy Policy</li></ol>
    <a class="doc-app" href="{game_url(g)}"><img src="{icon_src(g)}" alt="" width="30" height="30">{esc(g['title'])}</a>
    <h1>Privacy Policy</h1>
    <p>How the {esc(g['title'])} app for Android handles your information.</p>
  </div>
</section>

<div class="container doc-layout">
  <aside class="toc" aria-label="On this page">
    <p class="toc-title">On this page</p>
    <ol>{toc}</ol>
    <div class="toc-contact"><strong>Privacy questions?</strong><a href="mailto:{EMAIL}">{EMAIL}</a></div>
  </aside>
  <div>
    <details class="toc-mobile"><summary>On this page</summary><ol>{toc}</ol></details>
    <article class="doc">
{body}
    </article>
  </div>
</div>'''
    desc = f"Privacy policy for the {g['title']} app for Android by {STUDIO}."
    return page(games, f"Privacy Policy | {g['title']}", desc, privacy_url(g), f"/assets/img/{g['slug']}/feature.jpg",
                main, style=theme_style(g))


# ---------- 404 ----------

def build_404(games):
    main = f'''<section class="not-found">
  <div class="container">
    <div class="big grad-text">404</div>
    <h1>This page rolled away</h1>
    <p>The page you are looking for does not exist or has moved. Let's get you back to the games.</p>
    <a class="btn btn-primary" href="/">Back to home {icon('arrow')}</a>
  </div>
</section>'''
    return page(games, f'Page not found | {STUDIO}', 'This page could not be found.', '/404.html',
                '/assets/img/draw-rescue/feature.jpg', main)


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')
    print('wrote', rel)


def main():
    games = json.loads((SRC / 'games.json').read_text(encoding='utf-8'))
    write('index.html', build_home(games))
    write('404.html', build_404(games))
    for g in games:
        write(f"funfunnygames/{g['folder']}/index.html", build_game(games, g))
        write(f"funfunnygames/{g['folder']}/privacy.html", build_privacy(games, g))


if __name__ == '__main__':
    main()
