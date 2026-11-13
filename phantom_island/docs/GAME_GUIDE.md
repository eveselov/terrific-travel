# Phantom Island Game Guide

*Presents observations about different aspects of the game. It is supposed to contain most essential recommendations, not a full verbose manual.*

## Expedition

- The expedition is all the players together: one team, sent out by the Society to find out what happened to the lost ship *Halcyon*.
- You join it by typing `begin` on the title page (Limbo). Mrs. Fairweather, in the Society Office, explains the task.
- You lead the expedition and command its ship: the crew follow your orders, and the ship goes where you decide (`sail` on the Deck). The ship herself has a voice and gives advice: `ask ship`.
- The expedition has its own ship and one shared journal. Where the ship is, and what has been found, is the same for every player.
- One player alone is a whole expedition; more players simply share the work.

## Everything fits together

This is what makes Phantom Island different: its details are not random. Distances, dates, numbers, the weather, the birds, the plants and the people's stories all depend on each other, the way they do in the real world.

- If two things don't seem to fit, one of them is wrong, and finding out which one is often a clue in itself.
- Things that look like scenery may matter: a word in a description, the direction of a wind, what a plant is doing on an island.
- You don't have to dig deep to finish the adventure. But if you want to know *why* something is so, the knowledge is there: ask the Ship, read the books, use the instruments.

## The screen

The web client has three panes. Everything in Map and Focus is also told in the text, so the game can be played without them (over telnet, for example).

- **Main**: the story as text: what you see, what people say, the journal. Your own commands are shown in green after a dashed line; other players' turns come after a fainter dotted line.
- **Map**, titled "Your map": where you are. It changes with the part of the adventure: a plan of the port, the *Halcyon*'s chart at sea (with your ship's track), and a map of the island. `map` describes the current map in words.
- **Focus**, titled "You are looking at": a picture of what's in front of you. That's the room when you arrive or type `look`, and whatever you last looked at with `look <something>` or `examine`: a thing, a part of the room, or a person. Talking to someone (`ask`) doesn't change it: the topic of a question is often far away, or not a thing at all.

## Playing together

- Players in the same room see each other; players in different rooms don't.
- In a room, everyone hears what you `say`, `ask`, `read` and `use`, and sees you come, go, pick things up and put them down. Looking (`look`, `examine`) and your `journal` are private.
- Talk to other players with `say <text>` (the whole room), `whisper <name> = <text>` (one person in the room) or `page <name> = <text>` (anyone, anywhere). `ask` is only for the story's characters.
- In the web client, your own commands are shown in green after a dashed line, and other players' turns after a fainter dotted line, so you can tell them apart.
- The journal is shared: a clue found by anyone goes into it, and every player hears about it, wherever they are.
- Splitting up is faster: some tasks have two halves, such as the noon sight on the Deck and the chronometer in the Cabin. Something you carry (a book, the chart) is with you, not with the others, until you drop it or log out.
- Nobody gets left behind: the ship won't sail while someone is still ashore. Someone joining late, while the ship is away, starts on the Deck and catches up with `journal`.

## Journal

- The journal is the expedition's notebook of clues: `journal` (or `notes`, `clues`) shows it.
- A clue is a fact shown in **yellow**, in what someone says, in what you look at, or in what an instrument or book shows. Right after it comes a line starting "New in the journal:", so a clue is never missed, even without colours.
- Entries are kept in the order they were found, each with who found it, where, and from whom or what. When another source confirms a clue later, it is added to the same entry, so you can see who agrees with whom.
- There is one journal for the whole expedition: everyone sees the same entries, and every player hears of a new clue at once, wherever they are.
- The same clue can turn up in different words from different sources. Finding it again adds no new entry: you're shown the entry it matches, so you can see they're the same fact.
- The journal matters to the story too: some people only tell the truth once the right clue is in it, so it pays to come back and ask again.

## General Tips

- Don't trust everything the characters say. Sometimes they don't know the truth, sometimes they lie, sometimes they are just mistaken - like in real life.
- Conditions in the game change over time. What was impossible before might worth trying now, after previous interactions... Don't hesitate re-trying.

