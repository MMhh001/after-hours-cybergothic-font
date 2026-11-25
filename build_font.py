"""Build AfterHoursCyberGothic.otf and a high-res specimen sheet PNG."""
from pathlib import Path
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parent
OTF_PATH = OUT_DIR / "AfterHoursCyberGothic.otf"
SPECIMEN_PATH = OUT_DIR / "specimen-sheet.png"

# Metrics (1000 UPM)
ASCENT = 820
DESCENT = -200
CAP = 720
XH = 500


def draw_poly(pen, pts):
    pen.moveTo(pts[0])
    for pt in pts[1:]:
        pen.lineTo(pt)
    pen.closePath()


def rect(x1, y1, x2, y2):
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]


def chamfer_rect(x1, y1, x2, y2, bl=0, br=0, tr=0, tl=0):
    """CCW rectangle with optional 45-degree chamfered corners."""
    pts = []
    if bl > 0:
        pts.extend([(x1 + bl, y1), (x2 - br, y1)])
    else:
        pts.extend([(x1, y1), (x2 - br, y1)])
    if br > 0:
        pts.append((x2, y1 + br))
    pts.append((x2, y2 - tr))
    if tr > 0:
        pts.append((x2 - tr, y2))
    pts.append((x1 + tl, y2))
    if tl > 0:
        pts.append((x1, y2 - tl))
    if bl > 0:
        pts.append((x1, y1 + bl))
    return pts


def gothic_stem(x, y1, y2, w=108, cut_top=True, cut_bot=True):
    """Vertical Gothic pillar with diamond/chamfered terminals."""
    t_cut = 32 if cut_top else 0
    b_cut = 32 if cut_bot else 0
    return chamfer_rect(x, y1, x + w, y2, bl=0, br=b_cut, tr=0, tl=t_cut)


def hbar(x1, x2, y, h=64, cut_l=14, cut_r=14):
    """High-contrast horizontal bar with subtle cyber chamfer."""
    return chamfer_rect(x1, y, x2, y + h, bl=cut_l, br=0, tr=cut_r, tl=0)


def diag_bar(x1, y1, x2, y2, w=88):
    """True perpendicular-normal diagonal stroke polygon (CCW)."""
    dx = x2 - x1
    dy = y2 - y1
    length = (dx * dx + dy * dy) ** 0.5 or 1.0
    nx = -dy / length * (w / 2.0)
    ny = dx / length * (w / 2.0)
    return [
        (round(x1 - nx), round(y1 - ny)),
        (round(x2 - nx), round(y2 - ny)),
        (round(x2 + nx), round(y2 + ny)),
        (round(x1 + nx), round(y1 + ny)),
    ]


def pointed_frame(x1, y1, x2, y2, stroke=104, hstroke=66, peak=88, notch=True):
    """Return [outer_ccw, inner_cw] for pointed Gothic-cyber arch frame."""
    cx = (x1 + x2) // 2
    outer = [
        (x1 + 52, y1),
        (x2 - 52, y1),
        (x2, y1 + 56),
        (x2, y2 - peak),
        (cx + 36, y2),
        (cx - 36, y2),
        (x1, y2 - peak),
        (x1, y1 + 56),
    ]
    ix1, iy1 = x1 + stroke, y1 + hstroke
    ix2, iy2 = x2 - stroke, y2 - hstroke
    inner = [
        (ix1 + 18, iy1),
        (ix1, iy1 + 22),
        (ix1, iy2 - 58),
        (cx - 18, iy2),
        (cx + 18, iy2),
        (ix2, iy2 - 58),
        (ix2, iy1 + 22),
        (ix2 - 18, iy1),
    ]
    return [outer, inner]


def make_glyphs():
    """Construct glyph contour lists: char -> (advance_width, [poly_pts, ...])."""
    g = {}
    L = 64  # left sidebearing
    W = 104  # main vertical stem
    H = 64   # thin horizontal bar

    # Space
    g[" "] = (280, [])

    # Uppercase A-Z (Cap height = 720)
    g["A"] = (620, [
        gothic_stem(L, 0, CAP - 90, W),
        gothic_stem(620 - L - W, 0, CAP - 90, W),
        [(L, CAP - 110), (310 - 44, CAP), (310 + 44, CAP), (620 - L, CAP - 110),
         (620 - L - W, CAP - 110), (310, CAP - 56), (L + W, CAP - 110)],
        hbar(L + W - 10, 620 - L - W + 10, 230, H),
        chamfer_rect(268, 360, 352, 430, bl=18, tr=18),  # cyber core diamond
    ])
    g["B"] = (600, [
        gothic_stem(L, 0, CAP, W),
        hbar(L + W - 8, 490, CAP - H, H, 0, 26),
        hbar(L + W - 8, 465, 348, H, 0, 20),
        hbar(L + W - 8, 500, 0, H, 0, 26),
        gothic_stem(418, 384, CAP - 32, W - 8),
        gothic_stem(432, 32, 378, W - 4),
    ])
    g["C"] = (580, [
        gothic_stem(L, 48, CAP - 48, W),
        hbar(L + 32, 520, CAP - H, H, 20, 20),
        hbar(L + 32, 520, 0, H, 20, 20),
        gothic_stem(422, CAP - 190, CAP - 42, W - 12),
        gothic_stem(422, 42, 195, W - 12),
    ])
    g["D"] = (610, [
        gothic_stem(L, 0, CAP, W),
        hbar(L + W - 8, 495, CAP - H, H, 0, 34),
        hbar(L + W - 8, 495, 0, H, 0, 34),
        gothic_stem(442, 48, CAP - 48, W),
    ])
    g["E"] = (560, [
        gothic_stem(L, 0, CAP, W),
        hbar(L + W - 8, 502, CAP - H, H, 0, 28),
        hbar(L + W - 8, 430, 340, H, 0, 22),
        hbar(L + W - 8, 502, 0, H, 0, 28),
    ])
    g["F"] = (540, [
        gothic_stem(L, 0, CAP, W),
        hbar(L + W - 8, 492, CAP - H, H, 0, 28),
        hbar(L + W - 8, 415, 340, H, 0, 22),
    ])
    g["G"] = (620, [
        gothic_stem(L, 48, CAP - 48, W),
        hbar(L + 32, 540, CAP - H, H, 20, 24),
        hbar(L + 32, 540, 0, H, 20, 24),
        gothic_stem(448, CAP - 195, CAP - 42, W - 10),
        gothic_stem(448, 36, 330, W - 6),
        hbar(310, 546, 275, H, 22, 0),
    ])
    g["H"] = (630, [
        gothic_stem(L, 0, CAP, W),
        gothic_stem(630 - L - W, 0, CAP, W),
        hbar(L + W - 8, 630 - L - W + 8, 336, H),
    ])
    g["I"] = (320, [
        gothic_stem(106, 0, CAP, W),
        hbar(60, 260, CAP - H, H),
        hbar(60, 260, 0, H),
    ])
    g["J"] = (520, [
        gothic_stem(348, 56, CAP, W),
        hbar(210, 466, CAP - H, H),
        hbar(L + 34, 410, 0, H, 24, 24),
        gothic_stem(L, 46, 220, W - 10),
    ])
    g["K"] = (610, [
        gothic_stem(L, 0, CAP, W),
        diag_bar(L + W - 6, 310, 520, CAP, 94),
        diag_bar(240, 385, 535, 0, 98),
    ])
    g["L"] = (530, [
        gothic_stem(L, 0, CAP, W),
        hbar(L + W - 8, 482, 0, H, 0, 26),
        gothic_stem(412, 0, 140, 74, cut_top=True, cut_bot=False),
    ])
    g["M"] = (720, [
        gothic_stem(L, 0, CAP, W),
        gothic_stem(720 - L - W, 0, CAP, W),
        diag_bar(L + W - 10, CAP, 360, 250, 88),
        diag_bar(720 - L - W + 10, CAP, 360, 250, 88),
        chamfer_rect(318, 220, 402, 310, bl=18, tr=18),
    ])
    g["N"] = (640, [
        gothic_stem(L, 0, CAP, W),
        gothic_stem(640 - L - W, 0, CAP, W),
        diag_bar(L + W - 12, CAP, 640 - L - W + 12, 0, 96),
    ])
    g["O"] = (640, pointed_frame(L, 0, 640 - L, CAP))
    g["P"] = (590, [
        gothic_stem(L, 0, CAP, W),
        hbar(L + W - 8, 495, CAP - H, H, 0, 28),
        hbar(L + W - 8, 495, 315, H, 0, 28),
        gothic_stem(426, 350, CAP - 34, W - 6),
    ])
    g["Q"] = (650, pointed_frame(L, 0, 650 - L, CAP) + [
        diag_bar(365, 190, 595, -55, 86),
    ])
    g["R"] = (610, [
        gothic_stem(L, 0, CAP, W),
        hbar(L + W - 8, 505, CAP - H, H, 0, 28),
        hbar(L + W - 8, 505, 325, H, 0, 28),
        gothic_stem(436, 360, CAP - 34, W - 8),
        diag_bar(295, 340, 545, 0, 96),
    ])
    g["S"] = (580, [
        hbar(L + 26, 510, CAP - H, H, 22, 22),
        gothic_stem(L, 355, CAP - 36, W),
        hbar(L + 30, 485, 332, H, 20, 20),
        gothic_stem(414, 36, 368, W),
        hbar(L, 490, 0, H, 22, 22),
    ])
    g["T"] = (590, [
        gothic_stem(243, 0, CAP - H + 10, W),
        hbar(44, 546, CAP - H, H, 26, 26),
        gothic_stem(44, CAP - 145, CAP - 20, 58),
        gothic_stem(488, CAP - 145, CAP - 20, 58),
    ])
    g["U"] = (620, [
        gothic_stem(L, 46, CAP, W),
        gothic_stem(620 - L - W, 46, CAP, W),
        hbar(L + 36, 620 - L - 36, 0, H, 24, 24),
    ])
    g["V"] = (620, [
        diag_bar(L + 42, CAP, 310, 0, 96),
        diag_bar(620 - L - 42, CAP, 310, 0, 96),
        chamfer_rect(262, 0, 358, 95, bl=18, br=18),
    ])
    g["W"] = (760, [
        diag_bar(L + 36, CAP, 220, 0, 88),
        diag_bar(380, CAP - 230, 220, 0, 82),
        diag_bar(380, CAP - 230, 540, 0, 82),
        diag_bar(760 - L - 36, CAP, 540, 0, 88),
    ])
    g["X"] = (610, [
        diag_bar(L + 40, CAP, 610 - L - 40, 0, 98),
        diag_bar(610 - L - 40, CAP, L + 40, 0, 98),
    ])
    g["Y"] = (600, [
        diag_bar(L + 42, CAP, 300, 315, 92),
        diag_bar(600 - L - 42, CAP, 300, 315, 92),
        gothic_stem(248, 0, 355, W),
    ])
    g["Z"] = (580, [
        hbar(L, 518, CAP - H, H, 24, 24),
        diag_bar(505, CAP - 32, L + 55, 32, 92),
        hbar(L, 518, 0, H, 24, 24),
    ])

    # Lowercase a-z (x-height = 500, ascender = 760, descender = -180)
    LW = 94
    g["a"] = (530, [
        hbar(92, 442, XH - H, H, 20, 20),
        gothic_stem(368, 0, XH - 28, LW),
        hbar(88, 410, 220, H, 20, 0),
        gothic_stem(L, 32, 250, LW - 6),
        hbar(90, 442, 0, H, 20, 20),
    ])
    g["b"] = (550, [
        gothic_stem(L, 0, 760, LW),
        hbar(L + LW - 6, 460, XH - H, H, 0, 22),
        hbar(L + LW - 6, 460, 0, H, 0, 22),
        gothic_stem(392, 34, XH - 34, LW),
    ])
    g["c"] = (490, [
        gothic_stem(L, 34, XH - 34, LW),
        hbar(L + 28, 438, XH - H, H, 18, 18),
        hbar(L + 28, 438, 0, H, 18, 18),
        gothic_stem(356, XH - 140, XH - 28, LW - 16),
        gothic_stem(356, 28, 140, LW - 16),
    ])
    g["d"] = (550, [
        gothic_stem(550 - L - LW, 0, 760, LW),
        hbar(92, 550 - L - LW + 6, XH - H, H, 22, 0),
        hbar(92, 550 - L - LW + 6, 0, H, 22, 0),
        gothic_stem(L, 34, XH - 34, LW),
    ])
    g["e"] = (520, [
        gothic_stem(L, 34, XH - 34, LW),
        hbar(L + 28, 444, XH - H, H, 18, 18),
        hbar(L + LW - 8, 458, 228, H, 0, 18),
        gothic_stem(370, 255, XH - 34, LW - 8),
        hbar(L + 28, 446, 0, H, 18, 18),
    ])
    g["f"] = (390, [
        gothic_stem(136, 0, 725, LW),
        hbar(160, 345, 760 - H, H, 18, 18),
        hbar(56, 330, XH - H, H, 16, 16),
    ])
    g["g"] = (550, pointed_frame(L, 32, 550 - L, XH, stroke=90, hstroke=58, peak=34) + [
        gothic_stem(550 - L - LW, -145, XH - 24, LW),
        hbar(115, 550 - L - 28, -180, H, 20, 20),
    ])
    g["h"] = (550, [
        gothic_stem(L, 0, 760, LW),
        hbar(L + LW - 6, 456, XH - H, H, 0, 22),
        gothic_stem(392, 0, XH - 30, LW),
    ])
    g["i"] = (275, [
        gothic_stem(90, 0, XH, LW),
        chamfer_rect(86, 585, 188, 685, bl=20, br=20, tr=20, tl=20),
    ])
    g["j"] = (300, [
        gothic_stem(132, -145, XH, LW),
        hbar(40, 200, -180, H, 18, 18),
        chamfer_rect(128, 585, 230, 685, bl=20, br=20, tr=20, tl=20),
    ])
    g["k"] = (520, [
        gothic_stem(L, 0, 760, LW),
        diag_bar(L + LW - 6, 220, 445, XH, 86),
        diag_bar(210, 280, 455, 0, 88),
    ])
    g["l"] = (280, [
        gothic_stem(92, 0, 760, LW),
        hbar(118, 232, 0, H, 0, 16),
    ])
    g["m"] = (760, [
        gothic_stem(L, 0, XH, LW),
        hbar(L + LW - 6, 668, XH - H, H, 0, 24),
        gothic_stem(333, 0, XH - 28, LW),
        gothic_stem(602, 0, XH - 30, LW),
    ])
    g["n"] = (550, [
        gothic_stem(L, 0, XH, LW),
        hbar(L + LW - 6, 456, XH - H, H, 0, 22),
        gothic_stem(392, 0, XH - 30, LW),
    ])
    g["o"] = (540, pointed_frame(L, 0, 540 - L, XH, stroke=92, hstroke=58, peak=36))
    g["p"] = (550, [
        gothic_stem(L, -180, XH, LW),
        hbar(L + LW - 6, 460, XH - H, H, 0, 22),
        hbar(L + LW - 6, 460, 0, H, 0, 22),
        gothic_stem(392, 34, XH - 34, LW),
    ])
    g["q"] = (550, [
        gothic_stem(550 - L - LW, -180, XH, LW),
        hbar(92, 550 - L - LW + 6, XH - H, H, 22, 0),
        hbar(92, 550 - L - LW + 6, 0, H, 22, 0),
        gothic_stem(L, 34, XH - 34, LW),
    ])
    g["r"] = (420, [
        gothic_stem(L, 0, XH, LW),
        hbar(L + LW - 6, 376, XH - H, H, 0, 24),
        gothic_stem(302, XH - 155, XH - 24, 72),
    ])
    g["s"] = (480, [
        hbar(88, 412, XH - H, H, 18, 18),
        gothic_stem(L, 250, XH - 28, LW - 4),
        hbar(88, 396, 222, H, 18, 18),
        gothic_stem(328, 28, 258, LW - 4),
        hbar(68, 400, 0, H, 18, 18),
    ])
    g["t"] = (400, [
        gothic_stem(134, 30, 685, LW),
        hbar(56, 340, XH - H, H, 16, 16),
        hbar(155, 340, 0, H, 16, 16),
    ])
    g["u"] = (550, [
        gothic_stem(L, 34, XH, LW),
        gothic_stem(550 - L - LW, 0, XH, LW),
        hbar(L + 28, 550 - L - 28, 0, H, 20, 0),
    ])
    g["v"] = (530, [
        diag_bar(L + 36, XH, 265, 0, 86),
        diag_bar(530 - L - 36, XH, 265, 0, 86),
    ])
    g["w"] = (700, [
        diag_bar(L + 30, XH, 200, 0, 80),
        diag_bar(350, XH - 130, 200, 0, 74),
        diag_bar(350, XH - 130, 500, 0, 74),
        diag_bar(700 - L - 30, XH, 500, 0, 80),
    ])
    g["x"] = (520, [
        diag_bar(L + 36, XH, 520 - L - 36, 0, 88),
        diag_bar(520 - L - 36, XH, L + 36, 0, 88),
    ])
    g["y"] = (530, [
        diag_bar(L + 36, XH, 270, 0, 86),
        diag_bar(530 - L - 36, XH, 160, -180, 86),
    ])
    g["z"] = (490, [
        hbar(L, 428, XH - H, H, 18, 18),
        diag_bar(416, XH - 28, L + 46, 28, 82),
        hbar(L, 428, 0, H, 18, 18),
    ])

    # Numerals 0-9 (Cap height = 720)
    g["0"] = (600, pointed_frame(L, 0, 600 - L, CAP) + [
        diag_bar(185, 165, 415, 555, 68),
    ])
    g["1"] = (420, [
        gothic_stem(176, 0, CAP, W),
        diag_bar(86, 560, 224, CAP, 72),
        hbar(82, 348, 0, H, 18, 18),
    ])
    g["2"] = (580, [
        hbar(L + 20, 495, CAP - H, H, 20, 22),
        gothic_stem(412, 345, CAP - 34, W),
        hbar(L + 20, 488, 326, H, 20, 20),
        gothic_stem(L, 34, 360, W),
        hbar(L, 516, 0, H, 20, 22),
    ])
    g["3"] = (580, [
        hbar(L + 20, 495, CAP - H, H, 20, 22),
        gothic_stem(412, 370, CAP - 34, W),
        hbar(170, 495, 336, H, 20, 18),
        gothic_stem(412, 34, 365, W),
        hbar(L + 20, 495, 0, H, 20, 22),
    ])
    g["4"] = (600, [
        gothic_stem(L + 8, 250, CAP, W - 4),
        hbar(L + 8, 536, 230, H, 0, 20),
        gothic_stem(395, 0, CAP, W),
    ])
    g["5"] = (580, [
        hbar(L, 505, CAP - H, H, 20, 22),
        gothic_stem(L, 355, CAP - 34, W),
        hbar(L, 495, 332, H, 0, 22),
        gothic_stem(414, 34, 368, W),
        hbar(L + 20, 495, 0, H, 20, 22),
    ])
    g["6"] = (590, [
        gothic_stem(L, 34, CAP - 36, W),
        hbar(L + 26, 495, CAP - H, H, 20, 22),
        hbar(L + W - 8, 505, 336, H, 0, 22),
        gothic_stem(422, 34, 370, W),
        hbar(L + 26, 505, 0, H, 20, 22),
    ])
    g["7"] = (560, [
        hbar(L, 498, CAP - H, H, 20, 22),
        diag_bar(488, CAP - 34, 210, 0, 96),
    ])
    g["8"] = (600, [
        hbar(L + 24, 514, CAP - H, H, 20, 20),
        hbar(L + 24, 514, 336, H, 18, 18),
        hbar(L + 24, 514, 0, H, 20, 20),
        gothic_stem(L, 368, CAP - 34, W - 6),
        gothic_stem(432, 368, CAP - 34, W - 6),
        gothic_stem(L, 34, 364, W - 6),
        gothic_stem(432, 34, 364, W - 6),
    ])
    g["9"] = (590, [
        gothic_stem(422, 34, CAP - 34, W),
        hbar(L + 26, 502, CAP - H, H, 20, 22),
        gothic_stem(L, 355, CAP - 34, W - 4),
        hbar(L + 26, 455, 332, H, 20, 0),
        hbar(L + 30, 502, 0, H, 20, 22),
    ])

    # Common punctuation
    g["."] = (240, [chamfer_rect(68, 0, 172, 108, bl=20, br=20, tr=20, tl=20)])
    g[","] = (240, [chamfer_rect(68, -95, 172, 108, bl=36, tr=20)])
    g["-"] = (380, [hbar(70, 310, 260, 68, 16, 16)])
    g["!"] = (270, [gothic_stem(84, 185, CAP, 102), chamfer_rect(84, 0, 186, 106, bl=20, tr=20)])
    g["?"] = (500, [
        hbar(L + 20, 420, CAP - H, H, 20, 20),
        gothic_stem(336, 360, CAP - 32, 96),
        hbar(196, 415, 330, H, 18, 18),
        gothic_stem(196, 185, 360, 96),
        chamfer_rect(194, 0, 296, 106, bl=20, tr=20),
    ])
    g[":"] = (250, [
        chamfer_rect(74, 380, 176, 486, bl=20, tr=20),
        chamfer_rect(74, 0, 176, 106, bl=20, tr=20),
    ])
    g[";"] = (250, [
        chamfer_rect(74, 380, 176, 486, bl=20, tr=20),
        chamfer_rect(74, -95, 176, 106, bl=36, tr=20),
    ])
    g["'"] = (220, [gothic_stem(66, 470, CAP, 86)])
    g['"'] = (380, [gothic_stem(66, 470, CAP, 82), gothic_stem(222, 470, CAP, 82)])
    g["/"] = (440, [diag_bar(368, CAP, 72, 0, 86)])
    g["("] = (340, [
        gothic_stem(110, 40, CAP - 40, 92),
        hbar(130, 265, CAP - H, H, 20, 0),
        hbar(130, 265, 0, H, 20, 0),
    ])
    g[")"] = (340, [
        gothic_stem(138, 40, CAP - 40, 92),
        hbar(75, 210, CAP - H, H, 0, 20),
        hbar(75, 210, 0, H, 0, 20),
    ])
    g["#"] = (620, [
        diag_bar(195, CAP, 145, 0, 74),
        diag_bar(455, CAP, 405, 0, 74),
        hbar(65, 555, 430, 62),
        hbar(45, 535, 215, 62),
    ])
    g["&"] = (620, [
        gothic_stem(L, 38, CAP - 38, W - 8),
        hbar(L + 24, 435, CAP - H, H, 18, 18),
        hbar(L + 24, 520, 0, H, 18, 18),
        diag_bar(110, CAP - 60, 525, 45, 86),
        gothic_stem(425, 45, 290, W - 12),
    ])
    g["@"] = (720, pointed_frame(L, 0, 720 - L, CAP, stroke=82, hstroke=56) + [
        gothic_stem(255, 195, 485, 76),
        gothic_stem(415, 195, 485, 76),
        hbar(255, 491, 432, 54),
        hbar(255, 491, 195, 54),
    ])
    return g


def build_otf():
    glyph_map = make_glyphs()
    glyph_order = [".notdef", "space"] + [
        f"g_{ord(ch)}" if not ch.isalnum() else ch for ch in glyph_map if ch != " "
    ]
    char_to_gname = {" ": "space"}
    for ch in glyph_map:
        if ch != " ":
            char_to_gname[ch] = f"g_{ord(ch)}" if not ch.isalnum() else ch

    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(glyph_order)
    cmap = {ord(ch): gname for ch, gname in char_to_gname.items()}
    fb.setupCharacterMap(cmap)

    char_strings = {}
    metrics = {}

    # .notdef
    pen = T2CharStringPen(600, None)
    draw_poly(pen, [(60, 0), (540, 0), (540, 720), (60, 720)])
    draw_poly(pen, [(130, 70), (130, 650), (470, 650), (470, 70)])
    char_strings[".notdef"] = pen.getCharString()
    metrics[".notdef"] = (600, 60)

    for ch, (adv, polys) in glyph_map.items():
        gname = char_to_gname[ch]
        pen = T2CharStringPen(adv, None)
        for poly in polys:
            draw_poly(pen, poly)
        char_strings[gname] = pen.getCharString()
        lsb = min((pt[0] for poly in polys for pt in poly), default=0)
        metrics[gname] = (adv, lsb)

    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT)
    fb.setupNameTable({
        "familyName": "After Hours CyberGothic",
        "styleName": "Regular",
        "uniqueFontIdentifier": "AfterHoursCyberGothic-Regular-v1.0",
        "fullName": "After Hours CyberGothic Regular",
        "psName": "AfterHoursCyberGothic-Regular",
        "version": "Version 1.000",
    })
    fb.setupOS2(sTypoAscender=ASCENT, sTypoDescender=DESCENT, usWinAscent=ASCENT, usWinDescent=abs(DESCENT), sxHeight=XH, sCapHeight=CAP)
    fb.setupPost()
    fb.setupCFF(
        psName="AfterHoursCyberGothic-Regular",
        fontInfo={"FullName": "After Hours CyberGothic Regular", "FamilyName": "After Hours CyberGothic"},
        charStringsDict=char_strings,
        privateDict={},
    )
    fb.save(str(OTF_PATH))
    tt = TTFont(str(OTF_PATH))
    assert len(tt.getGlyphOrder()) == len(glyph_order)
    print(f"Saved OTF: {OTF_PATH} ({OTF_PATH.stat().st_size} bytes, glyphs={len(glyph_order)})")


def build_specimen():
    W, H = 1600, 1000
    img = Image.new("RGB", (W, H), (10, 12, 22))
    draw = ImageDraw.Draw(img)

    # Subtle cyber grid background
    for gx in range(0, W, 40):
        draw.line([(gx, 0), (gx, H)], fill=(18, 22, 38), width=1)
    for gy in range(0, H, 40):
        draw.line([(0, gy), (W, gy)], fill=(18, 22, 38), width=1)

    f_hero = ImageFont.truetype(str(OTF_PATH), 132)
    f_sub = ImageFont.truetype(str(OTF_PATH), 64)
    f_set = ImageFont.truetype(str(OTF_PATH), 46)
    f_ui = ImageFont.load_default(size=22)
    f_small = ImageFont.load_default(size=18)

    # Header tag
    draw.rectangle([(60, 40), (1540, 108)], fill=(18, 24, 42), outline=(0, 240, 255), width=2)
    draw.text((84, 62), "AFTER HOURS CYBERGOTHIC  //  OPEN-TYPE DISPLAY SYSTEM (.OTF)  //  SYSTEM SPECIMEN", fill=(0, 240, 255), font=f_ui)

    # 1. Expressive Hero Treatment (Neon + Chromatic Split Shadow)
    draw.text((84, 140), "01 / EXPRESSIVE HERO TREATMENT (132px)", fill=(165, 175, 205), font=f_small)
    hero_txt = "AFTER HOURS"
    draw.text((88, 186), hero_txt, fill=(255, 42, 133), font=f_hero)
    draw.text((78, 178), hero_txt, fill=(0, 240, 255), font=f_hero)
    draw.text((83, 182), hero_txt, fill=(246, 248, 255), font=f_hero)
    draw.line([(83, 336), (1150, 336)], fill=(255, 42, 133), width=3)

    # 2. Clean Website Heading Treatment
    draw.text((84, 368), "02 / CLEAN WEBSITE HEADING TREATMENT (64px - MOBILE-LEGIBLE HIGH CONTRAST)", fill=(165, 175, 205), font=f_small)
    draw.rectangle([(80, 402), (1040, 505)], fill=(19, 25, 42), outline=(72, 86, 130), width=2)
    draw.text((108, 422), "AFTER HOURS", fill=(242, 246, 255), font=f_sub)

    # 3. Full Glyph Coverage Box
    draw.text((84, 535), "03 / SUPPORTED GLYPH SET (A-Z, a-z, 0-9, BASIC PUNCTUATION)", fill=(165, 175, 205), font=f_small)
    draw.rectangle([(80, 568), (1520, 815)], fill=(15, 20, 34), outline=(55, 70, 110), width=2)
    draw.text((108, 594), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", fill=(235, 244, 255), font=f_set)
    draw.text((108, 668), "abcdefghijklmnopqrstuvwxyz", fill=(180, 232, 255), font=f_set)
    draw.text((108, 740), "0123456789  .,-!?:;'\"&/#@()", fill=(255, 135, 200), font=f_set)

    # 4. System Rules Footer
    rules = [
        "GOTHIC BONES: 104u heavy vertical pillars + 64u thin crossbars (1.63x contrast) + pointed arch roofs",
        "CYBERPUNK CUTS: consistent 45-degree 32u bevelled terminals & diagonal zero/core circuit geometry",
        "PHONE READABILITY: open counters, crisp 20u side-cuts, and clean baseline rhythm down to 18px",
    ]
    y = 842
    for idx, line in enumerate(rules, 1):
        draw.text((84, y), f"RULE 0{idx}: {line}", fill=(190, 208, 235), font=f_small)
        y += 38

    img.save(str(SPECIMEN_PATH), optimize=True)
    print(f"Saved Specimen: {SPECIMEN_PATH} ({SPECIMEN_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    build_otf()
    build_specimen()
