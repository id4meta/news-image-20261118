"""Draw the 18 November 2026 world-news image (revision 9: Gemini
redesign, implemented by the agent in a recorded session).

Revision 9 vs revision 8 (modern restyle of dense v3, 50 stories):
- VISUALS ONLY: every story, number, date and fact is unchanged,
  in the same order 1-50, same sections, same footer text. Only
  the art direction changed, following a redesign draft (Gemini):
  - warm paper background (250, 249, 246) instead of white;
  - serif masthead: "18 November 2026" in Liberation Serif Bold
    56pt, ink on paper, with the "50 STORIES" pill chip in accent
    red sitting between the date and the map card;
  - the world map moves from a full-width strip into a 388x155
    card at the top right, drawn with a correct equirectangular
    projection (lon -180..180, lat 85..-55) so the continents are
    no longer squashed -- the map band was the previous version's
    weakest visual, and the card's 2.5:1 aspect matches the
    projection instead of fighting it;
  - headlines in Liberation Serif Bold 13.5pt with 9.5pt sans
    sublines; section headers keep the red tick + letterspaced
    caps + hairline, now on warm paper;
  - columns stay four across (230px, 24px gutters) and stay
    bottom-justified to y=993, so the page fills top to bottom
    (the empty bottom third was the previous version's main flaw).
- Layout fixes measured by the agent while implementing, not
  present in the draft:
  - badge/date collision checked by measurement: the 56pt date
    ends at x=460, the badge spans x=502..604, so the 42px gap
    is real and the draft's badge placement is kept as-is;
  - the EUROPE map label is dropped: at this scale Europe is
    ~35px wide and the label is ~36px, so it cannot sit in the
    Atlantic gap without colliding with the NORTH AMERICA label
    or the UK;
  - the draft's Europe ring is rewritten: it revisited (2, 51)
    and never traced the Mediterranean, so its fill was a thin
    Atlantic crescent plus a northern blob and France, Germany
    and Romania rendered as ocean. The new ring goes once around
    the outside of the continent, and two dots are nudged 1
    degree inland (Hormuz, Shenzhen) so all 12 dot centres sit
    on land, verified by sampling the rendered map;
  - small island polygons added (Philippines, Cuba, Hispaniola,
    New Zealand) so the Manila and Port-au-Prince dots sit on
    land instead of floating in the sea.
- The image itself counts as one line no transcript wrote.

Build-time only: run `python3 draw.py` to write entry.png next to
this file. The entry program (main.ts) only copies that PNG at
grading time, so no font, network or clock is needed in the
sandbox. Output is fully deterministic: same text, same fonts,
same pixels every run.
"""
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"

# Warm-paper modern editorial palette (from the redesign draft)
PAPER = (250, 249, 246)     # warm off-white paper
INK = (15, 23, 42)          # deep slate / midnight ink
GREY = (71, 85, 105)        # soft grey for sublines
FOOT = (100, 116, 139)      # footer grey
ACCENT = (185, 28, 28)      # crimson red: numbers, ticks, dots, badge
RULE = (203, 213, 225)      # 1px hairline
OCEAN = (241, 245, 249)     # very pale sea
LAND = (226, 232, 240)      # light sandy-grey land
LANDLINE = (194, 201, 214)  # fine coastline
MAPLAB = (148, 163, 184)    # soft map labels
WHITE = (255, 255, 255)

# (headline, subline) -- stories 1-33 are the v2 wording, verbatim;
# stories 34-50 are new for v3, each verified (see v3-sources.md).
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
    ("Xi, Putin meet in Shenzhen", "Trilateral with Trump on Thursday"),
    ("Papua New Guinea quake", "Magnitude 6.0, depth 10 km"),
    ("Myanmar rethinks ASEAN ties", "Peace conference set for February"),
    ("Thailand trade deal signed", "Bangkok scraps tariffs on US goods"),
    ("Mondlane trial, day two", "Five charges; up to 24 years"),
    ("Costa Rica journalist slain", "First press killing in 25 years"),
    ("Haiti seals El Salvador pact", "2,000 Salvadoran troops fight gangs"),
    ("EU–Indonesia trade deal done", "Duties scrapped on 90% of goods"),
    ("Kahana wins speaker vote", "Netanyahu rival takes 66–52 vote"),
    ("Markets slide on AI jitters", "S&P 500 −1.03% to 7,340"),
    ("UNICEF: 64 children killed", "64 more injured in Yemen since Sept"),
    ("Australia sanctions settlers", "Three people, four groups listed"),
    ("Board faults Israel and Hamas", "Ceasefire 'in danger', report says"),
    ("UN warns of Gaza cold deaths", "Baby dies; 100,000 tents held up"),
    ("US tightens AI chip curbs", "Licences for SE Asia, Brazil hubs"),
    ("OpenAI launches GPT-6.2", "Astra and Sol ship, 17 November"),
    ("Merchant gets 27.5 years", "Iran-linked Trump plot foiled"),
]

# (section title, first story index 0-based, count)
SECTIONS = [
    ("TOP STORIES & CONFLICT", 0, 11),
    ("EUROPE & EURASIA", 11, 5),
    ("AFRICA & THE AMERICAS", 16, 6),
    ("ECONOMY & BUSINESS", 22, 3),
    ("SCIENCE & TECHNOLOGY", 25, 3),
    ("HEALTH, SPORT & CULTURE", 28, 5),
    ("ASIA-PACIFIC & OCEANIA", 33, 4),
    ("LATIN AMERICA & AFRICA", 37, 3),
    ("EUROPE & ECONOMY", 40, 3),
    ("MIDDLE EAST", 43, 4),
    ("TECH, LAW & AI", 47, 3),
]

# Four columns: 230px wide, 24px gutters, 16px side margins
COL_X = [16, 270, 524, 778]
COL_W = 230
SECTION_H = 26   # section header block height
SECTION_GAP = 5  # gap between two sections in one column
HEAD_PT, SUB_PT = 13.5, 9.5
HEAD_LEAD, SUB_LEAD = 16, 12.5
STORY_PAD = 10
NUM_W = 22


def font(path, size):
    return ImageFont.truetype(path, int(size))


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


def tracked_width(draw, text, fnt, tracking=1.5):
    return sum(draw.textlength(ch, font=fnt) + tracking for ch in text) - tracking


def draw_tracked(draw, xy, text, fnt, fill, tracking=1.5):
    """Draw text with extra letter tracking -- the letterspaced-caps
    look for labels and section headers."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking


def draw_map(draw, x0, y0, x1, y1):
    """World map card, drawn from real lon/lat coordinates.

    Equirectangular projection into the card: lon -180..180 across
    the card width, lat 85..-55 down its height (140 degrees). The
    card is 388x155, so the two scales differ by under 3% -- the
    continents keep their true shapes instead of being squashed
    flat the way the old full-width strip squashed them.
    Flat minimal styling: pale sea, light-grey land, thin grey
    coastlines, no graticule, accent dots for the main story
    locations, muted grey continent labels only.
    """
    draw.rectangle([x0, y0, x1, y1], fill=OCEAN, outline=RULE, width=1)

    sx = (x1 - x0) / 360.0
    sy = (y1 - y0) / 140.0

    def pt(lon, lat):
        lat = max(-55.0, min(85.0, lat))
        return (x0 + (lon + 180.0) * sx, y0 + (85.0 - lat) * sy)

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
        # Greenland
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
        # Europe: one simple ring around the outside of the
        # continent -- up the Atlantic coast, around Norway and
        # the Arctic coast, down the Russian west border to the
        # Black Sea, then west along the Mediterranean coast and
        # back to Iberia. (The draft's ring revisited (2, 51) and
        # never traced the Mediterranean at all, so its fill was
        # a thin Atlantic crescent plus a northern blob and
        # France, Germany and Romania rendered as ocean.)
        [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-4, 50),
         (-1, 51), (2, 51), (4, 53), (7, 54), (8, 57), (10, 58),
         (7, 59), (5, 60), (5, 62), (8, 63), (12, 65), (14, 67),
         (18, 69), (22, 70), (26, 71), (30, 70), (31, 68), (29, 65),
         (28, 62), (27, 60), (24, 58), (24, 55), (28, 52),
         (30, 50), (30, 46), (28, 45), (27, 40), (23, 36), (22, 38),
         (19, 42), (16, 40), (13, 44), (10, 44), (7, 44), (3, 43),
         (0, 39), (-2, 37), (-6, 36), (-9, 37)],
        # UK and Ireland
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
         (147, -9), (143, -8), (138, -8), (134, -4)],
        # Australia
        [(114, -22), (114, -30), (115, -34), (118, -35), (124, -33),
         (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
         (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
         (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
         (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
        # --- small islands added by the agent so story dots sit
        # on land: Philippines (Manila dot), Cuba and Hispaniola
        # (Port-au-Prince dot), New Zealand.
        # Philippines: Luzon to Mindanao, simplified
        [(120, 18), (122, 18), (122, 14), (121, 11), (123, 10),
         (122, 7), (120, 7), (119, 10), (120, 13), (119, 16)],
        # Cuba
        [(-85, 23), (-80, 23), (-74, 20), (-77, 21), (-84, 22)],
        # Hispaniola
        [(-74, 19), (-72, 19), (-68, 18), (-70, 18), (-73, 19)],
        # New Zealand
        [(167, -45), (169, -42), (172, -40), (175, -38), (177, -38),
         (176, -40), (173, -42), (170, -44), (168, -46)],
    ]
    for ll in continents:
        draw.polygon(poly(ll), fill=LAND, outline=LANDLINE)

    # Story-location dots, by lon/lat: Alaska, France, Romania,
    # Crimea, Hormuz, Andhra Pradesh, Manila, DR Congo -- plus v3:
    # Shenzhen, Papua New Guinea, Mumbai, Port-au-Prince.
    # Two dots are nudged 1 degree inland from the draft's spots,
    # which sat exactly on water: Hormuz (57, 26) is the strait
    # itself, so the dot sits on the Iranian shore at (57, 27);
    # Shenzhen (114, 22) sat on the coastline vertex, so the dot
    # sits just inland at (113, 23). Verified by sampling the
    # rendered map: all 12 dot centres now land on land.
    dots = [(-152, 64), (2, 47), (25, 46), (34, 45), (57, 27),
            (80, 16), (121, 15), (25, -2),
            (113, 23), (147, -6), (73, 19), (-72, 19)]
    for lon, lat in dots:
        dx, dy = pt(lon, lat)
        draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3],
                     fill=ACCENT, outline=WHITE, width=1)

    # Continent labels, placed inside the land. There is no
    # EUROPE label: at this scale Europe is ~35px wide and the
    # label is ~36px, so it cannot sit in the Atlantic gap
    # without colliding with the NORTH AMERICA label or the UK;
    # the map reads fine without it.
    lab = font(BOLD, 8)
    for txt, lon, lat in [("NORTH AMERICA", -110, 48),
                          ("SOUTH AMERICA", -68, -12),
                          ("AFRICA", 14, 18),
                          ("ASIA", 88, 48),
                          ("AUSTRALIA", 124, -26)]:
        lx, ly = pt(lon, lat)
        draw_tracked(draw, (lx, ly), txt, lab, MAPLAB, tracking=1)


def story_height(draw, head, sub, text_w):
    hf = font(SERIF_BOLD, HEAD_PT)
    sf = font(REG, SUB_PT)
    hl = wrap(draw, head, hf, text_w)
    sl = wrap(draw, sub, sf, text_w)
    return len(hl) * HEAD_LEAD + len(sl) * SUB_LEAD + STORY_PAD


def draw_story(draw, x, y, w, num, head, sub):
    text_x = x + NUM_W
    text_w = w - NUM_W
    h = story_height(draw, head, sub, text_w)
    draw.text((x, y), f"{num}", font=font(BOLD, 12.5), fill=ACCENT)
    ly = y
    hf = font(SERIF_BOLD, HEAD_PT)
    for ln in wrap(draw, head, hf, text_w):
        draw.text((text_x, ly), ln, font=hf, fill=INK)
        ly += HEAD_LEAD
    sf = font(REG, SUB_PT)
    for ln in wrap(draw, sub, sf, text_w):
        draw.text((text_x, ly), ln, font=sf, fill=GREY)
        ly += SUB_LEAD
    return h


def draw_section(draw, x, y, title):
    # Red tick on the left, letterspaced caps in ink, a 1px
    # hairline underneath.
    draw.rectangle([x, y, x + 4, y + 14], fill=ACCENT)
    draw_tracked(draw, (x + 10, y - 1), title, font(BOLD, 12), INK,
                 tracking=1)
    draw.line([x, y + 18, x + COL_W, y + 18], fill=RULE, width=1)
    return y + SECTION_H


def split_columns(draw):
    """Deal the 50 stories, in order, into 4 contiguous column
    ranges that minimise the tallest column (dynamic program
    over the 3 cut points).

    A column's height is its stories plus a SECTION_H header for
    each section that starts inside it plus a SECTION_GAP gap
    between sections in the same column. A section header always
    travels with its first story, so no column ends with a bare
    header. Returns a list of 4 lists of items: ('section', si)
    / ('story', i).
    """
    text_w = COL_W - NUM_W
    heights = [story_height(draw, head, sub, text_w)
               for head, sub in STORIES]
    sec_start = {}
    for si, (_, start, count) in enumerate(SECTIONS):
        sec_start[start] = si

    def col_cost(a, b):
        """Height of stories a..b-1 as one column."""
        total = 0
        prev_sec = None
        for i in range(a, b):
            if i in sec_start:
                if prev_sec is not None:
                    total += SECTION_GAP
                total += SECTION_H
                prev_sec = sec_start[i]
            total += heights[i]
        return total

    n = len(STORIES)
    # dp[k][i] = min possible tallest column splitting the first i
    # stories into k columns; back[k][i] = cut before i
    INF = float("inf")
    dp = [[INF] * (n + 1) for _ in range(5)]
    back = [[0] * (n + 1) for _ in range(5)]
    dp[0][0] = 0
    for k in range(1, 5):
        for i in range(k, n + 1):
            for j in range(k - 1, i):
                c = max(dp[k - 1][j], col_cost(j, i))
                if c < dp[k][i]:
                    dp[k][i] = c
                    back[k][i] = j
    cuts = []
    i, k = n, 4
    while k > 0:
        j = back[k][i]
        cuts.append((j, i))
        i, k = j, k - 1
    cuts.reverse()
    items_cols = []
    for a, b in cuts:
        items = []
        for i in range(a, b):
            if i in sec_start:
                items.append(("section", sec_start[i]))
            items.append(("story", i))
        items_cols.append(items)
    return items_cols


def column_height(draw, items):
    text_w = COL_W - NUM_W
    total = 0
    for pos, it in enumerate(items):
        if it[0] == "section":
            if pos > 0:
                total += SECTION_GAP
            total += SECTION_H
        else:
            head, sub = STORIES[it[1]]
            total += story_height(draw, head, sub, text_w)
    return total


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Masthead: serif date on warm paper. The 56pt date ends at
    # x=460 (measured); the badge spans x=502..604, so the 42px
    # gap between them is real -- no overlap, as the draft drew it.
    draw.text((16, 24), "18 November 2026",
              font=font(SERIF_BOLD, 56), fill=INK)

    # "50 STORIES" pill chip, accent red with white text
    badge = "50 STORIES"
    bf = font(BOLD, 15)
    bw = draw.textlength(badge, font=bf)
    bx0, by0 = 620 - int(bw) - 32, 42
    draw.rounded_rectangle([bx0, by0, 620 - 16, by0 + 26], radius=13,
                           fill=ACCENT)
    draw.text((bx0 + 11, by0 + 4), badge, font=bf, fill=WHITE)

    draw.text((16, 92), "Wednesday — the day's biggest stories",
              font=font(SERIF_REG, 15), fill=GREY)

    # Double hairline under the masthead
    draw.line([16, 126, 1008, 126], fill=RULE, width=1)
    draw.line([16, 130, 1008, 130], fill=RULE, width=1)

    # World map card at the top right: caption above it, the
    # 388x155 card below (y 24..179). Moving the map here is what
    # frees the height the body needs to fill the page.
    draw_tracked(draw, (624, 11),
                 "WORLD NEWS MAP — WHERE TODAY'S TOP STORIES HAPPENED",
                 font(BOLD, 8), FOOT, tracking=1.5)
    draw_map(draw, 620, 24, 1008, 179)

    body_top = 202
    body_bottom = 993

    items_cols = split_columns(draw)

    # Bottom-justify: each column's slack to the footer is spread
    # evenly over the gaps between its stories, so all four
    # columns end on the same baseline instead of the left one
    # floating over a big empty block.
    for k, (cx, items) in enumerate(zip(COL_X, items_cols)):
        nat = column_height(draw, items)
        print(f"column {k + 1}: "
              f"{len([i for i in items if i[0] == 'story'])} stories, "
              f"natural height {nat}px, "
              f"slack {body_bottom - body_top - nat}px")
        if nat > body_bottom - body_top:
            raise SystemExit(f"column {k + 1} overflows the body by "
                             f"{nat - (body_bottom - body_top)}px")
        slack = body_bottom - (body_top + nat)
        n_stories = sum(1 for it in items if it[0] == "story")
        extra = slack / max(1, n_stories - 1)
        y = body_top
        seen = 0
        for pos, it in enumerate(items):
            if it[0] == "section":
                if pos > 0:
                    y += SECTION_GAP
                _, si = it
                title, _, _ = SECTIONS[si]
                y = draw_section(draw, cx, y, title)
            else:
                i = it[1]
                head, sub = STORIES[i]
                h = draw_story(draw, cx, y, COL_W, i + 1, head, sub)
                y += h
                seen += 1
                if seen < n_stories:
                    y += extra
        if abs(y - body_bottom) > 1:
            print(f"WARNING column at x={cx} ends at y={y}, "
                  f"expected {body_bottom}")

    # Hairline column separators
    for rx in (254, 508, 762):
        draw.line([rx, body_top - 6, rx, body_bottom + 4],
                  fill=RULE, width=1)

    # Footer: hairline above, muted small type; honest about the
    # dated items
    draw.line([(16, body_bottom + 5), (1008, body_bottom + 5)],
              fill=RULE, width=1)
    draw.text((16, body_bottom + 10),
              "Headlines of 18 Nov 2026 — measles, GPT-6.2, Kahana, Merchant, Thailand: 17 Nov; "
              "chip rule, Costa Rica killing: 16 Nov; Ebola figures to 12 Nov.",
              font=font(REG, 11), fill=FOOT)

    img.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
