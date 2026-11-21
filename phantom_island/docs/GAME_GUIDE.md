# Phantom Island Game Guide

**It is 1790. Fifteen years ago the ship *Halcyon* sailed to chart a small island far out in the ocean, and was never heard of again. Now her compass has turned up in your own harbour. You lead the expedition that goes to find out what really happened.**

Phantom Island is a mystery to solve together, in words and pictures:

- **A real detective story.** Nobody hands you the answer. People tell you what they believe, and not all of them are right; things you can see for yourself don't lie. Collect the facts in the expedition's journal, compare the witnesses, and work out the truth.
- **Every detail has a reason.** Distances, dates, the wind, the birds, the plants: nothing is random, and it all fits together the way the real world does. When two things don't fit, you've found something.
- **Real skills of the age of sail.** Find your latitude from the noon sun with a sextant, your longitude with a ship's clock, and your way across an ocean the way explorers did. What you learn goes into your own notebook, and it grows as you understand more.
- **Better together.** Play alone, or with friends and family as one crew: split up, share what you find, explain to each other what you've learned. No fast reflexes needed, only curiosity.

*The rest of this guide is the essentials of how to play, not a full manual.*

## Expedition

- The expedition is all the players together: one team, sent out by the Society to find out what happened to the lost ship *Halcyon*.
- You join it by typing `begin` on the title page (Limbo). Mrs. Fairweather, in the Society Office, explains the task. You are the expedition's captain: the crew sail the ship, and you decide where she goes and what to look into. Playing together, everyone is a captain.
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
- Splitting up is faster: one can talk to people while another looks around. Some tasks have two steps, such as the noon sight and then the chronometer; anyone can do either, at any time. Something you carry (a book, the chart) is with you, not with the others, until you drop it or log out.
- Nobody gets left behind: the ship won't sail while someone is still ashore. Someone joining late, while the ship is away, starts on the Deck and catches up with `journal`.

## Talking and moving

- `ask <someone>` greets them, and they suggest things to ask about. `ask <someone> about <something>` asks. `about` is always needed for a topic, so `ask ship` always means the Ship, never a question about ships.
- After that, `ask about <something>` (or `ask him`, `her`, `them about …`) goes on talking to the same person, as long as they're still there. With only one person around, `ask about …` is enough from the start.
- The start of a long name is enough: `ask fair about the chart`.
- Anyone can be asked about themselves: `ask barnaby about yourself`, or `ask tui about you`.
- Walk with the exit's name (`east`, `aboard`) or with `go`: `go east`, `go to the market`.
- On the island, you only know the paths you've found or been shown. A new one is announced: "(A new path: the Village, south of the Forest Path.)", and appears on the map. Climbing somewhere high, and making friends, both help.
- Some people only tell what they know to those who show respect. They'll say what that takes, and they'll notice when you do it: "(Elder Ama's respect: 1 of 2.)"

## Sailing

- Orders are given on the Deck with `sail`. On its own, `sail` tells you where the ship is and what you can order there.
- A place at sea is a position: two numbers, the **latitude** (how far north or south) and the **longitude** (how far east or west). The island's position is written on the *Halcyon*'s chart in the chart house, on the Deck: `read chart`, and `examine chart` for a closer look.
- Give the position as your order: `sail to <latitude> <longitude>`, for example `sail to 10 north 25 east`. The Ship repeats the order and explains the course before she sets off.
- Out at sea, where no chart helps, you can also sail by direction (`sail west`), or simply `sail home`.
- A voyage takes a few moments of real time: a few lines tell the days at sea while the ship moves along the chart in the Map pane. Nothing needs doing meanwhile: the crew sail her.
- Not sure where to go? `ask ship about course`.

## Notebook

- Your `notebook` is your own: the ideas you've learned about how the world works, such as how latitude is measured. The journal is for the expedition's clues; the notebook is for understanding.
- An entry grows as you learn more: first you hear of something, then someone explains it, and at last you do it yourself.
- It shows the areas you've started ("Navigation: 2 of 9"). `notebook sources` shows who taught you what, and who else knows it: ask them to explain!

## Journal

- The journal is the expedition's notebook of clues: `journal` (or `notes`, `clues`) shows it. Once Mrs. Fairweather has told you the mission, the expedition's task stands at the top: the three questions the Society wants answered. If you lose track of what you're here for, look there.
- A clue is a fact shown in **yellow**, in what someone says, in what you look at, or in what an instrument or book shows. Right after the scene comes a quieter line in grey, starting "Noted in the journal:", so a clue is never missed, even without colours. The same line says when your notebook learned something.
- What's new since you last looked is marked "(new)": clues in the journal, possibilities in the report, questions in `think`. The journal's last lines tell you when `think` or the report has something new.
- Entries are kept in the order they were found, one line each. `journal sources` shows who found each one, where, and from whom or what. When another source confirms a clue later, it is added to the same entry, so you can see who agrees with whom.
- There is one journal for the whole expedition: everyone sees the same entries, and every player hears of a new clue at once, wherever they are.
- The same clue can turn up in different words from different sources. Finding it again adds no new entry: you're shown the entry it matches, so you can see they're the same fact.
- The journal matters to the story too: some people only tell the truth once the right clue is in it, so it pays to come back and ask again.

## Report

- `report` is your case board, anywhere, at any time: the task's three questions, and for each one the possibilities you have come across so far. New possibilities come up as the expedition finds things out. Whenever you don't know what to do next, look at it.
- When you think you know an answer, pick its letter: `report 1 b`. `report 2` shows one question on its own. Not sure? A council helps you work it out (see Council).
- The Society wants proof: an answer is only accepted once the journal holds the clues that show it. If an answer doesn't fit, or can't be proved yet, you're told why, and where you might look. That's not failing: go and look, and come back.
- One player's answer counts for the whole expedition, and the journal shows it under the question.
- When clues in the journal fit together, a question about them comes up in `think`. The game won't answer these questions; working them out, together or by asking around, is what gets you to the report.
- A question leaves `think` once it's settled: by a council, or by the report question it leads to.
- `think compass` (or `think 2`, a journal number) shows only the questions about that clue.
- Under a question you see the ideas from your notebook that help with it, and where to learn the ones you don't have yet.
- Once all three questions are answered, the whole story is told, page by page (`report more`), with the real history behind it.

## Council

- When the expedition has a big decision to make aboard, the Ship will say so: call a `council`. The crew gather, and the Ship asks the questions that settle it, one at a time. Answer each with its letter: `council b`.
- An answer only counts once the journal shows it. If it doesn't yet, the Ship tells you where to look, and the council waits: type `council` again when you're ready, and it carries on where it stopped.
- When the council has decided, the order is still yours to give.
- Some councils answer the Society's questions. Then the report shows what the council concluded, and the council tells you how to write it in: `report 2 d`, for example. You type it: the report is yours to sign.
- On the island, when you've seen enough, go back aboard and call a council: the Ship helps you put the Society's answers together.
- Playing together, everyone in the room is at the council, and anyone can answer. Talk it over first!
- Positions can be given as orders too: `sail to 14 south 40 west`.

## Hints

- Stuck? Type `hint`, anywhere. The first hint is a gentle nudge; type `hint` again for a clearer one, and a third time for exactly what to type. When the expedition finds something new, the hints start gently again.
- Aboard, the Ship gives the hint. Ashore, you think it over with the journal.
- If nothing new has been found for a while, a hint comes by itself, once.

## General Tips

- Don't trust everything the characters say. Sometimes they don't know the truth, sometimes they lie, sometimes they are just mistaken - like in real life.
- Conditions in the game change over time. What was impossible before might worth trying now, after previous interactions... Don't hesitate re-trying.

