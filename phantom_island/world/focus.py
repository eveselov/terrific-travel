"""
The web client's Focus pane: the current room's picture (later also things being examined).

A place with an `image` in the content files shows that picture. Without one, the pane shows
a placeholder card with the place's name, so every place has something there in stage A1.
The Focus pane only ever repeats what the text already says, so telnet players miss nothing.
"""

from html import escape


def _placeholder_svg(title: str) -> str:
    """A parchment card with the title, standing in for a picture still to be made."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 300" role="img" '
        f'aria-label="{escape(title)}" class="pi-picture">'
        '<rect x="6" y="6" width="468" height="288" rx="14" fill="#f3e6c4" '
        'stroke="#7a4a21" stroke-width="6"/>'
        '<rect x="22" y="22" width="436" height="256" rx="8" fill="none" '
        'stroke="#c9a96e" stroke-width="2" stroke-dasharray="8 6"/>'
        '<text x="240" y="150" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="34" font-weight="bold" fill="#3b2a14">{escape(title)}</text>'
        '<text x="240" y="195" text-anchor="middle" font-family="Georgia, serif" '
        'font-size="18" font-style="italic" fill="#7a4a21">a picture will go here</text>'
        "</svg>"
    )


def render_focus_html(title: str, image_url: str | None) -> str:
    """The Focus pane's content for a place with this title and (optional) picture."""
    if image_url is None:
        picture: str = _placeholder_svg(title)
    else:
        picture = f'<img class="pi-picture" src="{escape(image_url)}" alt="{escape(title)}">'
    return f'<div class="pi-focus"><div class="pi-pane-title">{escape(title)}</div>{picture}</div>'
