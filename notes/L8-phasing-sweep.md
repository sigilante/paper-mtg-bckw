# L8 — Phasing sweep: can phasing suspend, window or mark an Aura term?

Line L8. Author: L8 subagent, 2026-11-21. Inputs: `README.md`, `notes/L7-forced.md`, `notes/L3-battlefield-graph.md`
("Phasing (examined, not used)"), `notes/L5-rules-checks.md` Q5. Nothing was simulated; no Lean, no code in the repo.

Provenance tags: **[read]** = Oracle text or ruling exactly as the Scryfall API returned it on 2026-11-21 (paginated
`/cards/search`, `unique=cards`, `include_extras=true`, generic client name, one request per 150 ms; plus
`/cards/named` and the rulings URI for ~22 cards), or CR text copied from L5 Q5 (CR effective 2026-11-06).
**[inferred]** = my reading of quoted text; no ruling found. **[guessed]** = unchecked.
I did NOT refetch the Comprehensive Rules (rules beyond L5's quotations are marked "not rechecked").

## 1. The sweep

Queries and result counts (all pages followed until `has_more` was false):

| query | cards |
|---|---|
| `o:phasing` | 18 |
| `o:"phasing"` (same, control) | 18 |
| `keyword:phasing` | 13 |
| `o:"phase out"` | 26 |
| `o:"phases out"` | 37 |
| `o:"phase in"` | 8 |
| `o:"phases in"` | 6 |
| `o:"phased out"` | 3 |
| `o:"phased-out"` | 1 |
| `o:"phased in"` | 0 (HTTP 404 = no match) |
| **union of the above** | **76** |
| `o:phase` (broad: also "combat phase", "main phase") | 317 |
| `o:/\bphas(e\|es\|ed\|ing)\b/` (broad regex) | 328 |

The two broad queries add no phasing card. I filtered their 329-card union locally: of the 253 cards beyond the 76,
3 contain the substring "phase in" and are false positives (Cyclonus, the Saboteur; Sphinx of the Second Sun; Temple
of Atropos: "…postcombat main phase in…"); the rest mention only turn phases ("steps and phases end", Topsy Turvy,
Runed Terror, Fatespinner, Clocknapper, Abbot of the Sacred Meeple). **Union: 76 cards that mention phasing.**
Counts are of Oracle cards (`unique=cards`), digital-only and extras included: Frenetic Efreet Avatar (MTGO Vanguard)
turned up, so the default did not hide digital cards.

Not paper-legal (all marked in the table): Ferris Wheel (Unfinity attraction), Old Fogey (Un-set, set code und),
Syr Konrad's Squire (set code unk, Un-set), Human (token), The Doctor's Childhood Barn and Unyaro (planes), Frenetic Efreet
Avatar (Vanguard, MTGO only). The other 69 are Vintage- and Commander-legal per Scryfall's `legalities` field [read].

## 2. The table (all 76, alphabetical)

"can phase" is capitalised where the card can phase a non-creature permanent other than itself. "keyword square wave" =
the 702.26a rhythm of section 4. N = "until its controller's next untap" (the reminder-text wording is "until your next
turn" or "before its controller untaps during their next untap step"; Scryfall rulings agree).

| # | name | type | can phase | who chooses | trigger kind | duration | paper-legal |
|---|---|---|---|---|---|---|---|
| 1 | Blink Dog | Creature — Dog | itself (creature) | self | activated {3}{W} | until its controller's next untap | yes |
| 2 | Breezekeeper | Creature — Djinn | itself (creature) | self | static keyword (forced every untap) | keyword square wave | yes |
| 3 | Brokers Confluence | Instant | target creature | targeted, mode may repeat x3 | one-shot spell (instant) | until its controller's next untap | yes |
| 4 | Change of Plans | Instant | creatures you control (X targets, any number) | chosen (may) | one-shot spell (instant) | until its controller's next untap | yes |
| 5 | Clever Concealment | Instant | ANY NONLAND PERMANENT you control (any number of targets) | targeted, any number | one-shot spell (instant, convoke) | until its controller's next untap | yes |
| 6 | Cloak of Invisibility | Enchantment — Aura | GRANTS phasing to enchanted creature | enchanted permanent | static (Aura) | keyword square wave | yes |
| 7 | Crystal Golem | Artifact Creature — Golem | itself (artifact creature) | self | mandatory trigger, every end step | until its controller's next untap | yes |
| 8 | Disciple of Caelus Nin | Creature — Human Wizard | ALL permanents except itself and up to 5 chosen per player (incl. Auras, tokens) | each player chooses up to 5 to keep | mandatory ETB trigger + static 'Permanents can't phase in' | indefinite (while Disciple is on the battlefield) | yes |
| 9 | Divine Smite | Instant | creature or planeswalker an opponent controls | targeted | one-shot spell (instant) | until its controller's next untap | yes |
| 10 | Dream Fighter | Creature — Human Soldier | itself and the creature blocking/blocked | fixed (self + that creature) | mandatory trigger | until its controller's next untap | yes |
| 11 | Equipoise | Enchantment | lands, then artifacts, then creatures of target player (count in excess of yours) | Equipoise's controller chooses which | mandatory trigger, every upkeep (repeatable) | until its controller's next untap | yes |
| 12 | Ertai's Familiar | Creature — Illusion | itself (creature) | self | static keyword; {U} can't phase out | keyword square wave | yes |
| 13 | Ferris Wheel | Artifact — Attraction | target creature | targeted | Attraction visit (repeatable, un-set) | until a die roll <=3 | NO (un-/acorn/plane/token, not constructed-legal) |
| 14 | Frenetic Efreet | Creature — Efreet | itself (creature) | self (coin flip) | activated {0} | until its controller's next untap | yes |
| 15 | Frenetic Efreet Avatar | Vanguard | GRANTS phasing to EACH PERMANENT YOU CONTROL | static | static (Vanguard) | keyword square wave | NO (MTGO-only Vanguard) |
| 16 | Galadriel's Dismissal | Instant | target creature, or each creature of target player (kicked) | targeted | one-shot spell (instant) | until its controller's next untap | yes |
| 17 | Gallifrey Falls // No More | Instant // Instant | any number of target creatures you control | targeted, any number | one-shot spell (instant, fuse) | until its controller's next untap | yes |
| 18 | Guardian of Faith | Creature — Spirit Knight | any number of other target creatures you control | targeted, any number | mandatory ETB trigger | until its controller's next untap | yes |
| 19 | Haystack | Artifact | target creature you control | targeted | activated {2},{T} | until its controller's next untap | yes |
| 20 | Hostile Hostel // Creeping Inn | Land // Artifact Creature — Horror Construct | itself (back face creature) | self | activated {4} | until its controller's next untap | yes |
| 21 | Human | Token Creature — Human | nothing (blocks phase-in: 'Permanents can't phase in') | static | static (token) | indefinite | NO (un-/acorn/plane/token, not constructed-legal) |
| 22 | Kaito Shizuki | Legendary Planeswalker — Kaito | itself (planeswalker) | self | mandatory trigger (end step, if entered this turn) | until its controller's next untap | yes |
| 23 | Katabatic Winds | Enchantment | itself (enchantment) | self | static keyword | keyword square wave | yes |
| 24 | King of the Oathbreakers | Legendary Creature — Spirit Noble | itself or another Spirit you control (when targeted) | fixed | mandatory trigger | until its controller's next untap | yes |
| 25 | March of Swirling Mist | Instant | up to X target creatures | targeted | one-shot spell (instant) | until its controller's next untap | yes |
| 26 | Merfolk Raiders | Creature — Merfolk Soldier | itself (creature) | self | static keyword | keyword square wave | yes |
| 27 | Mist Dragon | Creature — Dragon | itself (creature) | self | activated {3}{U}{U} | until its controller's next untap | yes |
| 28 | Old Fogey | Summon — Dinosaur | itself (creature) | self | static keyword (Un-set) | keyword square wave | NO (un-/acorn/plane/token, not constructed-legal) |
| 29 | Oubliette | Enchantment | target creature | targeted | mandatory ETB trigger | until Oubliette leaves the battlefield | yes |
| 30 | Out of Time | Enchantment | ALL creatures (untapped first) | all | mandatory ETB trigger; Vanishing | until Out of Time leaves | yes |
| 31 | Perch Protection | Instant | ALL permanents you control (only if gift promised) | all | one-shot spell (instant) | until its controller's next untap | yes |
| 32 | Rainbow Efreet | Creature — Efreet | itself (creature) | self | activated {U}{U} | until its controller's next untap | yes |
| 33 | Reality Ripple | Instant | target ARTIFACT, creature, or land | targeted | one-shot spell (instant) | until its controller's next untap | yes |
| 34 | Renegade Silent | Creature — Alien Horror | itself (creature) | self | mandatory trigger, every end step | until its controller's next untap | yes |
| 35 | Ripples of Potential | Instant | ANY PERMANENTS you control that received a counter from the proliferate | chosen, any number | one-shot spell (instant) | until its controller's next untap | yes |
| 36 | Robe of Stars | Artifact — Equipment | equipped creature | equipped | activated {1}{W} | until its controller's next untap | yes |
| 37 | Sandbar Crocodile | Creature — Crocodile | itself (creature) | self | static keyword | keyword square wave | yes |
| 38 | Sapphire Charm | Instant | target creature an opponent controls (one mode) | targeted | one-shot spell (instant) | until its controller's next untap | yes |
| 39 | Shimmer | Enchantment | GRANTS phasing to each land of a chosen land type (all players) | chosen once, as it enters | static | keyword square wave | yes |
| 40 | Shimmering Efreet | Creature — Efreet | itself; and target creature when it phases in | targeted | static keyword + mandatory trigger | until its controller's next untap | yes |
| 41 | Slip Out the Back | Instant | target creature | targeted | one-shot spell (instant) | until its controller's next untap | yes |
| 42 | Spatial Binding | Enchantment | prevents: target permanent can't phase out | targeted | activated (pay 1 life) | until your next upkeep | yes |
| 43 | Spectral Adversary | Creature — Spirit | up to N other target ARTIFACTS, CREATURES and/or ENCHANTMENTS | targeted, up to N | optional ('may pay') ETB, then reflexive trigger | until its controller's next untap | yes |
| 44 | Syr Konrad's Squire | Creature — Human Knight | nothing (reacts to being phased out) | - | triggered (reaction only) | - | NO (un-/acorn/plane/token, not constructed-legal) |
| 45 | Talon Gates of Madara | Land — Gate | up to one target creature | targeted (up to one) | mandatory ETB trigger | until its controller's next untap | yes |
| 46 | Taniwha | Legendary Creature — Serpent | itself; and ALL LANDS YOU CONTROL | all | static keyword + mandatory trigger, every upkeep | until its controller's next untap | yes |
| 47 | Teferi's Curse | Enchantment — Aura | GRANTS phasing to enchanted ARTIFACT or creature | enchanted | static (Aura) | keyword square wave | yes |
| 48 | Teferi's Drake | Creature — Drake | itself (creature) | self | static keyword | keyword square wave | yes |
| 49 | Teferi's Honor Guard | Creature — Human Knight | itself (creature) | self | activated {U}{U} | until its controller's next untap | yes |
| 50 | Teferi's Imp | Creature — Imp | itself (creature) | self | static keyword | keyword square wave | yes |
| 51 | Teferi's Isle | Legendary Land | itself (LAND) | self | static keyword | keyword square wave | yes |
| 52 | Teferi's Protection | Instant | ALL permanents you control | all | one-shot spell (instant) | until its controller's next untap | yes |
| 53 | Teferi's Realm | World Enchantment | ALL NONTOKEN permanents of one chosen type: artifact / creature / land / non-Aura enchantment | the upkeep player chooses | mandatory trigger, every player's upkeep | until its controller's next untap | yes |
| 54 | Teferi's Reproach | Instant | ALL NONLAND permanents target opponent controls | all (of one opponent) | one-shot spell (instant) | until its controller's next untap | yes |
| 55 | Teferi's Veil | Enchantment | each creature you control that attacked | fixed | mandatory trigger | until its controller's next untap | yes |
| 56 | Teferi, Master of Time | Legendary Planeswalker — Teferi | target creature you don't control | targeted | loyalty ability (-3) | until its controller's next untap | yes |
| 57 | Teferi, Timeless Voyager | Legendary Planeswalker — Teferi | each creature target opponent controls | all (of one opponent) | loyalty ability (-8) | they can't phase in until end of your next turn | yes |
| 58 | Temporal Firestorm | Sorcery | up to X creatures/planeswalkers you control | chosen | one-shot spell (sorcery) | until its controller's next untap | yes |
| 59 | The City on the Edge of Forever | Enchantment — Saga | ALL artifacts and creatures | all | mandatory chapter I (Saga) | until its controller's next untap (but a 0/1 Human token stops phase-in) | yes |
| 60 | The Doctor's Childhood Barn | Plane — Gallifrey | one target nonland permanent per opponent | targeted | triggered on chaos (die roll) | until a player planeswalks | NO (un-/acorn/plane/token, not constructed-legal) |
| 61 | The Moment | Legendary Artifact | target creature you control | targeted | activated {2},{T} | until The Moment leaves | yes |
| 62 | The Pandorica | Legendary Artifact | another target NONLAND PERMANENT | targeted | activated {1}{W},{T}, sorcery speed (repeatable) | until The Pandorica untaps or leaves | yes |
| 63 | The Phasing of Zhalfir | Enchantment — Saga | another target NONLAND PERMANENT | targeted | MANDATORY triggers, chapters I and II | until you stop controlling the Saga | yes |
| 64 | The War Doctor | Legendary Creature — Time Lord Doctor | nothing (counts phase-outs) | - | triggered (reaction only) | - | yes |
| 65 | Time and Tide | Instant | all creatures with phasing (and phases in all phased-out creatures) | all | one-shot spell (instant) | - | yes |
| 66 | Tolarian Drake | Creature — Drake | itself (creature) | self | static keyword | keyword square wave | yes |
| 67 | U.S.S. Defiant, Mirror Migrant | Legendary Artifact — Spacecraft | itself (artifact) and up to one target creature you control | targeted (up to one) | mandatory ETB trigger | until its controller's next untap | yes |
| 68 | Unite the Coalition | Instant | target PERMANENT (any); mode may be chosen up to 5 times | targeted | one-shot spell (instant) | until its controller's next untap | yes |
| 69 | Unyaro | Plane — Zhalfir | all creatures | all | mandatory trigger (plane) | until a player planeswalks | NO (un-/acorn/plane/token, not constructed-legal) |
| 70 | Vanishing | Enchantment — Aura | enchanted creature | enchanted | activated {U}{U} (Aura) | until its controller's next untap | yes |
| 71 | Vaporous Djinn | Creature — Djinn | itself (creature) | self | mandatory trigger every upkeep unless you pay | until its controller's next untap | yes |
| 72 | Vision Charm | Instant | target ARTIFACT (one mode) | targeted | one-shot spell (instant) | until its controller's next untap | yes |
| 73 | Vision, Synthezoid Avenger | Legendary Artifact Creature — Robot Hero | itself (artifact creature) | self (modal) | mandatory modal trigger | until its controller's next untap | yes |
| 74 | Vodalian Illusionist | Creature — Merfolk Wizard | target creature | targeted | activated {U}{U},{T} | until its controller's next untap | yes |
| 75 | Vronos, Masked Inquisitor | Legendary Planeswalker — Vronos | up to two other target planeswalkers you control | targeted | loyalty ability (+1), delayed to next end step | until its controller's next untap | yes |
| 76 | Warping Wurm | Creature — Wurm | itself (creature) | self | static keyword + upkeep trigger unless you pay | keyword square wave | yes |

## 3. Oracle text, quoted exactly as Scryfall returns it

For every card that can phase a non-creature permanent other than a card's own creature self, plus every card that
grants phasing, plus the blockers/guards (Spatial Binding, Human). `//` separates faces.

**Unite the Coalition** (Instant, dmc)
> Choose five. You may choose the same mode more than once.
> • Target permanent phases out.
> • Target player draws a card.
> • Exile target player's graveyard.
> • Unite the Coalition deals 2 damage to any target.
> • Destroy target artifact or enchantment.

**Clever Concealment** (Instant, msc)
> Convoke (Your creatures can help cast this spell. Each creature you tap while casting this spell pays for {1} or one mana of that creature's color.)
> Any number of target nonland permanents you control phase out. (Treat them and anything attached to them as though they don't exist until your next turn.)

**The Pandorica** (Legendary Artifact, who)
> You may choose not to untap The Pandorica during your untap step.
> {1}{W}, {T}: Untap another target nonland permanent, then it phases out. It can't phase in for as long as The Pandorica remains tapped. When The Pandorica becomes untapped or leaves the battlefield, that permanent phases in. Activate only as a sorcery.

**The Phasing of Zhalfir** (Enchantment — Saga, dmu)
> Read ahead (Choose a chapter and start with that many lore counters. Add one after your draw step. Skipped chapters don't trigger. Sacrifice after III.)
> I, II — Another target nonland permanent phases out. It can't phase in for as long as you control this Saga.
> III — Destroy all creatures. For each creature destroyed this way, its controller creates a 2/2 black Phyrexian creature token.

**Spectral Adversary** (Creature — Spirit, mid)
> Flash
> Flying
> When this creature enters, you may pay {1}{U} any number of times. When you pay this cost one or more times, put that many +1/+1 counters on this creature, then up to that many other target artifacts, creatures, and/or enchantments phase out.

**Disciple of Caelus Nin** (Creature — Human Wizard, brc)
> When this creature enters, starting with you, each player chooses up to five permanents they control. All permanents other than this creature that weren't chosen this way phase out.
> Permanents can't phase in.

**Teferi's Protection** (Instant, 2x2)
> Until your next turn, your life total can't change and you gain protection from everything. All permanents you control phase out. (While they're phased out, they're treated as though they don't exist. They phase in before you untap during your untap step.)
> Exile Teferi's Protection.

**Perch Protection** (Instant, plst)
> Gift an extra turn (You may promise an opponent a gift as you cast this spell. If you do, they take an extra turn after this one.)
> Create four 2/2 blue Bird creature tokens with flying. If the gift was promised, all permanents you control phase out, and until your next turn, your life total can't change and you gain protection from everything.
> Exile Perch Protection.

**Teferi's Reproach** (Instant, frc)
> Choose target opponent. Until that player's next turn, they gain protection from everything and their life total can't change. All nonland permanents they control phase out. (While they're phased out, they're treated as though they don't exist. They phase in before that player untaps during their next untap step.)
> Exile Teferi's Reproach.

**Ripples of Potential** (Instant, eoc)
> Proliferate, then choose any number of permanents you control that had a counter put on them this way. Those permanents phase out. (To proliferate, choose any number of permanents and/or players, then give each another counter of each kind already there. Treat phased-out permanents and anything attached to them as though they don't exist until their controller's next turn.)

**Teferi's Realm** (World Enchantment, vis)
> At the beginning of each player's upkeep, that player chooses artifact, creature, land, or non-Aura enchantment. All nontoken permanents of that type phase out. (While they're phased out, they're treated as though they don't exist. Each one phases in before its controller untaps during their next untap step.)

**Equipoise** (Enchantment, vis)
> At the beginning of your upkeep, for each land target player controls in excess of the number you control, choose a land that player controls, then the chosen permanents phase out. Repeat this process for artifacts and creatures. (While they're phased out, they're treated as though they don't exist. They phase in before that player untaps during their next untap step.)

**Taniwha** (Legendary Creature — Serpent, mir)
> Trample
> Phasing (This phases in or out before you untap during each of your untap steps. While it's phased out, it's treated as though it doesn't exist.)
> At the beginning of your upkeep, all lands you control phase out. (They phase in before you untap during your next untap step.)

**Reality Ripple** (Instant, mir)
> Target artifact, creature, or land phases out. (While it's phased out, it's treated as though it doesn't exist. It phases in before its controller untaps during their next untap step.)

**Vision Charm** (Instant, vis)
> Choose one —
> • Target player mills four cards.
> • Choose a land type and a basic land type. Each land of the first chosen type becomes the second chosen type until end of turn.
> • Target artifact phases out. (While it's phased out, it's treated as though it doesn't exist. It phases in before its controller untaps during their next untap step.)

**The City on the Edge of Forever** (Enchantment — Saga, trk)
> (As this Saga enters and after your draw step, add a lore counter. Sacrifice after III.)
> I — All artifacts and creatures phase out. Create a 0/1 white Human creature token with "Permanents can't phase in." (Treat phased-out permanents and anything attached to them as though they don't exist.)
> II — You draw two cards and each player loses 2 life.
> III — Sacrifice a creature token. If you do, you gain 5 life.

**The Doctor's Childhood Barn** (Plane — Gallifrey, who)
> Creatures enter tapped.
> Whenever chaos ensues, for each opponent, choose up to one target nonland permanent that opponent controls. Untap those permanents. They phase out. They can't phase in for as long as The Doctor's Childhood Barn remains face up. When a player planeswalks, those permanents phase in.

**Vronos, Masked Inquisitor** (Legendary Planeswalker — Vronos, cmm)
> +1: Up to two other target planeswalkers you control phase out at the beginning of the next end step. (Treat them and anything attached to them as though they don't exist until your next turn.)
> −2: For each opponent, return up to one target nonland permanent that player controls to its owner's hand.
> −7: Target artifact you control becomes a 9/9 Construct artifact creature and gains vigilance, indestructible, and "This creature can't be blocked."

**Temporal Firestorm** (Sorcery, dmu)
> Kicker {1}{W} and/or {1}{U} (You may pay an additional {1}{W} and/or {1}{U} as you cast this spell.)
> Choose up to X creatures and/or planeswalkers you control, where X is the number of times this spell was kicked. Those permanents phase out.
> Temporal Firestorm deals 5 damage to each creature and each planeswalker.

**Divine Smite** (Instant, afr)
> Target creature or planeswalker an opponent controls phases out. If that permanent is black, exile it instead. (If it phases out, treat it and anything attached to it as though they don't exist until its controller's next turn.)

**U.S.S. Defiant, Mirror Migrant** (Legendary Artifact — Spacecraft, trc)
> Flash
> When U.S.S. Defiant enters, it and up to one target creature you control phase out. (Treat them and anything attached to them as though they don't exist until your next turn.)
> Station
> 8+ | Flying

**Teferi's Isle** (Legendary Land, mir)
> Phasing (This phases in or out before you untap during each of your untap steps. While it's phased out, it's treated as though it doesn't exist.)
> Teferi's Isle enters tapped.
> {T}: Add {U}{U}.

**Katabatic Winds** (Enchantment, vis)
> Phasing (This phases in or out before you untap during each of your untap steps. While it's phased out, it's treated as though it doesn't exist.)
> Creatures with flying can't attack or block, and their activated abilities with {T} in their costs can't be activated.

**Kaito Shizuki** (Legendary Planeswalker — Kaito, neo)
> At the beginning of your end step, if Kaito entered this turn, he phases out.
> +1: Draw a card. Then discard a card unless you attacked this turn.
> −2: Create a 1/1 blue Ninja creature token with "This token can't be blocked."
> −7: You get an emblem with "Whenever a creature you control deals combat damage to a player, search your library for a blue or black creature card, put it onto the battlefield, then shuffle."

**Vision, Synthezoid Avenger** (Legendary Artifact Creature — Robot Hero, msc)
> Flying
> Whenever a player casts a spell, if it isn't that player's turn, choose one —
> • Put a +1/+1 counter on Vision.
> • Vision phases out. (Treat him and anything attached to him as though they don't exist until your next turn.)

**Crystal Golem** (Artifact Creature — Golem, mir)
> At the beginning of your end step, this creature phases out. (While it's phased out, it's treated as though it doesn't exist. It phases in before you untap during your next untap step.)

**Teferi's Curse** (Enchantment — Aura, mir)
> Enchant artifact or creature
> Enchanted permanent has phasing. (It phases in or out before its controller untaps during each of their untap steps. While it's phased out, it's treated as though it doesn't exist.)

**Cloak of Invisibility** (Enchantment — Aura, mir)
> Enchant creature
> Enchanted creature has phasing and can't be blocked except by Walls. (It phases in or out before its controller untaps during each of their untap steps. While it's phased out, it's treated as though it doesn't exist.)

**Shimmer** (Enchantment, mir)
> As this enchantment enters, choose a land type.
> Each land of the chosen type has phasing. (It phases in or out before its controller untaps during each of their untap steps. While it's phased out, it's treated as though it doesn't exist.)

**Frenetic Efreet Avatar** (Vanguard, pmoa)
> Each permanent you control has phasing. (It phases in or out before you untap during each of your untap steps. While it's phased out, it's treated as though it doesn't exist.)
> At the beginning of your end step, flip a coin. If you win the flip, take an extra turn after this one.

**Spatial Binding** (Enchantment, mir)
> Pay 1 life: Until your next upkeep, target permanent can't phase out.

**Human** (Token Creature — Human, ttrk)
> Permanents can't phase in.

## 4. Answers

### 4a. Which cards can phase an Aura (or any enchantment / any permanent) other than themselves? [read from section 3, classification mine]

Reading "Aura" as "an Aura permanent, token or not, that I put on the board":

| card | reach | chosen / forced | repeatable? | single / mass | until |
|---|---|---|---|---|---|
| **Unite the Coalition** | target permanent (any) | chosen (targeted) | one-shot; the mode can be taken up to 5 times in one cast | up to 5 single targets | N |
| **Clever Concealment** | any number of target nonland permanents you control | chosen | one-shot | any number | N |
| **The Pandorica** | another target nonland permanent | chosen | **activated, repeatable**, but it taps itself and is Legendary, so one held permanent at a time; sorcery speed | single | until Pandorica untaps or leaves (resume is under the player's control) |
| **The Phasing of Zhalfir** | another target nonland permanent | **mandatory trigger** (chapters I and II; a target is required if one exists) | 2 shots per Saga | single | while you control the Saga |
| **Spectral Adversary** | up to N other target artifacts, creatures and/or enchantments | chosen ("may pay", then reflexive trigger) | one-shot per cast | up to N | N |
| **Disciple of Caelus Nin** | everything except itself and what each player chooses to keep (up to 5 each) | mandatory ETB, but each player's keep-set is a choice | one-shot | mass | indefinite: static "Permanents can't phase in" |
| **Teferi's Protection** / **Perch Protection** (gift) | all permanents you control (Auras directly) | forced by the spell, no choice | one-shot | mass | N |
| **Teferi's Reproach** | all nonland permanents target opponent controls | forced, but one target player | one-shot | mass | N |
| **Ripples of Potential** | permanents you control that got a counter from the proliferate | chosen subset | one-shot | any number | N |
| **The Doctor's Childhood Barn** (not legal) | one nonland permanent per opponent | chosen, on a die-roll trigger | — | single | until a planeswalk |
| **Teferi's Realm** | ALL NONTOKEN permanents of one type; the type list is "artifact, creature, land, or non-Aura enchantment" | the upkeep player picks the type (forced mass) | every upkeep | mass | N |

Realm checked [read]: the list says "non-Aura enchantment" and "nontoken", so it **excludes Auras and excludes
tokens**. Ruling: "Does not affect token permanents, only cards." A nontoken land or artifact phases, and takes its
Auras with it (indirectly).

What phases only non-Aura permanent types (so it helps only via the host, 4d): Reality Ripple (artifact, creature or
land), Vision Charm (artifact), Equipoise (lands, artifacts, creatures; mandatory every upkeep), Taniwha (all your
lands; mandatory every upkeep), The City on the Edge of Forever (all artifacts and creatures; once), Teferi's
Isle / Katabatic Winds / Kaito / Crystal Golem / Vision / U.S.S. Defiant (themselves only).

Direct answer to "forced vs chosen, repeatable vs one-shot, single vs mass" for Auras:

- **Forced AND repeatable AND hits an Aura directly: none.** (Realm is forced and repeatable but cannot touch Auras;
  Taniwha and Equipoise never name Auras.)
- **Forced, Aura-capable:** Zhalfir I/II (a target is chosen unless it is unique, two shots), Disciple (mass, indefinite,
  one shot), Teferi's Protection / Reproach (mass, one shot, but the *player* casts them).
- **Chosen, repeatable:** only The Pandorica (one slot).
- **Chosen, one-shot, up to five at once:** Unite the Coalition (any permanent), Clever Concealment, Spectral Adversary.

### 4b. Which cards GRANT phasing to another permanent? [read]

Verified by searching the 76 texts for "has/have/gain(s)/get(s) phasing": exactly four.

| card | grants it to | note |
|---|---|---|
| Teferi's Curse (Aura) | enchanted **artifact or creature** | Aura; not a land, not an Aura/enchantment as printed |
| Cloak of Invisibility (Aura) | enchanted **creature** | |
| Shimmer | **each land of a chosen land type**, all players | static; one type per Shimmer; multiple Shimmers allowed (it is a plain Enchantment, not World) |
| Frenetic Efreet Avatar (Vanguard) | **each permanent you control** | MTGO only, not paper. The only grant that reaches Auras; same-controller, so it flips *everything* at once |

Not grants (checked, as they only phase their own targets or themselves): Vodalian Illusionist, Dream Fighter,
Teferi's Protection, Guardian of Faith, Slip Out the Back, Clever Concealment, Oubliette, Out of Time, Blink Dog,
Reality Ripple, Shimmering Efreet, Teferi's Realm. Cards with printed phasing are listed in the table ("static keyword").

An Aura cannot be given phasing by any printed grant in paper. Two layers could change that, since Curse says
"Enchant artifact or creature" and phasing is granted to the enchanted permanent: any effect that makes an Aura an
**artifact** (found by two extra queries, `o:"permanents are artifacts"`, `o:"are artifacts in addition"`,
`o:"becomes an artifact"`, 70 hits, not read exhaustively):

- **Mycosynth Lattice** (Artifact): "All permanents are artifacts in addition to their other types. All cards that
  aren't on the battlefield, spells, and permanents are colorless. Players may spend mana as though it were mana of any color."
- **Encroaching Mycosynth** (Artifact): "Nonland permanents you control are artifacts in addition to their other types. …"
- **Memnarch** (Legendary Artifact Creature): "{1}{U}{U}: Target permanent becomes an artifact in addition to its other types. (This effect lasts indefinitely.) …" (per-node, repeatable, chosen)
- Liquimetal Coating, Liquimetal Torque, Argent Mutation (until end of turn); Memnarchitect (not legal).

All Vintage/Commander-legal except Memnarchitect. [read]. Under Lattice every phasing effect that names "artifact"
(Curse, Reality Ripple, Vision Charm, Equipoise's artifact pass, Teferi's Realm "artifact") reaches every permanent,
Auras included [inferred from the card texts; no ruling checked for Curse enchanting an Aura-that-is-an-artifact].

### 4c. Mass / type-based phasing as a forced global clock [read + inferred]

| device | what flips | forced? | rhythm (one controller, untap steps U1, U2, …) |
|---|---|---|---|
| keyword phasing on the anchor (Teferi's Isle; or Shimmer on the anchor's land type; or a phasing creature as anchor) | the anchor and, indirectly, the whole term | yes: no choice at all | out at U1, in at U2, out at U3: **hidden from U1 through the opponent's following turn, visible from U2 through the next one** |
| **Taniwha** | all your lands, every upkeep Taniwha is phased in | mandatory trigger; no choice | Taniwha itself has phasing, so the trigger fires every other turn; lands are out from that upkeep until the next untap: a 2-turn square wave, forced, lands only |
| **Teferi's Realm** | all nontoken permanents of the type the upkeep player names | forced given the choice; the choice is real (four options) | out at the upkeep, in at that player's next untap: **visible only between untap and the upkeep trigger resolving**, i.e. one priority window per turn (while the Realm trigger is on the stack). Excludes Auras and tokens; a nontoken anchor land (type "land") takes the whole term with it. Under Lattice ("artifact") it also takes every nontoken Aura. |
| **Equipoise** | for each type (land, artifact, creature) the target player's permanents in excess of yours; you choose which | mandatory but chosen | one-turn rhythm; can be made unique when the excess equals the count |
| Time and Tide / Teferi's Veil / City on the Edge / Out of Time / Unyaro | creatures (and artifacts) only | — | — |

Could any act as a forced clock that alternately hides and reveals *part* of the term? Only the whole term or nothing,
unless interior nodes carry phasing. Every device above flips the *host class* (lands, artifacts, creatures), and the
README term has exactly one such object, the anchor. The clock is **data-independent**: its period is fixed by the
turn structure (four half-turns for the keyword), not by what is on the board. Teferi's Realm's "nontoken" matters
only as a design lever: build the term from **tokens** (Estrid's Mask-style Aura tokens, Flash Photography copies) and
Realm cannot touch it even under Lattice; build it from cards and Realm can.

### 4d. Indirect phasing as the workaround: hosts at argument positions

**Interposed artifact hosts do not exist.** An Aura has one host (303.4d) and the only edge in the encoding is
"attached to". Only Auras, Equipment and Fortifications attach. An artifact can be a host, but a plain artifact is
not attached to anything, so an argument subtree hanging from "its own artifact" has no edge to the spine. Equipment
attaches to creatures only (L7: 704.5p, 301.5c) and Fortifications to lands, which cannot themselves be attached.
So the chain cannot pass through a non-Aura node. [inferred from L3/L7 tables, which I took as given]

**What works instead: make the cell itself an artifact.** A cell is an Aura permanent. Under Mycosynth Lattice
(everything), Encroaching Mycosynth (your nonland permanents) or Memnarch (a chosen node, indefinitely) it is also an
artifact, so Teferi's Curse can enchant it ("Enchant artifact or creature") and gives it phasing. That cell phases out
at its controller's untap step and its entire subtree (the argument roots and later cells, 702.26g) goes with it,
and back at the controller's next untap. Cost: one extra Aura (the Curse) per cell, which is itself a child of the
cell and travels with it when the cell is moved, and dies in the 704.5m cascade with it. Not simulated.

Rhythm: out at U1, in at U2, out at U3 (702.26a). The cell is hidden from U1 through the opponent's following turn and
visible from U2 through the opponent's following turn. Phase is set by the turn on which
the Curse resolves (the cell phases out at the controller's next untap) and by the controller of the *cell* (not of
the Curse).

**Is a square wave on an argument useful or harmful? Harmful or inert.**
- Reduction needs the head, x, y, z all visible at the same time: S x y z needs x (move), y (move), z (copy). A
  hidden argument cannot be moved or copied (702.26b), so the cooperative player must wait up to two turns. K's
  discard is unaffected (the junk is garbage anyway).
- The clock cannot depend on the term, so it cannot say "this argument is needed now".
- Two cells with different controllers flip on different untap steps, giving a second phase. With two players, that
  is the most phase structure available (multiplayer would add more); it is a fixed clock, not a counter.

### 4e. Rules subtleties (CR text quoted from L5 Q5 unless marked)

1. **When**: 702.26a: "During each player's untap step, before the active player untaps permanents, all
   phased-in permanents with phasing that player controls "phase out." Simultaneously, all phased-out permanents that
   had phased out under that player's control phase in." Both directions happen in one simultaneous event.
2. **No enter/leave triggers**: 702.26d: "The phasing event doesn't actually cause a permanent to change zones or
   control, even though it's treated as though it's not on the battlefield and not under its controller's control while
   it's phased out. Zone-change triggers don't trigger when a permanent phases in or out. Tokens continue to exist on
   the battlefield while phased out. Counters and stickers remain on a permanent while it's phased out." 702.26j:
   "Abilities that trigger when a permanent becomes attached or unattached from an object or player don't trigger when
   that permanent phases in or out." Rulings agree (Pandorica, Oubliette: "Phasing out doesn't cause any "leaves the
   battlefield" abilities to trigger. Similarly, phasing in won't cause any "enters the battlefield" abilities to
   trigger.") [read]
3. **Nonexistent**: 702.26b: "…a phased-out permanent is treated as though it does not exist. It can't affect or be
   affected by anything else in the game." Rulings: "It can't be the target of spells or abilities, its static
   abilities have no effect on the game, its triggered abilities can't trigger…" [read]
4. **Indirect**: 702.26g: "When a permanent phases out, any Auras, Equipment, or Fortifications attached to that
   permanent phase out at the same time. This alternate way of phasing out is known as phasing out "indirectly." An
   Aura, Equipment, or Fortification that phased out indirectly won't phase in by itself, but instead phases in along
   with the permanent it's attached to." 702.26h: "If an object would simultaneously phase out directly and
   indirectly, it just phases out indirectly." That the recursion reaches Auras on Auras is [inferred] from 702.26g
   applying to "a permanent" (L5 says the same); I found no ruling with an Aura-on-Aura example, so a subtree phasing
   out as a whole is [inferred], not [read].
5. **Direct, host gone**: 702.26i: "An Aura, Equipment, or Fortification that phased out directly will phase in
   attached to the object or player it was attached to when it phased out, if that object is still in the same zone or
   that player is still in the game. If not, that Aura, Equipment, or Fortification phases in unattached. State-based
   actions apply as appropriate." Rulings: an Aura "that phases in unattached will be put into its owner's graveyard as
   a state-based action" [read].
6. **SBAs and phased-out Auras**: 704.5m (L5): "If an Aura is attached to an illegal object or player, or is not
   attached to an object or player, that Aura is put into its owner's graveyard." A phased-out object "does not exist"
   (702.26b), so 704.5m does not fire on it while it is out [inferred]. For an Aura whose host phased out directly:
   the Aura phased out indirectly with it (702.26g, 702.26h), so nothing fires either way. For an Aura that phased out
   *directly* while its host stays in: it is simply invisible; its host leaving makes 704.5m act only at phase-in
   (702.26i). So K's discard cascade pauses at the phased-out node and resumes at the controller's next untap.
7. **Target loss**: 608.2b (L5): "If the spell or ability specifies targets, it checks whether the targets are still
   legal… If all its targets, for every instance of the word "target," are now illegal, the spell or ability doesn't
   resolve." Teferi's Protection ruling [read]: "A permanent phasing out causes a spell or ability on the stack to have
   an illegal target if it targets that permanent. As a spell or ability tries to resolve, if all its targets are
   illegal, that spell or ability doesn't resolve and none of its effects happen…" So **a parked spell targeting a
   node fizzles if the node phases out in the meantime**; phasing cannot protect a pointer, it kills it. (Phase-in
   would not restore it: the object that returns is the same object, but the spell has already been removed
   when it tried to resolve [inferred].)
8. **Copy**: 707.2 as used in L7: a token copy copies copiable values, not status, counters or attachments. A
   phased-out permanent cannot be targeted by Flash Photography or Extravagant Replication (702.26b), so it cannot be
   copied by them at all; a copy of a phased-in permanent whose attachments are phased out carries no attachments
   anyway and enters phased in [inferred from 707.2 as stated in L7; "status is not copiable" not rechecked here].
9. **Controller matters**: the phase-in comes at the controller's untap. Rulings: "If a token is phased out, it will
   phase in as your next untap step begins." and "If you gain control of another player's permanent and it phases out,
   if the duration of the control-change effect expires before it phases in, that permanent phases in under that other
   player's control as your next untap step begins." [read]. An Aura's controller and its host's controller can
   differ; a directly phased Aura wakes at its own controller's untap.
10. **Disciple, Human token, City on the Edge**: "Permanents can't phase in" freezes the whole board until the source
    leaves; Disciple's ruling: "If an effect causes a permanent to phase out "until" some event occurs, and that event
    occurs while Disciple of Caelus Nin is still on the battlefield, the phased out permanent stays phased out
    forever." [read]. (A deliberate "never resume" operation, not useful here.)
11. Not rechecked: 702.26c, e, f, k–p beyond the one-line summaries in L5 (and the rule 502.1 text that orders phasing
    before untapping). 702.26p: "Multiple instances of phasing on the same permanent are redundant." (via L5).

## 5. Verdict

**(i) Cooperative "suspend argument, reduce head, resume": available, buys nothing the README machine lacks.**
With real, paper-legal cards you can park a subtree: **Unite the Coalition** (instant, any permanent, up to five
targets, back at the controller's next untap), **Clever Concealment** (your nonland permanents), **The Pandorica**
(sorcery speed, one slot, you control the resume). Park the cell and the whole chain below it goes with it, and
the cascade of K's discard then waits for phase-in (702.26i), so the *visible* board is clean immediately and the
junk dies at the next untap. That is deferred garbage collection and a tidy board. It does **not** give:
(a) protection from the copy/move engine: the engine is the player (Guildmage and Flash Photography are targeted), and
nobody needs protection from himself; it would matter for an automatic engine, but then the same engine needs the
subtree visible when it must act; (b) call-by-need: the README never reduces an argument that is not the head, so there
is nothing to defer, and sharing is impossible anyway (303.4d, one host per Aura; copies do not carry attachments);
(c) a demand signal: phase-in is clock- or player-driven, never "when the head needs it".

**(ii) A forced phasing device usable as mark or window for L7's cursor machine: honest answer, no.**
What exists: forced, repeatable flips of the *anchor class* (Taniwha: lands; Teferi's Realm: nontoken artifact /
creature / land / non-Aura enchantment, with a real four-way choice; keyword phasing on Teferi's Isle or Shimmer;
Equipoise with a choice). None phases an Aura. The only way to put phasing on an interior node is
Lattice / Encroaching Mycosynth / Memnarch + Teferi's Curse, which gives a forced but data-independent square wave
on a cell and its suffix. A cursor machine needs a mark that moves with the term; a clock cannot move with it.
The only forced direct Aura phase-outs (Zhalfir I/II; Disciple; Teferi's Protection/Reproach) are one- or two-shot,
and Zhalfir's target is a choice unless made unique with the L7 angle-2 tricks.

**(iii) Most promising mechanism, or dead end.** Phasing is a **dead end as an enabler of forced reduction**, and only
a convenience for the cooperative player. The least bad mechanism, sketched on K x Ω (Ω any non-normalizing term)
with Lattice on the table: Island ← K ← c1 ← x, c1 ← c2 ← Ω. Cast Unite the Coalition (or put a Curse on c2) so c2
and Ω's entire subtree are phased out. Move x to the Island (Guildmage), sacrifice K (Auratog): c1 goes by 704.5m; c2
is invisible and stays attached to c1's grave; at the controller's next untap it phases in unattached and dies, and
Ω's nodes follow by successive 704.5m. This makes explicit that nothing reduced Ω, but the README already never
touches Ω. On S K K x the same device is harmful: S needs z visible to copy it. A call-by-need or normal-order
*enforcer* is the one conceptual fit I can see: in a hypothetical **forced-parallel** machine (L7's Gross–Knuth
remark) every redex would fire, including ones inside arguments, and hiding argument sub-spines would stop that.
That needs a forced, data-dependent direct phase-out of an Aura, which no card provides. [guessed]; not developed.

## 6. What I did not check

- Gatherer/Scryfall rulings for every one of the 76 cards: I read rulings for 22 (Pandorica, Zhalfir, Unite the
  Coalition, Clever Concealment, Disciple, Realm, Shimmer, Protection, Spectral Adversary, Curse, Equipoise,
  Taniwha, Ripples, Teferi's Isle, Reproach, Oubliette, Reality Ripple, Cloak, the Barn, Time and Tide, Perch
  Protection, the Avatar). Teferi's Curse, Taniwha, Reality Ripple, Cloak, Time and Tide, Teferi's Isle have
  no rulings. Nothing says whether Curse can enchant an Aura made an artifact by Lattice.
- The Comprehensive Rules were not refetched (an attempt to download the whole page was blocked); 702.26 and 608.2b
  are quoted as L5 and L2 recorded them. Rules 502.1, 702.26c/e/f/k–o, 707.2's exact status wording, 603.3b and the
  APNAP ordering of simultaneous upkeep triggers were not rechecked.
- Whether an Aura-on-Aura subtree phases out recursively under 702.26g: inferred only, no ruling with that shape.
- Mana costs and castability of the card set (Unite the Coalition is a 5-mode spell; Clever Concealment's convoke;
  Pandorica's {1}{W}); not tallied against the "11 cards" budget of the README.
- The artifact-granting sweep (`becomes an artifact`) returned 70 cards of which I looked at the first page only;
  other "all permanents are artifacts" style effects may exist. Layer interactions of Lattice with Auras (613) not
  checked.
- Multiplayer phase offsets (more than two controllers) and control-changing nodes as phase shifters: noted, not worked out.
- No simulation: the S K K x / K x Ω traces above are hand traces, not run through `lines/L7` or the L3 simulator.
- Scryfall's search matches reminder text; "o:" phrasings other than those listed (e.g. "phase them out", "phase it
  out") were covered only through the broad `o:phase` and regex sweeps filtered locally.
