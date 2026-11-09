# Multiplayer

That changes the design in a rather fundamental and, I think, very interesting way. Multiplayer isn't simply an additional feature here. It could become one of the strongest reasons for having multiple world models in the first place.

I particularly like your idea that two players could occupy the same geographical location while experiencing different world models.

In fact, I would make this one of the central principles of TerrificTravel:

Two explorers can inhabit the same place, at the same time, but experience different realities.

Let's explore what this could mean.

# 1. Two players, two worlds, one location

Imagine two players exploring our fictional Mediterranean island.

Shared geographical location

Multiplayer

[Digital illustration - Hire a Freelance Illustrator Services | Fiverr](https://images.openai.com/static-rsc-4/3DAwjz6pkfGdtQRh2Fa0EkwiUaV3izrrsL2UYIFI8XvMasjiNWHUEtlYvEhQu-c_9lyP4xGiVGfZQDOWpej0pfur1UEQBCiQo5nk9LOgYKVP-TYjZA9bnDgg0i_BHQ6ca87aPuMCbqXmgvi0tdEY_v0ha9d0MESLhgTUQQDVnZw?purpose=inline)

[fiverr.com](https://www.fiverr.com/leaklide/do-incredible-fantasy-maps-for-you?utm_source=chatgpt.com)

Player A

Homeric world

[Odysseus and the Cyclops: The Story That Shows Exactly Why Being Too Clever Is Also a Kind of Flaw | Book of World History](https://images.openai.com/static-rsc-4/BEMxCbPTaCZsjaN11g4BCqZTZljGHDpGEgpwZbRohWwWqm3TQwUdXY7dK7h4lA-m9xdR0hOMbLJmsHAc3JJNgHrL_WHnBjXpBfbjKL6lrxVTpfbVQVMQMGML9GATlNVG7xjG9GjcvSvRkc3htSsltbH1xPtaQ4xH1VVVL7CQLEs?purpose=inline)

The harbour is visited by Odysseus. A mysterious stranger is approaching.

Player B

Modern scientific world

[Apolonia, el puerto en el siglo III a.C. - Jean-Claude Golvin](https://images.openai.com/static-rsc-4/UABpFTbUuqmtaJBfswxDWwJEqguBrLdxBHs4ahvivL4qpSHdN8tiWmPPHiscYp9QniSjSWCIWmdB4FtNrXTzP4HSNzCo_hE9aPNotOItVSmuS7mz6W02i-FR0X0POCoIUuznFY9qHz10ZYEHsga7s5ikfVAWqSBpyq6391ktSkc?purpose=inline)

The harbour contains archaeological remains. A research vessel is approaching.

Shared underlying event

Something is approaching the island by sea. Both players can investigate it, but interpret it differently.

This immediately creates opportunities for cooperation.

Player A might see a mythological creature. Player B might see an unusual animal or a natural phenomenon.

They can exchange observations and try to understand what is happening.

# 2. World-model collisions

I would introduce the concept of a World Collision.

A collision occurs when two or more world models overlap at the same geographical location.

There are several possible types.

## A. Complementary perceptions

Two players see different aspects of the same event.

For example:

- Player A sees a strange light in the sky.
- Player B sees an astronomical phenomenon.
- Neither has the complete explanation.

They must share information.

## B. Incompatible realities

The two worlds have different physical rules.

For example:

- In one world, a river can be crossed by walking over its surface.
- In another, it is an ordinary river.
- A player in the first world discovers a route that the second player cannot use.

They must find a way to cooperate despite the differences.

## C. Objects that cross worlds

An object might exist in several world models but have different properties.

For example:

| Object          | Homeric world                | Modern world               |
| --------------- | ---------------------------- | -------------------------- |
| A bronze sword  | A weapon of legendary origin | An archaeological artefact |
| A stone         | A sacred object              | A geological specimen      |
| A plant         | A magical herb               | A medicinal plant          |
| A constellation | A mythological figure        | A group of stars           |

Some objects might even be transferable between worlds.

## D. Contradictory events

An event might have different consequences in different models.

A player could accidentally change something in one world that causes a corresponding change in another.

This introduces an interesting question: are these worlds independent, or are they different projections of one underlying reality?

I would leave that question open initially.

# 3. The shared world and individual perspectives

I think the underlying architecture should distinguish three things:

Shared

Geographical world

The common spatial structure: locations, connections, landmarks, and possibly shared events.

Individual

Player perspective

The world model through which a player currently experiences the environment.

Interactive

Cross-world interactions

Objects, characters, events, and actions that connect different world models.

This is important because I wouldn't necessarily create completely independent game worlds for every player.

Instead, players share a persistent environment, but its representation and available interactions depend on their current world model.

A simplified conceptual representation might be:

\\[ S=(L,T,M_1,M_2,\ldots,M_n) \\]

where:

- \\(L\\) is the shared geographical structure.
- \\(T\\) is the temporal context.
- \\(M_i\\) is the state of world model \\(i\\).

Each player has an active perspective:

\\[ P_i=(location_i, worldview_i) \\]

This is only a conceptual model, but it provides a useful starting point for implementation.

# 4. The multiplayer interface

I would make the presence of other players visible without allowing it to dominate the screen.

For example:

The Harbour

2 explorers online

[Chios Maris Aegaei eiusdem nominis Insulae Civitas. - Old map by BRAUN, G. / HOGENBERG, F.](https://images.openai.com/static-rsc-4/PFhbXVEJbtxoL-MjEVfSyeFARlZ9f6glPrNy34Xi1Dfv1WHuN7owuWcMnXJ9pS1McXPsEKmW3NRh45hE8HjeGcNLbpClVKi_rXQm5ivICrIODUF0kM6P1ahle6IEwRwf9Jd9njnoe_GTz7AvVcwWOOVIuok_ZAONnXj86AfM4y8?purpose=inline)

[swaen.com](https://www.swaen.com/listing/chios-maris-aegaei-eiusdem-nominis-insulae-civitas/41876?utm_source=chatgpt.com)

Explorer A

Homeric world · At the harbour

You

Explorer B

Modern world · At the harbour

Present

Recent shared events

- Explorer B discovered an unusual stone.
- Explorer A heard a strange voice from the sea.
- Explorer B examined the stone.
- A mysterious ship appeared offshore.

I would also include a shared conversation channel, but distinguish ordinary conversation from in-game observations.

For instance:

- Chat: Players can communicate freely.
- Observation: A player can share something they actually see.
- Discovery: A player can publish a discovery into the shared journal.

This distinction could become useful when players have different information.

# 5. Multiplayer puzzles could be exceptional

Here is an example of a puzzle that would be difficult or impossible to implement in an ordinary single-player game.

[Antikythera Mechanism: The Ancient Greek Astronomical Computer](https://images.openai.com/static-rsc-4/cUtQfyvEdgaJ6FSwEx-st77tEn5v8Zax119F2X-npn-YyUDxAQro2WUfnf1H30iYDK29viXn77pKIZU0fEypNrvUtoTqULe1iWHdVB5Kke_oYJNp8sGBZYvtE0Us-LUR2zXFeYuX1UScp1Fir--0jeKr-ONVSLYny6jwAIppaz8?purpose=inline)

[mystreal.com](https://www.mystreal.com/history/antikythera-mechanism/?utm_source=chatgpt.com)

The Temple of the Seven Stars

Two players discover an ancient mechanism.

Player A is in the Homeric world:

- Sees seven mythological figures.
- Can communicate with a guardian.
- Knows the legendary names of the stars.

Player B is in the modern scientific world:

- Sees seven astronomical positions.
- Can calculate their relative positions.
- Recognizes a particular constellation.

Neither can solve the mechanism alone.

They must exchange information and coordinate their actions.

This is exactly the sort of experience that could make playing together memorable.

And it teaches astronomy, mythology, and the history of scientific knowledge without becoming a lesson.

# 6. A few multiplayer rules I would consider

There are some design questions worth addressing eventually.

| Question                                    | My initial preference                                           |
| ------------------------------------------- | --------------------------------------------------------------- |
| Can players occupy the same location?       | Yes, even in different world models.                            |
| Can they see each other?                    | Not necessarily; depends on the models.                         |
| Can they communicate?                       | Always through an independent chat channel.                     |
| Can they exchange objects?                  | Sometimes, depending on object properties.                      |
| Can they change world models independently? | Yes.                                                            |
| Can they affect one another?                | Yes, where the models intersect.                                |
| Is the world persistent?                    | Yes, at least at the level of important discoveries and events. |
| Can players explore separately?             | Absolutely.                                                     |

I would avoid requiring players to remain together. Parallel exploration is potentially just as interesting as cooperation.

# 7. An additional idea: world-model groups

Eventually, there could be more than two players.

Imagine a group of four explorers:

- One in the Greek mythological world.
- One in the medieval Christian world.
- One in the Ptolemaic world.
- One in the modern scientific world.

All are exploring the same island.

They can compare observations, discover contradictions, and work together on problems.

This could become a very distinctive multiplayer experience: not simply exploring a virtual geographical world, but exploring the relationship between different ways of understanding reality.

# 8. What this means for the first prototype

I would now change my earlier recommendation slightly.

Rather than designing a single-player prototype and adding multiplayer later, I would build the initial prototype with two players in mind from the beginning.

Not sophisticated multiplayer, though.

## First multiplayer experiment

Recommended scope

One island, two players, two world models.

[A Fantasy Campaign Map - Arvyre - by 2-Minute Tabletop](https://images.openai.com/static-rsc-4/CTeQc1APn5DRCTMMNPtmSnW-uaD-j6nqfF0ZUP3AAvvqlhMKffAJZ42yGiDDaG8D_SFoQQ0Snu32ftrcrfAiIwpbteVujxOWr52s_g4FdbzhCQOe_HVVAMAa0aULxbVApzGZ7qQqVz_aGU0Osl0xPUzrDi8LkM4SrACv4cQ_3LA?purpose=inline)

[2minutetabletop.com](https://2minutetabletop.com/fantasy-campaign-map-arvyre/?utm_source=chatgpt.com)

- Both players can move independently.
- Both can see who is online and where the other player is.
- Each can switch world models independently.
- They share some objects and events.
- They can communicate.
- At least one puzzle requires cooperation across world models.
- Their discoveries persist between sessions.

This is enough to establish whether the central multiplayer concept works.

Technically, it also suggests that Evennia becomes a more interesting candidate, because persistent multiplayer objects, rooms, characters, and events are already part of its design.

I would still keep the graphical browser interface separate from the underlying Python game engine.

## My most important design recommendation

I would make one distinction explicit in the design:

The players share a world, but they do not necessarily share a reality.

That is much more interesting than simply having two avatars explore the same map.

It also gives TerrificTravel a potentially distinctive identity: a cooperative exploration game in which players learn not only about the world, but about the different ways in which a world can be understood.

And I think that could be a wonderful experience for two young explorers working together.