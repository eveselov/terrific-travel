"""Turning the game's raw output into the text a player reads.

Colours matter in a text game: they tell the player what to notice. The player agent
can't see colours, so coloured text is wrapped in tags named after the colour, for
example `<white>compass</white>`. It is told what each tag looks like on screen, never
what the game means by it: working that out is part of playing.
"""

import re

# Control sequences: CSI (colours, cursor moves...) and OSC (window titles...).
CSI: re.Pattern[str] = re.compile(r"\x1b\[([0-9;?]*)([@-~])")
OSC: re.Pattern[str] = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")

# The 8 basic colours, by their number in SGR codes 30-37 and 90-97.
BASIC: tuple[str, ...] = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
# Their usual RGB, normal and bright, for matching 256-colour and true-colour codes.
PALETTE: dict[str, tuple[int, int, int]] = {
    "grey": (128, 128, 128),
    "red": (205, 0, 0),
    "green": (0, 205, 0),
    "yellow": (205, 205, 0),
    "blue": (0, 0, 238),
    "magenta": (205, 0, 205),
    "cyan": (0, 205, 205),
    "white": (255, 255, 255),
    "silver": (192, 192, 192),
}


def colour_name(red: int, green: int, blue: int) -> str:
    """The nearest named colour to an RGB value."""

    def distance(name: str) -> int:
        r, g, b = PALETTE[name]
        return (r - red) ** 2 + (g - green) ** 2 + (b - blue) ** 2

    return min(PALETTE, key=distance)


def xterm_rgb(number: int) -> tuple[int, int, int]:
    """The RGB of one of the 256 xterm colours."""
    if number < 16:
        bright: bool = number >= 8
        base: int = number % 8
        level: int = 255 if bright else 205
        rgb: tuple[int, int, int] = (
            level if base & 1 else 0,
            level if base & 2 else 0,
            level if base & 4 else 0,
        )
        if number == 7:
            return (192, 192, 192)
        if number == 8:
            return (128, 128, 128)
        return rgb
    if number < 232:
        cube: int = number - 16
        steps: tuple[int, ...] = (0, 95, 135, 175, 215, 255)
        return (steps[cube // 36], steps[(cube // 6) % 6], steps[cube % 6])
    grey: int = 8 + (number - 232) * 10
    return (grey, grey, grey)


class ColourState:
    """The foreground colour as SGR codes change it."""

    def __init__(self) -> None:
        self.bold: bool = False
        self.basic: int | None = None  # 0-7 from codes 30-37
        self.bright: bool = False  # codes 90-97
        self.rgb: tuple[int, int, int] | None = None  # 256-colour or true colour

    def reset(self) -> None:
        self.bold, self.basic, self.bright, self.rgb = False, None, False, None

    def apply(self, params: str) -> None:
        codes: list[int] = [int(part) if part.isdigit() else 0 for part in params.split(";")]
        index: int = 0
        while index < len(codes):
            code: int = codes[index]
            if code == 0:
                self.reset()
            elif code == 1:
                self.bold = True
            elif code == 22:
                self.bold = False
            elif 30 <= code <= 37 or 90 <= code <= 97:
                self.basic, self.bright, self.rgb = code % 10, code >= 90, None
            elif code == 39:
                self.basic, self.bright, self.rgb = None, False, None
            elif code in (38, 48) and index + 1 < len(codes):
                mode: int = codes[index + 1]
                if mode == 5 and index + 2 < len(codes):
                    if code == 38:
                        self.basic, self.rgb = None, xterm_rgb(codes[index + 2])
                    index += 2
                elif mode == 2 and index + 4 < len(codes):
                    if code == 38:
                        self.basic = None
                        self.rgb = (codes[index + 2], codes[index + 3], codes[index + 4])
                    index += 4
            index += 1

    def name(self) -> str | None:
        """The colour's name, or None for ordinary text."""
        if self.rgb is not None:
            named: str = colour_name(*self.rgb)
            return None if named == "silver" else named
        if self.basic is None:
            return "white" if self.bold else None
        lit: bool = self.bold or self.bright
        if self.basic == 7:  # plain white is ordinary text; bright white stands out
            return "white" if lit else None
        if self.basic == 0:
            return "grey" if lit else None
        return BASIC[self.basic]


def to_screen(raw: str) -> str:
    """The game's output as plain text, coloured parts in tags, lines tidied."""
    raw = OSC.sub("", raw).replace("\r\n", "\n").replace("\r", "\n")
    state: ColourState = ColourState()
    out: list[str] = []
    current: str | None = None
    position: int = 0
    for match in CSI.finditer(raw):
        out.append(raw[position : match.start()])
        position = match.end()
        if match.group(2) != "m":
            continue  # cursor moves and the like: nothing to read
        state.apply(match.group(1))
        colour: str | None = state.name()
        if colour != current:
            if current is not None:
                out.append(f"</{current}>")
            if colour is not None:
                out.append(f"<{colour}>")
            current = colour
    out.append(raw[position:])
    if current is not None:
        out.append(f"</{current}>")
    text: str = "".join(out)
    text = re.sub(r"<(\w+)>(\s*)</\1>", r"\2", text)  # colour on spaces only
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text)  # bell, stray escapes...
    lines: list[str] = [line.rstrip() for line in text.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
