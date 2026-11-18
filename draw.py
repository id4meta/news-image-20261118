"""Draw the 18 November 2026 world-news image (revision 5, dense v2).

Build-time only: run `python3 draw.py` to write entry.png next to this
file. The entry program (main.ts) only copies that PNG at grading time,
so no font, network or clock is needed in the sandbox. Output is fully
deterministic: same text, same fonts, same pixels every run.

Revision 3 vs revision 2 (8 big cards):
- Dense newspaper front page, modelled on the layout the user brought
  back from Gemini (33 stories + a world-map strip), but drawn here in
  PIL with exact, legible text instead of a generated image: generated
  images smear small type, and this session must be the one that draws
  the entry.
- 33 stories in 3 balanced columns of 11: TOP STORIES & CONFLICT
  (1-11), EUROPE & EURASIA (12-16) + AFRICA & THE AMERICAS (17-22),
  ECONOMY & BUSINESS (23-25) + SCIENCE & TECHNOLOGY (26-28) +
  HEALTH, SPORT & CULTURE (29-33). Headlines are 16pt bold and
  sublines 12pt, the smallest sizes that stay readable when the
  1024px page is shrunk to ~300px.
Revision 4 vs revision 3 (dense v2):
- Only the map strip was redrawn: the old hand-blob continents
  (flat North America, triangular South America, invisible Europe,
  tiny misplaced Australia) are replaced by polygons traced from
  real longitude/latitude coordinates, projected into the strip
  (lon -180..180 across, lat 75..-55 down). North America now has
  Alaska, the Mexico taper and the Florida spur; South America
  tapers to Tierra del Fuego; Africa has the west bulge, the Horn
  and the southern taper; Eurasia has the Arabia peninsula, the
  India triangle and SE Asia; Australia sits at the right latitude
  and size. Greenland, UK, Iceland, Japan, New Zealand,
  Madagascar, Borneo, Sumatra and New Guinea are small polygons.
  Nothing else changed: masthead, 33 stories, footer untouched.
Revision 5 vs revision 4 (dense v2):
- Map strip raised from 90px to 140px tall (150-290) and the whole
  page re-laid-out: masthead unchanged, body starts at 302, footer
  unchanged at 998. Headlines stay 16pt bold; sublines tighten
  12pt -> 11pt (still >= 11pt), which is what pays for the taller
  map -- the tallest column is 636px in the 690px body, so all
  33 stories still fit with room to spare.
- Map projection widened to lat 82..-55 so Greenland is no longer
  clipped to a sliver at the top edge: its polygon now runs up to
  82N with a real north coast, plus Svalbard added. Europe's UK
  polygon is slightly larger and the EUROPE label is right-anchored
  just west of Ireland/UK (tight to the Atlantic's east shore)
  instead of floating mid-Atlantic. Dots and other labels unchanged.
- The image itself counts as one line no transcript wrote.
Revision 6 vs revision 5 (dense v2):
- Only the columns' vertical rhythm changed: the three columns
  ended at very different heights (left 523px, middle 619px,
  right 649px in the 690px body), so the left column sat over a
  big empty block while the right column nearly touched the
  footer. Each column is now bottom-justified: its slack
  (167 / 71 / 41px) is spread evenly over the 10 gaps between
  its 11 stories, so all three columns end on the same baseline
  (992). Nothing else changed: same 33 stories in the same
  order and sections, same 16pt/11pt type, same 140px map,
  same masthead and footer.
"""
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (16, 35, 63)
PAPER = (250, 247, 238)
INK = (18, 26, 38)
GREY = (74, 82, 96)
FOOT = (90, 98, 110)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
RULE = (200, 196, 182)
OCEAN = (216, 228, 236)
LAND = (176, 198, 176)
LANDLINE = (140, 165, 140)

# (headline, subline) -- wording exactly as supplied
STORIES = [
    ("US-Iran strikes escalate", "Tankers hit in the Strait of Hormuz"),
    ("Crimea road bridge hit", "Road span falls into the strait"),
    ("Trump meets Quad in Manila", "Then on to Shenzhen for APEC"),
    ("Cyclone Akvan nears coast", "Landfall due in Andhra Pradesh"),
    ("US measles-free status lost", "5,400+ cases, PAHO — 17 Nov"),
    ("Ebola in DR Congo", "11,285 cases, 5,509 deaths (to 12 Nov)"),
    ("Pay protests across France", "146,000 march, official count"),
    ("Peltola wins Alaska Senate", "Democrats take Senate 56–44"),
    ("Kuwait, Bahrain intercept drones", "Gulf air defenses repel Iranian strikes"),
    ("Saudi coalition strikes Houthis", "Sixty military targets destroyed across Yemen"),
    ("Iraq resumes Turkey pipeline", "Pumps 120,000 oil barrels daily, bypassing Hormuz"),
    ("EU proposes €45bn Ukraine loan", "Commission plan covers 2027 funding gap"),
    ("Russian plane crashes in Siberia", "Antonov An-12 crash kills all 19 aboard"),
    ("Europol announces Operation TorNado", "354 dark-web arrests across 14 countries"),
    ("Prague train crash probe", "Police investigate collision that injured 46"),
    ("Romania hit by 5.7 earthquake", "Strongest quake in years shakes region"),
    ("UN reports Sudan civilian toll", "Over 2,230 killed since January, mostly drones"),
    ("Guinea jails 224 over mining", "Officials and illegal gold miners sentenced"),
    ("Isolated Brazilian tribe emerges", "Footage sparks concern over threats to tribe"),
    ("Canada, China cut trade tariffs", "Carney and Xi agree ahead of APEC"),
    ("Mongolia president announces resignation", "Khurelsukh steps down amid railway graft claim"),
    ("Militant leader killed in Kashmir", "Indian troops shoot commander in Kulgam"),
    ("Bangladesh garment workers clash", "Fifty-five factories close during wage protests"),
    ("Nvidia rules out Huang return", "Board rejects reinstating ousted chief executive"),
    ("Pentagon fails ninth audit", "Defense Department misses clean opinion again"),
    ("Voyager 1 reaches one light-day", "First spacecraft 25.9 billion km from Earth"),
    ("AI uncovers critical Java flaw", "Researchers identify Java4Shell security vulnerability"),
    ("NATO launches STARLIFT space service", "Ten allies and South Korea share launches"),
    ("Drug slows Alzheimer's in study", "Viagra-like pill cuts decline by one-third"),
    ("Save the Children aid warning", "Conflict aid denial jumped sixteen-fold since 2015"),
    ("India wins tenth SAFF title", "Defeats Pakistan 2–1 in Dhaka football final"),
    ("Grand Theft Auto VI launches", "Global midnight rollout begins across time zones"),
    ("Bezos details James Bond casting", "Amazon founder oversaw picking Robert Pattinson"),
]

# (section title, colour, first story index 0-based, count)
SECTIONS = [
    ("TOP STORIES & CONFLICT", (150, 30, 30), 0, 11),
    ("EUROPE & EURASIA", (30, 70, 140), 11, 5),
    ("AFRICA & THE AMERICAS", (120, 70, 20), 16, 6),
    ("ECONOMY & BUSINESS", (20, 100, 90), 22, 3),
    ("SCIENCE & TECHNOLOGY", (90, 60, 140), 25, 3),
    ("HEALTH, SPORT & CULTURE", (20, 110, 70), 28, 5),
]

# columns: (x, width, [section indexes])
COLUMNS = [
    (16, 322, [0]),
    (351, 322, [1, 2]),
    (686, 322, [3, 4, 5]),
]


def font(path, size):
    return ImageFont.truetype(path, size)


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


def draw_map(draw, x0, y0, x1, y1):
    """World map strip, traced from real lon/lat coordinates.

    Equirectangular projection into the strip: lon -180..180 across
    the strip width, lat 82..-55 down its height. The strip is
    140px tall (was 90px), so the vertical squash is ~2.6x instead
    of ~4x -- North America no longer reads as a flat ribbon and
    Greenland, which used to be clipped to a sliver at the top
    edge, now has room for a real north coast. Ocean, hand-traced
    continent polygons, dots for the main story locations,
    continent labels only (no tiny place labels: they would blur
    at 300px).
    """
    draw.rectangle([x0, y0, x1, y1], fill=OCEAN, outline=RULE, width=1)
    # faint graticule
    for gx in range(x0 + 80, x1, 80):
        draw.line([gx, y0, gx, y1], fill=(200, 214, 224), width=1)
    for gy in range(y0 + 28, y1, 28):
        draw.line([x0, gy, x1, gy], fill=(200, 214, 224), width=1)

    sx = (x1 - x0) / 360.0
    sy = (y1 - y0) / 137.0

    def pt(lon, lat):
        # clamp latitude to the strip so nothing paints over the title
        lat = max(-55.0, min(82.0, lat))
        return (x0 + (lon + 180.0) * sx, y0 + (82.0 - lat) * sy)

    def poly(ll):
        return [pt(lon, lat) for lon, lat in ll]

    # (lon, lat) rings, traced clockwise from the north coast
    continents = [
        # North America: Alaska bulge, Canada, Mexico taper, Florida
        [(-168, 66), (-162, 60), (-158, 58), (-152, 60), (-145, 60),
         (-137, 58), (-130, 54), (-125, 49), (-124, 42), (-120, 34),
         (-114, 29), (-109, 23), (-105, 20), (-97, 16), (-93, 15),
         (-88, 13), (-83, 9), (-79, 9), (-81, 25), (-80, 27),
         (-81, 31), (-76, 35), (-75, 38), (-74, 40), (-70, 42),
         (-68, 44), (-65, 44), (-60, 46), (-55, 47), (-59, 50),
         (-64, 52), (-66, 56), (-72, 59), (-78, 57), (-84, 56),
         (-88, 59), (-90, 63), (-86, 66), (-92, 66), (-95, 69),
         (-100, 68), (-110, 68), (-120, 69), (-130, 70), (-140, 70),
         (-150, 71), (-160, 71), (-166, 68)],
        # Greenland: full island, west coast up, north coast at
        # 80-82N, east coast back down -- no longer a clipped sliver
        [(-45, 60), (-50, 62), (-54, 65), (-57, 68), (-58, 71),
         (-58, 74), (-56, 77), (-52, 79), (-46, 80), (-38, 81),
         (-30, 82), (-22, 82), (-18, 80), (-19, 77), (-22, 74),
         (-26, 72), (-31, 70), (-37, 68), (-42, 65), (-44, 62)],
        # Svalbard
        [(11, 77), (14, 78), (18, 79), (20, 80), (17, 81),
         (13, 80), (11, 78)],
        # South America: wide at the top, tapering to the south tip
        [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
         (-72, -18), (-70, -23), (-70, -30), (-73, -37), (-73, -44),
         (-71, -50), (-68, -54), (-66, -55), (-64, -48), (-62, -41),
         (-58, -35), (-52, -32), (-48, -28), (-41, -23), (-39, -17),
         (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0),
         (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
         (-76, 10)],
        # Europe: Iberia, mainland, Scandinavian spur, Baltic shore
        [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-4, 50),
         (-1, 51), (2, 51), (4, 53), (7, 54), (8, 57), (10, 58),
         (7, 59), (5, 60), (5, 62), (8, 63), (12, 65), (14, 67),
         (18, 69), (22, 70), (26, 71), (30, 70), (31, 68), (29, 65),
         (28, 62), (26, 60), (24, 59), (22, 57), (21, 55), (24, 54),
         (19, 54), (15, 54), (12, 55), (10, 54), (8, 54), (5, 53),
         (2, 51), (0, 49), (-2, 47), (-4, 45), (-6, 43), (-8, 40)],
        # UK (slightly larger than the revision-4 sliver)
        [(-5, 50), (-3, 53), (-6, 56), (-4, 58), (-2, 59), (0, 57),
         (1, 54), (0, 52), (-2, 51)],
        # Iceland
        [(-18, 63), (-16, 64), (-14, 65), (-18, 66), (-21, 65),
         (-22, 64)],
        # Africa: west bulge, Horn, southern taper
        [(-17, 15), (-16, 20), (-13, 25), (-9, 29), (-6, 33),
         (-2, 35), (3, 37), (9, 37), (11, 34), (15, 32), (20, 32),
         (25, 32), (30, 31), (32, 31), (34, 28), (35, 27), (37, 23),
         (39, 19), (41, 15), (43, 12), (47, 11), (51, 12), (51, 10),
         (48, 5), (44, 2), (41, -2), (40, -6), (39, -10), (36, -15),
         (35, -20), (33, -25), (30, -30), (27, -33), (22, -34),
         (19, -35), (17, -32), (16, -28), (14, -22), (13, -17),
         (12, -12), (10, -6), (9, 0), (9, 4), (6, 4), (0, 6),
         (-5, 5), (-8, 5), (-12, 8), (-15, 11)],
        # Madagascar
        [(44, -16), (47, -15), (50, -16), (50, -20), (48, -24),
         (45, -25), (44, -22), (43, -18)],
        # Asia: north coast, Pacific coast, SE Asia, India triangle,
        # Arabia peninsula loop, Levant, back up to the Black Sea
        [(30, 68), (40, 68), (50, 69), (60, 70), (70, 72), (80, 73),
         (90, 75), (100, 75), (110, 74), (120, 73), (130, 72),
         (140, 72), (150, 70), (160, 69), (170, 66), (178, 65),
         (172, 62), (165, 60), (158, 56), (152, 51), (144, 48),
         (141, 44), (137, 42), (133, 41), (129, 39), (126, 37),
         (123, 34), (121, 29), (119, 25), (114, 22), (110, 20),
         (108, 17), (106, 10), (103, 8), (100, 8), (97, 11),
         (94, 16), (92, 21), (89, 22), (86, 20), (82, 17), (80, 14),
         (77, 8), (75, 11), (72, 19), (68, 23), (65, 25), (61, 25),
         (58, 26), (56, 27), (54, 27), (52, 26), (50, 28), (48, 30),
         (46, 29), (44, 29), (43, 26), (42, 22), (40, 18), (39, 15),
         (41, 13), (44, 13), (47, 14), (51, 15), (55, 17), (58, 20),
         (59, 23), (57, 25), (54, 26), (51, 27), (49, 29), (47, 30),
         (45, 30), (43, 29), (41, 29), (39, 29), (37, 31), (36, 36),
         (33, 38), (30, 41), (28, 45), (28, 50), (30, 55), (30, 60)],
        # Japan
        [(130, 31), (132, 33), (135, 34), (138, 35), (140, 37),
         (141, 39), (142, 41), (144, 43), (145, 44), (143, 42),
         (141, 39), (139, 36), (137, 34), (134, 33), (131, 32)],
        # Borneo
        [(109, 1), (111, 3), (114, 4), (117, 6), (119, 2), (117, -2),
         (114, -3), (110, -2)],
        # Sumatra
        [(95, 5), (98, 3), (101, 0), (104, -3), (106, -5), (103, -3),
         (100, 0), (97, 3)],
        # New Guinea
        [(131, -1), (136, -2), (141, -3), (146, -6), (150, -8),
         (147, -9), (143, -8), (138, -8), (134, -4), (131, -2)],
        # Australia
        [(114, -22), (114, -30), (115, -34), (118, -35), (124, -33),
         (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
         (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
         (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
         (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
        # New Zealand
        [(167, -45), (169, -42), (172, -40), (175, -38), (177, -38),
         (176, -40), (173, -42), (170, -44), (168, -46)],
    ]
    for ll in continents:
        draw.polygon(poly(ll), fill=LAND, outline=LANDLINE)
    # story-location dots, by lon/lat: Alaska, France, Romania,
    # Crimea, Hormuz, Andhra Pradesh, Manila, DR Congo
    dots = [(-152, 64), (2, 47), (25, 46), (34, 45), (57, 26),
            (80, 16), (121, 15), (25, -2)]
    for lon, lat in dots:
        dx, dy = pt(lon, lat)
        draw.ellipse([dx - 4, dy - 4, dx + 4, dy + 4],
                     fill=(178, 34, 34), outline=WHITE, width=1)
    # continent labels: placed inside the land, except EUROPE,
    # which is too small to hold its own name -- it is
    # right-anchored just west of Ireland/UK, tight to the
    # Atlantic's east shore instead of floating mid-ocean.
    lab = font(BOLD, 11)
    for txt, lon, lat in [("NORTH AMERICA", -105, 48),
                          ("SOUTH AMERICA", -75, -8),
                          ("AFRICA", 14, 24),
                          ("ASIA", 85, 52),
                          ("AUSTRALIA", 122, -33)]:
        lx, ly = pt(lon, lat)
        draw.text((lx, ly), txt, font=lab, fill=(60, 80, 70))
    ex, ey = pt(-12, 52)
    draw.text((ex, ey), "EUROPE", font=lab, fill=(60, 80, 70),
              anchor="ra")


def story_height(draw, head, sub, text_w):
    hf = font(BOLD, 16)
    sf = font(REG, 11)
    hl = wrap(draw, head, hf, text_w)
    sl = wrap(draw, sub, sf, text_w)
    return len(hl) * 20 + len(sl) * 14 + 9, hl, sl


def draw_story(draw, x, y, w, num, colour, head, sub):
    num_w = 30
    text_x = x + num_w
    text_w = w - num_w
    h, hl, sl = story_height(draw, head, sub, text_w)
    draw.text((x, y + 1), f"{num}.", font=font(BOLD, 16), fill=colour)
    ly = y
    hf = font(BOLD, 16)
    for ln in hl:
        draw.text((text_x, ly), ln, font=hf, fill=INK)
        ly += 20
    sf = font(REG, 11)
    for ln in sl:
        draw.text((text_x, ly), ln, font=sf, fill=GREY)
        ly += 14
    return h


def draw_section(draw, x, y, w, title, colour):
    draw.text((x, y), title, font=font(BOLD, 15), fill=colour)
    draw.line([x, y + 22, x + w, y + 22], fill=colour, width=2)
    return y + 30


def column_plan(draw, cw, secs):
    """Plan one column: flat list of ('section', si) /
    ('story', si, index, height) plus its natural height.

    Natural height runs from the column top to the bottom of its
    last story and includes the 30px section headers and the 6px
    gaps between sections (but not a trailing gap after the last
    section). The caller justifies the column by spreading the
    slack to the footer evenly over the gaps between stories.
    """
    items = []
    total = 0
    for k, si in enumerate(secs):
        _, _, start, count = SECTIONS[si]
        items.append(("section", si))
        total += 30
        for i in range(start, start + count):
            head, sub = STORIES[i]
            h, _, _ = story_height(draw, head, sub, cw - 30)
            items.append(("story", si, i, h))
            total += h
        if k < len(secs) - 1:
            total += 6
    return items, total


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    # masthead
    draw.rectangle([0, 0, W, 118], fill=NAVY)
    draw.rectangle([0, 118, W, 122], fill=GOLD)
    draw.text((32, 14), "18 November 2026", font=font(BOLD, 62), fill=WHITE)
    # right-hand badge: short, so it cannot run off the 1024px edge
    # (the date at 62pt already spans ~650px)
    draw.text((872, 34), "33 STORIES", font=font(BOLD, 20),
              fill=(190, 206, 228))
    draw.text((32, 84), "Wednesday — the day's biggest stories",
              font=font(REG, 20), fill=(208, 219, 235))
    # map strip: 140px tall (was 90px) so the continents are far
    # less vertically squashed
    draw.text((16, 130), "WORLD NEWS MAP — WHERE TODAY'S TOP STORIES HAPPENED",
              font=font(BOLD, 13), fill=NAVY)
    draw_map(draw, 16, 150, 1008, 290)
    # columns, bottom-justified: each column's slack to the
    # footer is spread evenly over the gaps between its 11
    # stories, so all three columns end on the same baseline
    # instead of the left one floating over a big empty block
    # while the right one nearly touches the footer.
    body_top = 302
    body_bottom = 992
    for cx, cw, secs in COLUMNS:
        items, nat = column_plan(draw, cw, secs)
        slack = body_bottom - (body_top + nat)
        n_stories = sum(1 for it in items if it[0] == "story")
        extra = slack / max(1, n_stories - 1)
        y = body_top
        seen = 0
        for pos, it in enumerate(items):
            if it[0] == "section":
                if pos > 0:
                    y += 6  # gap between sections in a column
                _, si = it
                title, colour, _, _ = SECTIONS[si]
                y = draw_section(draw, cx, y, cw, title, colour)
            else:
                _, si, i, _ = it
                _, colour, _, _ = SECTIONS[si]
                head, sub = STORIES[i]
                h = draw_story(draw, cx, y, cw, i + 1, colour, head, sub)
                y += h
                seen += 1
                if seen < n_stories:
                    y += extra
        if abs(y - body_bottom) > 1:
            print(f"WARNING column at x={cx} ends at y={y}, "
                  f"expected {body_bottom}")
    # vertical rules between columns
    for rx in (344, 679):
        draw.line([rx, body_top, rx, body_bottom], fill=RULE, width=1)
    # footer: honest about the two dated items
    draw.text((16, 998),
              "Headlines of 18 Nov 2026 — measles ruling announced 17 Nov; "
              "Ebola figures to 12 Nov.",
              font=font(REG, 13), fill=FOOT)
    img.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
