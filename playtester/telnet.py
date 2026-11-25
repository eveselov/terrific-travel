"""A small telnet client: enough to log in to an Evennia game and play it as text.

Python 3.13 no longer has `telnetlib`, and a player needs very little of telnet: the
client refuses every option the server offers (compression, window size, MSDP...),
so the server falls back to plain text with ANSI colours. Colours are kept: the game
uses them for meaning (white words to follow up, yellow clues), and a kid sees them.
"""

import codecs
import socket
import time

IAC: int = 255  # "interpret as command": starts every telnet command
DONT: int = 254
DO: int = 253
WONT: int = 252
WILL: int = 251
SB: int = 250  # subnegotiation begins ...
SE: int = 240  # ... and ends


class TelnetParser:
    """Splits what the server sends into text and the replies telnet needs.

    Feed it bytes as they arrive (a command can be split between two reads); it returns
    the text and keeps the answers to send back in `replies`.
    """

    def __init__(self) -> None:
        self.replies: bytearray = bytearray()
        self._state: str = "text"  # text, iac, option, sub, sub_iac
        self._verb: int = 0
        self._decoder: codecs.IncrementalDecoder = codecs.getincrementaldecoder("utf-8")(
            errors="replace"
        )

    def feed(self, data: bytes) -> str:
        """The text in `data`, telnet commands taken out and answered."""
        text: bytearray = bytearray()
        for byte in data:
            if self._state == "text":
                if byte == IAC:
                    self._state = "iac"
                else:
                    text.append(byte)
            elif self._state == "iac":
                if byte == IAC:  # an escaped 255 is a real byte of text
                    text.append(byte)
                    self._state = "text"
                elif byte in (DO, DONT, WILL, WONT):
                    self._verb = byte
                    self._state = "option"
                elif byte == SB:
                    self._state = "sub"
                else:  # GA, NOP, EOR...: nothing to do
                    self._state = "text"
            elif self._state == "option":
                self._answer(self._verb, byte)
                self._state = "text"
            elif self._state == "sub":
                if byte == IAC:
                    self._state = "sub_iac"
            elif self._state == "sub_iac":
                self._state = "text" if byte == SE else "sub"
        return self._decoder.decode(bytes(text))

    def _answer(self, verb: int, option: int) -> None:
        """Refuse everything: "I won't" to DO, "please don't" to WILL."""
        if verb == DO:
            self.replies += bytes((IAC, WONT, option))
        elif verb == WILL:
            self.replies += bytes((IAC, DONT, option))

    def take_replies(self) -> bytes:
        """The replies gathered so far, which the caller now sends."""
        replies: bytes = bytes(self.replies)
        self.replies.clear()
        return replies


class TelnetClient:
    """One connection to the game, read a screenful at a time."""

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self._socket: socket.socket | None = None
        self._parser: TelnetParser = TelnetParser()
        self.closed: bool = False  # the server ended the connection

    def connect(self) -> None:
        try:
            self._socket = socket.create_connection((self.host, self.port), timeout=10.0)
        except OSError as error:
            raise ConnectionError(
                f"Can't reach the game at {self.host}:{self.port} ({error}). "
                "Is the server running (uv run evennia start, inside the game folder)?"
            ) from error

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def send(self, line: str) -> None:
        """Type one line, as a player presses Enter."""
        self._live().sendall(line.encode("utf-8") + b"\r\n")

    def read(self, quiet: float, first_wait: float = 10.0, longest: float = 60.0) -> str:
        """Everything the game sends until it has been quiet for `quiet` seconds.

        Waits up to `first_wait` seconds for the first text (an answer can be slow), and
        never longer than `longest` in all, so a chatty game can't hold the reader forever.
        """
        sock: socket.socket = self._live()
        chunks: list[str] = []
        started: float = time.monotonic()
        heard: bool = False
        while time.monotonic() - started < longest:
            sock.settimeout(quiet if heard else first_wait)
            try:
                data: bytes = sock.recv(4096)
            except TimeoutError:
                break
            if not data:  # the server closed the connection
                self.closed = True
                break
            heard = True
            chunks.append(self._parser.feed(data))
            replies: bytes = self._parser.take_replies()
            if replies:
                sock.sendall(replies)
        return "".join(chunks)

    def _live(self) -> socket.socket:
        if self._socket is None:
            raise ConnectionError("Not connected to the game.")
        return self._socket
