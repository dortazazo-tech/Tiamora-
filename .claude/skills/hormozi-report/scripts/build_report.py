#!/usr/bin/env python3
"""
Hormozi Report — dashboard renderer.

Takes a structured report.json and emits ONE self-contained .html file:
a long-form formal written report wrapped in a navigable dashboard shell.

Usage:
    python build_report.py report.json [-o "Output Name.html"]

The display and label faces (Antarctican, Carbon) plus the logo are base64-embedded
from an optional brand.config.json when one is present — base64 never
passes through model context, it goes straight from disk into the file. Missing
assets degrade to a system stack rather than failing. The BODY face (Outfit) is
not embedded and falls back to system-ui on a machine that lacks it; add an
`outfit_ttf` key to brand.config.json to bake it in.

Uppercase-only display faces are deliberately unsupported for labels: they render digits,
lowercase and punctuation as BLANK glyphs, which defeats browser font fallback
and silently erases every number. Do not add it back.

The output has no external requests: no CDN, no webfont link, no remote images.
It opens offline, prints clean, and can be handed to a client as one file.
"""
import sys, os, json, base64, argparse, html, re, datetime

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_BRAND = os.path.join(SKILL_ROOT, "brand.config.json")
_HOME_BRAND = os.path.expanduser("~/.claude/skills/hormozi-report/brand.config.json")
# The skill is vendored into this repo, so a brand config sitting next to it is the
# one to honour. Upstream's home-directory path stays as the fallback.
DEFAULT_BRAND = _SKILL_BRAND if os.path.isfile(_SKILL_BRAND) else _HOME_BRAND

FALLBACK_COLORS = {
    "bg": "#08080C", "ink": "#F5F5FA", "crypto_blue": "#2600EF", "purple": "#5001D6",
    "neon_yellow": "#FEFF20", "hot_pink": "#FE329B", "red_pink": "#FF0053", "grey": "#787878",
}


# ---------------------------------------------------------------- helpers

def expand(p):
    return os.path.expanduser(os.path.expandvars(p)) if p else p


def load_brand(path):
    path = expand(path)
    if not path or not os.path.exists(path):
        # Not a warning: the fallback is the supported default. Reserve "!" for
        # the citation-integrity warnings, which mean something is actually wrong.
        print(f"  · no brand config at {path} — using fallback palette + system fonts")
        return {"colors": dict(FALLBACK_COLORS), "fonts": {}, "logo_path": None}
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    colors = dict(FALLBACK_COLORS)
    colors.update(cfg.get("colors") or {})
    cfg["colors"] = colors
    return cfg


def font_face(family, path, weight=None):
    path = expand(path)
    if not path or not os.path.exists(path):
        return None
    ext = os.path.splitext(path)[1].lower()
    fmt = {".otf": "opentype", ".ttf": "truetype", ".woff": "woff", ".woff2": "woff2"}.get(ext, "opentype")
    mime = {".otf": "font/otf", ".ttf": "font/ttf", ".woff": "font/woff", ".woff2": "font/woff2"}.get(ext, "font/otf")
    with open(path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode()
    w = f"font-weight:{weight};" if weight else ""
    return (f"@font-face{{font-family:'{family}';{w}font-display:swap;"
            f"src:url(data:{mime};base64,{data}) format('{fmt}');}}")


def logo_uri(path):
    path = expand(path)
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode()
    ext = os.path.splitext(path)[1].lower()
    mime = "image/svg+xml" if ext == ".svg" else ("image/jpeg" if ext in (".jpg", ".jpeg") else "image/png")
    return f"data:{mime};base64,{data}"


def e(s):
    """Escape for HTML text nodes. NULs are dropped — rich() uses them as sentinels."""
    return html.escape("" if s is None else str(s).replace("\x00", ""), quote=True)


_CODE = re.compile(r"`([^`]+?)`", re.S)
_BOLD = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", re.S)
_ITAL = re.compile(r"(?<![*\w])\*(?=\S)([^*]+?)(?<=\S)\*(?![*\w])")
_STASH = re.compile(r"\x00(\d+)\x00")


def rich(s):
    """Escape, then re-enable a tiny markdown subset: **bold**, *italic*, `code`.

    `code` runs FIRST and its contents are parked behind a sentinel the emphasis
    passes cannot match, so a backtick span protects its own asterisks. Emphasis
    delimiters must hug non-space characters, which leaves stray asterisks in
    prose (arithmetic, globs, bullet lists) inert. Italic cannot span `**`, so
    ***triple*** no longer misnests into <strong><em>...</strong></em>.
    """
    out = e(s)
    stash = []

    def park(m):
        stash.append(m.group(1))
        return f"\x00{len(stash) - 1}\x00"

    out = _CODE.sub(park, out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _ITAL.sub(r"<em>\1</em>", out)
    return _STASH.sub(lambda m: f"<code>{stash[int(m.group(1))]}</code>", out)


def slug(s, fallback="s"):
    out = re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")
    return out or fallback


def hhmmss(seconds):
    """Human label for a cite. Out-of-range input returns None so the caller
    degrades to a generic label rather than manufacturing false agreement with
    the URL (clamping a negative to 0:00 would silently 'match' a t=0s link)."""
    try:
        n = int(float(seconds))
    except (TypeError, ValueError, OverflowError):
        return None
    if n < 0 or n > 86400 * 2:
        return None
    h, rem = divmod(n, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


_ALLOWED_HOSTS = ("https://www.youtube.com/", "https://youtube.com/", "https://youtu.be/",
                  "https://m.youtube.com/")


def safe_url(u):
    """Citation hrefs are restricted to YouTube over https.

    The product promise is that every link opens the original public video, so a
    host allowlist is the right strictness. Anything else -- javascript:, data:,
    a hallucinated URL shape -- degrades to the same no-link rendering that a
    missing timestamp_url already produces.
    """
    u = (u or "").strip()
    if u.lower().startswith(_ALLOWED_HOSTS):
        return u
    if u:
        print(f"  ! rejected non-YouTube citation URL: {u[:80]}", file=sys.stderr)
    return ""


def check_stamp(url, start_seconds):
    """Warn when the t= parameter disagrees with start_seconds. Non-fatal.

    report-spec.md tells the writer that a disagreement means the link is wrong;
    without this the highest-stakes failure in the tool is silent."""
    m = re.search(r"[?&]t=(\d+)", url or "")
    if not m:
        return
    try:
        declared = int(float(start_seconds))
    except (TypeError, ValueError):
        return
    if abs(int(m.group(1)) - declared) > 2:
        print(f"  ! citation mismatch: t={m.group(1)}s vs start_seconds={declared} — {url}",
              file=sys.stderr)


def paras(value):
    """Accept a string or list of strings; return a list of non-empty paragraphs."""
    if not value:
        return []
    if isinstance(value, str):
        return [p.strip() for p in value.split("\n\n") if p.strip()]
    return [str(p).strip() for p in value if str(p).strip()]


# ---------------------------------------------------------------- evidence

def subsections(sec):
    """Usable subsections only — a malformed entry is skipped, not fatal."""
    return [s for s in (sec.get("subsections") or []) if isinstance(s, dict)]


def evidence_items(sub):
    """Usable evidence entries only: dicts carrying a quote or a link."""
    return [ev for ev in (sub.get("evidence") or [])
            if isinstance(ev, dict) and (ev.get("quote") or ev.get("timestamp_url"))]


def collect_sources(sections):
    """Group every cited passage by video, preserving order of first appearance."""
    by_video = {}
    for sec in sections:
        for sub in subsections(sec):
            for ev in evidence_items(sub):
                vid = ev.get("episode_id") or ev.get("timestamp_url") or "unknown"
                slot = by_video.setdefault(vid, {
                    "episode_id": ev.get("episode_id"),
                    "title": ev.get("title") or "Untitled",
                    "published": ev.get("published"),
                    "cites": [],
                })
                slot["cites"].append({
                    "timestamp_url": ev.get("timestamp_url"),
                    "start_seconds": ev.get("start_seconds"),
                    "section": sec.get("title"),
                })
    return list(by_video.values())


def render_evidence(ev, idx):
    url = safe_url(ev.get("timestamp_url"))
    check_stamp(url, ev.get("start_seconds"))
    stamp = hhmmss(ev.get("start_seconds"))
    label = stamp or "source"
    quote = (ev.get("quote") or "").strip()
    # Keep quotes short — policy is paraphrase-and-link, not wholesale reproduction.
    if len(quote) > 480:
        quote = quote[:477].rstrip() + "…"
    meta = " &middot; ".join(x for x in [e(ev.get("title")), e(ev.get("published"))] if x)
    link = (f'<a class="ts" href="{e(url)}" target="_blank" rel="noopener noreferrer">'
            f'<span class="play">&#9654;</span>{e(label)}</a>') if url else ""
    # A citation may carry a link without a pull-quote; render the caption alone
    # rather than an empty bordered box that reads as a broken quote.
    block = f'<blockquote>{e(quote)}</blockquote>' if quote else ""
    return (
        f'<figure class="ev{"" if quote else " ev-bare"}" data-ev="{idx}">'
        f'{block}'
        f'<figcaption><span class="ev-meta">{meta}</span>{link}</figcaption>'
        f'</figure>'
    )


# ---------------------------------------------------------------- sections

def render_constraint_board(constraints, valid_ids):
    """The three ranked constraints, as the first thing the reader touches.

    Each card is a button that scrolls to the section analysing it. A target
    that does not resolve to a real anchor is dropped rather than shipped as a
    dead click.
    """
    cards = []
    for i, c in enumerate(sorted(
            [x for x in constraints if isinstance(x, dict)],
            key=lambda x: x.get("rank") or 99)[:3], 1):
        rank = c.get("rank") or i
        target = c.get("target") if c.get("target") in valid_ids else ""
        try:
            impact = max(0, min(100, int(float(c.get("impact", 0)))))
        except (TypeError, ValueError):
            impact = 0
        metric = (f'<span class="cmetric">{rich(c.get("metric"))}</span>'
                  if c.get("metric") else "")
        go = '<span class="cgo">Jump to analysis &rarr;</span>' if target else ""
        cards.append(
            f'<button class="ccard r{rank}" data-target="{e(target)}" type="button">'
            f'<span class="rank">{e(rank)}</span>'
            f'<h3>{rich(c.get("title") or "Untitled")}</h3>'
            f'<p>{rich(c.get("note") or "")}</p>{metric}'
            f'<span class="meter"><i data-w="{impact}"></i></span>{go}'
            f'</button>')
    if not cards:
        return ""
    return (
        '<div class="board"><div class="board-head">'
        '<h2>Top three constraints</h2>'
        '<span class="board-hint">Ranked by impact &middot; click to jump</span>'
        f'</div><div class="cboard">{"".join(cards)}</div></div>')


def render_action_panel(actions):
    """The action plan as a working checklist rather than a table to admire."""
    rows = [a for a in (actions or []) if isinstance(a, dict) and a.get("action")]
    if not rows:
        return ""
    items = []
    for i, a in enumerate(rows):
        meta = " &middot; ".join(x for x in [e(a.get("owner")), e(a.get("due"))] if x)
        why = f'<div class="awhy">{rich(a.get("why"))}</div>' if a.get("why") else ""
        items.append(
            f'<li><button class="acheck" type="button" data-id="a{i}" aria-pressed="false" '
            f'aria-label="Mark action {i + 1} complete"></button>'
            f'<span class="atext"><span class="aact">{rich(a.get("action"))}</span>{why}</span>'
            + (f'<span class="ameta">{meta}</span>' if meta else "") + '</li>')
    return (
        '<div class="apanel">'
        '<svg width="0" height="0" style="position:absolute"><defs>'
        '<linearGradient id="gr" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0%" stop-color="var(--blue)"/>'
        '<stop offset="100%" stop-color="var(--purple)"/></linearGradient></defs></svg>'
        '<div class="ap-head">'
        '<span class="ring"><svg width="54" height="54">'
        '<circle class="bg" cx="27" cy="27" r="24"></circle>'
        '<circle class="fg" cx="27" cy="27" r="24"></circle></svg>'
        f'<b>0/{len(rows)}</b></span>'
        '<span><h2>Action plan</h2>'
        '<p>Ordered by impact on the constraint. Tick them off — progress is remembered.</p>'
        '</span></div>'
        f'<ul class="alist">{"".join(items)}</ul>'
        '<div class="ap-foot">Full detail, owners and review cadence in the sections below.</div>'
        '</div>')


def render_subsection(sub, sec_id, n):
    sid = sub.get("id") or f"{sec_id}-{n}"
    out = [f'<article class="sub" id="{e(sid)}">']
    out.append(f'<button class="sub-head" type="button"><span class="chev"></span>'
               f'<h3>{rich(sub.get("title") or "Untitled")}</h3></button>')
    out.append('<div class="sub-body">')

    if sub.get("plain"):
        out.append(f'<p class="plain"><span class="plain-tag">In plain terms</span>{rich(sub["plain"])}</p>')

    for p in paras(sub.get("body")):
        out.append(f"<p>{rich(p)}</p>")

    ev_list = evidence_items(sub)
    if ev_list:
        # Evidence sits behind a toggle so the argument reads as prose and the
        # reader opens the receipts when they want them. The count is always
        # visible, so nothing is hidden — only deferred. Print forces it open.
        label = f'{len(ev_list)} source passage{"s" if len(ev_list) != 1 else ""}'
        wrap_id = f"ev-{slug(sid, 'x')}"
        out.append('<div class="ev-block">')
        out.append(f'<button class="evtoggle" type="button" data-for="{e(wrap_id)}" '
                   f'data-label="{e(label)}">Show {e(label)}</button>')
        out.append(f'<div class="ev-wrap" id="{e(wrap_id)}">')
        out.append('<div class="ev-head"><span class="lbl lbl-src">Source evidence</span>'
                   f'<span class="ev-count">{e(label)}</span></div>')
        for i, ev in enumerate(ev_list):
            out.append(render_evidence(ev, i))
        out.append("</div></div>")

    if sub.get("synthesis"):
        out.append('<div class="synth"><span class="lbl lbl-syn">Our reading</span>')
        for p in paras(sub["synthesis"]):
            out.append(f"<p>{rich(p)}</p>")
        out.append("</div>")

    call = sub.get("callout")
    if call and call.get("text"):
        kind = slug(call.get("type") or "note", "note")
        out.append(f'<aside class="callout c-{e(kind)}"><span class="c-kind">{e(call.get("type") or "Note")}</span>'
                   f'<p>{rich(call["text"])}</p></aside>')

    out.append("</div></article>")
    return "\n".join(out)


def render_section(sec, n):
    sec_id = sec.get("id") or slug(sec.get("title"), f"section-{n}")
    subs = subsections(sec)
    out = [f'<section class="sec" id="{e(sec_id)}">']
    out.append('<header class="sec-head">')
    out.append(f'<span class="sec-num">{n:02d}</span>')
    out.append(f'<h2>{rich(sec.get("title") or "Untitled")}</h2>')
    if sec.get("summary"):
        out.append(f'<p class="sec-sum">{rich(sec["summary"])}</p>')
    out.append("</header>")
    for i, sub in enumerate(subs, 1):
        out.append(render_subsection(sub, sec_id, i))
    out.append("</section>")
    return "\n".join(out), sec_id, subs


RESERVED_IDS = {"snapshot", "actions", "scorecard", "sources", "assumptions", "navsearch"}


def assign_ids(sections):
    """Stamp a unique, concrete `id` onto every section and subsection.

    Runs once, before any rendering, so nav and body agree by construction.
    Without it two sections sharing a title slug to the same anchor and the
    second nav link jumps to the first; a user section titled "Sources" would
    collide with the built-in appendix the same way.
    """
    seen = set(RESERVED_IDS)

    def unique(base):
        cand, i = base, 2
        while cand in seen:
            cand, i = f"{base}-{i}", i + 1
        seen.add(cand)
        return cand

    for n, sec in enumerate(sections, 1):
        sec["id"] = unique(sec.get("id") or slug(sec.get("title"), f"section-{n}"))
        for i, sub in enumerate(subsections(sec), 1):
            if True:
                sub["id"] = unique(sub.get("id") or f"{sec['id']}-{i}")


def render_nav(sections):
    items = []
    for n, sec in enumerate(sections, 1):
        sec_id = sec.get("id") or slug(sec.get("title"), f"section-{n}")
        subs = subsections(sec)
        kids = []
        for i, sub in enumerate(subs, 1):
            sid = sub.get("id") or f"{sec_id}-{i}"
            kids.append(f'<li><a href="#{e(sid)}" class="nav-sub">{e(sub.get("title") or "Untitled")}</a></li>')
        kid_html = f'<ul class="nav-kids">{"".join(kids)}</ul>' if kids else ""
        items.append(
            f'<li class="nav-group">'
            f'<a href="#{e(sec_id)}" class="nav-top"><span class="nav-n">{n:02d}</span>'
            f'<span>{e(sec.get("title") or "Untitled")}</span></a>{kid_html}</li>'
        )
    return "".join(items)


NA_CELL = '<span class="na">&mdash;</span>'


def render_table(rows, cols):
    rows = [r for r in (rows or []) if isinstance(r, dict)]
    if not rows:
        return ""
    head = "".join(f"<th>{e(label)}</th>" for _, label in cols)
    body = []
    for r in rows:
        cells = []
        for key, _ in cols:
            val = r.get(key)
            # NA_CELL is hoisted out of the f-string deliberately: a backslash and a
            # reused quote delimiter inside a replacement field only became legal in
            # Python 3.12 (PEP 701), and this file claims 3.11+.
            cells.append(f"<td>{rich(val) if val not in (None, '') else NA_CELL}</td>")
        body.append(f"<tr>{''.join(cells)}</tr>")
    return f'<div class="tw"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


# ---------------------------------------------------------------- template

CSS = r"""
__ANTARCTICAN_FACE__
__CARBON_FACE__

/* The label face must have a full character set. An uppercase-A-Z-only face —
   defines digits, lowercase and punctuation as BLANK glyphs, so the browser
   never falls back and every number silently disappears. Verified on the real
   font file. Do not reintroduce it for any string that can contain a digit. */
:root{
  --bg:__C_BG__; --ink:__C_INK__; --blue:__C_BLUE__; --purple:__C_PURPLE__;
  --yellow:__C_YELLOW__; --pink:__C_PINK__; --red:__C_RED__; --grey:__C_GREY__;
  --panel:#0E0E15; --panel2:#12121C; --line:#20202E;
  --head:'Antarctican Headline','Anton',system-ui,sans-serif;
  --sub:'Carbon',ui-monospace,'Share Tech Mono',SFMono-Regular,Menlo,monospace;
  --body:'Outfit','Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
  --grad:linear-gradient(103deg,var(--blue),var(--purple));
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);
  font-size:17px;line-height:1.72;-webkit-font-smoothing:antialiased}

/* ---------- shell ---------- */
.shell{display:grid;grid-template-columns:300px minmax(0,1fr);min-height:100vh}
.rail{position:sticky;top:0;height:100vh;overflow-y:auto;background:var(--panel);
  border-right:1px solid var(--line);padding:26px 18px 60px}
.rail::-webkit-scrollbar{width:8px}
.rail::-webkit-scrollbar-thumb{background:#25253a;border-radius:4px}
.brand{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.brand img{width:30px;height:30px;object-fit:contain}
.brand .bolt{width:30px;height:30px;border-radius:8px;background:var(--grad)}
.brand b{font-family:var(--head);font-size:16px;letter-spacing:.02em;font-weight:600}
.rail .kicker{font-family:var(--sub);font-size:10.5px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--grey);margin:0 0 22px 40px}
.navsearch{width:100%;background:var(--panel2);border:1px solid var(--line);color:var(--ink);
  border-radius:9px;padding:9px 11px;font-family:var(--body);font-size:13.5px;margin-bottom:16px}
.navsearch::placeholder{color:#55556a}
.navsearch:focus{outline:none;border-color:var(--purple)}
nav ul{list-style:none;margin:0;padding:0}
.nav-group{margin-bottom:3px}
.nav-top{display:flex;gap:10px;align-items:baseline;text-decoration:none;color:#B9B9CC;
  font-size:13.5px;font-weight:600;padding:7px 9px;border-radius:8px;line-height:1.35}
.nav-top:hover{background:#181826;color:#fff}
.nav-n{font-family:var(--sub);font-size:10px;color:var(--grey);letter-spacing:.08em;flex:0 0 auto}
.nav-kids{margin:1px 0 8px 30px;border-left:1px solid var(--line);padding-left:11px}
.nav-sub{display:block;text-decoration:none;color:#7A7A93;font-size:12.5px;
  padding:4.5px 7px;border-radius:6px;line-height:1.4}
.nav-sub:hover{color:#fff;background:#181826}
.nav-top.on{color:#fff;background:#1B1B2B}
.nav-sub.on{color:var(--yellow)}
.nav-group.hide,.nav-kids li.hide{display:none}

/* ---------- main ---------- */
main{padding:0 0 120px;max-width:900px}
.wrap{padding:0 62px}

.hero{padding:58px 62px 40px;border-bottom:1px solid var(--line);position:relative;overflow:hidden}
.hero::after{content:"";position:absolute;inset:auto auto -140px -120px;width:380px;height:380px;
  background:var(--grad);filter:blur(120px);opacity:.20;pointer-events:none}
.eyebrow{font-family:var(--sub);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--grey);margin:0 0 16px}
.hero h1{font-family:var(--head);font-weight:600;font-size:clamp(34px,4.4vw,52px);
  line-height:1.08;margin:0 0 20px;letter-spacing:-.01em}
.hero .lede{font-size:19px;color:#C8C8DA;margin:0;max-width:62ch;line-height:1.65}
.hero-meta{display:flex;flex-wrap:wrap;gap:9px;margin-top:26px}
.chip{font-family:var(--sub);font-size:11px;letter-spacing:.09em;text-transform:uppercase;
  border:1px solid var(--line);background:var(--panel);color:#9C9CB4;
  padding:6px 12px;border-radius:999px}
.chip.on{border-color:transparent;background:var(--grad);color:#fff}

.verdict{margin:34px 0 0;padding:26px 28px;border-radius:16px;background:var(--panel);
  border:1px solid var(--line);border-left:3px solid transparent;
  border-image:var(--grad) 1;border-image-slice:1}
.verdict .lbl{margin-bottom:12px}
.verdict h2{font-family:var(--head);font-weight:600;font-size:25px;line-height:1.22;margin:0 0 12px}
.verdict p{margin:0;color:#C2C2D6}

.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:12px;margin:30px 0 0}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:17px 18px}
.tile .t-l{font-family:var(--sub);font-size:10px;letter-spacing:.15em;text-transform:uppercase;
  color:var(--grey);display:block;margin-bottom:9px}
.tile .t-v{font-family:var(--head);font-weight:600;font-size:30px;line-height:1;
  background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.tile .t-n{display:block;font-size:12.5px;color:#82829A;margin-top:9px;line-height:1.5}

/* ---------- sections ---------- */
.sec{padding-top:64px;scroll-margin-top:20px}
.sec-head{margin-bottom:8px}
.sec-num{font-family:var(--sub);font-size:11px;letter-spacing:.2em;color:var(--grey);display:block;margin-bottom:9px}
.sec h2{font-family:var(--head);font-weight:600;font-size:31px;line-height:1.16;margin:0;letter-spacing:-.005em}
.sec-sum{color:#9E9EB6;font-size:16px;margin:11px 0 0;max-width:64ch}
.sub{padding-top:34px;scroll-margin-top:20px}
.sub h3{font-family:var(--body);font-weight:600;font-size:20.5px;line-height:1.35;
  margin:0 0 13px;color:#fff}
.sub p{margin:0 0 16px;color:#CFCFDF}
.sub code{font-family:var(--sub);font-size:.88em;background:#1A1A28;padding:2px 6px;border-radius:5px;color:var(--yellow)}
.sub strong{color:#fff;font-weight:600}

.plain{background:#101019;border:1px solid var(--line);border-radius:12px;
  padding:15px 18px;font-size:16px;color:#BFBFD4 !important}
.plain-tag{display:block;font-family:var(--sub);font-size:10px;letter-spacing:.15em;
  text-transform:uppercase;color:var(--yellow);margin-bottom:7px}

.lbl{display:inline-block;font-family:var(--sub);font-size:10px;letter-spacing:.15em;
  text-transform:uppercase;padding:3px 9px;border-radius:5px}
.lbl-src{background:rgba(38,0,239,.20);color:#9E93FF;border:1px solid rgba(80,1,214,.45)}
.lbl-syn{background:rgba(254,255,32,.09);color:var(--yellow);border:1px solid rgba(254,255,32,.28)}

.ev-block{margin:20px 0 22px}
.ev-head{display:flex;align-items:center;gap:11px;margin-bottom:11px}
.ev-count{font-size:11.5px;color:var(--grey);font-family:var(--sub);letter-spacing:.06em}
.ev{margin:0 0 9px;background:var(--panel2);border:1px solid var(--line);border-radius:12px;
  padding:16px 18px;transition:border-color .15s}
.ev:hover{border-color:#2E2E45}
.ev blockquote{margin:0;font-size:15.5px;line-height:1.68;color:#B4B4CA;font-style:italic}
.ev blockquote::before{content:"\201C";color:var(--purple);font-size:24px;line-height:0;
  vertical-align:-4px;margin-right:2px}
.ev figcaption{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;
  gap:10px;margin-top:13px;padding-top:12px;border-top:1px solid var(--line)}
.ev-bare figcaption{margin-top:0;padding-top:0;border-top:none}
.ev-meta{font-size:12px;color:#77778E;line-height:1.45}
.ts{display:inline-flex;align-items:center;gap:6px;text-decoration:none;font-family:var(--sub);
  font-size:11.5px;letter-spacing:.05em;color:#fff;background:var(--grad);
  padding:5px 11px;border-radius:999px;white-space:nowrap}
.ts:hover{opacity:.88}
.ts .play{font-size:8px}

.synth{margin:20px 0 22px;padding:17px 20px;border-radius:12px;
  background:rgba(254,255,32,.035);border:1px solid rgba(254,255,32,.16)}
.synth p{margin:11px 0 0;color:#C6C6D8}
.synth p:first-of-type{margin-top:11px}

.callout{margin:20px 0;padding:16px 19px;border-radius:12px;background:var(--panel);
  border:1px solid var(--line);border-left:3px solid var(--grey)}
.callout p{margin:7px 0 0;color:#C6C6D8}
.c-kind{font-family:var(--sub);font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--grey)}
.c-action{border-left-color:var(--yellow)} .c-action .c-kind{color:var(--yellow)}
.c-risk{border-left-color:var(--red)}     .c-risk .c-kind{color:var(--red)}
.c-note{border-left-color:var(--purple)}  .c-note .c-kind{color:#9E93FF}

/* ---------- tables ---------- */
.tw{overflow-x:auto;margin:20px 0;border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;min-width:520px;font-size:14.5px}
th{font-family:var(--sub);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--grey);text-align:left;padding:13px 16px;background:var(--panel2);
  border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:13px 16px;border-bottom:1px solid var(--line);color:#C4C4D6;vertical-align:top}
tr:last-child td{border-bottom:none}
.na{color:#4A4A5E}
.st{font-family:var(--sub);font-size:10px;letter-spacing:.1em;text-transform:uppercase;
  padding:2px 8px;border-radius:4px;white-space:nowrap}
.st-verified{background:rgba(38,0,239,.2);color:#9E93FF}
.st-inferred{background:rgba(254,255,32,.1);color:var(--yellow)}
.st-missing{background:rgba(255,0,83,.12);color:#FF6B96}

/* ---------- sources ---------- */
.srcgrid{display:grid;gap:10px;margin-top:20px}
.srccard{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.srccard h4{margin:0 0 4px;font-size:15.5px;font-weight:600;color:#fff;line-height:1.4}
.srccard .pub{font-size:12px;color:var(--grey);font-family:var(--sub);letter-spacing:.05em}
.stamps{display:flex;flex-wrap:wrap;gap:7px;margin-top:12px}

.foot{margin-top:70px;padding:26px 62px 0;border-top:1px solid var(--line);
  font-size:12.5px;color:#63637A;line-height:1.7}
.foot a{color:#8C8CA6}

.empty{color:var(--grey);font-style:italic}
.assumps{color:#CFCFDF;padding-left:20px;margin:0}
.assumps li{margin-bottom:9px}

/* ---------- reading progress ---------- */
.prog{position:fixed;top:0;left:0;height:2px;width:0;z-index:60;background:var(--grad);
  transition:width .1s linear}

/* ---------- constraint board ---------- */
.board{margin:34px 0 0}
.board-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;
  margin-bottom:14px;flex-wrap:wrap}
.board-head h2{font-family:var(--head);font-weight:600;font-size:23px;margin:0}
.board-hint{font-family:var(--sub);font-size:10.5px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--grey)}
.cboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:12px}
.ccard{position:relative;display:block;width:100%;text-align:left;cursor:pointer;
  background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:18px 19px 17px;font:inherit;color:inherit;overflow:hidden;
  transition:transform .16s cubic-bezier(.2,.8,.3,1),border-color .16s,box-shadow .16s}
.ccard::before{content:"";position:absolute;inset:0 auto 0 0;width:3px;background:var(--grad);
  opacity:.75}
.ccard:hover{transform:translateY(-3px);border-color:#33334d;
  box-shadow:0 10px 28px -14px rgba(80,1,214,.75)}
.ccard:focus-visible{outline:2px solid var(--purple);outline-offset:2px}
.ccard .rank{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;
  border-radius:7px;background:var(--grad);color:#fff;font-family:var(--sub);font-size:11px;
  margin-bottom:11px}
.ccard.r2 .rank,.ccard.r3 .rank{background:#1D1D2B;color:#9C9CB4;border:1px solid var(--line)}
.ccard.r2::before,.ccard.r3::before{background:#2A2A3E;opacity:1}
.ccard h3{font-family:var(--body);font-weight:600;font-size:17.5px;line-height:1.3;
  margin:0 0 7px;color:#fff}
.ccard p{margin:0;font-size:13.5px;line-height:1.55;color:#8E8EA6}
.ccard .cmetric{font-family:var(--sub);font-size:11px;letter-spacing:.06em;color:var(--yellow);
  display:block;margin-top:9px}
.meter{height:3px;border-radius:2px;background:#1C1C2A;margin-top:14px;overflow:hidden}
.meter i{display:block;height:100%;background:var(--grad);border-radius:2px;
  width:0;transition:width .9s cubic-bezier(.2,.8,.3,1)}
.ccard.r2 .meter i,.ccard.r3 .meter i{background:#4A4A6B}
.cgo{font-family:var(--sub);font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  color:#6E6E8A;margin-top:12px;display:block}
.ccard:hover .cgo{color:var(--yellow)}
@keyframes flash{0%,100%{box-shadow:0 0 0 0 rgba(80,1,214,0)}
  25%{box-shadow:0 0 0 3px rgba(80,1,214,.55)}}
.flash{animation:flash 1.1s ease-out}

/* ---------- action panel ---------- */
.apanel{margin:30px 0 0;background:var(--panel);border:1px solid var(--line);
  border-radius:16px;padding:22px 24px}
.ap-head{display:flex;align-items:center;gap:16px;margin-bottom:16px}
.ring{position:relative;flex:0 0 auto;width:54px;height:54px}
.ring svg{transform:rotate(-90deg);display:block}
.ring circle{fill:none;stroke-width:5}
.ring .bg{stroke:#1D1D2B}
.ring .fg{stroke:url(#gr);stroke-linecap:round;transition:stroke-dashoffset .5s ease}
.ring b{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-family:var(--sub);font-size:12px;color:#fff}
.ap-head h2{font-family:var(--head);font-weight:600;font-size:22px;margin:0 0 3px}
.ap-head p{margin:0;font-size:13px;color:var(--grey)}
.alist{list-style:none;margin:0;padding:0}
.alist li{display:flex;gap:13px;align-items:flex-start;padding:12px 0;
  border-top:1px solid var(--line)}
.alist li:first-child{border-top:none}
.acheck{flex:0 0 auto;width:21px;height:21px;margin-top:1px;border-radius:6px;cursor:pointer;
  border:1px solid #34344d;background:var(--panel2);display:flex;align-items:center;
  justify-content:center;color:transparent;font-size:11px;transition:.15s}
.acheck:hover{border-color:var(--purple)}
.acheck[aria-pressed="true"]{background:var(--grad);border-color:transparent;color:#fff}
.atext{flex:1;min-width:0}
.atext .aact{font-size:15px;color:#E4E4F0;line-height:1.5;font-weight:500}
.atext .awhy{font-size:13px;color:#7E7E96;line-height:1.55;margin-top:3px}
.alist li.done .aact{color:#5C5C74;text-decoration:line-through}
.alist li.done .awhy{color:#4A4A5E}
.ameta{flex:0 0 auto;font-family:var(--sub);font-size:10px;letter-spacing:.08em;
  text-transform:uppercase;color:#6E6E8A;border:1px solid var(--line);
  padding:3px 8px;border-radius:5px;white-space:nowrap}
.ap-foot{margin-top:15px;padding-top:13px;border-top:1px solid var(--line);
  font-size:12px;color:#5E5E76}

/* ---------- collapse / evidence toggle ---------- */
.sub-head{display:flex;align-items:flex-start;gap:11px;cursor:pointer;width:100%;
  background:none;border:none;padding:0;text-align:left;font:inherit;color:inherit}
.sub-head:focus-visible{outline:2px solid var(--purple);outline-offset:3px;border-radius:6px}
.chev{flex:0 0 auto;margin-top:6px;width:9px;height:9px;border-right:1.5px solid #6E6E8A;
  border-bottom:1.5px solid #6E6E8A;transform:rotate(45deg);transition:transform .2s}
.sub.closed .chev{transform:rotate(-45deg)}
.sub-head:hover .chev{border-color:var(--yellow)}
.sub.closed .sub-body{display:none}
.evtoggle{display:inline-flex;align-items:center;gap:8px;cursor:pointer;font:inherit;
  font-family:var(--sub);font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:#9E93FF;background:rgba(38,0,239,.13);border:1px solid rgba(80,1,214,.4);
  padding:7px 13px;border-radius:8px;transition:.15s}
.evtoggle:hover{background:rgba(38,0,239,.24);color:#fff}
.ev-wrap{display:none;margin-top:11px}
.ev-wrap.open{display:block}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:26px 0 0}
.minibtn{cursor:pointer;font:inherit;font-family:var(--sub);font-size:10.5px;letter-spacing:.1em;
  text-transform:uppercase;color:#8E8EA6;background:var(--panel);border:1px solid var(--line);
  padding:7px 12px;border-radius:7px;transition:.15s}
.minibtn:hover{color:#fff;border-color:#33334d}

/* ---------- responsive ---------- */
@media (max-width:980px){
  .shell{grid-template-columns:1fr}
  .rail{position:static;height:auto;border-right:none;border-bottom:1px solid var(--line);padding-bottom:22px}
  .nav-kids{display:none}
  .hero{padding:36px 24px 30px}
  .wrap,.foot{padding-left:24px;padding-right:24px}
  main{max-width:none}
}

/* ---------- print ---------- */
@media print{
  body{background:#fff;color:#111;font-size:11.5pt}
  .rail,.navsearch,.hero::after{display:none !important}
  .shell{display:block}
  .hero,.wrap,.foot{padding:0 0 12pt}
  .hero h1,.sec h2,.verdict h2{color:#000}
  .tile,.ev,.srccard,.callout,.verdict,.plain,.synth,.tw{
    background:#fff !important;border:1px solid #CCC !important;break-inside:avoid}
  .tile .t-v{color:#000 !important;-webkit-text-fill-color:#000}
  .sub p,.ev blockquote,td,.sec-sum{color:#222 !important}
  /* Everything below was white-on-white before. The synthesis marker and the
     inferred badge are the document's two integrity signals — losing them in a
     PDF is worse than losing decoration. */
  .sub h3,.srccard h4,.sub strong,.callout .c-kind,.sec-num,th{color:#000 !important}
  .sub code{background:#F2F2F2 !important;color:#111 !important}
  .lbl,.st,.plain-tag,.chip{color:#111 !important;background:none !important;
    border:1px solid #999 !important;-webkit-text-fill-color:#111}
  .synth p,.callout p,.verdict p,.hero .lede,.tile .t-n,.ev-meta,
  .srccard .pub,.assumps li{color:#222 !important}
  .plain{color:#222 !important}
  .na{color:#777 !important}
  .ts{background:none !important;color:#00E !important;padding:0}
  .ts::after{content:" (" attr(href) ")";font-size:8pt;color:#555;word-break:break-all}
  .sec{page-break-before:auto;padding-top:22pt}
  a{text-decoration:underline}
  /* Interactive chrome collapses to a flat document — every collapsed panel is
     forced open so a PDF never silently omits evidence. */
  .prog,.evtoggle,.bar,.chev,.cgo,.acheck,.board-hint{display:none !important}
  .sub.closed .sub-body,.ev-wrap{display:block !important}
  .ccard,.apanel,.alist li{background:#fff !important;border:1px solid #CCC !important;
    break-inside:avoid;transform:none !important;box-shadow:none !important}
  .ccard::before{background:#666 !important}
  .ccard h3,.ap-head h2,.board-head h2,.atext .aact{color:#000 !important}
  .ccard p,.atext .awhy,.ameta,.ap-foot{color:#333 !important}
  .ccard .rank{background:#000 !important;color:#fff !important;
    -webkit-text-fill-color:#fff;border:none !important}
  .ccard .cmetric{color:#111 !important}
  .meter{border:1px solid #999 !important;background:#fff !important}
  .meter i{background:#555 !important}
  .ring{display:none}
  .alist li.done .aact{text-decoration:line-through;color:#666 !important}
}
"""

JS = r"""
(function(){
  // Scrollspy — highlight the section/subsection currently in view.
  var links = [].slice.call(document.querySelectorAll('.nav-top,.nav-sub'));
  var map = {};
  links.forEach(function(a){
    var id = a.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) map[id] = {link:a, el:el};
  });
  var ids = Object.keys(map);
  function spy(){
    var best=null, bestTop=-Infinity, probe=window.innerHeight*0.22;
    ids.forEach(function(id){
      var top = map[id].el.getBoundingClientRect().top;
      if (top <= probe && top > bestTop){ bestTop = top; best = id; }
    });
    links.forEach(function(a){ a.classList.remove('on'); });
    if (best){
      map[best].link.classList.add('on');
      var grp = map[best].link.closest('.nav-group');
      if (grp){ var t = grp.querySelector('.nav-top'); if (t) t.classList.add('on'); }
    }
  }
  var tick=false;
  window.addEventListener('scroll', function(){
    if (tick) return; tick=true;
    requestAnimationFrame(function(){ spy(); tick=false; });
  }, {passive:true});
  spy();

  // Reading progress.
  var prog = document.getElementById('prog');
  function progress(){
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    if (prog) prog.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
  }
  window.addEventListener('scroll', progress, {passive:true});
  window.addEventListener('resize', progress);
  progress();

  // Constraint board — jump to the section that analyses this constraint,
  // then flash it so the reader lands with their eye in the right place.
  function goTo(id){
    var el = document.getElementById(id);
    if (!el) return;
    var sub = el.closest ? el.closest('.sub') : null;
    if (sub && sub.classList.contains('closed')) sub.classList.remove('closed');
    el.scrollIntoView({behavior:'smooth', block:'start'});
    el.classList.remove('flash');
    void el.offsetWidth;
    el.classList.add('flash');
  }
  [].slice.call(document.querySelectorAll('.ccard')).forEach(function(c){
    c.addEventListener('click', function(){ goTo(c.getAttribute('data-target')); });
  });

  // Impact meters fill once on first view.
  function fillMeters(){
    [].slice.call(document.querySelectorAll('.meter i')).forEach(function(m){
      m.style.width = (m.getAttribute('data-w') || 0) + '%';
    });
  }
  setTimeout(fillMeters, 220);

  // Action checklist. State persists per report where the browser allows it —
  // file:// origins sometimes refuse storage, so every access is guarded and the
  // list simply falls back to in-session state.
  var KEY = 'hormozi-report:' + (document.title || 'report');
  function load(){
    try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch(e){ return {}; }
  }
  function save(s){ try { localStorage.setItem(KEY, JSON.stringify(s)); } catch(e){} }
  var state = load();

  var ring = document.querySelector('.ring .fg');
  var ringTxt = document.querySelector('.ring b');
  var C = 2 * Math.PI * 24;
  if (ring){ ring.style.strokeDasharray = C; }

  function paint(){
    var boxes = [].slice.call(document.querySelectorAll('.acheck'));
    var done = 0;
    boxes.forEach(function(b){
      var on = !!state[b.getAttribute('data-id')];
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.textContent = on ? '✓' : '';
      b.closest('li').classList.toggle('done', on);
      if (on) done++;
    });
    if (ring && boxes.length){
      ring.style.strokeDashoffset = C * (1 - done / boxes.length);
    }
    if (ringTxt) ringTxt.textContent = done + '/' + boxes.length;
  }
  [].slice.call(document.querySelectorAll('.acheck')).forEach(function(b){
    b.addEventListener('click', function(){
      var id = b.getAttribute('data-id');
      state[id] = !state[id];
      save(state); paint();
    });
  });
  paint();

  // Collapsible subsections + on-demand evidence.
  [].slice.call(document.querySelectorAll('.sub-head')).forEach(function(h){
    h.addEventListener('click', function(){ h.closest('.sub').classList.toggle('closed'); });
  });
  [].slice.call(document.querySelectorAll('.evtoggle')).forEach(function(t){
    t.addEventListener('click', function(e){
      e.stopPropagation();
      var wrap = document.getElementById(t.getAttribute('data-for'));
      if (!wrap) return;
      var open = wrap.classList.toggle('open');
      t.textContent = (open ? 'Hide ' : 'Show ') + t.getAttribute('data-label');
    });
  });
  function setAll(closed){
    [].slice.call(document.querySelectorAll('.sub')).forEach(function(s){
      s.classList.toggle('closed', closed);
    });
  }
  var ea = document.getElementById('expandall'), ca = document.getElementById('collapseall'),
      es = document.getElementById('evall');
  if (ea) ea.addEventListener('click', function(){ setAll(false); });
  if (ca) ca.addEventListener('click', function(){ setAll(true); });
  if (es) es.addEventListener('click', function(){
    var wraps = [].slice.call(document.querySelectorAll('.ev-wrap'));
    var anyClosed = wraps.some(function(w){ return !w.classList.contains('open'); });
    wraps.forEach(function(w){ w.classList.toggle('open', anyClosed); });
    [].slice.call(document.querySelectorAll('.evtoggle')).forEach(function(t){
      t.textContent = (anyClosed ? 'Hide ' : 'Show ') + t.getAttribute('data-label');
    });
    es.textContent = anyClosed ? 'Hide all evidence' : 'Show all evidence';
  });

  // Everything opens for print, then restores.
  function beforePrint(){
    document.body.setAttribute('data-restore',
      [].slice.call(document.querySelectorAll('.sub.closed')).map(function(s){
        return s.id; }).join(','));
    setAll(false);
    [].slice.call(document.querySelectorAll('.ev-wrap')).forEach(function(w){
      w.classList.add('open'); });
  }
  window.addEventListener('beforeprint', beforePrint);
  if (window.matchMedia){
    var mq = window.matchMedia('print');
    if (mq.addEventListener) mq.addEventListener('change', function(ev){ if (ev.matches) beforePrint(); });
  }

  // Nav filter — type to narrow the topic hierarchy.
  var box = document.getElementById('navsearch');
  if (box){
    box.addEventListener('input', function(){
      var q = box.value.trim().toLowerCase();
      document.querySelectorAll('.nav-group').forEach(function(g){
        var kids = [].slice.call(g.querySelectorAll('.nav-kids li'));
        var topTxt = (g.querySelector('.nav-top')||{}).textContent || '';
        var topHit = !q || topTxt.toLowerCase().indexOf(q) > -1;
        var anyKid = false;
        kids.forEach(function(li){
          var hit = !q || li.textContent.toLowerCase().indexOf(q) > -1 || topHit;
          li.classList.toggle('hide', !hit);
          if (hit) anyKid = true;
        });
        g.classList.toggle('hide', !(topHit || anyKid));
      });
    });
  }
})();
"""

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>__CSS__</style>
</head><body>
<div class="prog" id="prog"></div>
<div class="shell">
  <aside class="rail">
    <div class="brand">__BRANDMARK__<b>__SUBJECT__</b></div>
    <p class="kicker">__KICKER__</p>
    <input id="navsearch" class="navsearch" type="search" placeholder="Filter topics&hellip;" autocomplete="off">
    <nav><ul>__NAV__</ul></nav>
  </aside>
  <main>
    <header class="hero">
      <p class="eyebrow">__EYEBROW__</p>
      <h1>__H1__</h1>
      <p class="lede">__LEDE__</p>
      <div class="hero-meta">__CHIPS__</div>
    </header>
    <div class="wrap">
      __CONSTRAINTS__
      __ACTIONPANEL__
      __VERDICT__
      __TILES__
      __SNAPSHOT__
      <div class="bar">
        <button class="minibtn" id="expandall" type="button">Expand all</button>
        <button class="minibtn" id="collapseall" type="button">Collapse all</button>
        <button class="minibtn" id="evall" type="button">Show all evidence</button>
      </div>
      __SECTIONS__
      __ACTIONS__
      __SCORECARD__
      __SOURCES__
      __ASSUMPTIONS__
    </div>
    <footer class="foot">__FOOT__</footer>
  </main>
</div>
<script>__JS__</script>
</body></html>
"""


# ---------------------------------------------------------------- build

def build(report, brand):
    meta = report.get("meta") or {}
    colors = brand.get("colors") or FALLBACK_COLORS
    fonts = brand.get("fonts") or {}

    sections = [s for s in (report.get("sections") or []) if isinstance(s, dict)]
    assign_ids(sections)

    # Anchors the constraint board is allowed to point at.
    valid_ids = set(RESERVED_IDS)
    for sec in sections:
        valid_ids.add(sec["id"])
        for sub in subsections(sec):
            valid_ids.add(sub["id"])
    board_html = render_constraint_board(report.get("constraints") or [], valid_ids)
    action_panel_html = render_action_panel(report.get("actions") or [])

    sec_html, nav_html = [], render_nav(sections)
    for n, sec in enumerate(sections, 1):
        h, _, _ = render_section(sec, n)
        sec_html.append(h)

    # --- hero chips
    chips = []
    mode = (meta.get("mode") or "full").lower()
    chips.append(f'<span class="chip on">{e("Full report" if mode.startswith("full") else "Quick answer")}</span>')
    if meta.get("date"):
        chips.append(f'<span class="chip">{e(meta["date"])}</span>')
    corpus = meta.get("corpus") or {}
    if corpus.get("videos") or corpus.get("segments"):
        chips.append(f'<span class="chip">{e(corpus.get("segments","?"))} passages &middot; '
                     f'{e(corpus.get("videos","?"))} videos</span>')
    total_cites = sum(len(sub.get("evidence") or [])
                      for s in sections for sub in subsections(s))
    chips.append(f'<span class="chip">{total_cites} citation{"s" if total_cites != 1 else ""}</span>')

    # --- verdict
    v = report.get("verdict") or {}
    verdict_html = ""
    if v.get("headline") or v.get("summary"):
        bits = ['<div class="verdict">', '<span class="lbl lbl-src">Executive diagnosis</span>']
        if v.get("headline"):
            bits.append(f'<h2>{rich(v["headline"])}</h2>')
        for p in paras(v.get("summary")):
            bits.append(f"<p>{rich(p)}</p>")
        if v.get("constraint"):
            bits.append(f'<p style="margin-top:14px"><strong>Primary constraint:</strong> {rich(v["constraint"])}'
                        + (f' &middot; <span style="color:#82829A">confidence: {e(v["confidence"])}</span>'
                           if v.get("confidence") else "") + "</p>")
        bits.append("</div>")
        verdict_html = "\n".join(bits)

    # --- metric tiles
    tiles = report.get("metrics") or []
    tiles_html = ""
    if tiles:
        cards = []
        for t in tiles:
            note = f'<span class="t-n">{rich(t.get("note"))}</span>' if t.get("note") else ""
            cards.append(f'<div class="tile"><span class="t-l">{e(t.get("label"))}</span>'
                         f'<span class="t-v">{e(t.get("value"))}</span>{note}</div>')
        tiles_html = f'<div class="tiles">{"".join(cards)}</div>'

    # --- snapshot
    snap = report.get("snapshot") or []
    snapshot_html = ""
    if snap:
        rows = []
        for r in snap:
            st = slug(r.get("status") or "", "")
            badge = f'<span class="st st-{e(st)}">{e(r.get("status"))}</span>' if st else ""
            rows.append({"field": r.get("field"), "value": r.get("value"), "_st": badge})
        body = "".join(
            f'<tr><td>{rich(r["field"])}</td><td>{rich(r["value"])}</td><td>{r["_st"]}</td></tr>'
            for r in rows)
        snapshot_html = (
            '<section class="sec" id="snapshot"><header class="sec-head">'
            '<span class="sec-num">00</span><h2>Verified business snapshot</h2>'
            '<p class="sec-sum">Every value below is marked verified, inferred, or missing. '
            'Recommendations that depend on an inferred or missing value are labelled where they appear.</p>'
            '</header><div class="tw"><table><thead><tr><th>Field</th><th>Value</th><th>Status</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div></section>')

    # --- actions
    actions = report.get("actions") or []
    actions_html = ""
    if actions:
        actions_html = (
            '<section class="sec" id="actions"><header class="sec-head">'
            '<span class="sec-num">&#9679;</span><h2>Prioritised action plan</h2>'
            '<p class="sec-sum">Ordered by expected impact on the primary constraint.</p></header>'
            + render_table(actions, [("priority", "#"), ("action", "Action"),
                                     ("why", "Why it moves the constraint"),
                                     ("owner", "Owner"), ("due", "By")])
            + "</section>")

    # --- scorecard
    score = report.get("scorecard") or []
    score_html = ""
    if score:
        score_html = (
            '<section class="sec" id="scorecard"><header class="sec-head">'
            '<span class="sec-num">&#9679;</span><h2>Scorecard</h2>'
            '<p class="sec-sum">What gets reviewed, by whom, and how often.</p></header>'
            + render_table(score, [("metric", "Metric"), ("baseline", "Baseline"), ("target", "Target"),
                                   ("owner", "Owner"), ("cadence", "Review cadence")])
            + "</section>")

    # --- sources appendix
    cards = []
    for s in collect_sources(sections):
        stamps = "".join(
            f'<a class="ts" href="{e(safe_url(c.get("timestamp_url")))}" target="_blank" rel="noopener noreferrer">'
            f'<span class="play">&#9654;</span>{e(hhmmss(c.get("start_seconds")) or "link")}</a>'
            for c in s["cites"] if safe_url(c.get("timestamp_url")))
        if not stamps:
            continue  # a source card with no working link reads as a broken citation
        pub = f'<span class="pub">{e(s["published"])}</span>' if s.get("published") else ""
        cards.append(f'<div class="srccard"><h4>{e(s["title"])}</h4>{pub}'
                     f'<div class="stamps">{stamps}</div></div>')

    if cards:
        sources_html = (
            '<section class="sec" id="sources"><header class="sec-head">'
            '<span class="sec-num">&#9679;</span><h2>Sources</h2>'
            f'<p class="sec-sum">{len(cards)} video{"s" if len(cards) != 1 else ""} cited. '
            'Every link opens the original public video at the exact second the passage begins.</p></header>'
            f'<div class="srcgrid">{"".join(cards)}</div></section>')
    else:
        # Deliberately loud rather than absent: a diagnosis with no citations is
        # a fact the reader needs, not an empty block to hide.
        sources_html = ('<section class="sec" id="sources"><header class="sec-head">'
                        '<span class="sec-num">&#9679;</span><h2>Sources</h2></header>'
                        '<p class="empty">No passages were cited in this report.</p></section>')

    # --- assumptions
    assumptions = report.get("assumptions") or []
    assumptions_html = ""
    if assumptions:
        lis = "".join(f"<li>{rich(a)}</li>" for a in assumptions)
        assumptions_html = (
            '<section class="sec" id="assumptions"><header class="sec-head">'
            '<span class="sec-num">&#9679;</span><h2>Risks, assumptions &amp; missing data</h2></header>'
            f'<div class="sub"><ul class="assumps">{lis}</ul></div></section>')

    # --- nav gets the appendix entries too
    extra_nav = []
    if snapshot_html:
        extra_nav.append(('snapshot', 'Verified snapshot'))
    nav_html = "".join(
        f'<li class="nav-group"><a href="#{e(i)}" class="nav-top"><span class="nav-n">&#9679;</span>'
        f'<span>{e(l)}</span></a></li>' for i, l in extra_nav) + nav_html
    tail_nav = []
    if actions_html:
        tail_nav.append(('actions', 'Action plan'))
    if score_html:
        tail_nav.append(('scorecard', 'Scorecard'))
    tail_nav.append(('sources', 'Sources'))
    if assumptions_html:
        tail_nav.append(('assumptions', 'Risks & assumptions'))
    nav_html += "".join(
        f'<li class="nav-group"><a href="#{e(i)}" class="nav-top"><span class="nav-n">&#9679;</span>'
        f'<span>{e(l)}</span></a></li>' for i, l in tail_nav)

    # --- brandmark
    uri = logo_uri(brand.get("logo_path"))
    brandmark = f'<img src="{uri}" alt="">' if uri else '<span class="bolt"></span>'

    # --- css tokens
    css = CSS
    for token, face in (("__ANTARCTICAN_FACE__", font_face("Antarctican Headline", fonts.get("antarctican_otf"), "600")),
                        ("__CARBON_FACE__", font_face("Carbon", fonts.get("carbon_otf")))):
        css = css.replace(token, face or f"/* {token} unavailable — system fallback */")
        if face:
            print(f"  + {token} embedded")
    for token, key in (("__C_BG__", "bg"), ("__C_INK__", "ink"), ("__C_BLUE__", "crypto_blue"),
                       ("__C_PURPLE__", "purple"), ("__C_YELLOW__", "neon_yellow"),
                       ("__C_PINK__", "hot_pink"), ("__C_RED__", "red_pink"), ("__C_GREY__", "grey")):
        css = css.replace(token, colors.get(key, FALLBACK_COLORS[key]))

    title = meta.get("title") or "Business Diagnosis"
    subject = meta.get("subject") or "Business Report"
    foot = ("Evidence is drawn from public MoreMozi YouTube transcripts. Full credit for the source material "
            "belongs to Alex Hormozi, the MoreMozi channel, and the applicable video owners and guests. "
            "This is an independent analysis and is not affiliated with, endorsed by, or operated by "
            "Alex Hormozi or Acquisition.com. Educational source retrieval &mdash; not legal, financial, "
            "or individualised professional advice. Captions may contain transcription errors.")

    tokens = {
        "__CSS__": css, "__JS__": JS, "__TITLE__": e(title),
        "__BRANDMARK__": brandmark, "__SUBJECT__": e(subject),
        "__KICKER__": e(meta.get("kicker") or "Citation-backed diagnosis"),
        "__NAV__": nav_html, "__EYEBROW__": e(meta.get("eyebrow") or "Business diagnosis"),
        "__H1__": rich(title), "__LEDE__": rich(meta.get("lede") or ""),
        "__CHIPS__": "".join(chips), "__VERDICT__": verdict_html, "__TILES__": tiles_html,
        "__CONSTRAINTS__": board_html, "__ACTIONPANEL__": action_panel_html,
        "__SNAPSHOT__": snapshot_html, "__SECTIONS__": "\n".join(sec_html),
        "__ACTIONS__": actions_html, "__SCORECARD__": score_html,
        "__SOURCES__": sources_html, "__ASSUMPTIONS__": assumptions_html,
        "__FOOT__": foot,
    }
    # Single pass. Sequential str.replace would re-scan already-injected content,
    # so a report whose prose contains a literal __SECTIONS__ would have the whole
    # body spliced into it by a later replace. One regex sweep is order-independent
    # and never revisits what it just wrote.
    return re.sub(r"__[A-Z0-9_]+__", lambda m: tokens.get(m.group(0), m.group(0)), PAGE)


# ---------------------------------------------------------------- markdown

def md_table(rows, cols):
    if not rows:
        return []
    out = ["| " + " | ".join(label for _, label in cols) + " |",
           "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows:
        out.append("| " + " | ".join(
            str(r.get(k, "") or "—").replace("|", "\\|") for k, _ in cols) + " |")
    return out + [""]


def render_markdown(report):
    """The plain-text twin of the dashboard.

    This is NOT a deliverable — the HTML is. It exists so a later conversation
    can answer questions about a finished report by reading ~4k words of clean
    prose instead of a 200KB HTML file full of base64 font data, or the verbose
    JSON. Always written alongside the render.
    """
    meta = report.get("meta") or {}
    L = [f"# {meta.get('title', 'Business Diagnosis')}", ""]
    sub = " · ".join(x for x in [meta.get("subject"), meta.get("date"), meta.get("eyebrow")] if x)
    if sub:
        L += [f"*{sub}*", ""]
    if meta.get("lede"):
        L += [meta["lede"], ""]

    v = report.get("verdict") or {}
    if v:
        L += ["---", "", "## Executive diagnosis", ""]
        if v.get("headline"):
            L += [f"**{v['headline']}**", ""]
        for p in paras(v.get("summary")):
            L += [p, ""]
        if v.get("constraint"):
            conf = f" (confidence: {v['confidence']})" if v.get("confidence") else ""
            L += [f"**Primary constraint:** {v['constraint']}{conf}", ""]

    if report.get("metrics"):
        L += ["## Key figures", ""]
        for t in report["metrics"]:
            note = f" — {t['note']}" if t.get("note") else ""
            L.append(f"- **{t.get('label')}:** {t.get('value')}{note}")
        L.append("")

    if report.get("snapshot"):
        L += ["## Verified business snapshot", ""]
        L += md_table(report["snapshot"],
                      [("field", "Field"), ("value", "Value"), ("status", "Status")])

    for i, sec in enumerate(report.get("sections") or [], 1):
        L += ["---", "", f"## {i:02d}. {sec.get('title', 'Untitled')}", ""]
        if sec.get("summary"):
            L += [f"*{sec['summary']}*", ""]
        for sub_ in subsections(sec):
            L += [f"### {sub_.get('title', 'Untitled')}", ""]
            if sub_.get("plain"):
                L += [f"> **In plain terms.** {sub_['plain']}", ""]
            for p in paras(sub_.get("body")):
                L += [p, ""]
            for ev in sub_.get("evidence") or []:
                quote = (ev.get("quote") or "").strip()
                if len(quote) > 480:
                    quote = quote[:477].rstrip() + "…"
                stamp = hhmmss(ev.get("start_seconds")) or "link"
                L += [f"> {quote}", ">",
                      f"> — [{ev.get('title', 'source')} · {stamp}]({ev.get('timestamp_url', '')})", ""]
            if sub_.get("synthesis"):
                L += ["**Our reading.**", ""]
                for p in paras(sub_["synthesis"]):
                    L += [p, ""]
            call = sub_.get("callout")
            if call and call.get("text"):
                L += [f"**{str(call.get('type', 'Note')).title()}:** {call['text']}", ""]

    if report.get("actions"):
        L += ["---", "", "## Prioritised action plan", ""]
        L += md_table(report["actions"],
                      [("priority", "#"), ("action", "Action"),
                       ("why", "Why it moves the constraint"), ("owner", "Owner"), ("due", "By")])

    if report.get("scorecard"):
        L += ["## Scorecard", ""]
        L += md_table(report["scorecard"],
                      [("metric", "Metric"), ("baseline", "Baseline"), ("target", "Target"),
                       ("owner", "Owner"), ("cadence", "Review cadence")])

    srcs = collect_sources(report.get("sections") or [])
    if srcs:
        L += ["---", "", "## Sources", ""]
        for s in srcs:
            stamps = ", ".join(
                f"[{hhmmss(c.get('start_seconds')) or 'link'}]({c.get('timestamp_url', '')})"
                for c in s["cites"] if c.get("timestamp_url"))
            pub = f" ({s['published']})" if s.get("published") else ""
            L.append(f"- **{s['title']}**{pub} — {stamps}")
        L.append("")

    if report.get("assumptions"):
        L += ["## Risks, assumptions & missing data", ""]
        L += [f"- {a}" for a in report["assumptions"]] + [""]

    L += ["---", "",
          "*Evidence is drawn from public MoreMozi YouTube transcripts. Full credit for the source "
          "material belongs to Alex Hormozi, the MoreMozi channel, and the applicable video owners "
          "and guests. Independent analysis, not affiliated with or endorsed by Alex Hormozi or "
          "Acquisition.com. Educational source retrieval — not legal, financial, or individualised "
          "professional advice. Captions may contain transcription errors.*"]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Render a Hormozi report JSON into a self-contained HTML dashboard.")
    ap.add_argument("spec", help="path to report.json")
    ap.add_argument("-o", "--out", help="output .html path (default: alongside the spec)")
    ap.add_argument("--brand", default=DEFAULT_BRAND, help="path to brand.config.json")
    ap.add_argument("--no-markdown", action="store_true",
                    help="skip the report.md companion (not recommended — it is what later "
                         "conversations read to answer questions about the report)")
    args = ap.parse_args()

    spec_path = expand(args.spec)
    if not os.path.exists(spec_path):
        print(f"spec not found: {spec_path}", file=sys.stderr)
        return 1
    try:
        # utf-8-sig, not utf-8: Windows editors and PowerShell 5.1's
        # Set-Content -Encoding utf8 write a BOM, which utf-8 refuses to decode.
        with open(spec_path, encoding="utf-8-sig") as f:
            report = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"{spec_path}: not valid JSON — {exc}", file=sys.stderr)
        return 1

    if not isinstance(report, dict):
        print(f"{spec_path}: top level must be a JSON object, got {type(report).__name__}",
              file=sys.stderr)
        return 1
    if not isinstance(report.get("sections") or [], list):
        print(f"{spec_path}: 'sections' must be a list, got "
              f"{type(report['sections']).__name__}", file=sys.stderr)
        return 1

    brand = load_brand(args.brand)
    html_out = build(report, brand)

    if args.out:
        out_path = expand(args.out)
    else:
        meta = report.get("meta") or {}
        stamp = meta.get("date") or datetime.date.today().isoformat()
        name = f"{meta.get('subject') or 'Business'} — Diagnosis — {stamp}.html"
        out_path = os.path.join(os.path.dirname(os.path.abspath(spec_path)), name)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    kb = os.path.getsize(out_path) / 1024
    n_sec = len(report.get("sections") or [])
    n_cite = sum(len(sub.get("evidence") or [])
                 for s in (report.get("sections") or []) if isinstance(s, dict) for sub in subsections(s))
    print(f"done — {out_path}")
    print(f"  {n_sec} sections · {n_cite} citations · {kb:.0f} KB · self-contained")

    if not args.no_markdown:
        md_path = os.path.join(os.path.dirname(os.path.abspath(out_path)), "report.md")
        md = render_markdown(report)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"  + report.md ({len(md.split()):,} words) — read this to answer questions later")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
