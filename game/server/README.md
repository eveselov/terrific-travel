# server/ 

This directory holds files used by and configuring the Evennia server 
itself.

Out of all the subdirectories in the game directory, Evennia does
expect this directory to exist, so you should normally not delete,
rename or change its folder structure.

When running you will find four new files appear in this directory: 

 - `server.pid` and `portal.pid`: These hold the process IDs of the
   Portal and Server, so that they can be managed by the launcher. If
   Evennia is shut down uncleanly (e.g. by a crash or via a kill
   signal), these files might erroneously remain behind. If so Evennia
   will tell you they are "stale" and they can be deleted manually.
 - `server.restart` and `portal.restart`: These hold flags to tell the
   server processes if it should die or start again. You never need to
   modify those files.
 - `evennia.db3`: This will only appear if you are using the default
   SQLite3 database; it a binary file that holds the entire game
   database; deleting this file will effectively reset the game for
   you and you can start fresh with `evennia migrate` (useful during
   development).  

## server/conf/

This subdirectory holds the configuration modules for the server. With
them you can change how Evennia operates and also plug in your own
functionality to replace the default. You usually need to restart the
server to apply changes done here. The most important file is the file
`settings.py` which is the main configuration file of Evennia. 

## server/logs/

This subdirectory holds various log files created by the running
Evennia server. It is also the default location for storing any custom
log files you might want to output using Evennia's logging mechanisms.

# Reseting The Game

## Two separate places things live

| What you do | Where it ends up | Tracked by git? |
|---|---|---|
| Building in the game: `dig`, `create`, `desc`, the tutorial world, accounts, characters | The database `game/server/evennia.db3` | **No** (git-ignored) |
| Writing code or files: Python typeclasses, commands, JS plugins, images | Files under `game/` | **Yes**, they show up in `git status` |
| Logs, `__pycache__`, `secret_settings.py` | Local files | No (ignored) |

So an in-game "Hello Travellers" can't leave anything in the repo. Only code we write can, and only once it's committed.

## Resetting the database
**Option A: back up now, restore later** (keeps your superuser and the tutorial world):
```powershell
cd C:\git\terrific-travel\game
uv run evennia stop
Copy-Item server\evennia.db3 server\evennia-clean.db3     # snapshot (also git-ignored)
uv run evennia start
# ... experiment ...
uv run evennia stop
Copy-Item server\evennia-clean.db3 server\evennia.db3 -Force   # back to the snapshot
uv run evennia start
```
Always stop the server before copying. Copying the file while the server is writing to it can corrupt it.

**Option B: wipe completely** (a fresh, empty Limbo):
```powershell
uv run evennia stop
Remove-Item server\evennia.db3
uv run evennia migrate
uv run evennia start      # asks for a superuser again
```
`secret_settings.py` isn't affected by either option.

## Keeping code experiments throw-away: use a git branch
```powershell
git switch -c try/hello-travellers     # experiment here, commit as you like
# ... later, to throw it all away:
git switch main
git branch -D try/hello-travellers
```
Branches stay on your PC unless you push them, so nothing reaches GitHub. To throw away uncommitted changes, run `git restore .` and then `git clean -fd`, which deletes new untracked files. **Never use `git clean -x`**: it would also delete the ignored files, including your database and `secret_settings.py`.

## The one catch: reset both together
Database objects remember which Python class they were made from, for example `typeclasses.ships.Ship`. If you delete the code but keep the database, those objects can't load, and Evennia reports errors about them. The reverse is harmless. So when you throw an experiment away, **switch the branch and restore the database snapshot at the same time.**

When we start the map demo, my suggestion is: take snapshot A first, then work on a `try/...` branch. Either way you're one step from where you are now.

# Building A Game With Images

## What's already built in
The web client has a **multimedia plugin**. Game code can send an image along with the text:
```python
character.msg(text="You stand on the quay at Port Royal.", image="/static/images/port_royal.png")
```
The web client shows the picture. Telnet clients, and later your AI agents, simply ignore the `image` part and get only the text. So **one message works for both audiences**, which suits your plan well.

There's also an **HTML plugin**: `msg(html="...")` sends ready-made HTML. That's how you'd do "a map with text labels on top": a picture with positioned labels, or an SVG drawing, possibly with a "you are here" marker.

Two practical details:
- Both plugins are **off by default**. Each player turns them on with the gear icon (Options) in the web client: "Enable multimedia image" and "Prefer … direct-HTML". If we want them on for everyone, we'd add a small change in `game/web/`.
- The web client is made of **panes** you can split and drag. A message can be addressed to a named pane, so the map can live in its own side panel instead of scrolling past in the main text.

## What we'd add ourselves (small, and the usual Evennia way)
The built-in plugins *add* each image to the bottom of a pane, like a chat log. That's fine for character portraits or a room picture when you walk in. A **world map** should instead stay in one panel and update in place. That needs a short JavaScript plugin of about 30 lines, plus a layout with a "Map" pane. Both go into `game/web/static/webclient/` and `game/web/templates/webclient/`, which are the folders Evennia provides for customising its web client. Nothing in Evennia itself gets patched.

Images live under `game/web/static/` and are served by Evennia's own web server.

## Where the pictures could come from
This is the educational bonus:
- **Real 17th–18th-century Caribbean charts.** Many are public domain, from the Library of Congress, Wikimedia Commons or the David Rumsey collection. The boys would sail on a real period map.
- **Their own drawings.** Scanned or drawn on a tablet, this is a great job for Vincent and Phoenix, and the art is then truly theirs. (We'd ask them about the content license for it later.)

## The limits (as we discussed before)
Static images, maps that update, portraits and sound effects are all easy. Animation or real-time movement would mean writing a JavaScript game inside the client, and that's not where Evennia shines.

The next step can be a small demo:
- a `Map` pane in the web client;
- two or three rooms that each send the map with labels and a "you are here" marker;
- a room picture that appears when you walk in.

I'd start with a placeholder image and leave the real map choice to the three of you.

# How To Play in the Demo

## Check the Server Status

From PowerShell, inside the `game` folder:

```powershell
cd C:\git\terrific-travel\game
uv run evennia status
```

When it's running, you'll see:
```
Portal: RUNNING (pid 26732)
Server: RUNNING (pid 24408)
```

When it's stopped, both lines say `NOT RUNNING`.

Evennia runs as two processes. The **Portal** handles player connections, and the **Server** runs the game itself. Both should say RUNNING. If only the Portal is running, the game crashed or is reloading: run `uv run evennia --log` to see why, then `uv run evennia start`.

A quick check from any folder is to see whether the web port answers:
```powershell
Test-NetConnection localhost -Port 4001 -InformationLevel Quiet   # True = running
```

## Play the game

You're in Limbo, so you're ready. The "tutorial" you see is just the tutorial world's exit listed there. Do this:

**1. Reload the browser page** (F5) once. A **Map** pane should appear on the right, showing "No map for this place." Limbo isn't on any map.

**2. Build the demo.** In the game's input line, type:
```
batchcode batch_map_demo
```
You should get "Map demo built. Type harbour to go there." Now `look` lists a new exit, **harbour**, next to tutorial.

**3. Go there:**
```
harbour
```
You should see:
- a placeholder picture of a pier and a boat, above the room description;
- in the Map pane, a blue sea with three islands labelled **Harbour**, **Lighthouse** and **Cove**, and a red ring marked "You are here" on Harbour.

**4. Walk around** and watch the marker move:
```
north          Harbour → Lighthouse
southeast      Lighthouse → Cove
west           Cove → Harbour
back           Harbour → Limbo (the map says "No map" again)
```
Typing `look` in any room shows its exits.

**If something's off:**
- **The Map pane isn't there:** press F12, open the **Console** tab, and send me any red lines.
- **The pane is there but stays empty after `harbour`:** tell me, and I'll check the server log.
- **You want to start the demo over:** `batchcode batch_map_demo_remove`, then build it again.

# How to Access the Server From Another Computer

**On your home network, yes. It's already set up and should work as is.** From outside the house it takes extra setup.

## Same network (Wi-Fi at home)
By default Evennia listens on every network connection, not just on this PC. On another computer, phone or tablet on the same Wi-Fi, open:

- **Web client:** <http://192.168.0.237:4001>
- **Telnet / MUD client:** host `192.168.0.237`, port `4000`

`192.168.0.237` is your PC's address on the Wi-Fi right now. I checked that the server answers on that address, and the Windows firewall has an inbound "allow" rule for Python, so other devices should get through. Two caveats:
- **The address can change** when the router hands out new ones, for example after a restart. `ipconfig` shows the current one. If you want it fixed, most routers let you reserve an address for a PC (often called "DHCP reservation").
- **Windows treats your Wi-Fi as a "Public" network,** and the Python rule allows connections on Public networks. That's fine at home, but on hotel or café Wi-Fi it means anyone there could reach the game too. To fix it, set your home Wi-Fi to **Private** (Settings → Network & internet → Wi-Fi → your network → Private) and allow the Python rule on Private networks only.

## From outside (the boys at their own homes)
Your router blocks incoming connections from the internet, so you need one of these:

| Option | Effort | Notes |
|---|---|---|
| **Tailscale** (free VPN for a small group) | Easy | Install it on your PC and theirs, and they use your Tailscale address. **Nothing is opened to the public internet.** My recommendation for family play. |
| **Port forwarding on your router** | Medium | Forward ports 4000–4002 to your PC. The whole internet can then reach it, bots included. Needs the security steps below. |
| **Rent a small server (VPS)** | More | It runs all the time without your PC. That's for later, if the game grows. |

The web client needs two ports: **4001** for the page and **4002** for the live connection (the websocket). That matters when you forward ports.

## Before anyone outside your home connects
- Use a strong password on your superuser account.
- Anyone who can reach the server can create an account, because registration is open by default. That's fine on the home network or over Tailscale. For a public server you'd turn it off with `NEW_ACCOUNT_REGISTRATION_ENABLED = False` and create the boys' accounts yourself.
- Your secret key is in place: you have `secret_settings.py`, created when the game folder was first set up.
