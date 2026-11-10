#!/usr/bin/env python3
"""Draws the PypeIt workflow diagrams as standalone SVG files.

HOW TO EDIT
  * Change the text in the diagram functions below (look for the lists of steps).
  * Each step is (title, subtitle, colour, dashed). Subtitle, colour and dashed are optional.
  * Colours: purple, gray, teal, coral, plain.  dashed=True gives a dashed outline.
  * Run:  python3 make_diagrams.py     -> the SVGs appear in the "diagrams" folder.
You can also open any SVG in a text editor, Inkscape or Illustrator and edit it directly.
"""
import os
import textwrap
from xml.sax.saxutils import escape

# fill, outline, title text, subtitle text
COLORS = {
    "plain":  ("#FFFFFF", "#444441", "#2C2C2A", "#5F5E5A"),
    "gray":   ("#F1EFE8", "#5F5E5A", "#2C2C2A", "#444441"),
    "purple": ("#EEEDFE", "#534AB7", "#26215C", "#3C3489"),
    "teal":   ("#E1F5EE", "#0F6E56", "#04342C", "#085041"),
    "coral":  ("#FAECE7", "#993C1D", "#4A1B0C", "#712B13"),
}
FONT = "Helvetica, Arial, sans-serif"
LINE = "#5F5E5A"
OUTDIR = "diagrams"


class Box:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    cx = property(lambda s: s.x + s.w / 2)
    cy = property(lambda s: s.y + s.h / 2)
    right = property(lambda s: s.x + s.w)
    bottom = property(lambda s: s.y + s.h)


def _wrap(w, title, sub):
    tl = textwrap.wrap(title, max(8, int((w - 24) / 8.0))) if title else []
    sl = textwrap.wrap(sub, max(8, int((w - 24) / 6.8))) if sub else []
    th = 18 * len(tl) + ((16 * len(sl) + (4 if tl else 0)) if sl else 0)
    return tl, sl, th


def box_height(w, title, sub="", minh=44):
    return max(minh, _wrap(w, title, sub)[2] + 24)


class Canvas:
    def __init__(self, width=680):
        self.w = width
        self.items = []
        self.maxy = 0

    def _track(self, y):
        self.maxy = max(self.maxy, y)

    def _rect(self, x, y, w, h, color, dashed=False, rx=8):
        fill, stroke, _, _ = COLORS[color]
        d = ' stroke-dasharray="5 4"' if dashed else ""
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1"{d}/>')

    def rect(self, x, y, w, h, color, dashed=False, rx=8):
        self.items.append(self._rect(x, y, w, h, color, dashed, rx))
        self._track(y + h)

    def _text(self, x, y, s, size=14, weight=400, color="#2C2C2A", anchor="middle"):
        return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
                f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')

    def text(self, x, y, s, size=14, weight=400, color="#2C2C2A", anchor="middle"):
        self.items.append(self._text(x, y, s, size, weight, color, anchor))
        self._track(y + 6)

    def box(self, x, y, w, title, sub="", color="plain", dashed=False, minh=44):
        _, _, tc, sc = COLORS[color]
        tl, sl, th = _wrap(w, title, sub)
        h = max(minh, th + 24)
        self.rect(x, y, w, h, color, dashed)
        cy = y + (h - th) / 2
        for i, line in enumerate(tl):
            self.text(x + w / 2, cy + 18 * i + 14, line, 14, 500, tc)
        base = cy + 18 * len(tl) + (4 if tl else 0)
        for i, line in enumerate(sl):
            self.text(x + w / 2, base + 16 * i + 12, line, 12, 400, sc if tl else tc)
        return Box(x, y, w, h)

    def arrow(self, pts, dashed=False, head=True):
        d = "M " + " L ".join(f"{px} {py}" for px, py in pts)
        dash = ' stroke-dasharray="4 3"' if dashed else ""
        mk = ' marker-end="url(#a)"' if head else ""
        self.items.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.3"{dash}{mk}/>')
        self._track(max(py for _, py in pts))

    def begin(self, x, y, w, color, title, sub="", dashed=True):
        self.items.append("")
        return dict(idx=len(self.items) - 1, x=x, y=y, w=w, color=color,
                    title=title, sub=sub, dashed=dashed)

    def inner_top(self, c):
        return c["y"] + (58 if c["sub"] else 40)

    def end(self, c, bottom):
        _, _, tc, sc = COLORS[c["color"]]
        parts = [self._rect(c["x"], c["y"], c["w"], bottom - c["y"], c["color"], c["dashed"], 12),
                 self._text(c["x"] + c["w"] / 2, c["y"] + 24, c["title"], 14, 500, tc)]
        if c["sub"]:
            parts.append(self._text(c["x"] + c["w"] / 2, c["y"] + 43, c["sub"], 12, 400, sc))
        self.items[c["idx"]] = "\n".join(parts)
        self._track(bottom)

    def legend(self, items, y, x=40):
        for label, color, dashed in items:
            self.rect(x, y, 14, 14, color, dashed, 3)
            self.text(x + 22, y + 11, label, 12, 400, "#444441", "start")
            x += 22 + int(len(label) * 6.6) + 30

    def save(self, name):
        os.makedirs(OUTDIR, exist_ok=True)
        h = int(self.maxy + 30)
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{h}" viewBox="0 0 {self.w} {h}">',
               '<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
               f'<path d="M2 1L8 5L2 9" fill="none" stroke="{LINE}" stroke-width="1.5" stroke-linecap="round"/></marker></defs>',
               f'<rect width="{self.w}" height="{h}" fill="#FFFFFF"/>'] + self.items + ["</svg>"]
        with open(os.path.join(OUTDIR, name), "w") as f:
            f.write("\n".join(svg))
        print("wrote", os.path.join(OUTDIR, name))


def norm(s):
    s = tuple(s) + ("",) * (4 - len(s)) if len(s) < 4 else tuple(s)
    return s[0], s[1], (s[2] or "purple"), bool(s[3])


def column(c, x, y, w, steps, gap=26, minh=44):
    boxes = []
    for s in steps:
        t, sub, col, dash = norm(s)
        b = c.box(x, y, w, t, sub, col, dash, minh)
        boxes.append(b)
        y = b.bottom + gap
    for a, b in zip(boxes, boxes[1:]):
        c.arrow([(a.cx, a.bottom), (b.cx, b.y - 2)])
    return boxes


def snake(c, xs, w, steps, per_col, top=36, gap=26):
    cols = []
    for i, x in enumerate(xs):
        cols.append(column(c, x, top, w, steps[i * per_col:(i + 1) * per_col], gap))
    for i in range(len(cols) - 1):
        a, b = cols[i][-1], cols[i + 1][0]
        gx = (xs[i] + w + xs[i + 1]) / 2
        c.arrow([(a.cx, a.bottom), (a.cx, a.bottom + 14), (gx, a.bottom + 14),
                 (gx, top - 16), (b.cx, top - 16), (b.cx, b.y - 2)])
    return cols


# ---------------------------------------------------------------- 1. overall
def d_overview():
    c = Canvas()
    b1 = c.box(40, 30, 176, "1. Initialization", "Read the reduction file + file headers", "gray", minh=76)
    b2 = c.box(252, 30, 176, "2. Standard stars", "Optional step", "purple", minh=76)
    b3 = c.box(464, 30, 176, "3. Science frames", "Main reduction", "purple", minh=76)
    c.arrow([(b1.right, b1.cy), (b2.x - 2, b2.cy)])
    c.arrow([(b2.right, b2.cy), (b3.x - 2, b3.cy)])
    notes = ["The reduction file wins over the headers",
             "Faint-object fallback: slit edges",
             "Faint-object fallback: standard star trace"]
    for b, n in zip((b1, b2, b3), notes):
        ny = b.bottom + 36
        nb = c.box(b.x, ny, b.w, "", n, "plain", True)
        c.arrow([(b.cx, b.bottom), (b.cx, ny)], dashed=True, head=False)
    c.save("01_overview.svg")


# ---------------------------------------------------------------- 2. loops
def d_loops():
    c = Canvas()
    o = c.begin(40, 30, 600, "gray", "Loop 1: calibration groups", "Frames that share the same calibrations", False)
    m = c.begin(64, 96, 552, "purple", "Loop 2: frame groups", "Combined frames, or single frames", False)
    i = c.begin(88, 160, 504, "teal", "Loop 3: each detector or mosaic", "Runs the per-detector steps (diagram 3)", False)
    c.end(i, 230)
    c.end(m, 254)
    c.end(o, 278)
    c.save("02_loops.svg")


# ---------------------------------------------------------------- 3. per detector
def d_per_detector():
    c = Canvas()
    steps = [("Make the calibrations", "Bias, flats, arcs, slits", "purple"),
             ("Basic image processing", "Clean the raw frame", "purple"),
             ("Sky model + find objects", "First rough pass", "purple"),
             ("Match to the slit-mask design", "Only if mask information exists", "gray", True),
             ("Extract spectra", "Boxcar and/or optimal", "teal")]
    b = column(c, 190, 30, 300, steps, 28, 56)
    c.arrow([(510, b[0].y), (510, b[2].bottom)], head=False)
    c.text(524, b[1].cy - 4, "First loop over", 12, 400, "#444441", "start")
    c.text(524, b[1].cy + 14, "all detectors", 12, 400, "#444441", "start")
    c.arrow([(510, b[4].y), (510, b[4].bottom)], head=False)
    c.text(524, b[4].cy - 4, "Second loop over", 12, 400, "#444441", "start")
    c.text(524, b[4].cy + 14, "all detectors", 12, 400, "#444441", "start")
    c.save("03_per_detector.svg")


# ---------------------------------------------------------------- 4. the three steps
def d_steps():
    c = Canvas()
    cal = c.box(40, 30, 600, "Calibrations", "Bias, dark, flat, arc, slits, tilts, wavelength", "purple", minh=52)
    p = c.box(40, 120, 176, "1. process", "Clean the raw image", "plain", minh=60)
    f = c.box(252, 120, 176, "2. findobj", "Find objects + sky", "plain", minh=60)
    x = c.box(464, 120, 176, "3. extract", "Pull 1D spectra", "plain", minh=60)
    c.arrow([(p.cx, cal.bottom), (p.cx, p.y - 2)])
    c.arrow([(p.right, p.cy), (f.x - 2, f.cy)])
    c.arrow([(f.right, f.cy), (x.x - 2, x.cy)])
    oy = x.bottom + 56
    o1 = c.box(432, oy, 100, "Spec1D", "1D spectra", "teal", minh=56)
    o2 = c.box(544, oy, 96, "Spec2D", "2D images", "coral", minh=56)
    c.arrow([(x.cx, x.bottom), (o1.cx, o1.y - 2)])
    c.arrow([(x.cx, x.bottom), (o2.cx, o2.y - 2)])
    c.legend([("Calibrations", "purple", False), ("Final 1D output", "teal", False),
              ("Final 2D output", "coral", False)], o1.bottom + 40)
    c.save("04_steps_and_outputs.svg")


# ---------------------------------------------------------------- 4a. inside process
def d_process():
    c = Canvas()
    steps = [("Convert to electron counts",),
             ("Remove pattern noise", "Only for some instruments", "gray", True),
             ("Estimate the readout noise",),
             ("Subtract the overscan level",),
             ("Trim and rotate", "To the standard orientation"),
             ("Subtract the bias image",),
             ("Subtract dark current",),
             ("Join detectors into a mosaic", "Only if requested", "gray", True),
             ("Correct the slit shift", "From instrument flexure"),
             ("Flat-field", "Pixel, slit illumination, colour response"),
             ("Remove smooth background", "Only when combining arcs from different lamps", "gray", True),
             ("Add photon noise + noise floor",),
             ("Mask cosmic rays",),
             ("Combine frames", "Same type, same calibration group")]
    cols = snake(c, [40, 370], 270, steps, 7, top=36)
    bottom = max(col[-1].bottom for col in cols)
    c.legend([("Always done", "purple", False), ("Only sometimes", "gray", True)], bottom + 30)
    c.save("05_inside_process.svg")


# ---------------------------------------------------------------- 4b. inside findobj
def d_findobj():
    c = Canvas()
    main = [("1. First sky fit", "Whole slit, no objects masked"),
            ("2. First object search",),
            ("3. Mask object pixels", "Hide objects from the sky fit"),
            ("4. Second sky fit", "Object pixels masked"),
            ("5. Second object search",),
            ("6. Trace each object", "Follow it along the slit")]
    column(c, 30, 30, 190, main, 26, 52)

    s = c.begin(250, 30, 200, "gray", "Inside steps 2 and 5", "")
    search = [("Straighten the sky-subtracted slit",),
              ("Clip outliers along wavelength", "Rejects cosmic rays"),
              ("Collapse along wavelength", "Signal-to-noise vs. slit position"),
              ("Smooth the result",),
              ("Pick peaks above the detection limit",),
              ("Drop peaks too close to the slit edges",),
              ("Keep only the brightest peaks", "Up to the allowed maximum")]
    sb = column(c, 262, c.inner_top(s), 176, search, 22)
    c.end(s, sb[-1].bottom + 16)

    t = c.begin(480, 30, 170, "gray", "Inside step 6", "")
    trace = [("Fit the object position vs. wavelength",),
             ("Faint object?", "Borrow the standard star trace")]
    tb = column(c, 492, c.inner_top(t), 146, trace, 22)
    c.end(t, tb[-1].bottom + 16)
    c.save("06_inside_findobj.svg")


# ---------------------------------------------------------------- 4c. inside extract
def d_extract():
    c = Canvas()
    e1 = c.box(40, 30, 300, "Group nearby objects", "Objects whose regions overlap go together", "purple", minh=56)
    e2 = c.box(40, e1.bottom + 26, 300, "Pick the region around each group", "", "purple", minh=44)
    c.arrow([(e1.cx, e1.bottom), (e1.cx, e2.y - 2)])

    lp = c.begin(40, e2.bottom + 26, 300, "gray", "Repeat a few rounds (4 by default)", "")
    loop = [("Fit each object's shape across the slit", "First round starts from a simple box sum"),
            ("Choose where the sky model can bend",),
            ("Fit sky and objects together", "Separates overlapping sources"),
            ("Update the noise estimate", "Uses the new sky model")]
    lb = column(c, 56, c.inner_top(lp), 268, loop, 22)
    c.end(lp, lb[-1].bottom + 16)
    c.arrow([(e2.cx, e2.bottom), (e2.cx, lp["y"] - 2)])

    fin = c.box(40, lb[-1].bottom + 16 + 26, 300, "Final extraction",
                "Optimal (standard Horne method) and boxcar (simple sum)", "purple", minh=60)
    c.arrow([(fin.cx, lb[-1].bottom + 16), (fin.cx, fin.y - 2)])

    oy = fin.bottom + 50
    o1 = c.box(40, oy, 140, "Spec1D", "1D spectra", "teal", minh=56)
    o2 = c.box(200, oy, 140, "Spec2D", "2D images", "coral", minh=56)
    c.arrow([(fin.cx, fin.bottom), (o1.cx, o1.y - 2)])
    c.arrow([(fin.cx, fin.bottom), (o2.cx, o2.y - 2)])

    # optional notes on the right, level with what they affect
    n1_text = "Optional: keep pixels that look different from the continuum (bright emission lines) instead of rejecting them"
    n2_text = "Optional: turn off local sky subtraction for very extended, bright emission lines"
    lp_cy = (lp["y"] + lb[-1].bottom + 16) / 2
    for text, cy in ((n2_text, lp_cy), (n1_text, fin.cy)):
        h = box_height(240, "", text)
        n = c.box(400, cy - h / 2, 240, "", text, "gray", True)
        c.arrow([(340, cy), (398, cy)], dashed=True, head=False)
    c.save("07_inside_extract.svg")


if __name__ == "__main__":
    d_overview()
    d_loops()
    d_per_detector()
    d_steps()
    d_process()
    d_findobj()
    d_extract()
