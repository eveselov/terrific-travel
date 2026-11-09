# Game Inception

**Question:** *I am designing a game on Evennia platform - some sort of travel a world populated with autonomous creatures, with visuals for locations and objects. The game must be interesting (fun and educational) for my 12 year old grandson.Please tell me what are existing games on that platform to take inspiration from?*

I think Evennia is a particularly interesting choice for this project. It gives you something more powerful than a conventional adventure-game engine: a persistent world in which objects, locations, characters, and creatures can have their own behavior, state, and interactions.

For your project, I would look at existing Evennia games from two perspectives:

1. Game design: exploration, quests, progression, social interaction, puzzles, and world-building.
2. Technical design: how creators implement rooms, objects, autonomous NPCs, combat, events, and persistent state.

One important distinction: Evennia is primarily a Python-based MUD/MU\* development framework, not a game marketplace like Steam. Its games range from traditional text adventures to elaborate role-playing worlds. You should not expect all of them to have the visual presentation you envision.

## 1. The most interesting existing Evennia projects

Here are the projects I would investigate, in roughly the order I think they are useful to your design.

[テキストベースRPG・MUDの可能性 - はてな村定点観測所](https://images.openai.com/static-rsc-4/z9A1aVy27-NBAWP2qrHL8e252RzH9gpLiJ-QT1qkm7IqiQGKsMJALv5Gs7n-7T3aIAkHj320Oo0ByB6aVh-tOX52TkQb3qhSbg5M5n_2Zm8vPvnjMMhR_bWfOMK5jM2b5YtNNqt3uBw2XcuMV75BxLUg0KcrYuCuqUQAgXBgK7w?purpose=inline)

1\. Arx: After the Reckoning

Study its world design

A substantial fantasy roleplaying world, heavily focused on player-driven storytelling, characters, social relationships, factions, and political intrigue.

Its source code was released publicly. It is probably the richest example of a large, developed Evennia game.

What to study: character models, objects, permissions, social systems, persistent world state, and how a large game is organized.

[Official Evennia guide to Arxcode](https://www.evennia.com/docs/latest/Howtos/Tutorial-Using-Arxcode.html?utm_source=chatgpt.com) · [Source code](https://github.com/Arx-Game/arxcode?utm_source=chatgpt.com)

[Esenthel Engine on Steam](https://images.openai.com/static-rsc-4/-1xQWXnOsd_ROgdLt6c9EnXR66SDYQLxSh5ni78w9T04XIp6gF4UxMcUg1Smb6vIvl0znVsb_zmn7mwbFWwDo5gFWnw4yx5AgTBzLk8-TydMHbPXgjW9ikKTbAt0MU67L-bch3lIU1kLerPnHKP5dUaTvQnWFGvAM9y_scT870g?purpose=inline)

2\. EvAdventure

My first recommendation

This is the example adventure game developed as part of Evennia's official beginner tutorial. It is based on the Knave tabletop RPG rules.

It demonstrates the construction of a playable adventure with rooms, characters, equipment, combat, exploration, and game mechanics.

What to study: how to turn Evennia's basic building blocks into an actual adventure.

[EvAdventure tutorial](https://www.evennia.com/docs/5.x/Howtos/Beginner-Tutorial/Part3/Beginner-Tutorial-Part3-Overview.html?utm_source=chatgpt.com) · [All Evennia tutorials](https://www.evennia.com/docs/latest/Howtos/Howtos-Overview.html?utm_source=chatgpt.com)

[Griatch's Evennia musings: Creating Evscaperoom, part 2](https://images.openai.com/static-rsc-4/FBWdXDl56KNKGfBCauy4ksWCjzOz0pigekvcoPb9mEix4bSLeIiwqgg3je0X7Ng7aOMUXt5xe7x7Yzy9JJhzz6eFSsxV9oOWDY1ncEeExAn-rK2A8IcRLYiLkJ9Ghyg7mA_aHf9k4-e35oC-wNO2ofRtaL-HQZc6oCSZnbMQ3NY?purpose=inline)

3\. EvscapeRoom

A multiplayer escape-room implementation, developed as an Evennia contribution.

What to study: interactive objects, environmental puzzles, clues, dependencies between actions, and how to make locations interesting without relying on combat.

This is particularly relevant if you want your grandson to learn things by experimenting with objects and solving problems.

[Source code](https://github.com/griatch/evscaperoom?utm_source=chatgpt.com)

[Dig Shovel Projects :: Photos, videos, logos, illustrations and branding :: Behance](https://images.openai.com/static-rsc-4/TyO8pjWF4sR_239tcjKzr8zg_XWtKI8AUDOuGnWFWJlbFUFed7RSuAz6uTGqO21bgRSS22MKjGPYnYX-5Hozqm3KlJrLL5wLjeV53_227JC4V_pTAuXv6rHeR-6cEieFApFETTrUvcNzWkRrrvQJ_Mk7pIcjEBhD0lpbd2N8hUo?purpose=inline)

4\. The Scourge Forest

A fantasy adventure with D&D 5e-inspired classes, monsters, equipment, levels, quests, and combat. It also supports solo adventures.

What to study: progression, adventure structure, monsters, inventory, and balancing difficulty.

[GitHub repository](https://github.com/TehFamine/the_scourge_forest?utm_source=chatgpt.com)

[Hackathon: GPT4-x-Alpaca Part 2: Creating a MUD with Evennia ::         Coder's Haven](https://images.openai.com/static-rsc-4/z1GMsMq2qJwINaBeuqcF1qmiM_MPqaHJx49Pw6dXTx3R6ETEvs1DSGu6Yt0uweSl6jmHtQm_NE1ccDweEjrdF20vGPZj_SytO-s2Fez2MWT8LRFGO9CMMXfd7UC8wfkDzF47D0jW0Ox_XcvmVOBsMKr5D3ZZBSsqHdOckCJFsrs?purpose=inline)

5\. Ainneve

An official community example game intended to provide a more complete starting point than the bare Evennia framework.

What to study: how to structure a game directory, organize typeclasses, and implement game-specific systems.

[GitHub repository](https://github.com/evennia/ainneve?utm_source=chatgpt.com)

One caveat: these projects have different levels of maturity. Some are source-code examples rather than polished, currently playable games. In particular, I would not assume that an old installation guide will work unchanged with today's Evennia.

## 2. A particularly interesting project: autonomous creatures

There is another project worth mentioning: aimud.

It is an experimental Evennia-based MUD in which the world, its inhabitants, and even available verbs can be generated by an LLM as the player explores. Generated content is cached for consistency.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://resources.writing-games.org\&sz=32)

MU\* Resources+1



This is conceptually close to your idea, although it is not a mature autonomous-agent simulation.

I would investigate it because your creatures could be much more interesting than conventional NPCs:

- They have individual needs, goals, and personalities.
- They move around the world independently.
- They remember encounters with the player.
- They interact with other creatures.
- They react to changes in their environment.
- They can cooperate, compete, hunt, hide, or protect their offspring.

This is where I think your game could become genuinely distinctive.

## 3. Where to find more games

The most useful starting point is the official [Evennia Game Index](https://games.evennia.com/?utm_source=chatgpt.com).

It lists games that have been built or are being developed using Evennia. Importantly, it also accepts projects that are not yet publicly playable.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.evennia.com\&sz=32)

Evennia latest documentation+1



You can also visit the [Evennia demo server](https://demo.evennia.com/?utm_source=chatgpt.com).

In particular, I recommend trying EvscapeRoom yourself. Its repository documents how to play it, and the author says it is available on the demo server. It is a nice example of making a relatively small environment interesting through interactions with objects.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



## 4. What I would borrow for your game

I would actually avoid copying any single existing Evennia game. Your concept is different enough to warrant its own design.

Here is how I would combine the ideas:

| Element                | Inspiration    | Your implementation                  |
| ---------------------- | -------------- | ------------------------------------ |
| World organization     | Arx            | Persistent interconnected world      |
| Exploration            | EvAdventure    | Discover locations and hidden areas  |
| Object interaction     | EvscapeRoom    | Manipulate objects and experiment    |
| Progression            | Scourge Forest | Unlock abilities and new territories |
| Autonomous inhabitants | aimud          | Creatures with independent behavior  |

## 5. One important consideration: visuals

Evennia provides a browser-based web client, but its traditional game model is text-oriented. You can customize the web interface using HTML, CSS, and JavaScript.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.evennia.com\&sz=32)

Evennia latest documentation+1



For your game, I would consider a hybrid presentation:

[Dense-forest, du dongdong | Game concept art, Environment concept art, Environment painting](https://images.openai.com/static-rsc-4/eZCsjM2ByzJ6glAC3KydMQ7xaTBhxksuEmQfYBNlgY0MNF5rbEAkmvgyJ_Px4b5XKkJprKWQqxLewCadlYgt3hJT6bMh-K6yj08qNvkbnU8iVgN8gY-0_8J3CIIWJjCMOb4m2xGGUR9ck2X4OGmlD2pb24GvndQ32odmwdLsAdQ?purpose=inline)

[Mobian: The Peak-Agile Climber Humanoid | AI Art Generator | Easy-Peasy.AI](https://images.openai.com/static-rsc-4/mcZSqN1acfk3MVb6PRdSPGgBqoFQFG4Neex8wPLUDsmIS6n_bRiSjzTe5cFTsWhNSSa30cdUG_nZ9WjzJVV-wxhiDb4kIWxm3zC4P9XvM5cY5djVqmxmYMfR86UxDK6_p97uqfltNXEucpJYSKDtjUEMxUTLw2x8NIervq_JoWo?purpose=inline)

[Screenshot of Mystery Age: The Imperial Staff (Windows, 2009) - MobyGames](https://images.openai.com/static-rsc-4/Tqrw244x3qJEwsGTy30psioRr3ILMZWyYThNwtCN9iJhOeeRAGj1Wtg7rqWPTR8eWdT3gjrv1tzMyOmCiD8guDrNKO7e-Eu3IWWkZEx8Zhb7MQvLSz_2ecvaL2xTECfLTAsog7O4f35KxdJVS-q9pefsDT-Bb_bmTtt58O9I0n0?purpose=inline)

11

- Location: an illustrated scene showing the current environment.
- Creatures: illustrated characters with recognizable appearances.
- Objects: visual representations that can be examined and manipulated.
- Interaction: a combination of natural-language conversation, commands, and clickable objects.
- Narrative: text describing what happens, including events the player didn't initiate.

I would keep Evennia responsible for the authoritative world state and game logic, while developing a customized browser frontend for the visual experience.

## 6. My main design recommendation

There is one thing I would emphasize particularly strongly.

Make the world interesting even when the player does nothing.

Imagine your grandson enters a forest clearing. He sees:

- A rabbit eating grass.
- A fox hiding behind a tree.
- Two squirrels chasing each other.
- A bird building a nest.
- An insect crawling over a fallen branch.

He can observe them, approach them, feed them, scare them, help them, or simply leave.

When he returns an hour later, the world has changed. The rabbit has moved, the bird has finished its nest, and the fox has caught something.

This could provide both entertainment and education: ecology, animal behavior, food chains, adaptation, natural selection, and environmental interdependence.

I would make learning emerge from exploration rather than present it as lessons or quizzes.

## 7. A question about the direction of your project

There are two rather different approaches to implementing this game, and I think the choice will significantly influence its architecture.

A. A simulated natural world

The central attraction is a living ecosystem. Creatures have internal states, needs, memories, relationships, and autonomous behavior. The player explores and influences this world.

B. An adventure game with intelligent inhabitants

The central attraction is the player's journey: exploration, discoveries, quests, puzzles, and challenges. Creatures are intelligent participants in the adventure.

Of course, these approaches can be combined, but one should probably dominate.

My personal inclination is toward A, with adventure elements added on top. A genuinely living world populated by autonomous creatures could be much more fascinating than another conventional fantasy RPG.

And it offers an excellent opportunity to introduce a 12-year-old to biology, ecology, artificial intelligence, and the idea of complex systems through play.

---
**Question:** 