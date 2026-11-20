#!/usr/bin/env python3
"""Draw the 19 November 2026 world-news front page (1024x1024 PNG).

One image, one day: the Shenzhen trilateral summit's Declaration Towards
Peace, the ICJ genocide verdict on Myanmar, the Gulf war reaching Riyadh,
and the third Kerch Bridge strike, plus an ALSO strip. Pure Pillow,
no network, deterministic: two runs write identical bytes.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR") or HERE
PATH = os.path.join(OUT, "entry.png")

W = H = 1024
MARGIN = 40
CONTENT = W - 2 * MARGIN  # 944

PAPER = (247, 243, 234)
INK = (24, 24, 22)
NAVY = (22, 35, 63)
GOLD = (201, 162, 39)
RED = (139, 26, 26)
GREY = (96, 92, 84)
RULE = (180, 172, 152)
QUOTE_BG = (235, 229, 214)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def fname(size):
    return font("DejaVuSans-Bold.ttf", size)


def fbody(size):
    return font("DejaVuSans.ttf", size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, fill, width, leading):
    """Draw a wrapped paragraph; return the y just below its last line."""
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, y, color=RULE, weight=2):
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=color, width=weight)
    return y + weight


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.text((W / 2, 22), "THE WORLD IN ONE PAGE", font=fname(46),
           fill=(247, 243, 234), anchor="ma")
    d.text((W / 2, 72), "THURSDAY, 19 NOVEMBER 2026",
           font=fbody(19), fill=(201, 162, 39), anchor="ma")
    d.rectangle([0, 96, W, 100], fill=GOLD)

    y = 118
    # ---- Main story -----------------------------------------------------
    d.text((MARGIN, y), "FIRST-EVER TRILATERAL SUMMIT  ·  SHENZHEN",
           font=fname(19), fill=RED)
    y += 30
    y = para(d, MARGIN, y,
             "Trump, Xi and Putin issue \u2018Declaration Towards Peace\u2019",
             fname(52), INK, CONTENT, 62)
    y += 8
    y = para(d, MARGIN, y,
             "After an hour behind closed doors at Kylin Villa, the leaders of "
             "the United States, China and Russia pledge UN reform, more fuel "
             "supplies and talks on nuclear risk \u2014 but say nothing about "
             "Ukraine or Iran, and set no dates.",
             fbody(23), (52, 50, 46), CONTENT, 29)
    y += 12
    # Pull quote from the declaration itself.
    d.rectangle([MARGIN, y, W - MARGIN, y + 48], fill=QUOTE_BG)
    d.rectangle([MARGIN, y, MARGIN + 6, y + 48], fill=RED)
    d.text((MARGIN + 22, y + 10),
           "\u201cA nuclear war cannot be won and must never be fought.\u201d",
           font=fname(24), fill=NAVY)
    d.text((MARGIN + 22, y + 34),
           "\u2014 the Declaration Towards Peace, Shenzhen",
           font=fbody(16), fill=GREY)
    y += 48 + 14
    y = rule(d, y)

    # ---- Two secondaries, side by side ----------------------------------
    y += 16
    sec_top = y
    col_w = (CONTENT - 24) // 2
    col2_x = MARGIN + col_w + 24

    d.text((MARGIN, y), "THE HAGUE  ·  GENOCIDE CASE",
           font=fname(18), fill=RED)
    d.text((col2_x, y), "THE GULF  ·  WAR SPREADS",
           font=fname(18), fill=RED)
    y += 28
    head_y = y
    left_end = para(d, MARGIN, head_y,
                    "ICJ finds Myanmar guilty of Rohingya genocide",
                    fname(29), INK, col_w, 36)
    right_end = para(d, col2_x, head_y,
                     "Houthi missile rattles Riyadh as war widens",
                     fname(29), INK, col_w, 36)
    y = max(left_end, right_end) + 8
    body_y = y
    left_end = para(d, MARGIN, body_y,
                    "By 9 votes to 6, the world\u2019s top court rules Myanmar "
                    "committed genocide in the 2017 clearance operations \u2014 "
                    "the first time a state has been found guilty of the crime. "
                    "Judges cite some 10,000 killed and order reparations; "
                    "Myanmar must report back within two years.",
                    fbody(19), (52, 50, 46), col_w, 24)
    right_end = para(d, col2_x, body_y,
                     "A missile threat towards the Saudi capital leaves debris "
                     "and damage, and the PIF Tower loses windows across seven "
                     "floors. A cruise missile aimed at the south is "
                     "intercepted, a tanker is hit near Hormuz, and Iran "
                     "readies a run of tankers at the US blockade.",
                     fbody(19), (52, 50, 46), col_w, 24)
    y = max(left_end, right_end) + 12
    # Vertical divider between the two columns, kicker to body end.
    d.line([(MARGIN + col_w + 12, sec_top),
            (MARGIN + col_w + 12, y - 4)], fill=RULE, width=2)
    y = rule(d, y)

    # ---- Kerch Bridge band ----------------------------------------------
    y += 16
    d.text((MARGIN, y), "CRIMEA  ·  THIRD STRIKE IN FOUR DAYS",
           font=fname(18), fill=RED)
    y += 28
    y = para(d, MARGIN, y,
             "Ukraine halts rail traffic on the Kerch Bridge",
             fname(30), INK, CONTENT, 38)
    y += 4
    y = para(d, MARGIN, y,
             "Neptune missiles hit the rail section days after the road span "
             "collapsed into the strait. No casualties are reported; Putin, "
             "speaking in Shenzhen, vows a painful reply.",
             fbody(19), (52, 50, 46), CONTENT, 24)
    y += 10
    y = rule(d, y)

    # ---- ALSO strip -------------------------------------------------------
    y += 10
    d.text((MARGIN, y), "ALSO", font=fname(18), fill=RED)
    y += 28
    also = [
        ("COP31", "Ministers in Antalya race to unblock a final climate text."),
        ("ART", "Van Gogh\u2019s \u2018Blossoming Chestnut Trees\u2019 sells for a "
                "record $190.4M at Sotheby\u2019s."),
        ("SENEGAL", "39 dead as a migrant boat capsizes off K\u00e9b\u00e9mer."),
    ]
    for label, text in also:
        d.text((MARGIN, y), label + " \u2014 ", font=fname(18), fill=INK)
        off = d.textlength(label + " \u2014 ", font=fname(18))
        d.text((MARGIN + off, y), text, font=fbody(18), fill=(52, 50, 46))
        y += 23

    # ---- Footer -----------------------------------------------------------
    d.text((MARGIN, H - 30),
           "Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 UN News \u00b7 ICJ \u00b7 "
           "Sotheby\u2019s",
           font=fbody(14), fill=GREY)
    d.text((W - MARGIN, H - 30), "19 NOVEMBER 2026",
           font=fname(14), fill=GREY, anchor="ra")

    assert y < H - 40, f"layout overflow: content ends at y={y}"
    img.save(PATH, format="PNG")
    print(f"wrote {PATH} ({os.path.getsize(PATH)} bytes, content ends y={y})")


if __name__ == "__main__":
    main()
