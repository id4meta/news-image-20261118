"""Draw the 18 November 2026 world-news image (revision 2).

Build-time only: run `python3 draw.py` to write entry.png next to this
file. The entry program (main.ts) only copies that PNG at grading time,
so no font, network or clock is needed in the sandbox. Output is fully
deterministic: same text, same fonts, same pixels every run.

Revision 2 vs revision 1:
- Bigger, higher-contrast type for the ~300px thumbnail: headline
  30 -> 34pt bold, tag 21 -> 23pt bold, subline in a darker grey,
  wider line spacing, and a taller card so nothing is cramped.
- Each card now has a hand-drawn geometric icon (PIL only, no
  external images) in a tinted disc, so the eight regions/topics
  are told apart at a glance, not just by the side bar.
- Wording tightened to what was verified: the measles headline is
  "US measles-free status lost" and its subline dates the ruling
  to 17 Nov; the Ebola subline gives the verified figures
  "11,285 cases, 5,509 deaths" and the footer dates them to
  12 Nov, instead of presenting them as 18 Nov numbers; the footer no longer claims every
  story happened on 18 Nov. No story was swapped, no new
  event was invented, and the Gulf item still only says tankers
  were hit -- no unverified sinking / oil-price claims.
"""
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (16, 35, 63)
PAPER = (247, 243, 232)
CARD = (255, 255, 255)
INK = (18, 26, 38)
GREY = (70, 78, 92)          # darker than v1 (90, 98, 110): readable at 300px
FOOT = (80, 88, 102)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)

# tag, colour, icon kind, headline, subline
STORIES = [
    ("GULF", (178, 34, 34), "ship",
     "US-Iran strikes escalate",
     "Tankers hit in the Strait of Hormuz"),
    ("UKRAINE", (30, 90, 168), "bridge",
     "Crimea road bridge hit",
     "Road span falls into the strait"),
    ("ASIA", (10, 110, 80), "globe",
     "Trump meets Quad in Manila",
     "Then on to Shenzhen for APEC"),
    ("INDIA", (150, 90, 10), "cyclone",
     "Cyclone Akvan nears coast",
     "Landfall due in Andhra Pradesh"),
    ("HEALTH", (120, 60, 160), "cross",
     "US measles-free status lost",
     "5,400+ cases, PAHO — 17 Nov"),
    ("AFRICA", (160, 60, 30), "virus",
     "Ebola in DR Congo",
     "11,285 cases, 5,509 deaths"),
    ("FRANCE", (20, 90, 140), "megaphone",
     "Pay protests across France",
     "146,000 march, official count"),
    ("USA", (150, 30, 60), "star",
     "Peltola wins Alaska Senate",
     "Democrats take Senate 56-44"),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def tint(colour, frac=0.88):
    """Blend a colour toward white for the icon disc background."""
    return tuple(int(c + (255 - c) * frac) for c in colour)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_icon(draw, cx, cy, kind, colour):
    """Hand-drawn geometric icon in a 36px tinted disc centred (cx, cy).

    The disc sits on the tag row (top right), so the headline below
    it gets the full card width -- at 34pt "Ebola in DR Congo" is
    352px wide and must not be squeezed into a 2-line wrap.
    """
    r = 18
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tint(colour))
    c = colour
    if kind == "ship":  # tanker + waves
        draw.polygon([(cx - 15, cy - 2), (cx + 15, cy - 2), (cx + 11, cy + 8),
                      (cx - 11, cy + 8)], fill=c)
        draw.rectangle([cx + 2, cy - 10, cx + 9, cy - 2], fill=c)
        draw.line([cx + 2, cy - 14, cx + 2, cy - 10], fill=c, width=2)
        for wy in (cy + 12, cy + 16):
            draw.arc([cx - 15, wy - 4, cx - 3, wy + 4], 0, 180, fill=c, width=2)
            draw.arc([cx - 1, wy - 4, cx + 11, wy + 4], 0, 180, fill=c, width=2)
    elif kind == "bridge":  # arch bridge
        draw.arc([cx - 15, cy - 12, cx + 15, cy + 12], 180, 360, fill=c, width=3)
        draw.line([cx - 16, cy + 2, cx + 16, cy + 2], fill=c, width=3)
        draw.line([cx - 12, cy + 2, cx - 12, cy + 12], fill=c, width=2)
        draw.line([cx + 12, cy + 2, cx + 12, cy + 12], fill=c, width=2)
        draw.line([cx, cy - 8, cx, cy + 2], fill=c, width=2)
    elif kind == "globe":  # world: circle + meridians
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=c, width=3)
        draw.ellipse([cx - 6, cy - 14, cx + 6, cy + 14], outline=c, width=2)
        draw.line([cx - 14, cy, cx + 14, cy], fill=c, width=2)
    elif kind == "cyclone":  # spiral: three offset arcs
        draw.arc([cx - 14, cy - 14, cx + 14, cy + 14], 200, 20, fill=c, width=3)
        draw.arc([cx - 9, cy - 9, cx + 9, cy + 9], 20, 200, fill=c, width=3)
        draw.arc([cx - 4, cy - 4, cx + 4, cy + 4], 200, 20, fill=c, width=3)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=c)
    elif kind == "cross":  # medical cross
        draw.rectangle([cx - 4, cy - 13, cx + 4, cy + 13], fill=c)
        draw.rectangle([cx - 13, cy - 4, cx + 13, cy + 4], fill=c)
    elif kind == "virus":  # spiked virus
        for a in range(0, 360, 45):
            rad = math.radians(a)
            x1, y1 = cx + 9 * math.cos(rad), cy + 9 * math.sin(rad)
            x2, y2 = cx + 15 * math.cos(rad), cy + 15 * math.sin(rad)
            draw.line([x1, y1, x2, y2], fill=c, width=3)
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=c)
    elif kind == "megaphone":
        draw.polygon([(cx - 12, cy - 4), (cx + 4, cy - 12), (cx + 4, cy + 12),
                      (cx - 12, cy + 4)], fill=c)
        draw.rectangle([cx - 16, cy - 4, cx - 12, cy + 4], fill=c)
        draw.arc([cx + 7, cy - 10, cx + 17, cy + 10], -60, 60, fill=c, width=2)
    elif kind == "star":  # five-point star (ballot / vote)
        pts = []
        for i in range(10):
            rad = math.radians(-90 + i * 36)
            rr = 15 if i % 2 == 0 else 6
            pts.append((cx + rr * math.cos(rad), cy + rr * math.sin(rad)))
        draw.polygon(pts, fill=c)


def draw_story(draw, x, y, w, h, num, tag, colour, kind, head, sub):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=CARD,
                           outline=(220, 216, 200), width=2)
    draw.rectangle([x, y + 14, x + 10, y + h - 14], fill=colour)
    # number badge (bigger than v1: 56 -> 64px)
    draw.ellipse([x + 22, y + 18, x + 86, y + 82], fill=colour)
    draw.text((x + 54, y + 50), str(num), font=font(BOLD, 30),
              fill=WHITE, anchor="mm")
    # icon disc, top right, on the tag row (above the headline)
    draw_icon(draw, x + w - 42, y + 40, kind, colour)
    # tag + headline + subline
    draw.text((x + 100, y + 24), tag, font=font(BOLD, 23), fill=colour)
    hf = font(BOLD, 34)
    lines = wrap(draw, head, hf, w - 118)
    ly = y + 56
    for ln in lines[:2]:
        draw.text((x + 100, ly), ln, font=hf, fill=INK)
        ly += 38
    sf = font(REG, 21)
    slines = wrap(draw, sub, sf, w - 118)[:2]
    # pin the subline block to the card bottom so rows align
    sy = y + h - 26 * len(slines) - 10
    for ln in slines:
        draw.text((x + 100, sy), ln, font=sf, fill=GREY)
        sy += 26


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    # header (slightly shorter than v1 so cards get more room)
    draw.rectangle([0, 0, W, 188], fill=NAVY)
    draw.rectangle([0, 188, W, 194], fill=GOLD)
    draw.text((32, 30), "WORLD NEWS  •  ONE DAY IN ONE PICTURE",
              font=font(BOLD, 25), fill=(190, 206, 228))
    draw.text((32, 62), "18 November 2026", font=font(BOLD, 88), fill=WHITE)
    draw.text((32, 152), "Wednesday — the day's biggest stories",
              font=font(REG, 27), fill=(208, 219, 235))
    # grid: 2 columns x 4 rows, taller cards than v1 (175 -> 178)
    mx, my, gap = 16, 208, 12
    cw = (W - 2 * mx - gap) // 2
    ch = 178
    for i, (tag, colour, kind, head, sub) in enumerate(STORIES):
        cx = mx + (i % 2) * (cw + gap)
        cy = my + (i // 2) * (ch + gap)
        draw_story(draw, cx, cy, cw, ch, i + 1, tag, colour, kind, head, sub)
    # footer: honest about the two dated items (grid ends at y=956)
    draw.text((32, 968),
              "Headlines of 18 Nov 2026 — measles ruling announced 17 Nov; "
              "Ebola figures to 12 Nov.",
              font=font(REG, 18), fill=FOOT)
    img.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
