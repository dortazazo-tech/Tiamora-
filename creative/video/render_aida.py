#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIAMORA — AIDA video renderer
Concept C1 "הסוללה" · Avatar: נועם · Belief 1: "זה האור, לא אתה"

Renders a 16s brand-compliant motion-graphics ad, sound-off-first, to MP4.
Deterministic: no AI video model, so no garbled Hebrew, no wrong lens colour
(the documented Seedance SKU-mismatch bug), no third-party trademarks.

Usage:  python3 render_aida.py <out.mp4> <width> <height>
"""
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- brand ----
NAVY = (12, 27, 51)      # #0C1B33  base
GOLD = (201, 144, 12)    # #C9900C  accent
CREAM = (250, 246, 239)  # #FAF6EF  type
MUTED = (168, 178, 196)  # secondary type on navy
BLUE = (86, 156, 255)    # the antagonist: blue light
AMBER = (238, 165, 60)   # the lens
DEAD = (74, 88, 112)     # the drained meter

# Liberation Sans is the only locally available family covering Hebrew,
# Latin, digits and punctuation in one file — mixed runs like
# "NIGHT · 97% חסימת אור כחול" need a single font or they render as tofu.
FONT_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

FPS = 30
DURATION = 16.0
SS = 2  # shape supersampling

SCENES = [(0.0, 4.2), (4.2, 9.0), (9.0, 13.0), (13.0, 16.0)]
XFADE = 0.4

_fc = {}


def font(size, bold=True):
    k = (int(size), bold)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONT_B if bold else FONT_R, int(size))
    return _fc[k]


# ------------------------------------------------------------- easing -------
def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def seg(t, start, dur):
    return smooth((t - start) / dur) if dur > 0 else 0.0


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1[:3], c2[:3]))


def A(c, a):
    return (c[0], c[1], c[2], int(round(255 * clamp(a))))


# ------------------------------------------------------------ layout --------
class L:
    """One composition for both 9:16 and 4:5.

    u  — canvas unit (1 for the text pass, SS for the shape pass)
    vs — vertical squeeze so 4:5 keeps the same reading rhythm
    sh — shape scale (u * vs);  ts — type scale
    """

    def __init__(self, w, h, u):
        self.w, self.h, self.u = w, h, u
        self.cx = w / 2
        design_h = h / u
        self.vs = clamp(design_h / 1920.0, 0.70, 1.0)
        self.sh = u * self.vs
        self.ts = clamp(design_h / 1920.0, 0.88, 1.0)
        # 9:16 runs in Reels/Stories, whose chrome eats the bottom ~17%;
        # 4:5 runs in feed, which only overlays a thin strip.
        if (h / w) > 1.5:
            self._t, self._b = 0.005, 0.900
        else:
            self._t, self._b = 0.030, 0.965

    def y(self, frac):
        """frac is composition-relative; the band keeps it clear of platform UI."""
        return self.h * (self._t + frac * (self._b - self._t))


# -------------------------------------------------------------- text --------
def text(d, xy, s, f, fill, spacing=0):
    # Pillow is built with libraqm: it runs the bidi algorithm and shapes the
    # run itself. Applying python-bidi on top would reverse Hebrew twice.
    if not spacing:
        # Base direction is forced: auto-detection puts a leading digit or a
        # Latin word ("97%…", "NIGHT · …") on the wrong side of a Hebrew line.
        d.text(xy, s, font=f, fill=fill, anchor="mm", direction="rtl")
        return
    ws = [d.textlength(ch, font=f) for ch in s]
    total = sum(ws) + spacing * (len(s) - 1)
    x = xy[0] - total / 2
    for ch, w in zip(s, ws):
        d.text((x, xy[1]), ch, font=f, fill=fill, anchor="lm")
        x += w + spacing


def rise(d, xy, s, f, fill, t, delay, dur=0.55, travel=26, spacing=0):
    """Fade + a small upward translate — the only entrance this ad uses."""
    p = seg(t, delay, dur)
    if p <= 0:
        return
    text(d, (xy[0], xy[1] + travel * (1 - p)), s, f, A(fill, p), spacing)


# ------------------------------------------------------------- shapes -------
def bg(w, h):
    """Navy with a soft centre lift — flat navy reads cheap on a phone."""
    img = Image.new("RGB", (w, h), NAVY)
    g = Image.new("L", (w // 8, h // 8), 0)
    gd = ImageDraw.Draw(g)
    cx, cy, r = w / 16, h / 16 * 0.92, max(w, h) / 15
    for i in range(30):
        p = i / 29
        rr = r * (1 - p * 0.75)
        gd.ellipse([cx - rr, cy - rr * 1.2, cx + rr, cy + rr * 1.2], fill=int(8 + 30 * p))
    img.paste(Image.new("RGB", (w, h), (27, 48, 82)), (0, 0), g.resize((w, h), Image.LANCZOS))
    return img


def battery(d, cx, cy, bw, bh, level, fill_c, frame_c):
    st = max(2, int(bw * 0.038))
    r = bw * 0.17
    x0, y0, x1, y1 = cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2
    nw, nh = bw * 0.34, bh * 0.032
    d.rounded_rectangle([cx - nw / 2, y0 - nh - st, cx + nw / 2, y0 - st],
                        radius=nh / 2, fill=frame_c)
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=frame_c, width=st)
    pad = st * 2.4
    fh = ((y1 - pad) - (y0 + pad)) * clamp(level)
    if fh > 2:
        d.rounded_rectangle([x0 + pad, y1 - pad - fh, x1 - pad, y1 - pad],
                            radius=max(1, r - pad * 0.6), fill=fill_c)


def eye(d, cx, cy, w, col, iris=None):
    h = w * 0.40
    st = max(3, int(w * 0.052))
    d.arc([cx - w / 2, cy - h, cx + w / 2, cy + h], 206, 334, fill=col, width=st)
    d.arc([cx - w / 2, cy - h, cx + w / 2, cy + h], 26, 154, fill=col, width=st)
    rr = w * 0.175
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=st)
    if iris:
        r2 = rr * 0.55
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=iris)


def screen(d, cx, cy, w, frame_c, glow_c):
    h = w * 1.36
    st = max(3, int(w * 0.052))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=w * 0.14, outline=frame_c, width=st)
    p = w * 0.14
    d.rounded_rectangle([cx - w / 2 + p, cy - h / 2 + p, cx + w / 2 - p, cy + h / 2 - p],
                        radius=w * 0.07, fill=glow_c)


def rays(d, x_from, x_to, cy, spread, col, phase, a_mul=1.0, count=5, width=6):
    """Marching dashes travelling screen → eye, i.e. right → left (RTL)."""
    span = x_from - x_to
    if span <= 0:
        return
    seg_len = span * 0.22
    for i in range(count):
        f = (i / (count - 1) - 0.5) if count > 1 else 0.0
        y = cy + f * spread
        a = (1.0 - abs(f) * 0.5) * a_mul
        for k in range(3):
            off = (phase + k / 3.0) % 1.0
            sx = x_from - off * (span + seg_len)
            ex = sx - seg_len
            sx, ex = min(sx, x_from), max(ex, x_to)
            if sx > ex:
                d.line([sx, y, ex, y], fill=A(col, a), width=width)


def curve(d, x0, y0, w, h, amp, col, progress, width=7):
    pts = []
    n = 60
    for i in range(n + 1):
        u = i / n
        e = 1.0 / (1.0 + pow(2.718281828, -(u - 0.48) * 11))
        pts.append((x0 + u * w, y0 - (0.05 + e * 0.95) * h * amp))
    keep = max(2, int(len(pts) * clamp(progress)))
    d.line(pts[:keep], fill=col, width=width, joint="curve")


# ------------------------------------------------------------- scenes -------
def s_attention(d, g, t):
    """A · הטלפון שלך נטען כל לילה. אתה — לא."""
    rise(d, (g.cx, g.y(0.212)), "הטלפון שלך נטען כל לילה.", font(64 * g.ts), CREAM, t, 0.15)
    rise(d, (g.cx, g.y(0.288)), "אתה — לא.", font(90 * g.ts), GOLD, t, 1.45)

    ap = seg(t, 0.30, 0.5)
    if ap <= 0:
        return
    bw, bh = 200 * g.sh, 430 * g.sh
    cy, gap = g.y(0.575), 235 * g.sh

    ph = lerp(0.45, 1.0, seg(t, 0.55, 1.9))                       # the phone charges
    battery(d, g.cx + gap, cy, bw, bh, ph, A(GOLD, ap), A(MUTED, ap * 0.7))

    dr = seg(t, 0.80, 2.2)                                        # you drain
    battery(d, g.cx - gap, cy, bw, bh, lerp(1.0, 0.34, dr),
            A(mix(BLUE, DEAD, dr), ap), A(MUTED, ap * 0.7))

    fl = font(42 * g.ts)
    ly = cy + bh / 2 + 66 * g.sh
    rise(d, (g.cx + gap, ly), "הטלפון שלך", fl, MUTED, t, 0.75, travel=14)
    rise(d, (g.cx - gap, ly), "אתה", fl, MUTED, t, 0.95, travel=14)


def s_interest(d, g, t):
    """I · the mechanism, in the exact approved wording."""
    f1 = font(62 * g.ts)
    rise(d, (g.cx, g.y(0.182)), "אור כחול בערב", f1, CREAM, t, 0.10)
    rise(d, (g.cx, g.y(0.248)), "מדכא את ייצור המלטונין", f1, CREAM, t, 0.32)

    cy = g.y(0.535)
    sx, ex = g.cx + 300 * g.sh, g.cx - 300 * g.sh
    ap = seg(t, 0.45, 0.5)
    if ap > 0:
        screen(d, sx, cy, 172 * g.sh, A(MUTED, ap), A(BLUE, ap * 0.85))
        eye(d, ex, cy, 248 * g.sh, A(CREAM, ap), A(BLUE, ap * 0.9))
    rp = seg(t, 0.85, 0.6)
    if rp > 0:
        rays(d, sx - 118 * g.sh, ex + 142 * g.sh, cy, 148 * g.sh, BLUE,
             (t * 0.5) % 1.0, a_mul=rp, width=max(3, int(7 * g.sh)))

    cp = seg(t, 1.5, 1.1)
    if cp > 0:
        cw, ch, by = 440 * g.sh, 140 * g.sh, g.y(0.735)
        d.line([g.cx - cw / 2, by, g.cx + cw / 2, by],
               fill=A(MUTED, 0.3 * cp), width=max(2, int(3 * g.sh)))
        curve(d, g.cx - cw / 2, by, cw, ch, 0.12, A(BLUE, cp), cp, max(3, int(7 * g.sh)))
        text(d, (g.cx, by + 54 * g.sh), "מלטונין", font(34 * g.ts), A(MUTED, cp * 0.9))

    f2 = font(44 * g.ts, bold=False)
    rise(d, (g.cx, g.y(0.852)), "לא רק הטלפון —", f2, MUTED, t, 2.1, travel=16)
    rise(d, (g.cx, g.y(0.906)), "כל מסך וכל מנורה בבית", f2, MUTED, t, 2.3, travel=16)


def s_desire(d, g, t):
    """D · the lens goes in — and nothing was given up."""
    rise(d, (g.cx, g.y(0.180)), "עדשת ענבר", font(60 * g.ts), CREAM, t, 0.10)
    rise(d, (g.cx, g.y(0.258)), "97% חסימת אור כחול", font(78 * g.ts), GOLD, t, 0.34)

    cy = g.y(0.535)
    sx, ex = g.cx + 300 * g.sh, g.cx - 300 * g.sh
    screen(d, sx, cy, 172 * g.sh, MUTED, BLUE)

    lp = seg(t, 0.55, 0.85)
    lx = lerp(sx - 40 * g.sh, g.cx + 35 * g.sh, lp)
    warm = clamp((lp - 0.35) / 0.65)

    rays(d, sx - 118 * g.sh, lx + 48 * g.sh, cy, 148 * g.sh, BLUE,
         (t * 0.5) % 1.0, width=max(3, int(7 * g.sh)))
    if warm > 0:
        rays(d, lx - 48 * g.sh, ex + 142 * g.sh, cy, 126 * g.sh, AMBER,
             (t * 0.5) % 1.0, a_mul=warm, count=4, width=max(3, int(6 * g.sh)))

    eye(d, ex, cy, 248 * g.sh, CREAM, mix(BLUE, AMBER, warm))

    if lp > 0:
        lw, lh = 90 * g.sh, 206 * g.sh
        d.rounded_rectangle([lx - lw / 2, cy - lh / 2, lx + lw / 2, cy + lh / 2],
                            radius=lw * 0.44, fill=A(AMBER, 0.82 * lp),
                            outline=A(AMBER, lp), width=max(3, int(7 * g.sh)))

    cp = seg(t, 1.35, 1.2)
    if cp > 0:
        cw, ch, by = 440 * g.sh, 140 * g.sh, g.y(0.735)
        d.line([g.cx - cw / 2, by, g.cx + cw / 2, by], fill=A(MUTED, 0.3), width=max(2, int(3 * g.sh)))
        curve(d, g.cx - cw / 2, by, cw, ch, lerp(0.12, 1.0, cp), AMBER, 1.0, max(3, int(7 * g.sh)))
        text(d, (g.cx, by + 54 * g.sh), "מלטונין", font(34 * g.ts), A(MUTED, 0.9))

    f2 = font(44 * g.ts, bold=False)
    rise(d, (g.cx, g.y(0.852)), "לא ויתרת על כלום.", f2, CREAM, t, 2.0, travel=16)
    rise(d, (g.cx, g.y(0.906)), "שינית את האור שנכנס לעין.", f2, MUTED, t, 2.2, travel=16)


def s_action(d, g, t):
    """A · the offer, worded exactly as the brand requires."""
    y = g.y(0.335)
    p = seg(t, 0.05, 0.6)
    if p > 0:
        text(d, (g.cx, y), "TIAMORA", font(94 * g.ts), A(CREAM, p), spacing=16 * g.ts)
        text(d, (g.cx, y + 80 * g.sh / g.u), "CLEAR VISION. A BRIGHTER YOU.",
             font(24 * g.ts, bold=False), A(GOLD, p * 0.95), spacing=6 * g.ts)
    rp = seg(t, 0.5, 0.6)
    if rp > 0:
        half = 240 * g.sh * rp
        d.line([g.cx - half, y + 140 * g.sh, g.cx + half, y + 140 * g.sh],
               fill=GOLD, width=max(2, int(3 * g.sh)))

    rise(d, (g.cx, g.y(0.548)), "NIGHT · 97% חסימת אור כחול", font(46 * g.ts), CREAM, t, 0.8)
    rise(d, (g.cx, g.y(0.650)), "14 לילות לנסות", font(70 * g.ts), GOLD, t, 1.1)
    rise(d, (g.cx, g.y(0.728)), "לא עבד — הכסף חוזר, המשקפיים נשארים",
         font(39 * g.ts, bold=False), MUTED, t, 1.4)


SCENE_FN = [s_attention, s_interest, s_desire, s_action]


# ------------------------------------------------------------ compositor ----
class TextOnly:
    """Draw proxy: passes type through, swallows geometry."""

    def __init__(self, d):
        self._d = d

    def text(self, *a, **k):
        return self._d.text(*a, **k)

    def textlength(self, *a, **k):
        return self._d.textlength(*a, **k)

    def __getattr__(self, _):
        return lambda *a, **k: None


class ShapesOnly:
    """Draw proxy: passes geometry through, swallows type."""

    def __init__(self, d):
        self._d = d

    def text(self, *a, **k):
        return None

    def __getattr__(self, n):
        return getattr(self._d, n)


def layer(idx, tl, w, h):
    """One scene as an RGBA overlay: shapes at SS×, Hebrew type at 1×."""
    shp = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    SCENE_FN[idx](ShapesOnly(ImageDraw.Draw(shp)), L(w * SS, h * SS, SS), tl)
    out = shp.resize((w, h), Image.LANCZOS)
    txt = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    SCENE_FN[idx](TextOnly(ImageDraw.Draw(txt)), L(w, h, 1), tl)
    out.alpha_composite(txt)
    return out


def render(out_path, w, h):
    base = bg(w, h)
    total = int(DURATION * FPS)
    proc = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-shortest",
        "-c:v", "libx264", "-preset", "slow", "-crf", "19",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "96k", out_path,
    ], stdin=subprocess.PIPE)

    cache = {}
    for i in range(total):
        t = i / FPS
        idx = 0
        for k, (s0, _) in enumerate(SCENES):
            if t >= s0:
                idx = k
        s0 = SCENES[idx][0]
        cur = layer(idx, t - s0, w, h)
        # cross-dissolve out of the previous scene, held on its last frame
        if idx > 0 and (t - s0) < XFADE:
            if idx not in cache:
                ps, pe = SCENES[idx - 1]
                cache[idx] = layer(idx - 1, pe - ps, w, h)
            cur = Image.blend(cache[idx], cur, smooth((t - s0) / XFADE))
        frame = base.copy()
        frame.paste(cur, (0, 0), cur)
        proc.stdin.write(frame.tobytes())
        if i % 90 == 0:
            print(f"  {i}/{total}", flush=True)

    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"  done -> {out_path}")


if __name__ == "__main__":
    render(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
