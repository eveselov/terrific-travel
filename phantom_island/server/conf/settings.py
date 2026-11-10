r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
# "Phantom Island" is a working title; the co-designers will choose the final one.
SERVERNAME = "Phantom Island"

# Ports: Evennia's defaults plus 10, so this game can run next to game/ (4000-4006).
TELNET_PORTS = [4010]
WEBSERVER_PORTS = [(4011, 4015)]  # (public web port, internal port)
WEBSOCKET_CLIENT_PORT = 4012
SSL_PORTS = [4013]  # only used if SSL_ENABLED
SSH_PORTS = [4014]  # only used if SSH_ENABLED
AMP_PORT = 4016  # internal Portal <-> Server link


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
