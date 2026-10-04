# -*- coding: utf-8 -*-
"""12V/5A QR flyback SMPS -- single-sheet schematic, standalone SVG."""

W, H = 2000, 1600
P = []
def add(*xs):
    for x in xs:
        if isinstance(x, (list, tuple)): add(*x)
        elif x: P.append(x)

# ----------------------------------------------------------------- prims
def wire(*pts):
    return '<polyline points="%s" class="w"/>' % " ".join("%g,%g" % p for p in pts)
def jct(x, y):
    return '<circle cx="%g" cy="%g" r="4.2" class="jct"/>' % (x, y)
def txt(x, y, s, cls="val", anc="start"):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return '<text x="%g" y="%g" class="%s" text-anchor="%s">%s</text>' % (x, y, cls, anc, s)
def rect(x, y, w, h, cls="comp", rx=0):
    return '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" class="%s"/>' % (x, y, w, h, rx, cls)

def lab(x, y, ref, val, anc="start"):
    o = []
    if ref: o.append(txt(x, y, ref, "ref", anc))
    if val: o.append(txt(x, y + (15 if ref else 0), val, "val", anc))
    return o

# ----------------------------------------------------------------- parts
def res_v(x, y1, y2, lx=0, ly=0, ref="", val="", anc="start", bw=14, bh=34):
    m = (y1 + y2) / 2.0
    return [wire((x, y1), (x, m - bh/2)), wire((x, m + bh/2), (x, y2)),
            rect(x - bw/2, m - bh/2, bw, bh)] + lab(x + lx, m + ly, ref, val, anc)

def res_h(x1, x2, y, lx=0, ly=0, ref="", val="", anc="middle", bw=34, bh=14):
    m = (x1 + x2) / 2.0
    return [wire((x1, y), (m - bw/2, y)), wire((m + bw/2, y), (x2, y)),
            rect(m - bw/2, y - bh/2, bw, bh)] + lab(m + lx, y + ly, ref, val, anc)

def fuse_h(x1, x2, y, lx, ly, ref, val, anc="middle"):
    m = (x1 + x2) / 2.0
    return [wire((x1, y), (m - 20, y)), wire((m + 20, y), (x2, y)),
            rect(m - 20, y - 11, 40, 22), wire((m - 20, y), (m + 20, y))] + lab(m + lx, y + ly, ref, val, anc)

def ntc_h(x1, x2, y, lx, ly, ref, val, anc="middle"):
    m = (x1 + x2) / 2.0
    return [wire((x1, y), (m - 17, y)), wire((m + 17, y), (x2, y)),
            rect(m - 17, y - 13, 34, 26),
            '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (m - 23, y + 19, m + 21, y - 19),
            txt(m + 23, y - 15, "T", "sym")] + lab(m + lx, y + ly, ref, val, anc)

def mov_v(x, y1, y2, lx, ly, ref, val, anc="end"):
    m = (y1 + y2) / 2.0
    return [wire((x, y1), (x, m - 17)), wire((x, m + 17), (x, y2)),
            rect(x - 13, m - 17, 26, 34),
            '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (x - 21, m + 23, x + 19, m - 23)
            ] + lab(x + lx, m + ly, ref, val, anc)

def cap_v(x, y1, y2, lx, ly, ref, val, anc="start", pw=26):
    m = (y1 + y2) / 2.0
    return [wire((x, y1), (x, m - 6)), wire((x, m + 6), (x, y2)),
            '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (x-pw/2, m-6, x+pw/2, m-6),
            '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (x-pw/2, m+6, x+pw/2, m+6)
            ] + lab(x + lx, m + ly, ref, val, anc)

def cap_h(x1, x2, y, lx, ly, ref, val, anc="middle", ph=28):
    m = (x1 + x2) / 2.0
    return [wire((x1, y), (m - 6, y)), wire((m + 6, y), (x2, y)),
            '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (m-6, y-ph/2, m-6, y+ph/2),
            '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (m+6, y-ph/2, m+6, y+ph/2)
            ] + lab(m + lx, y + ly, ref, val, anc)

def ecap_v(x, y1, y2, lx, ly, ref, val, anc="start", pw=30):
    m = (y1 + y2) / 2.0
    return [wire((x, y1), (x, m - 7)), wire((x, m + 10), (x, y2)),
            '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (x-pw/2, m-7, x+pw/2, m-7),
            '<path d="M %g,%g Q %g,%g %g,%g" class="c"/>' % (x-pw/2, m+12, x, m+2, x+pw/2, m+12),
            txt(x - pw/2 - 5, m - 12, "+", "sym", "end")] + lab(x + lx, m + ly, ref, val, anc)

def diode_v(x, y1, y2, lx, ly, ref, val, cath="down", anc="start", kind="std"):
    m, s = (y1 + y2) / 2.0, 13
    if cath == "down":
        tri = "%g,%g %g,%g %g,%g" % (x-s, m-s, x+s, m-s, x, m+3); by = m + 3
    else:
        tri = "%g,%g %g,%g %g,%g" % (x-s, m+s, x+s, m+s, x, m-3); by = m - 3
    o = [wire((x, y1), (x, m - s)), wire((x, m + s), (x, y2)),
         '<polygon points="%s" class="comp"/>' % tri,
         '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (x-s, by, x+s, by)]
    if kind == "zener":
        o.append('<path d="M %g,%g l -6,%g M %g,%g l 6,%g" class="c"/>'
                 % (x-s, by, 7 if cath=="down" else -7, x+s, by, -7 if cath=="down" else 7))
    return o + lab(x + lx, m + ly, ref, val, anc)

def diode_h(x1, x2, y, lx, ly, ref, val, cath="right", anc="middle", kind="std"):
    m, s = (x1 + x2) / 2.0, 13
    if cath == "right":
        tri = "%g,%g %g,%g %g,%g" % (m-s, y-s, m-s, y+s, m+3, y); bx = m + 3; sg = 1
    else:
        tri = "%g,%g %g,%g %g,%g" % (m+s, y-s, m+s, y+s, m-3, y); bx = m - 3; sg = -1
    o = [wire((x1, y), (m - s, y)), wire((m + s, y), (x2, y)),
         '<polygon points="%s" class="comp"/>' % tri,
         '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (bx, y-s, bx, y+s)]
    if kind == "schottky":
        o.append('<path d="M %g,%g l %g,0 l 0,5 M %g,%g l %g,0 l 0,-5" class="c"/>'
                 % (bx, y-s, sg*6, bx, y+s, -sg*6))
    return o + lab(m + lx, y + ly, ref, val, anc)

def ind_h(x1, x2, y, lx, ly, ref, val, n=4, anc="middle"):
    st = (x2 - x1) / float(n)
    d = "M %g,%g " % (x1, y) + " ".join("A %g,%g 0 0 0 %g,%g" % (st/2, st/2, x1+st*(i+1), y) for i in range(n))
    return ['<path d="%s" class="coil"/>' % d] + lab((x1+x2)/2.0 + lx, y + ly, ref, val, anc)

def coil_v(x, y1, y2, n=4, bulge="left"):
    st = (y2 - y1) / float(n); sw = 0 if bulge == "left" else 1
    d = "M %g,%g " % (x, y1) + " ".join("A %g,%g 0 0 %d %g,%g" % (st/2, st/2, sw, x, y1+st*(i+1)) for i in range(n))
    return '<path d="%s" class="coil"/>' % d

def nmos(xd, yc, lx, ly, ref, val, anc="start"):
    g, ch = xd - 26, xd - 18
    o = ['<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (g, yc-19, g, yc+19)]
    for a, b in ((yc-19, yc-8), (yc-5, yc+5), (yc+8, yc+19)):
        o.append('<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (ch, a, ch, b))
    o += [wire((ch, yc-13), (xd, yc-13), (xd, yc-34)),
          wire((ch, yc+13), (xd, yc+13), (xd, yc+34)),
          wire((ch, yc), (xd, yc)),
          '<polygon points="%g,%g %g,%g %g,%g" class="comp"/>' % (ch+9, yc, ch+20, yc-5, ch+20, yc+5),
          wire((g-30, yc), (g, yc))]
    return o + lab(xd + lx, yc + ly, ref, val, anc), (xd, yc-34), (xd, yc+34), (g-30, yc)

def opto(x, y, lx, ly, ref, val, anc="middle"):
    """box 120x100. pins: LED A (x+120,y+18) K (x+120,y+82); C (x,y+18) E (x,y+82)"""
    o = [rect(x, y, 120, 100, "box", 4)]
    cx, cy = x + 84, y + 50
    o += ['<polygon points="%g,%g %g,%g %g,%g" class="comp"/>' % (cx-13, cy-16, cx+13, cy-16, cx, cy+2),
          '<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (cx-13, cy+2, cx+13, cy+2),
          wire((cx, y+18), (cx, cy-16)), wire((cx, cy+2), (cx, y+82)),
          wire((x+120, y+18), (cx, y+18)), wire((x+120, y+82), (cx, y+82))]
    tx, ty = x + 36, y + 50
    o += ['<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (tx, ty-16, tx, ty+16),
          wire((tx, ty-11), (tx-18, ty-22), (x, y+18)),
          wire((tx, ty+11), (tx-18, ty+22), (x, y+82)),
          '<polygon points="%g,%g %g,%g %g,%g" class="comp"/>' % (tx-18, ty+22, tx-9, ty+13, tx-5, ty+24)]
    for k in (-5, 5):
        o.append('<path d="M %g,%g l -15,5 m 1,-5 l 4,4 m -4,-4 l 5,0" class="arr"/>' % (cx-20, cy+k))
    return o + lab(x + 60 + lx, y + ly, ref, val, anc)

def shunt(x, y, lx, ly, ref, val, anc="middle"):
    o = [rect(x, y, 70, 70, "box", 4),
         txt(x+35, y+31, "TLV", "sym", "middle"), txt(x+35, y+49, "431", "sym", "middle")]
    return o + lab(x+35+lx, y+ly, ref, val, anc), (x+70, y+35), (x+35, y), (x+35, y+70)

def flag(x, y, name, d="left"):
    wd = 20 + 8.2 * len(name)
    if d == "left":
        pts = "%g,%g %g,%g %g,%g %g,%g %g,%g" % (x, y, x-15, y-14, x-wd, y-14, x-wd, y+14, x-15, y+14)
        tx = (x - wd + x - 15) / 2.0
    else:
        pts = "%g,%g %g,%g %g,%g %g,%g %g,%g" % (x, y, x+15, y-14, x+wd, y-14, x+wd, y+14, x+15, y+14)
        tx = (x + wd + x + 15) / 2.0
    return ['<polygon points="%s" class="flag"/>' % pts, txt(tx, y+5, name, "net", "middle")]

def earth(x, y):
    o = [wire((x, y), (x, y+14))]
    for i, k in enumerate((28, 18, 9)):
        o.append('<line x1="%g" y1="%g" x2="%g" y2="%g" class="c"/>' % (x-k/2, y+14+i*7, x+k/2, y+14+i*7))
    return o

def sect(x, y, w, h, t):
    return [rect(x, y, w, h, "sect", 6), txt(x+14, y+23, t, "sect-t")]

CSS = """
text{font-family:'DejaVu Sans',Arial,Helvetica,sans-serif;fill:#101418}
.title{font-size:26px;font-weight:700}
.sub{font-size:12.5px;fill:#5b6672}
.warn{font-size:13px;font-weight:700;fill:#a3341c;letter-spacing:.4px}
.rule{stroke:#101418;stroke-width:1.4}
.frame{fill:none;stroke:#101418;stroke-width:1.8}
.sect{fill:#f7f8fa;stroke:#c8cfd8;stroke-width:1.2}
.sect-t{font-size:12px;font-weight:700;fill:#5b6672;letter-spacing:.7px}
.w{fill:none;stroke:#101418;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.c{stroke:#101418;stroke-width:2;fill:none;stroke-linecap:round}
.coil{fill:none;stroke:#101418;stroke-width:2.2}
.core{stroke:#101418;stroke-width:2}
.core2{stroke:#101418;stroke-width:2.6}
.comp{fill:#ffffff;stroke:#101418;stroke-width:2}
.box{fill:#ffffff;stroke:#101418;stroke-width:2}
.jct{fill:#101418}
.dot{fill:#101418}
.pin{fill:#ffffff;stroke:#101418;stroke-width:2}
.ref{font-size:13.5px;font-weight:700}
.val{font-size:11.5px;fill:#2d3640}
.note{font-size:10.5px;fill:#6b7682}
.note2{font-size:12.4px;fill:#2d3640}
.nhdr{font-size:12.4px;font-weight:700;letter-spacing:.5px}
.nwarn{font-size:12.4px;font-weight:700;fill:#a3341c}
.sym{font-size:13px;font-weight:700}
.pinl{font-size:11.5px;font-weight:700;fill:#2d3640}
.net{font-size:11.5px;font-weight:700}
.flag{fill:#eef1f5;stroke:#101418;stroke-width:1.5}
.barrier{stroke:#a3341c;stroke-width:2;stroke-dasharray:11 7;opacity:.85}
.bar-t{font-size:11px;font-weight:700;fill:#a3341c;letter-spacing:.8px}
.bar-s{font-size:10px;fill:#a3341c;opacity:.85}
.arr{stroke:#101418;stroke-width:1.5;fill:none}
.jumper{stroke:#101418;stroke-width:2;fill:none;stroke-dasharray:5 4}
"""

# ===================================================== frame / title
W2, H2 = 2000, 1680
P[:] = []
add('<rect width="%g" height="%g" fill="#ffffff"/>' % (W2, H2))
add(rect(14, 14, W2-28, H2-28, "frame", 4))
add(txt(34, 54, "12 V / 5 A (60 W) UNIVERSAL-INPUT QR FLYBACK SMPS", "title"))
add(txt(34, 79, "Rev v3-PRELIM  ·  120–265 V AC in  ·  12.0 V / 5 A out  ·  quasi-resonant flyback, optocoupler + TLV431 secondary-side feedback", "sub"))
add(txt(W2-34, 54, "PRELIMINARY — NOT VALIDATED", "warn", "end"))
add(txt(W2-34, 78, "Mains circuit. Qualified review + lab validation required before build.", "sub", "end"))
add('<line x1="34" y1="96" x2="%g" y2="96" class="rule"/>' % (W2-34))

BX = 1090
add('<line x1="%g" y1="112" x2="%g" y2="%g" class="barrier"/>' % (BX, BX, H2-74))
add(txt(BX-10, 130, "PRIMARY", "bar-t", "end"))
add(txt(BX+10, 130, "SECONDARY · SELV", "bar-t"))
add(txt(BX+10, 146, "reinforced insulation barrier", "bar-s"))

# ========================================= A : AC input
add(sect(34, 158, 772, 322, "A · AC INPUT / EMI FILTER / RECTIFIER / BULK"))
yL, yN, yP = 222, 320, 416
add(rect(46, 196, 42, 244, "box", 3))
add(txt(67, 190, "TB1", "ref", "middle"))
for yy, nm in ((yL, "L"), (yN, "N"), (yP, "PE")):
    add('<circle cx="88" cy="%g" r="5" class="pin"/>' % yy)
    add(txt(67, yy+5, nm, "sym", "middle"))
add(wire((93, yL), (104, yL)))
add(fuse_h(104, 168, yL, 0, -26, "F1", "T2A / 300 V~", "middle"))
add(wire((168, yL), (184, yL)))
add(ntc_h(184, 248, yL, 0, 46, "RT1", "10 Ω / 3 A NTC", "middle"))
add(wire((248, yL), (352, yL)))
add(wire((93, yN), (516, yN)))
add(jct(300, yL)); add(jct(300, yN))
add(mov_v(300, yL, yN, -14, 88, "MOV1", "TMOV14R300E", "end"))
add(jct(352, yL)); add(jct(352, yN))
add(cap_v(352, yL, yN, 16, 88, "CX1", "0.47 μF X2", "start"))
add(wire((352, yL), (392, yL)))
add(ind_h(392, 458, yL, 0, -40, "LF1", "2 × 15 mH / 1.5 A", 4, "middle"))
add(ind_h(392, 458, yN, 0, 0, "", "", 4))
for yy in (248, 256):
    add('<line x1="400" y1="%g" x2="450" y2="%g" class="core"/>' % (yy, yy))
add(wire((458, yL), (516, yL)))
add(jct(486, yL)); add(jct(486, yN))
add(cap_v(486, yL, yN, 0, 120, "CX2", "0.22 μF X2", "middle"))
add(rect(516, 196, 96, 148, "box", 3))
add(txt(564, 254, "DB1", "ref", "middle"))
add(txt(564, 274, "KBP210", "val", "middle"))
add(txt(564, 291, "1000 V / 4 A", "val", "middle"))
add(txt(522, yL+5, "~", "sym")); add(txt(522, yN+5, "~", "sym"))
add(txt(606, yL+5, "+", "sym", "end")); add(txt(606, yN+5, "−", "sym", "end"))
add(wire((612, yL), (644, yL), (644, 186), (700, 186)))
add(wire((612, yN), (644, yN), (644, 440), (700, 440)))
add(jct(672, 186)); add(jct(672, 440))
add(ecap_v(672, 186, 440, 22, -32, "EC1", "68 μF / 450 V", "start"))
add(txt(694, 322, "105 °C  ≥5000 h", "note"))
add(txt(694, 338, "or 2 × 47 μF / 450 V", "note"))
add(flag(700, 186, "+HVDC", "right"))
add(flag(700, 440, "PGND", "right"))
add(wire((93, yP), (272, yP)))
add(earth(272, yP))
add(txt(296, yP+6, "chassis / PE bond", "note"))

# ========================================= B : power stage
add(sect(822, 158, 468, 658, "B · TRANSFORMER / SWITCH / CLAMP / Vcc"))
add('<line x1="1082" y1="220" x2="1082" y2="760" class="core2"/>')
add('<line x1="1098" y1="220" x2="1098" y2="760" class="core2"/>')
add(txt(1020, 772, "T1 · EER28L", "ref", "end"))
add(txt(1020, 788, "winding order: note 8", "note", "end"))

# primary winding
add(coil_v(1060, 236, 356, 4, "left"))
add('<circle cx="1072" cy="230" r="4" class="dot"/>')
add(wire((1060, 236), (1060, 210), (900, 210)))
add(flag(900, 210, "+HVDC", "left"))
add(txt(1038, 250, "Np", "ref", "end")); add(txt(1038, 266, "58 T", "val", "end"))
add(txt(1034, 288, "2 \u00d7 0.4 mm", "note", "end"))
add(wire((1060, 356), (1060, 386)))
add(jct(1060, 386))

# RCD clamp : R15 || C13
add(jct(935, 210))
add(wire((935, 210), (935, 232)))
add(res_h(935, 1000, 232, 0, 0, "", ""))
add(cap_h(935, 1000, 300, 0, 0, "", ""))
add(wire((935, 232), (935, 300)))
add(wire((1000, 232), (1000, 300)))
for p in ((935, 232), (1000, 232), (935, 300), (1000, 300)):
    add(jct(*p))
add(txt(929, 236, "R15", "ref", "end")); add(txt(929, 251, "18 kΩ 2 W", "val", "end"))
add(txt(929, 304, "C13", "ref", "end")); add(txt(929, 319, "10 nF 630 V", "val", "end"))
add(wire((1000, 300), (1000, 320)))
add(diode_v(1000, 320, 376, -16, -4, "D3", "UF4007", "up", "end"))
add(jct(1000, 376))
add(wire((1000, 376), (1060, 376)))

# switch
qe, qd, qs, qg = nmos(1060, 410, -60, 60, "Q1", "700 V / 0.45 Ω", "end")
add(qe)
add(wire((1060, 376), qd))
add(wire(qs, (1060, 444)))
add(jct(1060, 444))
add(res_v(1060, 444, 502, -22, 58, "R11", "0.25 Ω 2 W", "end"))
add(wire((1060, 502), (1060, 556)))
add(wire((930, 556), (1060, 556)))
add(jct(1060, 556))
add(flag(930, 556, "PGND", "left"))
add(wire((1060, 444), (930, 444)))
add(flag(930, 444, "CS", "left"))
add(wire(qg, (930, 410)))
add(flag(930, 410, "GATE", "left"))
add(jct(1014, 410)); add(jct(1014, 444))
add(res_v(1014, 410, 444, 0, 0, "", ""))
add(txt(996, 400, "R12 · 10 kΩ", "val", "end"))

# aux winding + Vcc
add(coil_v(1060, 648, 738, 3, "left"))
add('<circle cx="1072" cy="744" r="4" class="dot"/>')
add(txt(1116, 684, "Naux", "ref")); add(txt(1116, 700, "10 T", "val"))
add(wire((1060, 648), (1026, 648)))
add(jct(1026, 648))
add(diode_h(1026, 962, 648, 0, 30, "D5", "UF4007", "left", "middle"))
add(wire((962, 648), (936, 648)))
add(jct(936, 648))
add(ecap_v(936, 648, 738, 0, 0, "", "", "end"))
add(txt(912, 700, "C15 · 22μF/35V", "val", "end"))
add(wire((1060, 738), (936, 738)))
add(jct(936, 738))
add(wire((936, 738), (900, 738)))
add(flag(900, 738, "PGND", "left"))
add(wire((936, 648), (900, 648)))
add(flag(900, 648, "VCC", "left"))
add(wire((1026, 648), (1026, 614), (900, 614)))
add(flag(900, 614, "VAUX", "left"))

# ========================================= G : barrier crossing
add(sect(960, 824, 330, 112, "G \u00b7 BARRIER"))
add(wire((1002, 866), (1040, 866)))
add(cap_h(1040, 1150, 866, 8, -30, "CY1", "4.7 nF  Y1", "middle"))
add(wire((1150, 866), (1178, 866)))
add(flag(1002, 866, "PGND", "left"))
add(flag(1178, 866, "SGND", "right"))
add(wire((1002, 910), (1064, 910)))
add(wire((1116, 910), (1178, 910)))
add('<circle cx="1070" cy="910" r="5" class="pin"/>')
add('<circle cx="1110" cy="910" r="5" class="pin"/>')
add('<path d="M 1070,910 Q 1090,894 1110,910" class="jumper"/>')
add(txt(1090, 928, "JP1 · optional V− to PE link", "note", "middle"))
add(flag(1002, 910, "PE", "left"))
add(flag(1178, 910, "SGND", "right"))

# ========================================= D : secondary
add(sect(1300, 158, 666, 410, "D · SECONDARY RECTIFIER / OUTPUT FILTER"))
add(coil_v(1128, 236, 356, 4, "right"))
add('<circle cx="1140" cy="350" r="4" class="dot"/>')
add(txt(1152, 278, "Ns", "ref")); add(txt(1152, 294, "8 T", "val"))
add(txt(1152, 312, "0.2 × 10 mm foil", "note"))
add(wire((1128, 236), (1128, 196), (1340, 196)))
add(wire((1128, 356), (1128, 476), (1340, 476)))
add(jct(1310, 196))
add(diode_h(1340, 1420, 196, 0, 38, "", "D4 · MBR20100CT", "right", "middle", "schottky"))
add(wire((1420, 196), (1890, 196)))
add(wire((1340, 476), (1890, 476)))
add(res_v(1310, 220, 300, 22, -6, "R21", "10 Ω 1 W", "start"))
add(cap_v(1310, 300, 390, 22, -6, "C21", "1 nF 100 V", "start"))
add(wire((1310, 390), (1310, 476)))
add(jct(1310, 476))
for x in (1468, 1524, 1580, 1636):
    add(jct(x, 196)); add(jct(x, 476))
    add(ecap_v(x, 196, 476, 0, 0, "", ""))
add(txt(1446, 336, "C31", "ref", "end"))
add(txt(1658, 336, "C34", "ref", "start"))
add(ind_h(1690, 1766, 196, 0, 42, "L1", "2.2 μH / 8 A", 4, "middle"))
add(jct(1820, 196)); add(jct(1820, 476))
add(ecap_v(1820, 196, 476, -22, -6, "C35", "470 μF 25 V", "end"))
add(rect(1890, 170, 50, 334, "box", 3))
add(txt(1915, 164, "TB2", "ref", "middle"))
for yy, nm in ((206, "V+"), (250, "V+"), (416, "V−"), (460, "V−")):
    add('<circle cx="1890" cy="%g" r="5" class="pin"/>' % yy)
    add(txt(1915, yy+5, nm, "sym", "middle"))
add(wire((1872, 196), (1872, 206), (1885, 206)))
add(wire((1872, 196), (1872, 250), (1885, 250)))
add(jct(1872, 196))
add(wire((1860, 476), (1860, 416), (1885, 416)))
add(wire((1860, 476), (1860, 460), (1885, 460)))
add(jct(1860, 476))
add(jct(1690, 196))
add(wire((1690, 196), (1690, 170)))
add(flag(1690, 170, "+12V_S", "right"))
add(jct(1690, 476))
add(wire((1690, 476), (1690, 502)))
add(flag(1690, 502, "SGND", "right"))
add(txt(1312, 534, "C31–C34 = 4 × 1000 μF / 25 V low-ESR 105 °C ≥5000 h · bank carries 6.6 A rms (note 4)", "note"))
add(txt(1312, 550, "D4 = 100 V / 20 A dual Schottky, both legs paralleled · feedback senses at the C31–C34 node (note 5)", "note"))

# ========================================= E/F : feedback + OVP
def fb_block(y0, title, optoref, optoval, shref, tag_out,
             r_led, r_bias, r_up, r_up_val, r_dn, extra_note, comp):
    yr, yopt = y0 + 30, y0 + 68
    la, lk   = yopt + 18, yopt + 82
    ysh      = y0 + 104
    yref     = ysh + 35
    add(sect(960, y0, 1006, 312, title))
    add(flag(1930, yr, "+12V_S", "left"))
    add(wire((1930, yr), (1304, yr)))
    add(opto(1030, yopt, 0, 122, optoref, optoval, "middle"))
    # LED drive
    add(jct(1200, yr))
    add(res_v(1200, yr, la, 22, 18, r_led, "4.7 kΩ", "start"))
    add(wire((1200, la), (1150, la)))
    # TLV431 bias + cathode path
    add(jct(1304, yr))
    add(res_v(1304, yr, lk, 22, -40, r_bias, "100 kΩ", "start"))
    add(jct(1304, lk))
    add(wire((1150, lk), (1340, lk), (1340, ysh - 26), (1415, ysh - 26), (1415, ysh)))
    sh, _, _, _ = shunt(1380, ysh, 60, 74, shref, "TLV431A", "start")
    add(sh)
    # divider
    add(jct(1570, yr))
    add(res_v(1570, yr, yref - 11, 22, 20, r_up, r_up_val, "start"))
    add(jct(1570, yref))
    add(wire((1570, yref - 11), (1570, yref + 11)))
    add(wire((1570, yref), (1450, yref)))
    add(res_v(1570, yref + 11, yref + 83, 22, 24, r_dn, "10.0 kΩ 1 %", "start"))
    add(wire((1570, yref + 83), (1570, yref + 151)))
    # compensation
    add(wire((1570, yref), (1700, yref)))
    yy = yref
    for ref, val, hgt, typ in comp:
        f = res_v if typ == "r" else cap_v
        add(f(1700, yy, yy + hgt, 22, -6, ref, val, "start"))
        yy += hgt
    add(wire((1700, yy), (1700, yref + 131), (1570, yref + 131)))
    add(jct(1570, yref + 131))
    # anode to SGND
    add(wire((1415, ysh + 70), (1415, yref + 109), (1570, yref + 109)))
    add(jct(1570, yref + 109))
    add(flag(1570, yref + 151, "SGND", "right"))
    # primary side
    add(wire((1030, la), (996, la)));  add(flag(996, la, tag_out, "left"))
    add(wire((1030, lk), (996, lk)));  add(flag(996, lk, "PGND", "left"))
    if extra_note: add(txt(1592, yref - 15, extra_note, "note"))

fb_block(950, "E · VOLTAGE FEEDBACK  ·  optocoupler + TLV431 secondary-side error amplifier",
         "U2", "PC817C · CTR derated 50 %", "U3", "FB",
         "R41", "R42", "R43", "86.6 kΩ 1 %", "R44",
         "(90.9 kΩ = 12.4 V)", [("R45", "1 kΩ", 44, "r"), ("C41", "22 nF", 59, "c")])
fb_block(1282, "F · INDEPENDENT SECONDARY OVP  ·  latching · trips at 14.05 V · note 9",
         "U5", "PC817C", "U4", "LATCH",
         "R51", "R52", "R53", "102 kΩ 1 %", "R54",
         "", [("C51", "100 nF", 103, "c")])

# ========================================= C : controller
add(sect(34, 1038, 900, 344, "C · QR CONTROLLER  ·  generic pinout, see note 1"))
add(rect(340, 1076, 220, 240, "box", 4))
add(txt(450, 1184, "U1", "ref", "middle"))
add(txt(450, 1206, "QR flyback", "val", "middle"))
add(txt(450, 1224, "controller", "val", "middle"))
for nm, yy in (("HV", 1116), ("VCC", 1176), ("GND", 1236), ("OTP", 1296)):
    add(wire((340, yy), (306, yy))); add(txt(352, yy+5, nm, "pinl"))
for nm, yy in (("GATE", 1116), ("CS", 1176), ("FB", 1236), ("ZCD", 1296)):
    add(wire((560, yy), (594, yy))); add(txt(548, yy+5, nm, "pinl", "end"))
add(wire((306, 1116), (210, 1116))); add(flag(210, 1116, "+HVDC", "left"))
add(wire((306, 1176), (210, 1176))); add(flag(210, 1176, "VCC", "left"))
add(wire((306, 1236), (210, 1236))); add(flag(210, 1236, "PGND", "left"))
add(jct(268, 1176)); add(jct(268, 1236))
add(cap_v(268, 1176, 1236, -20, -6, "C11", "100 nF", "end"))
add(wire((306, 1296), (268, 1296))); add(jct(268, 1296))
add(res_v(268, 1296, 1346, 20, -6, "RT2", "100 kΩ NTC B4250", "start"))
add(wire((268, 1346), (268, 1358))); add(flag(268, 1358, "PGND", "left"))
add(wire((268, 1296), (210, 1296))); add(flag(210, 1296, "LATCH", "left"))
add(res_h(594, 684, 1116, 0, -24, "R13", "22 Ω", "middle"))
add(wire((684, 1116), (778, 1116))); add(flag(778, 1116, "GATE", "right"))
add(res_h(594, 672, 1176, 0, -24, "R14", "1 kΩ", "middle"))
add(wire((672, 1176), (778, 1176))); add(flag(778, 1176, "CS", "right"))
add(jct(716, 1176))
add(cap_v(716, 1176, 1230, -22, -6, "C12", "100 pF", "end"))
add(wire((716, 1230), (716, 1244))); add(flag(716, 1244, "PGND", "right"))
add(wire((560, 1236), (778, 1236))); add(flag(778, 1236, "FB", "right"))
add(jct(612, 1236))
add(cap_v(612, 1236, 1292, -22, -6, "C14", "1 nF", "end"))
add(wire((612, 1292), (612, 1306))); add(flag(612, 1306, "PGND", "left"))
add(res_h(594, 684, 1296, 0, 32, "R16", "22 kΩ", "middle"))
add(wire((684, 1296), (778, 1296))); add(flag(778, 1296, "VAUX", "right"))

# ========================================= notes
add(sect(34, 500, 772, 516, "DESIGN BASIS / NOTES"))
nx, ny, lh = 50, 536, 18.4
notes = [
 ("hdr", "OPERATING POINT  (worst case = low line, full load)"),
 ("", "Vin 120–265 V AC  ·  Vbulk 140–375 V DC  ·  Vor 90 V  ·  n = Np/Ns = 7.25"),
 ("", "Lp 330 μH ±7 %  ·  Ipk 2.56 A  ·  Ipri,rms 0.92 A  ·  Dmax 0.39"),
 ("", "fsw 65 kHz low line → 86 kHz high line (clear of the 150 kHz CISPR edge)"),
 ("", "Isec,pk 18.4 A  ·  Isec,rms 8.26 A  ·  Icap,rms 6.57 A  ·  Bmax ≈ 0.17 T"),
 ("", "Vds,pk = 375 + 135 clamp ≈ 510 V + ring → 700 V part (1.5× on 465 V)"),
 ("", "Loss ≈ 8.3 W → η ≈ 88 %. Size the thermal path for 11.4 W (the 84 % floor)."),
 ("gap", ""),
 ("hdr", "NOTES"),
 ("", "1  U1 pinout is generic. Choose a QR IC with HV start-up, an OTP/latch pin,"),
 ("", "    ZCD input and programmable OCP timing, then re-derive R13/R14/R16."),
 ("", "2  F1 → RT1 → MOV1 → CX → LF1 → DB1 order is mandatory. Verify F1 I²t against"),
 ("", "    MOV1 surge current and RT1 cold resistance as a system at the M2c gate."),
 ("", "3  RT1 at 10 Ω sets 375 V / 40 A inrush. Once RT1 is hot it is LF1 leakage"),
 ("", "    inductance that keeps surge energy off EC1 — scope the bulk rail in TC11."),
 ("", "4  Output bank: 6.57 A rms needs ≥ 9.4 A of rating at 30 % derating. Alternative:"),
 ("", "    2 × 470 μF/25 V hybrid polymer — smaller, longer life, higher cost."),
 ("", "5  Feedback senses BEFORE L1 deliberately: the L1/C35 pole sits at ≈ 4.9 kHz,"),
 ("", "    inside the loop bandwidth. The 50 mV drop at 5 A (0.4 %) is in the budget."),
 ("", "6  TLV431 (80 μA min bias) replaces TL431 (1 mA) so opto feedback can still"),
 ("", "    meet a low no-load target. Expect ≤ 0.2 W at 230 V; measure before claiming."),
 ("", "7  CY1 4.7 nF Y1 → 0.39 mA at 265 V/50 Hz = 11 % of the 3.5 mA Class I limit."),
 ("", "8  T1 order: ½Np → 3×tape → shield (1 T Cu to PGND) → 3×tape → Ns foil →"),
 ("", "    3×tape → ½Np → Naux → outer tape. 3 mm margin tape, DTI ≥ 0.4 mm."),
 ("", "9  OVP must sit ≥ 0.75 V above the measured load-dump overshoot (TC7). If it"),
 ("", "    does not, fix the loop compensation — do not raise the OVP threshold."),
 ("warn2", "10  SAFETY: the primary is at mains potential. Isolation transformer + dim-bulb"),
 ("warn2", "      tester for first power-on, discharge EC1 before probing, never probe alone."),
]
i = 0
for kind, s in notes:
    if kind == "gap":
        i += 0.5; continue
    add(txt(nx, ny + i*lh, s, {"hdr": "nhdr", "warn2": "nwarn"}.get(kind, "note2")))
    i += 1

add('<line x1="34" y1="%g" x2="%g" y2="%g" class="rule"/>' % (H2-58, W2-34, H2-58))
add(txt(34, H2-34, "12 V / 5 A QR flyback · rev v3-PRELIM · from smps_12v_5a_technical_plan_v2.md + round-2 review · all values calculated, none measured", "sub"))
add(txt(W2-34, H2-34, "Sheet 1 of 1", "sub", "end"))

svg = ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
       'width="%g" height="%g" viewBox="0 0 %g %g">\n<style>%s</style>\n%s\n</svg>\n'
       % (W2, H2, W2, H2, CSS, "\n".join(P)))
open("/home/user/Choke-r-d/docs/design/smps_12v_5a_schematic.svg", "w", encoding="utf-8").write(svg)
print("ok: %d elements, %d bytes" % (len(P), len(svg)))
