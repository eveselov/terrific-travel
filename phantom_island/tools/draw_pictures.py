"""
Draws the Focus pane's pictures of Phantom Island (DECISIONS.md, 16 and the fixes of
2026-11-26/27): every detail, every place, and the view from the Deck at each of the ship's
positions, in the parchment-and-ink style of the hand-drawn pictures (crane.svg).

Each picture shows only what its `look` text (or the place's description) says, so a
picture never marks a clue and telnet players miss nothing. The characters and things were
drawn by hand and are not made here.

Run from inside the game folder, after changing a drawing:

    uv run python tools/draw_pictures.py

It rewrites the SVG files in web/static/phantom_island/pictures/. Then `uv run evennia
collectstatic --noinput` (or a restart) copies them where the web server reads them, and the
browser needs a refresh. The content files name each picture (`image:`).
"""

# Drawing data: SVG paths are long strings the formatter can't wrap.
# ruff: noqa: E501

import math
import sys
from pathlib import Path

Num = int | float
OUT: Path = (
    Path(__file__).resolve().parent.parent / "web" / "static" / "phantom_island" / "pictures"
)
WRITTEN: list[str] = []
INK, BROWN, WOOD, TAN, SAND = "#3b2a14", "#7a4a21", "#8b5a2b", "#c9a96e", "#e6d3a8"
PAPER, SEA, SEALINE, LEAF, LEAFLINE = "#f3e6c4", "#a9c2c8", "#6f8f9f", "#6f8f5f", "#3b5a2b"
RED, GOLD, GREY, SKIN = "#a8452e", "#d4a017", "#8a8f94", "#c98a5a"


def svg(name: str, title: str, note: str, body: str) -> None:
    text = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 300" role="img" '
        f'aria-label="{title}">\n'
        f"  <!-- {note} Only what the look text says; same style as crane.svg. -->\n"
        f"  <title>{title}</title>\n"
        f'  <defs><clipPath id="frame"><rect x="9" y="9" width="462" height="282" rx="11"/></clipPath></defs>\n'
        f'  <rect x="6" y="6" width="468" height="288" rx="14" fill="{PAPER}" '
        f'stroke="{BROWN}" stroke-width="6"/>\n'
        f'  <g clip-path="url(#frame)">\n{body}  </g>\n'
        f'  <rect x="6" y="6" width="468" height="288" rx="14" fill="none" '
        f'stroke="{BROWN}" stroke-width="6"/>\n</svg>\n'
    )
    (OUT / f"{name}.svg").write_text(text, encoding="utf-8")
    WRITTEN.append(name)


def g(inner: str, **attrs: str) -> str:
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f"  <g {a}>{inner}</g>\n"


def rect(
    x: Num, y: Num, w: Num, h: Num, fill: str, stroke: str = INK, sw: Num = 2, rx: Num = 0
) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def path(d: str, fill: str = "none", stroke: str = INK, sw: Num = 2.5, extra: str = "") -> str:
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def circle(cx: Num, cy: Num, r: Num, fill: str, stroke: str = INK, sw: Num = 2) -> str:
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def ellipse(cx: Num, cy: Num, rx: Num, ry: Num, fill: str, stroke: str = INK, sw: Num = 2) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def text(
    x: Num,
    y: Num,
    s: str,
    size: Num = 16,
    fill: str = INK,
    anchor: str = "middle",
    weight: str = "bold",
) -> str:
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Georgia, serif" font-size="{size}" font-weight="{weight}" fill="{fill}">{s}</text>'


def way(x: int, y: int, word: str, dx: int, dy: int) -> str:
    """A direction written in ink: the word, and under it a short arrow pointing that way."""
    cx, cy = x, y + 16
    sx, sy = cx - dx / 2, cy - dy / 2
    ex, ey = cx + dx / 2, cy + dy / 2
    ang = math.atan2(dy, dx)
    h1 = (ex - 8 * math.cos(ang - 0.5), ey - 8 * math.sin(ang - 0.5))
    h2 = (ex - 8 * math.cos(ang + 0.5), ey - 8 * math.sin(ang + 0.5))
    arrow = f"M{sx:.0f} {sy:.0f} L{ex:.0f} {ey:.0f} M{h1[0]:.0f} {h1[1]:.0f} L{ex:.0f} {ey:.0f} L{h2[0]:.0f} {h2[1]:.0f}"
    return text(x, y, word, 13, BROWN) + path(arrow, stroke=BROWN, sw=2)


# --- Pieces ---------------------------------------------------------------------------


def sea(top: int, bottom: int = 286, waves: int = 3) -> str:
    out = rect(14, top, 452, bottom - top, SEA, SEALINE, 0)
    out += path(f"M14 {top} H466", stroke=SEALINE, sw=2)
    for i in range(waves):
        y = top + 18 + i * (bottom - top - 24) // max(waves, 1)
        x0 = 40 + (i % 2) * 60
        out += path(
            f"M{x0} {y} q15 -7 30 0 t30 0 M{x0 + 200} {y + 6} q15 -7 30 0 t30 0",
            stroke=SEALINE,
            sw=2,
        )
    return out


def sky_line(y: int) -> str:
    return path(f"M14 {y} H466", stroke=SEALINE, sw=2)


def sand(top: int) -> str:
    return rect(14, top, 452, 286 - top, SAND, BROWN, 0) + path(
        f"M14 {top} H466", stroke=BROWN, sw=2
    )


def planks(top: int) -> str:
    out = rect(14, top, 452, 286 - top, TAN, BROWN, 0)
    for y in range(top, 286, 14):
        out += path(f"M14 {y} H466", stroke=WOOD, sw=2)
    return out


def palm(x: int, base: int, h: int = 150, lean: int = 20) -> str:
    tx, ty = x + lean, base - h
    trunk = path(
        f"M{x} {base} C{x - 4} {base - h * 0.4} {x + lean * 0.4} {base - h * 0.8} {tx} {ty}",
        stroke=WOOD,
        sw=9,
    )
    leaves = "".join(
        path(
            f"M{tx} {ty} C{tx + dx * 0.5} {ty + dy * 0.2 - 18} {tx + dx * 0.9} {ty + dy * 0.6} {tx + dx} {ty + dy} C{tx + dx * 0.6} {ty + dy * 0.6} {tx + dx * 0.3} {ty + dy * 0.2} {tx} {ty} Z",
            LEAF,
            LEAFLINE,
            2,
        )
        for dx, dy in ((-60, 22), (56, 26), (-40, -10), (44, -8), (6, 36))
    )
    nuts = circle(tx - 4, ty + 8, 5, WOOD) + circle(tx + 6, ty + 9, 5, WOOD)
    return trunk + leaves + nuts


def hut(x: int, base: int, w: int = 110, fill: str = TAN) -> str:
    h = w * 0.55
    walls = rect(x + w * 0.15, base - h * 0.4, w * 0.7, h * 0.4, "#d8c08e", BROWN, 2)
    roof = path(
        f"M{x} {base - h * 0.12} C{x + w * 0.1} {base - h * 0.9} {x + w * 0.35} {base - h * 1.2} {x + w / 2} {base - h * 1.2} "
        f"C{x + w * 0.65} {base - h * 1.2} {x + w * 0.9} {base - h * 0.9} {x + w} {base - h * 0.12} Z",
        fill,
        BROWN,
        2.5,
    )
    fringe = path(
        " ".join(
            f"M{x + w * f:.0f} {base - h * 0.14:.0f} v{h * 0.08:.0f}"
            for f in (0.1, 0.25, 0.4, 0.55, 0.7, 0.85)
        ),
        stroke="#a8803f",
        sw=2,
    )
    door = rect(x + w * 0.44, base - h * 0.32, w * 0.12, h * 0.32, "#5b4632", BROWN, 1.5)
    return walls + roof + fringe + door


def goat(x: int, y: int, s: float = 1.0, flip: bool = False, chew: bool = False) -> str:
    t = f'transform="translate({x} {y}) scale({-s if flip else s} {s})"'
    body = (
        ellipse(0, 0, 34, 18, "#8b5a2b")
        + path("M-22 14 v26 M-10 16 v24 M14 16 v24 M26 14 v26", stroke=INK, sw=4)
        + ellipse(40, -18, 14, 10, "#8b5a2b")
        + path("M34 -26 l-6 -14 M42 -27 l2 -15", stroke=INK, sw=3)
        + circle(44, -20, 2.5, "#e3b93a", INK, 1)
        + path("M52 -12 l4 10 l-6 -2", stroke=INK, sw=2)
        + path("M-34 -6 l-10 -6", stroke=INK, sw=3)
    )
    if chew:
        body += path("M54 -14 l26 6 l-4 -6 l10 2", LEAF, LEAFLINE, 2)
    return f"<g {t}>{body}</g>"


def gull(x: int, y: int, s: float = 1.0) -> str:
    return path(
        f"M{x - 14 * s} {y} q{7 * s} {-10 * s} {14 * s} 0 q{7 * s} {-10 * s} {14 * s} 0", sw=2.5
    )


def tern(x: int, y: int, s: float = 1.0) -> str:
    """A white tern flying left (west)."""
    return path(
        f"M{x} {y} l{-12 * s} {-2 * s} l{12 * s} {-8 * s} l{6 * s} {8 * s} l{12 * s} {-8 * s} l{-4 * s} {10 * s} l{8 * s} {4 * s} Z",
        "#ffffff",
        INK,
        1.5,
    )


def barrel(x: int, y: int, w: int = 44, h: int = 56, label: str = "") -> str:
    out = path(f"M{x} {y} q-6 {h / 2} 0 {h} h{w} q6 {-h / 2} 0 {-h} Z", WOOD, INK, 2)
    out += path(
        f"M{x - 3} {y + h * 0.25} h{w + 6} M{x - 3} {y + h * 0.75} h{w + 6}", stroke="#5b4632", sw=3
    )
    out += ellipse(x + w / 2, y, w / 2, 6, "#a8803f", INK, 2)
    if label:
        out += text(x + w / 2, y + h / 2 + 4, label, 9, PAPER)
    return out


def coil(cx: int, cy: int, r: int = 60) -> str:
    return "".join(
        ellipse(cx, cy - i * 5, r - i * 16, (r - i * 16) * 0.24, TAN if i == 0 else "none", WOOD, 6)
        for i in range(3)
    )


def ship(x: int, base: int, s: float = 1.0, furled: bool = True, name: str = "") -> str:
    t = f'transform="translate({x} {base}) scale({s})"'
    hull = path("M-90 -30 H90 L70 0 H-74 Z", "#2b2b2b", INK, 2.5)
    masts = path("M-40 -30 V-150 M20 -30 V-170 M70 -30 V-120", stroke=WOOD, sw=5)
    if furled:
        sails = path("M-60 -130 H-20 M-2 -150 H42 M52 -104 H88", stroke=PAPER, sw=7)
    else:
        sails = path(
            "M-66 -140 Q-40 -110 -66 -50 H-14 Q-40 -110 -14 -140 Z", "#fbf4e0", INK, 2
        ) + path("M-8 -160 Q20 -125 -8 -60 H48 Q20 -125 48 -160 Z", "#fbf4e0", INK, 2)
    rig = path("M-40 -150 L-90 -30 M20 -170 L90 -30 M20 -170 L-40 -150", stroke=BROWN, sw=1.5)
    label = text(50, -12, name, 10, PAPER) if name else ""
    return f"<g {t}>{hull}{masts}{sails}{rig}{label}</g>"


def tree(x: int, base: int, h: int = 160) -> str:
    return (
        path(f"M{x} {base} V{base - h}", stroke="#7a6a4a", sw=12)
        + ellipse(x, base - h - 10, 46, 34, LEAF, LEAFLINE, 2)
        + ellipse(x - 30, base - h + 10, 30, 22, LEAF, LEAFLINE, 2)
        + ellipse(x + 32, base - h + 8, 30, 22, LEAF, LEAFLINE, 2)
    )


def person(x: int, base: int, coat: str, s: float = 1.0) -> str:
    t = f'transform="translate({x} {base}) scale({s})"'
    return (
        f"<g {t}>"
        + path("M-24 0 C-26 -50 -16 -70 0 -70 C16 -70 26 -50 24 0 Z", coat, INK, 2.5)
        + circle(0, -86, 16, SKIN)
        + "</g>"
    )


def island_shape(cx: float, cy: float, s: float) -> str:
    """The island's outline as the chart and the hilltop show it."""
    t = f'transform="translate({cx} {cy}) scale({s})"'
    land = path(
        "M-50 -70 C-10 -96 60 -90 76 -44 C90 0 60 40 22 46 C12 62 -4 72 -18 66 C-8 62 0 54 -4 46 C-26 44 -44 36 -52 20 C-62 0 -64 -48 -50 -70 Z",
        SAND,
        INK,
        2.5,
    )
    lagoon = ellipse(62, -22, 26, 30, "#b8dcc0", INK, 1.8)
    lagoon_reef = path(
        "M70 -54 Q104 -22 70 10", stroke="#ffffff", sw=3, extra='stroke-dasharray="5 4"'
    )
    hill = path("M-30 -14 l12 -20 l12 20 M-16 -14 l10 -14 l10 14", "#c9a96e", INK, 2)
    forest = "".join(
        circle(x, y, 5, LEAF, LEAFLINE, 1)
        for x, y in (
            (-36, -50),
            (-20, -60),
            (0, -66),
            (18, -58),
            (-40, 6),
            (-22, 20),
            (0, 10),
            (14, 26),
            (24, -40),
            (-6, -36),
        )
    )
    reef = path(
        "M-70 -68 l-4 8 l4 8 l-4 8 l4 8 l-4 8 l4 8 l-4 8 l4 8 l-4 8 l4 8 l-4 8",
        stroke="#ffffff",
        sw=3,
    )
    return f"<g {t}>{land}{lagoon}{lagoon_reef}{forest}{hill}{reef}</g>"


def rail(top: int = 236) -> str:
    """The Good Hope's rail in the foreground, seen from her Deck."""
    out = rect(14, top, 452, 286 - top, TAN, BROWN, 0)
    out += path(f"M14 {top} H466", stroke=WOOD, sw=10)
    out += "".join(path(f"M{x} {top} V286", stroke=WOOD, sw=6) for x in range(50, 466, 70))
    return out


def awning_stall(x: int, base: int, w: int, color: str) -> str:
    return (
        path(f"M{x} {base - 90} H{x + w} L{x + w - 8} {base - 70} H{x + 8} Z", color, BROWN, 2)
        + rect(x + 6, base - 70, 5, 70, BROWN, BROWN, 0)
        + rect(x + w - 11, base - 70, 5, 70, BROWN, BROWN, 0)
        + rect(x, base - 28, w, 12, WOOD, INK, 2)
    )


def draw_details() -> None:
    """The details of the places and of the ship's positions (`look <detail>`)."""
    # --- The Society Office ---------------------------------------------------------------

    svg(
        "office_window",
        "The harbour below the window",
        "The Society Office's window: the busy harbour, the Good Hope at the end of the quay, sails furled.",
        g(
            rect(40, 30, 400, 240, PAPER, BROWN, 8)
            + rect(44, 120, 392, 90, SEA, SEALINE, 0)
            + path("M44 120 H436", stroke=SEALINE, sw=2)
            + path("M70 150 q15 -7 30 0 t30 0 M230 170 q15 -7 30 0 t30 0", stroke=SEALINE, sw=2)
            + rect(44, 210, 392, 52, "#c9b48a", BROWN, 2)
            + ship(330, 210, 0.55, True)
            + path("M90 160 l30 0 l-6 10 h-20 Z", WOOD, INK, 2)
            + path("M150 176 l40 0 l-8 12 h-26 Z", WOOD, INK, 2)
            + gull(120, 80)
            + gull(170, 64, 0.8)
            + path("M240 30 V270 M40 150 H440", stroke=BROWN, sw=6)
        ),
    )

    svg(
        "office_bookshelves",
        "Logbooks and journals on the shelves",
        "Rows of logbooks and journals, each with a year on its spine, margins full of red notes.",
        g(
            rect(40, 26, 400, 250, "#e6d3a8", BROWN, 3)
            + path("M40 108 H440 M40 190 H440", stroke=BROWN, sw=4)
            + "".join(
                rect(52 + i * 26, 40 + (i % 3) * 4, 22, 66 - (i % 3) * 4, c, INK, 1.5)
                + text(63 + i * 26, 90, str(1760 + i), 7, PAPER)
                for i, c in enumerate(
                    [
                        RED,
                        "#5b4632",
                        "#3f5a73",
                        WOOD,
                        RED,
                        "#5b4632",
                        "#6f8f5f",
                        WOOD,
                        "#3f5a73",
                        RED,
                        "#5b4632",
                        WOOD,
                        RED,
                        "#3f5a73",
                        "#5b4632",
                    ]
                )
            )
            + "".join(
                rect(52 + i * 26, 122 + (i % 2) * 6, 22, 66 - (i % 2) * 6, c, INK, 1.5)
                for i, c in enumerate(
                    [WOOD, "#3f5a73", RED, "#5b4632", WOOD, RED, "#6f8f5f", "#5b4632"]
                )
            )
            + rect(270, 130, 140, 54, "#fbf4e0", BROWN, 1.5)
            + path("M282 146 h80 M282 160 h70 M282 172 h86", stroke=TAN, sw=2)
            + path("M370 144 h30 M372 158 h26", stroke=RED, sw=2)
            + "".join(
                rect(52 + i * 30, 204 + (i % 2) * 4, 26, 62 - (i % 2) * 4, c, INK, 1.5)
                for i, c in enumerate(
                    [
                        RED,
                        WOOD,
                        "#3f5a73",
                        "#5b4632",
                        RED,
                        WOOD,
                        "#6f8f5f",
                        "#5b4632",
                        RED,
                        WOOD,
                        "#3f5a73",
                        "#5b4632",
                        WOOD,
                    ]
                )
            )
        ),
    )

    svg(
        "office_charts",
        "Rolled-up charts tied with ribbon",
        "Charts of coasts and seas, rolled and tied with ribbon; one open, blank far out in the ocean.",
        g(
            rect(150, 40, 290, 170, "#fbf4e0", BROWN, 2)
            + path("M160 60 C190 70 200 110 180 140 C170 160 176 190 160 200", "#e6d3a8", BROWN, 2)
            + path(
                "M190 80 H430 M190 130 H430 M190 180 H430 M260 40 V210 M350 40 V210",
                stroke="#e0caa0",
                sw=1.5,
            )
            + "".join(
                rect(40 + i * 8, 210 - i * 26, 210, 24, "#fbf4e0", BROWN, 2, 12)
                + path(f"M{130 + i * 8} {210 - i * 26} v24", stroke=RED, sw=5)
                for i in range(4)
            )
            + planks(244)
        ),
    )

    svg(
        "office_desk",
        "Mrs. Fairweather's desk",
        "A wide desk with neat piles of letters, an inkpot, a quill and a little brass bell.",
        g(
            rect(30, 150, 420, 26, WOOD, INK, 2.5)
            + rect(46, 176, 16, 100, BROWN)
            + rect(418, 176, 16, 100, BROWN)
            + "".join(
                rect(60 + i * 70, 150 - 8 - j * 6, 56, 6, "#fbf4e0", BROWN, 1.5)
                for i in range(3)
                for j in range(4 - i)
            )
            + rect(290, 124, 26, 26, INK, INK, 2, 4)
            + path("M310 124 L340 70", stroke="#5b4632", sw=3)
            + path("M340 70 q14 -10 18 4 q-10 4 -18 -4", "#fbf4e0", BROWN, 1.5)
            + path("M374 150 q0 -30 20 -30 q20 0 20 30 Z", GOLD, INK, 2)
            + circle(394, 116, 5, GOLD)
        ),
    )

    svg(
        "office_street",
        "The street below",
        "Carts rattling over the cobbles, and the market's shouting next door.",
        g(
            rect(14, 180, 452, 106, "#c9b48a", BROWN, 0)
            + "".join(
                ellipse(
                    30 + (i % 15) * 30 + (i // 15 % 2) * 15,
                    196 + (i // 15) * 22,
                    13,
                    8,
                    "#b39d72",
                    BROWN,
                    1.5,
                )
                for i in range(60)
            )
            + rect(40, 60, 120, 120, "#d8c08e", BROWN, 2)
            + rect(320, 50, 140, 130, "#d8c08e", BROWN, 2)
            + rect(70, 90, 30, 30, SEA, BROWN, 2)
            + rect(350, 80, 30, 30, SEA, BROWN, 2)
            + rect(200, 168, 110, 44, WOOD, INK, 2)
            + circle(222, 222, 18, TAN, INK, 3)
            + circle(290, 222, 18, TAN, INK, 3)
            + path("M200 182 l-36 6", stroke=INK, sw=3)
            + path("M330 120 q10 -10 0 -20 M342 126 q16 -16 0 -32", stroke=BROWN, sw=2.5)
        ),
    )

    # --- The Market -----------------------------------------------------------------------

    svg(
        "market_goods",
        "Goods from far away",
        "Silver fish, rope, sacks of pepper and cinnamon, brass lamps, a carved paddle, a huge shell and a feather cloak.",
        g(
            rect(30, 190, 420, 20, WOOD, INK, 2.5)
            + planks(250)
            + "".join(
                path(
                    f"M{50 + i * 22} {188} q10 -10 20 0 q-10 10 -20 0 Z M{70 + i * 22} 188 l6 -5 v10 Z",
                    "#c0c8cc",
                    INK,
                    1.5,
                )
                for i in range(3)
            )
            + coil(150, 186, 30)
            + path("M190 190 q4 -40 24 -40 q20 0 24 40 Z", "#a8452e", INK, 2)
            + path("M244 190 q4 -34 22 -34 q18 0 22 34 Z", "#8b5a2b", INK, 2)
            + path("M300 190 h30 l-4 -20 h-22 Z M308 170 q7 -16 14 0", GOLD, INK, 2)
            + path("M350 190 L420 110 M412 106 q14 -8 14 10 q-8 6 -14 -10", WOOD, INK, 3)
            + path("M352 186 q-10 -30 20 -36 q30 6 18 36 Z", "#f0d8c8", INK, 2)
            + path("M60 120 q40 -60 80 0 l-10 60 h-60 Z", RED, INK, 2)
            + "".join(path(f"M{70 + i * 12} 130 v40", stroke=GOLD, sw=2) for i in range(6))
        ),
    )

    svg(
        "market_traders",
        "Traders calling out their prices",
        "Everyone selling something, as loudly as they can.",
        g(
            sand(240)
            + person(100, 240, RED)
            + person(240, 240, "#3f5a73", 1.1)
            + person(380, 240, "#6f8f5f")
            + "".join(
                path(
                    f"M{x + 18} 136 q10 -6 0 -14 M{x + 26} 140 q18 -12 0 -26", stroke=BROWN, sw=2.5
                )
                for x in (100, 240, 380)
            )
            + text(120, 70, "Fresh today!", 15, BROWN, weight="normal")
            + text(330, 60, "Cheapest in the port!", 15, BROWN, weight="normal")
        ),
    )

    svg(
        "market_stall",
        "Silas Crane's stall",
        "Pots, cloth, knives, and in the middle, a brass compass that people point at.",
        g(
            path("M40 40 H440 L428 78 H52 Z", TAN, BROWN, 2)
            + rect(48, 78, 8, 196, BROWN)
            + rect(424, 78, 8, 196, BROWN)
            + rect(70, 200, 340, 18, WOOD, INK, 2.5)
            + path("M100 200 C96 176 132 176 128 200 Z", "#b5651d", INK, 2)
            + path("M150 200 C146 184 172 184 168 200 Z", "#9c7a54", INK, 2)
            + path("M330 200 l10 -26 h40 l10 26 Z", "#6f8f9f", INK, 2)
            + path("M190 198 l30 -10 M194 200 l30 -10", stroke="#7d7d7d", sw=3)
            + circle(270, 188, 13, GOLD)
            + circle(270, 188, 7, PAPER, BROWN, 1)
            + path("M286 172 l6 -6 M290 182 h8 M282 166 v-8", stroke=GOLD, sw=2)
            + path("M150 270 L230 196", stroke=SKIN, sw=6)
            + person(130, 286, "#3f5a73", 0.8)
        ),
    )

    # --- The Quay -------------------------------------------------------------------------

    svg(
        "quay_barrels",
        "Barrels for the Good Hope",
        "Barrels of salt beef, biscuit and water waiting to go aboard; some chalked GOOD HOPE.",
        g(
            rect(14, 236, 452, 50, "#c9b48a", BROWN, 0)
            + barrel(60, 180, 54, 66, "GOOD HOPE")
            + barrel(130, 184, 54, 62)
            + barrel(200, 180, 54, 66, "GOOD HOPE")
            + barrel(95, 116, 54, 62)
            + barrel(165, 116, 54, 62, "GOOD HOPE")
            + barrel(300, 190, 50, 56)
            + barrel(360, 186, 50, 60, "GOOD HOPE")
        ),
    )

    svg(
        "quay_rope",
        "Coils of tarred rope",
        "Thick hemp rope coiled in big rings, smelling of tar; Old Barnaby sits on one.",
        g(
            rect(14, 236, 452, 50, "#c9b48a", BROWN, 0)
            + coil(120, 230, 80)
            + coil(330, 236, 70)
            + path(
                "M300 228 C300 198 316 188 330 188 C344 188 360 198 360 228 Z", "#3f5a73", INK, 2.5
            )
            + circle(330, 174, 15, "#e2b98f")
            + path("M316 178 C318 198 342 198 344 178", "#ffffff", INK, 2)
            + path("M60 120 q8 -10 0 -20 M80 110 q8 -10 0 -20", stroke="#5b4632", sw=2)
        ),
    )

    svg(
        "quay_gulls",
        "Gulls over fish heads",
        "Grey and white gulls, loud and greedy, squabbling over fish heads.",
        g(
            rect(14, 220, 452, 66, "#c9b48a", BROWN, 0)
            + "".join(
                f'<g transform="translate({x} {y})">'
                + ellipse(0, 0, 26, 14, "#ffffff")
                + path("M-26 -2 l-14 -2 l14 8 Z", GREY, INK, 1.5)
                + path("M-10 -8 q16 -14 30 -2", GREY, INK, 2)
                + circle(22, -12, 9, "#ffffff")
                + path("M30 -12 l12 2 l-12 3 Z", GOLD, INK, 1.5)
                + circle(24, -14, 1.5, INK)
                + path("M-6 12 v12 M6 12 v12", sw=2)
                + "</g>"
                for x, y in ((140, 196), (280, 192))
            )
            + path("M200 216 q10 -8 20 0 q-10 8 -20 0 Z M220 216 l6 -5 v10 Z", "#c0c8cc", INK, 1.5)
            + gull(120, 90)
            + gull(330, 70)
            + gull(380, 110, 0.8)
            + path("M170 160 l6 -10 M186 166 l10 -6 M244 160 l-6 -10", stroke=BROWN, sw=2)
        ),
    )

    svg(
        "quay_harbour",
        "The harbour and the open ocean",
        "Ships at anchor, fishing boats, and beyond the harbour mouth the ocean stretching west.",
        g(
            sea(110, 286, 4)
            + ship(330, 190, 0.6)
            + ship(130, 170, 0.4)
            + path("M240 230 l40 0 l-8 12 h-24 Z", WOOD, INK, 2)
            + path("M380 250 l34 0 l-6 10 h-22 Z", WOOD, INK, 2)
            + way(70, 70, "WEST", -50, 0)
        ),
    )

    # --- The island -----------------------------------------------------------------------

    svg(
        "beach_lagoon",
        "The lagoon",
        "Warm, clear water over white sand, small fish, and your ship at anchor out in the lagoon.",
        g(
            rect(14, 100, 452, 186, "#c4dcdc", SEALINE, 0)
            + sky_line(100)
            + ship(330, 150, 0.45)
            + "".join(
                path(
                    f"M{x} {y} q8 -6 16 0 q-8 6 -16 0 Z M{x + 16} {y} l5 -4 v8 Z",
                    "#6f8f9f",
                    INK,
                    1.2,
                )
                for x, y in ((110, 220), (150, 236), (200, 214), (260, 246))
            )
            + path("M14 270 q120 -14 240 0 t212 0 V286 H14 Z", "#ffffff", BROWN, 1.5)
        ),
    )

    svg(
        "beach_palms",
        "Palms on the beach",
        "Tall bending trunks with a crown of long leaves, and a few coconuts.",
        g(
            sea(170, 214, 1)
            + sand(214)
            + palm(120, 250, 170, 30)
            + palm(260, 250, 190, -20)
            + palm(380, 250, 140, 36)
        ),
    )

    svg(
        "beach_path",
        "A path into the forest",
        "A narrow, trodden path climbing from the sand into the forest, to the northwest.",
        g(
            sand(200)
            + tree(110, 210, 110)
            + tree(220, 200, 130)
            + tree(380, 214, 110)
            + path(
                "M300 286 C280 250 250 230 200 210 C180 202 170 196 160 190", "#d8c08e", BROWN, 2
            )
            + path("M330 286 C300 250 270 226 220 206 C196 196 182 192 170 188", stroke=BROWN, sw=2)
            + way(430, 44, "NW", -24, -14)
        ),
    )

    svg(
        "beach_goats",
        "Three brown goats",
        "Three brown goats with yellow eyes; one chews a palm leaf.",
        g(
            sand(220)
            + goat(110, 210, 1.0)
            + goat(240, 220, 1.1, chew=True)
            + goat(380, 206, 0.9, flip=True)
        ),
    )

    svg(
        "village_huts",
        "Round huts of the village",
        "Small round huts of light poles, roofs of woven palm leaves hanging almost to the ground, a swept space between.",
        g(sand(220) + hut(40, 230, 120) + hut(190, 220, 110) + hut(320, 236, 130)),
    )

    svg(
        "village_fire",
        "A fire in a ring of stones",
        "A low fire in a ring of stones, something wrapped in leaves cooking in the ashes.",
        g(
            sand(180)
            + "".join(
                ellipse(240 + 90 * c, 220 + 30 * s, 16, 11, "#9a9a9a")
                for c, s in (
                    (-1, 0),
                    (-0.7, 0.7),
                    (0, 1),
                    (0.7, 0.7),
                    (1, 0),
                    (0.7, -0.7),
                    (0, -1),
                    (-0.7, -0.7),
                )
            )
            + ellipse(240, 222, 60, 16, "#7d7d7d", BROWN, 0)
            + path("M230 212 q-10 -30 6 -52 q4 24 14 30 q6 -18 0 -32 q22 22 6 54 Z", GOLD, RED, 2)
            + path("M200 222 q20 -10 40 0 q-20 10 -40 0 Z", LEAF, LEAFLINE, 2)
            + path("M262 226 q16 -8 32 0 q-16 8 -32 0 Z", LEAF, LEAFLINE, 2)
            + path("M236 140 q-10 -20 4 -40 M252 130 q10 -20 -4 -40", stroke=GREY, sw=2)
        ),
    )

    svg(
        "village_beams",
        "The big hut's dark beams",
        "The big hut stands on thick, dark beams, much heavier than the light wood of the other huts.",
        g(
            sand(240)
            + path("M60 120 L240 40 L420 120 Z", TAN, BROWN, 2.5)
            + rect(80, 118, 320, 20, "#3b2a14", INK, 2)
            + rect(96, 138, 26, 104, "#3b2a14", INK, 2)
            + rect(358, 138, 26, 104, "#3b2a14", INK, 2)
            + rect(226, 138, 26, 104, "#3b2a14", INK, 2)
            + "".join(path(f"M{x} 140 V240", stroke="#c9a96e", sw=4) for x in (150, 180, 290, 320))
            + hut(14, 246, 70)
            + hut(410, 250, 50)
        ),
    )

    svg(
        "reef_coral",
        "Coral in the shallow water",
        "Clear, shallow water over coral of every colour, branching like little trees; waves breaking white further out.",
        g(
            rect(14, 60, 452, 226, "#c4dcdc", SEALINE, 0)
            + path("M14 80 q40 -16 80 0 t80 0 t80 0 t80 0 t80 0 t66 0", "#ffffff", SEALINE, 2)
            + "".join(
                path(
                    f"M{x} 270 v-{h} M{x} {270 - h * 0.5} l-{h * 0.3} -{h * 0.3} M{x} {270 - h * 0.7} l{h * 0.3} -{h * 0.3}",
                    stroke=c,
                    sw=7,
                )
                for x, h, c in (
                    (60, 80, "#e48aa0"),
                    (120, 60, "#e3b93a"),
                    (190, 90, "#9a6ab0"),
                    (260, 70, "#e48aa0"),
                    (330, 84, "#e3b93a"),
                    (400, 66, "#9a6ab0"),
                )
            )
            + "".join(
                circle(x, 268, 14, c, INK, 1.5)
                for x, c in ((90, "#9a6ab0"), (230, "#e3b93a"), (370, "#e48aa0"))
            )
        ),
    )

    svg(
        "reef_bones",
        "A ship's ribs and a cannon on the reef",
        "At low tide: curved black timbers in two rows, furred with weed, and a long coral lump with a round mouth: a cannon.",
        g(
            rect(14, 60, 452, 226, "#c4dcdc", SEALINE, 0)
            + rect(14, 200, 452, 86, "#d9c9a8", BROWN, 0)
            + "".join(
                path(f"M{x} 220 C{x - 6} 160 {x + 10} 120 {x + 26} 106", stroke="#2b2b2b", sw=10)
                + path(f"M{x + 2} 200 c4 -10 -4 -16 2 -24", stroke=LEAF, sw=3)
                for x in (90, 150, 210, 270)
            )
            + "".join(
                path(f"M{x} 250 C{x + 6} 200 {x - 10} 170 {x - 26} 160", stroke="#2b2b2b", sw=10)
                for x in (330, 380, 430)
            )
            + path(
                "M150 260 C150 246 330 240 340 254 C344 266 156 276 150 260 Z", "#e8d8c8", INK, 2
            )
            + ellipse(340, 254, 9, 9, "#3b2a14")
            + "".join(circle(x, 252, 6, "#e48aa0", INK, 1) for x in (190, 240, 290))
        ),
    )

    svg(
        "forest_birds",
        "Birds hidden high in the leaves",
        "Whistling and chattering all around, but the birds stay hidden in the leaves.",
        g(
            tree(80, 286, 150)
            + tree(240, 286, 180)
            + tree(400, 286, 150)
            + "".join(
                path(f"M{x} {y} q6 -6 12 0 M{x + 4} {y - 14} q6 -6 12 0", stroke=BROWN, sw=2)
                for x, y in ((60, 110), (220, 70), (290, 100), (380, 120))
            )
            + text(150, 60, "♪", 26, BROWN)
            + text(340, 50, "♪", 22, BROWN)
            + text(200, 150, "♫", 22, BROWN)
        ),
    )

    svg(
        "forest_trees",
        "Tall trees with big green fruit",
        "Tall smooth trunks, broad shiny leaves, big green fruit hanging high up.",
        g(
            "".join(
                path(f"M{x} 286 V90", stroke="#8a7a5a", sw=16)
                + ellipse(x, 80, 60, 40, LEAF, LEAFLINE, 2)
                + circle(x - 16, 106, 11, "#9ab86a")
                + circle(x + 18, 110, 11, "#9ab86a")
                for x in (100, 260, 400)
            )
        ),
    )

    svg(
        "spring_water",
        "The spring",
        "Cold, sweet water, drunk from cupped hands.",
        g(
            sand(190)
            + path("M140 230 C140 196 340 196 340 230 C340 262 140 262 140 230 Z", SEA, SEALINE, 2)
            + path("M200 228 q15 -6 30 0 M250 236 q15 -6 30 0", stroke="#ffffff", sw=2)
            + path("M180 130 q20 30 40 34 q20 -4 40 -34", "#e2b98f", INK, 2.5)
            + path("M198 150 q22 12 44 0", SEA, SEALINE, 1.5)
            + "".join(ellipse(x, 220, 14, 9, "#9a9a9a") for x in (130, 350))
            + path(
                "M240 150 v30 M232 170 v20 M248 168 v22",
                stroke=SEALINE,
                sw=2,
                extra='stroke-dasharray="3 5"',
            )
        ),
    )

    svg(
        "spring_shoots",
        "Green shoots in straight rows",
        "Thin green shoots planted in straight rows like a garden; one pulled up shows a small white bulb.",
        g(
            sand(170)
            + "".join(
                path(
                    f"M{40 + i * 36} {200 + r * 30} q-4 -26 -10 -34 M{40 + i * 36} {200 + r * 30} q4 -26 8 -36",
                    stroke=LEAF,
                    sw=3,
                )
                for i in range(9)
                for r in range(3)
            )
            + path("M380 150 q4 -30 -6 -50 M380 150 q6 -30 14 -46", stroke=LEAF, sw=3)
            + ellipse(380, 160, 14, 12, "#fbf4e0")
            + path("M372 172 l-4 10 M380 172 v12 M388 172 l4 10", sw=1.5)
            + path("M386 130 q30 -10 40 6", stroke=SKIN, sw=8)
        ),
    )

    svg(
        "hilltop_smoke",
        "Smoke from a clearing",
        "Thin smoke rising from a clearing south of the forest, and the roofs of huts.",
        g(
            "".join(
                ellipse(x, 210 + (i % 2) * 10, 50, 32, LEAF, LEAFLINE, 2)
                for i, x in enumerate(range(40, 470, 60))
            )
            + hut(180, 200, 60)
            + hut(250, 196, 54)
            + path(
                "M220 150 q-12 -30 4 -60 q14 -30 -2 -60 M270 146 q12 -26 -2 -54", stroke=GREY, sw=3
            )
            + way(430, 44, "S", 0, 28)
        ),
    )

    svg(
        "hilltop_ocean",
        "Open ocean all round",
        "Empty ocean to the horizon, the pale green lagoon inside the reef, and the ship very small in it.",
        g(
            sea(60, 286, 3)
            + path("M120 286 C120 200 360 200 360 286 Z", "#b8dcc0", SEALINE, 2)
            + path(
                "M100 286 C100 186 380 186 380 286",
                stroke="#ffffff",
                sw=4,
                extra='stroke-dasharray="6 6"',
            )
            + ship(240, 262, 0.18)
        ),
    )

    svg(
        "hilltop_reef",
        "White surf down the west side",
        "A long line of white surf where waves break on the reef, thick forest between it and you.",
        g(
            sea(14, 286, 2)
            + path("M200 14 C190 100 200 200 190 286 H466 V14 Z", "#6f8f5f", LEAFLINE, 2)
            + "".join(
                ellipse(260 + (i % 4) * 56, 40 + (i // 4) * 50, 30, 20, "#7fa06a", LEAFLINE, 1.5)
                for i in range(20)
            )
            + path(
                "M150 20 q-10 20 0 40 q10 20 0 40 q-10 20 0 40 q10 20 0 40 q-10 20 0 40 q10 20 0 40 q-10 20 0 26",
                stroke="#ffffff",
                sw=8,
            )
            + way(60, 50, "W", -30, 0)
        ),
    )

    svg(
        "hilltop_coastline",
        "The island's coastline from above",
        "The coastline as the look text gives it: round in the east with the lagoon, a long reef down the west side, a little hooked cove in the south.",
        g(sea(14, 286, 2) + island_shape(250, 150, 1.55)),
    )

    svg(
        "cove_rocks",
        "Two arms of dark rock",
        "Two long arms of dark rock almost closing the cove off; calm water inside.",
        g(
            sea(14, 230, 2)
            + rect(14, 230, 452, 56, SAND, BROWN, 0)
            + path("M14 60 C120 70 180 110 200 160 C170 130 100 110 14 110 Z", "#4a4038", INK, 2.5)
            + path(
                "M466 60 C360 70 300 110 280 160 C310 130 380 110 466 110 Z", "#4a4038", INK, 2.5
            )
            + path("M100 30 q10 -6 20 0 M330 34 q10 -6 20 0", stroke="#ffffff", sw=3)
            + path("M180 200 q15 -4 30 0 M260 196 q15 -4 30 0", stroke="#c4dcdc", sw=2)
        ),
    )

    svg(
        "cove_slipway",
        "The old slipway",
        "A row of smooth logs laid down to the water, old wood chips half buried in the sand.",
        g(
            sea(14, 110, 1)
            + sand(110)
            + "".join(
                rect(120 + i * 4, 120 + i * 30, 240 - i * 8, 16, WOOD, INK, 2, 8) for i in range(5)
            )
            + "".join(
                path(f"M{x} {y} l8 -3 l-2 6 Z", "#d8b880", BROWN, 1)
                for x, y in (
                    (60, 160),
                    (90, 230),
                    (400, 190),
                    (420, 250),
                    (70, 270),
                    (380, 140),
                    (100, 200),
                    (430, 214),
                )
            )
        ),
    )

    # --- The Good Hope --------------------------------------------------------------------

    svg(
        "deck_chart_house",
        "The chart house",
        "A little wooden hut on deck: inside, the chart table, the chronometer, the sextant in its box, the chart, and two books on a shelf.",
        g(
            planks(250)
            + rect(90, 60, 300, 190, WOOD, INK, 3)
            + rect(110, 80, 260, 150, "#e6d3a8", BROWN, 2)
            + rect(120, 190, 240, 14, BROWN)
            + rect(130, 166, 70, 24, "#fbf4e0", BROWN, 1.5)
            + circle(250, 176, 14, GOLD)
            + rect(290, 172, 50, 18, BROWN)
            + rect(150, 100, 180, 8, BROWN)
            + rect(170, 72, 18, 28, "#5b6f3a")
            + rect(192, 74, 18, 26, "#6b3b2a")
        ),
    )

    svg(
        "deck_ship",
        "Standing on the Good Hope",
        "You can't see her whole: her deck under your feet, and timbers that creak like a voice.",
        g(
            planks(140)
            + path("M14 140 L120 60 H360 L466 140", "#d8c08e", BROWN, 2.5)
            + path("M120 60 H360", stroke=WOOD, sw=10)
            + path("M240 140 V30", stroke=WOOD, sw=12)
            + path("M100 200 q10 -8 0 -16 M380 220 q-10 -8 0 -16", stroke=BROWN, sw=2.5)
        ),
    )

    svg(
        "deck_masts",
        "Masts, rigging and sails",
        "Tall pine masts, a web of ropes, canvas sails, and the lookout's perch at the masthead.",
        g(
            planks(256)
            + path("M160 256 V30 M330 256 V50", stroke=WOOD, sw=10)
            + path(
                "M160 40 L40 256 M160 40 L280 256 M330 60 L220 256 M330 60 L450 256",
                stroke=BROWN,
                sw=1.5,
            )
            + path(
                "M110 70 Q160 100 110 170 H210 Q160 100 210 70 Z M290 90 Q330 120 290 190 H370 Q330 120 370 90 Z",
                "#fbf4e0",
                INK,
                2,
            )
            + rect(144, 26, 32, 12, BROWN)
            + text(160, 22, "masthead", 11, BROWN, weight="normal")
        ),
    )

    svg(
        "deck_wheel",
        "The ship's wheel",
        "A big wooden wheel with worn spokes, a sailor at it day and night.",
        g(
            planks(250)
            + rect(224, 160, 32, 90, WOOD)
            + circle(240, 140, 70, "none", WOOD, 10)
            + circle(240, 140, 14, BROWN)
            + "".join(
                path(f"M240 140 l{90 * c} {90 * s}", stroke=WOOD, sw=6)
                for c, s in (
                    (1, 0),
                    (0.71, 0.71),
                    (0, 1),
                    (-0.71, 0.71),
                    (-1, 0),
                    (-0.71, -0.71),
                    (0, -1),
                    (0.71, -0.71),
                )
            )
            + person(360, 250, "#3f5a73", 1.0)
            + path("M340 170 L300 150", stroke=SKIN, sw=6)
        ),
    )

    svg(
        "deck_crew",
        "The crew",
        "Weather-beaten sailors: Mr. Rowe with his log, Ned Tarrant the bosun, and young Kit.",
        g(
            planks(250)
            + person(140, 250, "#2f4a6b", 1.15)
            + rect(160, 180, 20, 28, BROWN)
            + person(260, 250, RED, 1.3)
            + person(370, 250, "#f8f4ea", 0.85)
            + text(400, 140, "?", 30, BROWN)
        ),
    )

    svg(
        "deck_timbers",
        "Oak planks of the deck",
        "Thick oak planks, scrubbed pale with sand and seawater; now and then they creak.",
        g(
            "".join(
                rect(14, 20 + i * 38, 452, 38, "#d8c08e" if i % 2 else "#cdb27e", BROWN, 2)
                + circle(60 + (i * 97) % 380, 39 + i * 38, 3, INK, INK, 1)
                for i in range(7)
            )
            + path("M200 140 q12 -10 0 -20 M216 146 q20 -16 0 -32", stroke=BROWN, sw=2.5)
        ),
    )

    svg(
        "port_barrels",
        "Barrels going aboard",
        "Salt beef, biscuit and water rolled up the plank and down into the hold, one barrel at a time.",
        g(
            planks(220)
            + path("M40 286 L200 200", stroke=WOOD, sw=14)
            + barrel(110, 196, 44, 52)
            + rect(260, 200, 140, 24, "#2b2b2b", INK, 2)
            + barrel(300, 140, 44, 52)
            + person(220, 220, "#3f5a73", 0.9)
        ),
    )

    svg(
        "port_harbour",
        "The harbour mouth to the west",
        "The harbour mouth opens to the west; beyond it, the ocean.",
        g(
            sea(120, 286, 3)
            + path("M14 120 H110 L130 150 H14 Z M466 120 H330 L310 150 H466 Z", "#c9b48a", BROWN, 2)
            + way(240, 70, "WEST", -60, 0)
        ),
    )

    svg(
        "charted_horizon",
        "An empty horizon",
        "Water meeting sky in a clean, empty line all round.",
        g(sea(150, 286, 4) + path("M14 150 H466", stroke=INK, sw=2.5)),
    )

    svg(
        "charted_sky",
        "Terns flying west at sunset",
        "Sunset at the charted position: white terns in long lines low over the water, all flying the same way, west (where the sun sets, to the left).",
        g(
            sea(180, 286, 3)
            + circle(80, 180, 40, "#f0b050", RED, 2)
            + rect(14, 181, 120, 50, SEA, SEA, 0)
            + path("M14 180 H466", stroke=SEALINE, sw=2)
            + "".join(
                tern(x, y, 1.2)
                for x, y in (
                    (200, 150),
                    (240, 156),
                    (280, 162),
                    (320, 168),
                    (260, 120),
                    (300, 126),
                    (340, 132),
                    (380, 138),
                )
            )
            + way(80, 50, "WEST", -60, 0)
        ),
    )

    svg(
        "open_sea",
        "Open sea all round",
        "Grey-blue waves in long rows, the wind in the rigging, an empty horizon (north, south or east of the chart's position).",
        g(
            rect(14, 120, 452, 166, "#9fb3bf", SEALINE, 0)
            + path("M14 120 H466", stroke=INK, sw=2)
            + "".join(
                path(
                    f"M{20 + (r % 2) * 30} {150 + r * 26} "
                    + " ".join("q15 -10 30 0 t30 0" for _ in range(7)),
                    stroke="#5f7380",
                    sw=2.5,
                )
                for r in range(5)
            )
            + path("M380 40 V120 M380 50 L440 110", stroke=BROWN, sw=1.5)
            + path("M300 70 q20 -6 40 0 M310 84 q16 -4 30 0", stroke=SEALINE, sw=2)
        ),
    )

    svg(
        "anchorage_island",
        "The island",
        "Green hills under a blue sky, a white beach, palm trees leaning over the water.",
        g(
            rect(14, 14, 452, 140, "#d8e6ea", SEALINE, 0)
            + sea(200, 286, 2)
            + path("M40 200 C80 110 160 80 240 100 C320 70 400 120 440 200 Z", LEAF, LEAFLINE, 2.5)
            + path(
                "M40 200 C120 186 360 186 440 200 C360 214 120 214 40 200 Z", "#ffffff", BROWN, 1.5
            )
            + palm(110, 196, 70, 18)
            + palm(360, 196, 64, -16)
        ),
    )

    svg(
        "under_way_sea",
        "Under way",
        "The bow rising and falling, salt spray, waves running on to the horizon.",
        g(
            sea(110, 286, 4)
            + path("M140 286 L240 170 L340 286 Z", WOOD, INK, 3)
            + path("M240 170 V286", stroke=BROWN, sw=2)
            + "".join(
                circle(x, y, 4, "#ffffff", SEALINE, 1)
                for x, y in (
                    (200, 160),
                    (220, 146),
                    (260, 150),
                    (280, 162),
                    (240, 136),
                    (210, 176),
                    (272, 178),
                )
            )
        ),
    )

    svg(
        "ship_from_shore",
        "The Good Hope from the shore",
        "A sturdy old ship, broad in the beam, hull black with tar, her name in white across the stern.",
        g(sea(150, 240, 2) + sand(240) + ship(240, 220, 1.0, True, "GOOD HOPE")),
    )


def draw_rooms() -> None:
    """The places, the Deck, and the view from the Deck at each position."""
    svg(
        "place_limbo",
        "Phantom Island",
        "The title page: 1790, the Halcyon lost, and a brass compass engraved HALCYON.",
        g(
            sea(170, 286, 3)
            + rect(14, 14, 452, 156, "#efe0b8", BROWN, 0)
            + ship(140, 196, 0.6, False)
            + text(300, 80, "PHANTOM", 38, BROWN)
            + text(300, 122, "ISLAND", 38, BROWN)
            + text(300, 150, "1790", 16, BROWN, weight="normal")
            + circle(390, 226, 34, GOLD)
            + circle(390, 226, 24, PAPER, BROWN, 1.5)
            + path("M390 206 L396 226 L390 246 L384 226 Z", RED, INK, 1.5)
            + text(390, 274, "HALCYON", 11, BROWN)
        ),
    )

    svg(
        "place_office",
        "The Society Office",
        "A quiet room lined with bookshelves and rolled-up charts; a large desk by the window over the harbour.",
        g(
            rect(14, 14, 452, 210, "#e8d6ae", BROWN, 0)
            + planks(224)
            + rect(30, 34, 120, 190, "#e6d3a8", BROWN, 2)
            + path("M30 96 H150 M30 160 H150", stroke=BROWN, sw=3)
            + "".join(
                rect(36 + i * 14, 44 + (i % 3) * 3, 12, 50 - (i % 3) * 3, c, INK, 1)
                for i, c in enumerate(
                    [RED, "#5b4632", "#3f5a73", WOOD, RED, "#6f8f5f", "#5b4632", WOOD]
                )
            )
            + "".join(
                rect(36 + i * 14, 108 + (i % 2) * 4, 12, 50 - (i % 2) * 4, c, INK, 1)
                for i, c in enumerate(
                    [WOOD, "#3f5a73", RED, "#5b4632", WOOD, RED, "#6f8f5f", "#3f5a73"]
                )
            )
            + "".join(rect(40, 168 + i * 13, 100, 11, "#fbf4e0", BROWN, 1.5, 5) for i in range(4))
            + rect(240, 40, 190, 120, SEA, BROWN, 8)
            + path("M335 40 V160 M240 100 H430", stroke=BROWN, sw=5)
            + ship(395, 150, 0.3)
            + rect(200, 176, 250, 16, WOOD, INK, 2.5)
            + rect(214, 192, 12, 60, BROWN)
            + rect(424, 192, 12, 60, BROWN)
            + rect(250, 166, 40, 10, "#fbf4e0", BROWN, 1.5)
            + rect(380, 162, 14, 14, INK, INK, 1, 3)
        ),
    )

    svg(
        "place_market",
        "The Market",
        "Stalls crowding the square, traders calling out, and a small crowd at one stall.",
        g(
            sand(220)
            + awning_stall(30, 220, 110, RED)
            + awning_stall(170, 230, 130, TAN)
            + awning_stall(330, 220, 110, "#6f8f9f")
            + person(200, 270, "#3f5a73", 0.7)
            + person(240, 274, "#6f8f5f", 0.75)
            + person(280, 270, RED, 0.7)
            + circle(235, 196, 7, GOLD)
            + text(90, 60, "Fresh today!", 13, BROWN, weight="normal")
            + text(390, 60, "Cheapest!", 13, BROWN, weight="normal")
        ),
    )

    svg(
        "place_quay",
        "The Quay",
        "A long stone quay: barrels and coils of rope, gulls, an old sailor on a coil, and the Good Hope moored at the end.",
        g(
            sea(110, 286, 3)
            + path("M14 286 L14 200 L330 160 L330 186 L40 286 Z", "#c9b48a", BROWN, 2)
            + ship(400, 200, 0.55, True)
            + barrel(80, 182, 30, 38)
            + barrel(116, 176, 30, 38)
            + coil(200, 196, 34)
            + path(
                "M184 184 C184 166 192 160 200 160 C208 160 216 166 216 184 Z", "#3f5a73", INK, 2
            )
            + circle(200, 152, 9, "#e2b98f")
            + gull(260, 90)
            + gull(300, 70, 0.8)
            + gull(150, 110, 0.7)
        ),
    )

    svg(
        "place_beach",
        "The Lagoon Beach",
        "A curve of white sand around a calm green lagoon, leaning palms, the forest and its path to the northwest, goats above the beach, the ship at anchor.",
        g(
            rect(14, 14, 452, 130, "#d8e6ea", SEALINE, 0)
            + "".join(ellipse(x, 120, 50, 36, LEAF, LEAFLINE, 2) for x in range(30, 300, 60))
            + rect(14, 140, 452, 146, "#b8dcc0", SEALINE, 0)
            + path("M14 200 C120 150 330 150 466 190 V286 H14 Z", "#fbf4e0", BROWN, 2)
            + ship(380, 176, 0.3)
            + palm(90, 230, 120, 40)
            + palm(180, 220, 110, 30)
            + goat(260, 150, 0.45)
            + goat(300, 146, 0.45, flip=True)
            + path("M60 150 L110 120", stroke="#d8c08e", sw=6)
        ),
    )

    svg(
        "place_village",
        "The Village",
        "Huts with roofs of woven leaves around beaten earth, smoke from a cooking fire, and one big hut on dark, heavy beams.",
        g(
            sand(200)
            + hut(30, 220, 100)
            + hut(340, 220, 110)
            + path("M150 130 L250 80 L350 130 Z", TAN, BROWN, 2.5)
            + rect(160, 128, 180, 12, "#3b2a14")
            + "".join(rect(x, 140, 14, 70, "#3b2a14") for x in (168, 243, 318))
            + "".join(
                ellipse(240 + 30 * c, 248 + 10 * s, 7, 5, "#9a9a9a")
                for c, s in ((-1, 0), (0, 1), (1, 0), (0, -1))
            )
            + path("M236 246 q-6 -16 4 -28 q2 14 8 16 q4 -10 0 -18 q12 12 2 30 Z", GOLD, RED, 2)
            + path("M240 210 q-8 -20 4 -40 q10 -20 0 -40", stroke=GREY, sw=2.5)
        ),
    )

    svg(
        "place_reef",
        "The Western Reef",
        "A long coral reef, waves breaking white on its outer edge, clear shallow water, and huge dark shapes standing up like bones.",
        g(
            rect(14, 14, 452, 70, "#d8e6ea", SEALINE, 0)
            + rect(14, 84, 452, 202, "#c4dcdc", SEALINE, 0)
            + path(
                "M14 96 q30 -14 60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t60 0 t32 0",
                "#ffffff",
                SEALINE,
                2,
            )
            + "".join(
                path(f"M{x} 200 C{x - 4} 160 {x + 8} 130 {x + 22} 118", stroke="#2b2b2b", sw=8)
                for x in (180, 220, 260, 300)
            )
            + "".join(
                path(f"M{x} 270 v-{h} M{x} {270 - h * 0.5} l-{h * 0.3} -{h * 0.3}", stroke=c, sw=5)
                for x, h, c in (
                    (60, 40, "#e48aa0"),
                    (110, 30, "#e3b93a"),
                    (380, 44, "#9a6ab0"),
                    (430, 34, "#e48aa0"),
                )
            )
            + rect(14, 250, 452, 36, "#e6d3a8", BROWN, 0)
        ),
    )

    svg(
        "place_forest",
        "The Forest Path",
        "A narrow path climbing between tall trees with broad leaves; birds calling somewhere above.",
        g(
            tree(70, 286, 190)
            + tree(180, 270, 170)
            + tree(310, 270, 170)
            + tree(420, 286, 190)
            + path(
                "M200 286 C220 240 250 220 240 180 C236 160 246 150 250 140",
                stroke="#d8c08e",
                sw=22,
            )
            + text(150, 50, "♪", 20, BROWN)
            + text(350, 40, "♫", 20, BROWN)
        ),
    )

    svg(
        "place_spring",
        "The Spring",
        "Clear water bubbling between mossy rocks, a little stream, and green shoots in neat rows beside it.",
        g(
            rect(14, 14, 452, 272, "#dfe8c8", LEAFLINE, 0)
            + "".join(
                ellipse(x, y, 34, 22, "#8a9a7a", INK, 2)
                for x, y in ((150, 120), (220, 108), (290, 122))
            )
            + path("M220 130 C230 170 200 200 230 240 C250 270 240 286 250 286", stroke=SEA, sw=18)
            + path("M206 136 q14 -14 28 0", SEA, SEALINE, 2)
            + "".join(
                path(
                    f"M{300 + i * 26} {200 + r * 30} q-3 -18 -7 -24 M{300 + i * 26} {200 + r * 30} q3 -18 6 -26",
                    stroke=LEAF,
                    sw=3,
                )
                for i in range(6)
                for r in range(3)
            )
        ),
    )

    svg(
        "place_hilltop",
        "The Hilltop",
        "The whole island below: the lagoon in the east, the reef in the west, open ocean all round, smoke rising south of the forest.",
        g(
            sea(14, 286, 2)
            + island_shape(240, 150, 1.25)
            + path("M232 150 q-6 -14 2 -26 q6 -12 0 -24", stroke=GREY, sw=2.5)
            + path("M14 286 C120 240 360 240 466 286 Z", "#8a9a6a", LEAFLINE, 2)
        ),
    )

    svg(
        "place_cove",
        "The Boat Cove",
        "A small sheltered cove behind two arms of rock; sand sloping down to the water past an old slipway of logs.",
        g(
            sea(14, 180, 2)
            + path("M14 40 C110 50 170 100 190 150 C160 120 90 100 14 100 Z", "#4a4038", INK, 2.5)
            + path(
                "M466 40 C370 50 310 100 290 150 C320 120 390 100 466 100 Z", "#4a4038", INK, 2.5
            )
            + sand(180)
            + "".join(
                rect(180 + i * 3, 196 + i * 18, 120 - i * 6, 10, WOOD, INK, 2, 5) for i in range(4)
            )
        ),
    )

    svg(
        "place_deck",
        "The Deck of the Good Hope",
        "Masts and rigging overhead, the wheel at the stern, the little chart house beside it, and the crew at the ropes.",
        g(
            planks(230)
            + path("M150 230 V24 M320 230 V40", stroke=WOOD, sw=10)
            + path(
                "M150 30 L40 230 M150 30 L260 230 M320 46 L220 230 M320 46 L440 230",
                stroke=BROWN,
                sw=1.5,
            )
            + path("M110 60 Q150 90 110 160 H190 Q150 90 190 60 Z", "#fbf4e0", INK, 2)
            + rect(350, 160, 90, 70, WOOD, INK, 2.5)
            + rect(380, 190, 22, 40, "#5b4632", BROWN, 1.5)
            + circle(290, 190, 26, "none", WOOD, 6)
            + person(70, 230, "#2f4a6b", 0.7)
            + person(240, 230, RED, 0.75)
        ),
    )

    svg(
        "view_port",
        "In port, from the Deck",
        "Moored at the quay: sailors carrying the last barrels aboard, the harbour opening to the west.",
        g(
            sea(120, 236, 2)
            + path("M14 120 H200 L220 200 H14 Z", "#c9b48a", BROWN, 2)
            + barrel(60, 140, 30, 38)
            + barrel(110, 146, 30, 38)
            + person(170, 196, "#3f5a73", 0.6)
            + way(380, 70, "WEST", -60, 0)
            + rail()
        ),
    )

    svg(
        "view_charted",
        "Open sea at the chart's position",
        "Open sea in every direction, no island, seabirds wheeling high in the evening sky.",
        g(
            rect(14, 14, 452, 150, "#f0d8b0", BROWN, 0)
            + sea(164, 236, 2)
            + path("M14 164 H466", stroke=INK, sw=2)
            + "".join(
                gull(x, y, 0.7) for x, y in ((180, 60), (220, 44), (260, 70), (300, 52), (240, 90))
            )
            + rail()
        ),
    )

    svg(
        "view_open_sea",
        "Open sea",
        "Open sea in every direction and no island anywhere; the wind humming in the rigging.",
        g(
            rect(14, 14, 452, 140, "#d8e6ea", SEALINE, 0)
            + rect(14, 154, 452, 82, "#9fb3bf", SEALINE, 0)
            + path("M14 154 H466", stroke=INK, sw=2)
            + "".join(
                path(
                    f"M{30 + (r % 2) * 30} {176 + r * 20} "
                    + " ".join("q15 -8 30 0 t30 0" for _ in range(7)),
                    stroke="#5f7380",
                    sw=2,
                )
                for r in range(3)
            )
            + path("M240 14 V236 M240 30 L120 236 M240 30 L360 236", stroke=BROWN, sw=1.5)
            + rail()
        ),
    )

    svg(
        "view_anchorage",
        "At anchor off the island",
        "At anchor in a calm lagoon; a green island ahead with a white beach and palm trees.",
        g(
            rect(14, 14, 452, 120, "#d8e6ea", SEALINE, 0)
            + rect(14, 134, 452, 102, "#b8dcc0", SEALINE, 0)
            + path("M50 170 C90 90 170 70 250 90 C330 60 410 110 440 170 Z", LEAF, LEAFLINE, 2.5)
            + path(
                "M50 170 C120 158 370 158 440 170 C370 182 120 182 50 170 Z", "#ffffff", BROWN, 1.5
            )
            + palm(120, 168, 56, 14)
            + palm(350, 168, 52, -12)
            + rail()
        ),
    )

    svg(
        "view_under_way",
        "Under way",
        "Leaning a little in the wind, spray over the bow, the crew busy at the ropes, the sea all round to the horizon.",
        g(
            '<g transform="rotate(-4 240 150)">'
            + rect(-20, 110, 520, 200, SEA, SEALINE, 0)
            + "".join(
                path(f"M{x} {y} q15 -7 30 0 t30 0", stroke=SEALINE, sw=2)
                for x, y in ((40, 140), (300, 150), (120, 190), (360, 200))
            )
            + "</g>"
            + path("M160 236 L240 150 L320 236", WOOD, INK, 3)
            + "".join(
                circle(x, y, 4, "#ffffff", SEALINE, 1)
                for x, y in ((210, 140), (230, 126), (256, 132), (276, 146))
            )
            + path("M60 236 L120 60 M410 236 L360 60", stroke=BROWN, sw=1.5)
            + person(90, 236, "#3f5a73", 0.6)
            + person(390, 236, RED, 0.6)
            + rail()
        ),
    )


def main() -> None:
    global OUT
    if len(sys.argv) > 1:
        OUT = Path(sys.argv[1])
    draw_details()
    draw_rooms()
    print(f"{len(WRITTEN)} pictures written to {OUT}")


if __name__ == "__main__":
    main()
