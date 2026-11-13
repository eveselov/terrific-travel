## Third-party libraries for the web client

Evennia's web client normally loads these libraries from CDNs on the internet. Phantom
Island keeps local copies here, so the web client also works offline (for example on a
ship with no Wi-Fi). They are used by
[templates/webclient/base.html](../../templates/webclient/base.html).

| Folder | Library | Downloaded from |
|---|---|---|
| `jquery-3.2.1/` | jQuery 3.2.1 | code.jquery.com |
| `bootstrap-4.0.0-beta/` | Bootstrap 4.0.0-beta (CSS and JS) | maxcdn.bootstrapcdn.com |
| `popper-1.11.0/` | Popper.js 1.11.0 | cdnjs.cloudflare.com |
| `golden-layout/` | GoldenLayout 1.x ("latest" from golden-layout.com) | golden-layout.com |
| `favico-0.3.10/` | Favico.js 0.3.10 | cdnjs.cloudflare.com |

These are the same versions Evennia 6.1's template asks for. The jQuery, Bootstrap and
Popper files match the integrity hashes in Evennia's template. Don't edit these files.
After an Evennia upgrade, compare Evennia's `webclient/base.html` with ours, in case it
now loads different versions.
