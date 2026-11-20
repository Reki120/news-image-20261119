#!/usr/bin/env python3
"""Draw entry.png: one image summing up the world news of Thursday 19 November 2026.

Full-day refresh (round 2): the round-1 image was drawn before the day's
outcomes landed. This version carries the summit's four-point declaration,
the verified ICJ genocide verdict and the third Kerch Bridge strike.

Deterministic: fixed layout, fixed fonts, no randomness, no timestamps.
Run:  python3 draw_entry.py   (writes entry.png next to this file,
or into $MAKEFUN_OUTPUT_DIR when that is set)
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

W, H = 1024, 1024

# Palette
INK = (13, 20, 36)          # deep navy background
PANEL = (21, 32, 54)        # panel fill
PAPER = (245, 239, 224)     # cream text
MUTED = (178, 188, 205)     # secondary text
RED = (216, 58, 44)         # accent red
GOLD = (224, 165, 38)       # accent gold
TEAL = (64, 156, 178)       # accent teal
LINE = (84, 98, 122)        # hairline


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


BOLD = "DejaVuSans-Bold.ttf"
REG = "DejaVuSans.ttf"


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, fill, max_w, leading=1.18):
    lines = wrap(draw, text, fnt, max_w)
    lh = int(fnt.size * leading)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def centered(draw, cx, y, text, fnt, fill):
    w_ = draw.textlength(text, font=fnt)
    draw.text((cx - w_ / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------- flags
def flag_us(draw, x, y, w_, h_):
    stripe = h_ / 13.0
    for i in range(13):
        col = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
        draw.rectangle([x, y + i * stripe, x + w_, y + (i + 1) * stripe + 1], fill=col)
    cw, ch = w_ * 0.42, stripe * 7
    draw.rectangle([x, y, x + cw, y + ch], fill=(60, 59, 110))
    r = max(2, int(h_ * 0.028))
    for row in range(5):
        for col_i in range(6):
            sx = x + cw * (col_i + 0.5) / 6
            sy = y + ch * (row + 0.5) / 5
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))


def flag_cn(draw, x, y, w_, h_):
    draw.rectangle([x, y, x + w_, y + h_], fill=(222, 41, 16))
    # one large star and four small ones, drawn as filled circles with a star glyph feel
    def star(cx, cy, r, rot=0):
        import math
        pts = []
        for i in range(10):
            ang = rot + math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.42
            pts.append((cx + rr * math.cos(ang), cy - rr * math.sin(ang)))
        draw.polygon(pts, fill=(255, 222, 0))
    star(x + w_ * 0.16, y + h_ * 0.28, h_ * 0.17)
    for dx, dy in [(0.34, 0.12), (0.38, 0.30), (0.38, 0.48), (0.34, 0.64)]:
        star(x + w_ * dx, y + h_ * dy, h_ * 0.07)


def flag_ru(draw, x, y, w_, h_):
    third = h_ / 3.0
    draw.rectangle([x, y, x + w_, y + third + 1], fill=(245, 245, 245))
    draw.rectangle([x, y + third, x + w_, y + 2 * third + 1], fill=(0, 57, 166))
    draw.rectangle([x, y + 2 * third, x + w_, y + h_], fill=(213, 43, 30))


def flag_panel(draw, x, y, w_, h_, draw_flag):
    rounded(draw, [x, y, x + w_, y + h_], 14, fill=(255, 255, 255))
    inset = 5
    # clip flag into the rounded panel by drawing on a temp image
    tmp = Image.new("RGB", (w_ - 2 * inset, h_ - 2 * inset), (255, 255, 255))
    td = ImageDraw.Draw(tmp)
    draw_flag(td, 0, 0, w_ - 2 * inset, h_ - 2 * inset)
    mask = Image.new("L", tmp.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, tmp.size[0], tmp.size[1]], radius=10, fill=255)
    return tmp, mask, (x + inset, y + inset)


# ---------------------------------------------------------------- main
def main():
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    M = 44  # page margin

    # ---- masthead ------------------------------------------------------
    d.text((M, 30), "WORLD NEWS IN ONE IMAGE", font=font(BOLD, 25), fill=RED)
    datestr = "THURSDAY 19 NOVEMBER 2026"
    dw = d.textlength(datestr, font=font(BOLD, 25))
    d.text((W - M - dw, 30), datestr, font=font(BOLD, 25), fill=GOLD)
    d.line([M, 74, W - M, 74], fill=GOLD, width=3)
    d.line([M, 82, W - M, 82], fill=LINE, width=1)

    # ---- main story ----------------------------------------------------
    y = 92
    d.text((M, y), "SHENZHEN, CHINA — APEC SUMMIT · 90 MINUTES", font=font(BOLD, 26), fill=RED)
    y += 40
    y = text_block(
        d, M, y,
        "TRUMP, XI AND PUTIN ISSUE 'DECLARATION TOWARDS PEACE'",
        font(BOLD, 58), PAPER, W - 2 * M, leading=1.12,
    )
    y += 8
    y = text_block(
        d, M, y,
        "After their first-ever three-way meeting at Kylin Villa, the leaders of "
        "the United States, China and Russia pledge a nuclear war 'cannot be won "
        "and must never be fought', talks on cutting nuclear risks and more "
        "refined oil output — but the declaration says nothing on Ukraine or Iran.",
        font(REG, 25), MUTED, W - 2 * M, leading=1.22,
    )

    # flags row
    y += 16
    fw, fh, gap = 292, 104, 30
    fx = M
    for draw_flag, label in [
        (flag_us, "UNITED STATES"),
        (flag_cn, "CHINA"),
        (flag_ru, "RUSSIA"),
    ]:
        tmp, mask, pos = flag_panel(d, fx, y, fw, fh, draw_flag)
        img.paste(tmp, pos, mask)
        centered(d, fx + fw / 2, y + fh + 8, label, font(BOLD, 20), PAPER)
        fx += fw + gap
    y += fh + 40

    d.line([M, y, W - M, y], fill=LINE, width=1)
    y += 18

    # ---- secondary stories ----------------------------------------------
    stories = [
        (GOLD, "THE HAGUE",
         "ICJ FINDS MYANMAR GUILTY OF GENOCIDE",
         "By 9 votes to 6, the UN's top court rules Myanmar committed genocide "
         "against the Rohingya in 2017 — the first state ever found guilty — "
         "and orders reparations and safe return."),
        (RED, "MIDDLE EAST",
         "GULF WAR SPREADS TO SAUDI ARABIA",
         "Iran's drones hit a US base in Kuwait and Bahrain for a fourth time "
         "in six days; Saudi Arabia intercepts a Houthi missile aimed at "
         "Riyadh, and a tanker is struck in the Strait of Hormuz."),
        (TEAL, "UKRAINE",
         "THIRD STRIKE HALTS KERCH BRIDGE RAIL",
         "Hours before Putin's Shenzhen summit, a third Ukrainian strike in "
         "four days halts rail traffic on the Kerch Bridge to Crimea, days "
         "after a 227-metre road span fell into the strait."),
    ]
    col_w = (W - 2 * M - 2 * 26) // 3
    top = y
    for i, (accent, kicker, head, body) in enumerate(stories):
        x = M + i * (col_w + 26)
        d.rectangle([x, top, x + 46, top + 6], fill=accent)
        d.text((x, top + 16), kicker, font=font(BOLD, 20), fill=accent)
        text_block(d, x, top + 48, head, font(BOLD, 24), PAPER, col_w, leading=1.16)
        text_block(d, x, top + 118, body, font(REG, 19.5), MUTED, col_w, leading=1.26)

    # ---- also strip -------------------------------------------------------
    strip_y = 928
    d.line([M, strip_y, W - M, strip_y], fill=GOLD, width=2)
    also = ("ALSO TODAY — COP31 in Antalya enters its decisive phase as ministers "
            "wrestle over fossil fuels  •  One dead, dozens missing as a migrant "
            "boat capsizes off Senegal  •  Van Gogh sells for a record $190.4 million "
            "in New York")
    text_block(d, M, strip_y + 14, also, font(REG, 20.5), PAPER, W - 2 * M, leading=1.3)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", HERE)
    out = os.path.join(out_dir, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
