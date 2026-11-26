"""The console, kept: everything a run prints also goes into a text file beside its report.

`runs/<game>-<persona>-<time>.txt` has the same name as the report (`.md`). A new
playthrough (`--reset`, or `--manual`) starts the file; a run that carries a playthrough on
appends to it, so one file holds every sitting, as the report does. The screen still shows
everything.
"""

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO


class Tee:
    """A text stream that writes to the screen and to a file."""

    def __init__(self, screen: TextIO, file: TextIO) -> None:
        self.screen: TextIO = screen
        self.file: TextIO = file

    def write(self, text: str) -> int:
        self.screen.write(text)
        self.file.write(text)
        return len(text)

    def flush(self) -> None:
        self.screen.flush()
        self.file.flush()

    def isatty(self) -> bool:
        return self.screen.isatty()

    @property
    def encoding(self) -> str:
        return self.screen.encoding


@contextmanager
def console_log(path: Path, append: bool) -> Iterator[None]:
    """While the body runs, copy what is printed (and errors) into `path`."""
    path.parent.mkdir(exist_ok=True)
    screen_out: TextIO = sys.stdout
    screen_err: TextIO = sys.stderr
    with open(path, "a" if append else "w", encoding="utf-8") as file:
        if append and path.stat().st_size:
            file.write("\n")  # a blank line between sittings, as on the screen
        sys.stdout = Tee(screen_out, file)
        sys.stderr = Tee(screen_err, file)
        try:
            yield
        finally:
            sys.stdout = screen_out
            sys.stderr = screen_err
