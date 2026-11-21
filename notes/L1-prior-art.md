# L1 — Prior art on computation in Magic: the Gathering

Date: 2026-11-21. Surveyor: L1 subagent (dispatched by dara). Question: PLAN.md.

Provenance legend. **[read]** = I fetched the page/PDF this session. Several pages were read through
WebFetch, which returns a model-written summary, not verbatim text; those are marked **[read, summarized]**
and card names/numbers in them should be re-checked against the PDF before being quoted in a paper.
**[search]** = only a search-result snippet seen. **[recall]** = my memory, unverified. **[infer]** = my inference.

## Bottom line

- Nothing found that embeds lambda calculus, SKI/combinatory logic, a stack machine as such, term rewriting,
  or functional programming in MtG. Every serious construction is a Turing-machine / register-machine
  style embedding. (Queries listed in section 3.)
- Two constructions exist: (a) Churchill–Biderman–Herrick (CBH), a (2,18) UTM on a creature-token tape;
  (b) Yin–Churchill (FUN 2024), a 12-register / unbounded-memory / return-stack microcontroller,
  one program instruction per ~turn cycle. Both are forced (no player choices) and both avoid "may".
- The nearest thing to a "native" data structure in prior art: (b) uses counters-on-tokens as integers,
  a *return stack of phased-out tokens* (a genuine linked stack, section 1b), and library order as a cyclic
  program tape. Nothing uses the play stack (rules sense) as a computation device in a published construction.
- The "huge damage without infinite" community work is about fast growth via doubling/copy effects, not
  about universal computation; I could not retrieve the richest sources (section 2d).

## 1. Churchill, Biderman, Herrick, "Magic: The Gathering is Turing Complete"

- arXiv:1904.09828 (v2). https://arxiv.org/abs/1904.09828 ; HTML https://ar5iv.labs.arxiv.org/html/1904.09828 ;
  published at FUN 2021 (LIPIcs), https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FUN.2021.9 ;
  author copy https://www.toothycat.net/~hologram/Magic/LIPIcs.FUN.2021.9.pdf.
  Status: [read, summarized] the ar5iv HTML (arxiv.org/pdf returned only compressed streams; I saw just the
  section headings). The mechanism below is the summary's account; the `Rules` and card-count details are
  not independently checked against the PDF.

**Theorem.** A two-player game (Alice, Bob), all moves after setup forced, where Alice wins iff Rogozhin's
(2,18) universal Turing machine halts. Hence the outcome of a forced end-game is undecidable. Non-halting
manifests as an infinite deterministic loop, a draw under rule 104.4b (mandatory loop).

**Tape.** Cells are creature tokens. Symbol = creature type (18 types, Aetherborn ... Sliver). Position
relative to the head = power/toughness: the head cell is a 2/2; green tokens (3/3, 4/4, ...) to the left,
white tokens to the right, so the size says the distance from the head. Control tracks the head: Bob controls
the tape except the newest token, which Alice takes via Illusory Gains. Unbounded tape: a green Lhurgoyf and a
white Rat mark the ends; Shared Triumph naming Lhurgoyf/Rat grows the end markers, and Cephalid (blank)
fills new cells.

**State.** Two states (q1, q2) = two sets of Rotlung Reanimators + Xathrid Necromancers (the transition rules).
Cloak of Invisibility phases one set out; only one set is phased in at a time. Phasing toggles at the
controller's turn start; a normal cycle lasts 4 turns each, a state-changing cycle 3, shifting the phase.
Changing state replaces seven of Bob's Rotlung Reanimators by Xathrid Necromancers (which make tapped tokens).

**Read / write.** Alice casts Infest (-2/-2 to all), which kills the head token; the Reanimator/Necromancer
keyed to that creature type triggers ("Whenever Rotlung Reanimator or another Cleric dies, create a 2/2 black
Zombie" -- the text is *edited* per rule). The new token's type is the symbol written; its colour is the
direction (white left, green right). Text-changing: Artificial Evolution (creature-type words), Glamerdye
(colour words), Prismatic Lace (colours), Olivia Voldaren (hacked to give a type) so each generic Reanimator
becomes a specific transition rule. Illusory Gains steals the newest token.

**Moving the head.** Cleansing Beam (2 damage to the head and every creature sharing its colour);
Privileged Position + Steely Resolve (naming Assembly-Worker, with Olivia giving that type) restrict targeting
so the head token is the only legal target; Vigor (one per player) converts prevented damage into +1/+1
counters (net two counters on the tokens on the side the head leaves); Soul Snuffers (-1/-1 counter on each
creature) and two Dread of Night (hacked: "Black creatures get -1/-1") shrink/kill; Prismatic Lace and Fungus
Sliver keep the infrastructure alive.

**Forcing everything.** Wild Evocation (each upkeep each player casts a random card from hand, free if able);
Wheel of Sun and Moon (resolved cards go to library bottom, preserving order -- a "recycling" device);
Choke (Alice's single Island never untaps, so she cannot cast anything otherwise); Blazing Archon (both
players; creatures can't attack you); Recycle (Bob skips draw, so no decking); Mesmeric Orb (mills Alice, with
Wheel redirecting to the bottom).

**Halting.** Coalition Victory (a land of each basic type and a creature of each colour); Prismatic Omen
(Alice's one land has all basic types) and Prismatic Lace (all colours but blue); reading symbol 17 in state A
makes a phased-in Reanimator create a blue Assassin under Alice, completing the colours -> Alice wins.

**Full card list (Table III, 60-card Legacy deck) [read, summarized]:**
Bootstrap/mana: 4 Ancient Tomb, 4 Lotus Petal, 4 Grim Monolith, 4 Power Artifact, 4 Gemstone Array, 4 Staff of
Domination. Tokens: Memnarch, Stolen Identity. Editing: Artificial Evolution, Olivia Voldaren, Glamerdye,
Prismatic Lace, Donate, Reality Ripple. Logic: Rotlung Reanimator, Cloak of Invisibility, Infest, Cleansing
Beam, Soul Snuffers, Illusory Gains, Privileged Position, Steely Resolve, Vigor, Fungus Sliver, Dread of Night.
Forced play: Wild Evocation, Wheel of Sun and Moon. Infinite tape: Shared Triumph. State change: Xathrid
Necromancer, Mesmeric Orb. Halting: Coalition Victory, Prismatic Omen, Choke. Remove choices: Recycle, Blazing
Archon. Setup: Djinn Illuminatus, Reito Lantern, Claws of Gix, Riptide Replicator, Capsize. Cleanup: Karn
Liberated, Fathom Feeder. (The table lists 1 of each except where counts shown.) Setup: Ancient Tomb/Lotus
Petal bootstrap Grim Monolith + Power Artifact for unbounded colourless mana, Gemstone Array gives colours,
Staff of Domination draws the deck, Stolen Identity/Memnarch make token copies, Riptide Replicator + Capsize
build the tape, Karn Liberated exiles the setup permanents.

**Rules the paper leans on [read, summarized]:** 104.4b (mandatory infinite loop = draw; the summary says the
paper does not use the phrase "mandatory loop"); APNAP trigger ordering (active player's triggers go on the
stack first); the untap step gives no priority; deliberate avoidance of "may" effects (the 2012/2014 versions
needed "may" choices to be taken, which broke determinism); tournament-rules "shortcuts" for skipping
loops. Conjectures about move-legality/transition computability left open.

**Relevance to us.** We do NOT want its tape/UTM route. Reusable: forced-trigger discipline (section 5),
text hacking, phasing as a *conditional enabling switch*, Wheel of Sun and Moon as an order-preserving recycler,
single-legal-target engineering, and the lesson that "forcedness" is the dominant card cost (about half
the deck).

## 2. Other constructions

### 2a. Churchill's earlier Turing machine (2010-2014) and website
- Site: https://toothycat.net/~hologram/Turing/About.html (overview), Cards.html, HowItWorks.html,
  Difficulties.html, Future.html (older versions). [read, summarized]; the pages were thin.
- Origin: a 2010 Draw3Cards.com question "Is Magic Turing-complete?". Versions 1-4 used Wolfram's (2,3)
  machine (universal by Alex Smith's proof; Churchill notes they lacked the non-repeating tape so were not
  truly universal), built from tokens with Teysa, Orzhov Scion + Mind Bend triggers on three token colours,
  and Time and Tide (cast via Isochron Scepter, Spellbinder, Toshiro Umezawa, Chancellor of the Spires in
  successive versions) to phase state sets. These needed player "may" choices (Kazuul Warlord, scepter
  activation). Version 4 was the 2012 internet-famous one (Boing Boing 2012-09-12).
- Version 5 (the "current" page): Rogozhin (2,18). Tape = two chains of tokens, Zombies to the right of the head
  and Yetis to the left; distance = toughness (cell next to head has toughness 1, next 2, ...); symbol =
  creature type (1-18), side = Zombie/Yeti. Move right: new Yeti created, Yetis +1, Zombies -1 so the smallest
  Zombie dies (done with Kazuul Warlord and Noxious Ghoul; +1/+1 vs -1/-1 effects). 43 Rotlung Reanimators
  (hacked by Artificial Evolution) are the transition rules. State change = Time and Tide phasing Reanimator sets
  (Chancellor of the Spires recurred by Necroskitter / Gather Specimens, killed by Tajuru Archer / Blight
  Sickle). Out-of-tape: a Construct created at the bottom of the stack... (the page says "a Construct ability
  at the bottom of the stack"; I do not understand the mechanism from the summary -- unverified). Halting: Vengeful
  Dead with Aether Flash killing an Assassin. Churchill's stated goal of version 6: remove all "may" (Cathars'
  Crusade for Kazuul Warlord; Omen Machine or Wild Evocation to force Time and Tide).
- Difficulties page: states the tape problem (zones are unordered; stack, graveyard, library do not make a
  tape, so tokens of different sizes are used), casting an instant from a trigger, and running out of tape.

### 2b. Yin & Churchill, "A Programming Language Embedded in Magic: The Gathering" (FUN 2024)
- https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FUN.2024.31 ; PDF
  https://drops.dagstuhl.de/storage/00lipics/lipics-vol291-fun2024/LIPIcs.FUN.2024.31/LIPIcs.FUN.2024.31.pdf ;
  full version https://www.toothycat.net/~hologram/Magic/Magic_Microcontroller_full.pdf ; simulator
  https://www.toothycat.net/~hologram/Magic/MTGProgSimulatorText.html . [read: I extracted the text with
  pdftotext and read sections 1-6 and Appendix B.28-B.32 myself.]
- **Language.** 12 registers r0..r11 (arbitrary non-negative integers), unbounded addressed memory, one Boolean
  flag, plus Set/Zero/Add/Add1/Halve/SubCond/Mult/DivCeil/Load/Store/jumps (relative, cyclic program)/
  CallFwd/CallBwd/CallBwdR/Return/comparisons/inputs (Alice/Bob choose integers)/Rand6/Rand20/Halt{D,A,B}.
  A superset of a Melzak-style register machine. Sample programs: Collatz counterexample search, Nim.
  Speed: about one cycle of turns per instruction (vs. billions of turns for 1+1 on the UTM: the paper
  reports 3,958,876,878 game cycles for a 2-state unary adder computing 1+1, and over 40 million tape symbols
  for 2+3 with the straightforward compiler).
- **Program = library order.** The program is a cyclic sequence of basic lands (12 symbols incl. snow-covered and
  Wastes) in Alice's library. Three combat phases per turn (Bloodthirster + double strike gives extra combats)
  each read one card: Vaevictis Asmadi, the Dire (edited to a 1/1) makes Alice sacrifice the "program permanent"
  and reveals the next library card onto the battlefield; Wheel of Sun and Moon sends the sacrificed card to the
  library bottom, so the library rotates. Bob has Tajuru Preserver so he does not sacrifice.
- **Conditional enabling = the core trick.** Every "instruction permanent" is made a creature with a type X_n,
  all X_n creatures become Saprolings (via edited Dralnu's Crusade), Life and Limb makes Saprolings lands,
  Blood Sun removes all abilities from lands. Twelve Dralnu's Crusade tokens (forced to attack with Grand Melee;
  only flyers/islandwalkers can attack due to Stormtide Leviathan) get +1/+1 from a Strata Scythe imprinted with
  the corresponding basic land; only the boosted one is blocked by Bob's Dream Fighter, and both phase out,
  which un-Saprolings the creatures of the matching type for the rest of the turn cycle. So "read a card"
  = "phase out the card that disables type X_n". Three position-slots (X, Y, Z) with disjoint type families.
- **Registers = counters.** Register r_n is a token Joraga Warcaller (Elves get +1/+1 per +1/+1 counter on it);
  value = number of +1/+1 counters; the active register is the one whose disabling Crusade is phased out.
  Memory slot at address A with value V = a Mouse token with V/V base and A counters (zero = no token).
  Flag = a card in Bob's library (0) or hand (1), toggled by Wheel (discard) and Tomorrow, Azami's Familiar (draw).
- **Return stack = linked tokens (B.29-B.31).** Each stack entry is an Oubliette token copy with +1/+1
  counters encoding the return offset; each new push token phases out the previous top (Arwen, Weaver of
  Hope adds the counters; its phase-out ability is aimed at the previous top; Spellbane Centaur keeps it off other
  blue creatures); Return pops by destroying the top (wither damage adjusts the counters, Sosuke destroys it)
  which phases the earlier token back in. Empty stack -> a Celestial Convergence phases in and the game draws.
  This is the only genuine "spine" stack I found in prior art; it works through *phasing as a pointer*.
- **Targeting discipline.** "Masked Gorgon" edits give protection from creature types so that exactly one legal
  target exists (colour-/type-coded: only red creatures targetable by Reflections, etc.); Spectral Guardian,
  Sterling Grove, Ivory Mask make most things untargetable; abilities with zero legal targets never go on the
  stack.
- Forcedness cards: Grand Melee, Stormtide Leviathan, Worship (both players at 1 life; damage still dealt so
  triggers fire), Root Maze + Choke (program permanents enter tapped and stay tapped), Recycle, Mirror Gallery,
  Suppression Bonds, Stony Silence, Cursed Totem, Corrosive Mentor. Card-modification techniques in Appendix B
  of the full paper (Artificial Evolution, Mind Bend, Prismatic Lace, Urza Prince of Kroog + Memnarch for
  token copies of noncreatures, Progenitor Mimic copying then overriding types, Bludgeon Brawl, ...).
- Relevance: closest published thing to a "machine with a stack"; but program/data are not terms, and unbounded
  data lives only in counters on tokens. [infer] A combinator evaluator could reuse the *phasing-pointer linked
  stack* and the *counter-valued variables*, not the instruction decoder.

### 2c. Biderman, "Magic: the Gathering is as Hard as Arithmetic"
- arXiv:2003.05119, https://arxiv.org/abs/2003.05119 , HTML https://ar5iv.labs.arxiv.org/html/2003.05119.
  [read, summarized]. Mate-in-n is Delta^0_n-hard (via Post's theorem, one quantifier per turn, a number chosen
  each turn), and optimal play is non-arithmetic in general. Cards added to the CBH toolbox: Delay,
  Clockspinning, suspend (timing); Tetzimoc, Primal Death, Human Frailty, Grave Betrayal, Infernal Reckoning,
  Reality Acid (cleanup); Ageless Entity + Helm of the Host, Daggerdrome Imp, Umbral Mantle, Magus of the
  Coffers, Prismatic Omen, Moat, Choke (tape/head/unbounded black mana); Panoptic Mirror + Cruel
  Entertainment and Teferi's Curse (alternate who controls whose turn, giving a choice gadget). Numbers in
  binary. Not about combinators; relevant only as a source of delay and player-control gadgets.

### 2d. Other complexity / "big number" results
- Chatterjee & Ibsen-Jensen, "The Complexity of Deciding Legality of a Single Step of Magic: the Gathering",
  ECAI 2016, doi:10.3233/978-1-61499-672-9-1432, https://research-explorer.ista.ac.at/record/478 .
  [search] coNP-complete in general (blocking legality, single-player instances suffice); P for restricted card
  sets. Not a computation construction.
- "Large Finite Numbers in a Casual Game", Annatala Wolf, FOM list, 2017-05-03:
  https://cs.nyu.edu/pipermail/fom/2017-May/020475.html . [search] (WebFetch returned 404). Per the snippet: Magic
  forces a player to name a finite number of loop iterations, so numbers must be writable; a better
  recursive strategy exists; links a longer write-up. I have NOT read it.
- MTG Salvation threads: "most turn 1 damage in a deck with no infinite"
  https://www.mtgsalvation.com/forums/magic-fundamentals/magic-general/615089-most-turn-1-damage-in-a-deck-with-no-infinite ;
  a Quanta draft (https://www.quantamagazine.org/wp-content/uploads/2024/11/Massive-Damage-Challenge-Old.pdf)
  reportedly cites a thread "To Graham's Number and beyond" and a 2^^6 example [search only]; I could not read
  either (fetch exceeded size limit; a partial download was truncated). Soniccenter "megacombo" pages
  (https://soniccenter.org/sm/mtg/megacombo.html) blocked automated fetching. So the claim that this community
  work builds fast-growing hierarchies from copy/stack tricks is [search/recall], not verified by me.
- Good Morning Magic / MTGGoldfish record: Devilish Valet + Jaxis/Fable (copy) + Bootleggers' Stash +
  Stimulus Package + Tend the Pests; doubling per creature entering, ~2^31 hit Arena's power cap; the huge
  headline number (5.52e51...) is hypothetical. https://www.mtggoldfish.com/articles/5-521-397-077-432-461-029-947-804-689-821-620-361-960-881-777-736-309-244-130-019-damage-in-standard
  [read, summarized]. Mechanism: a "doubling when a creature enters" counter, iterated by token generators:
  exponential in token count. Arena-specific caps (250 creatures, ~2.1e9 power).
- Zimone, All-Questioning twin-prime combo (fall 2024, Reddit user its-summer-somewhere): copies creatures,
  makes them lands, Zimone triggers when land count is prime (twice in a row at twin primes), so damage is
  unbounded iff the twin prime conjecture holds. https://www.scientificamerican.com/article/magic-the-gathering-fans-harness-prime-number-puzzle-as-a-game-strategy/
  [read, summarized]. It is a *predicate on a counter* (primality of the land count) driving control flow
  inside normal rules: the one example I found of arithmetic done "natively" without Turing-machine scaffolding.
- Star City Games, "Magic Puzzles - Large Numbers", Jeff Till, 2007-02-26 (https://articles.starcitygames.com/articles/magic-puzzles-large-numbers/)
  [read, summarized]: puzzle format for creating unbounded resources with rules caveats (storm copies,
  bounce loops). Gives the flavour of "no infinity, only chosen finite numbers".
- "How to Build a Computer from a Collectible Card Game" (Medium, Super Jump) and Hackaday/Boing
  Boing/MIT Tech Review pieces are popular summaries of CBH [search]; I did not read them.

## 3. Searches for combinator / lambda / stack / rewriting embeddings (honest negative)

Queries tried (web search, standard mode), all returning only CBH, Biderman, Yin-Churchill and popularizations:
1. "Magic: the Gathering" "lambda calculus" OR "combinatory logic" OR "SKI combinator" card game computation
2. Magic the Gathering "stack machine" OR "term rewriting" OR "functional programming" OR "tag system" OR "Fractran" OR "counter machine" cards
3. reddit Magic the Gathering lambda calculus implemented in MTG cards "lambda"
4. "Magic: the Gathering" "Church numerals" OR "Y combinator" OR "beta reduction" OR "Brainfuck" OR "Conway's Game of Life" cards implementation
5. Alex Churchill Magic the Gathering Turing machine toothycat hologram Magic
6. Magic the Gathering most damage without infinite combo copy spells stack exponential community "Busy Beaver" OR "fast-growing"
(plus the topic-specific searches behind sections 1, 2, 4.)
Result: no hit for lambda calculus, SKI/BCKW, combinatory logic, term rewriting, functional programming,
Fractran, counter machine, Church numerals, Y combinator in MtG. Tag systems appear only as a compilation
stage: per Yin-Churchill's intro, someone compiled TM -> 2-tag system -> UTM(2,18) -> Magic (the "author of
[1]", a simulator study; reference [1] not identified by me). Biderman mentions Conway's Life only as analogy
[search]. Search coverage is a web-search engine, not Reddit/Discord/MTG Salvation/Stack Exchange internals;
an absence here does not exclude forum posts. I did not query StackExchange (rpg/puzzling/cs) directly.
Yin-Churchill's intro says CBH made Magic the first widely played tabletop game shown Turing complete in its usual format [read].

## 4. Other card games (brief)

- Yu-Gi-Oh!: arXiv:2603.02863, Nicolosi, Pisciotta, Bresolin, "Optimal play in Yu-Gi-Oh! TCG is hard" (v1, 3 Mar
  2026), retitled "Deciding winning strategies in Yu-Gi-Oh! TCG is hard" (v2, 11 Mar 2026). Exists. https://arxiv.org/abs/2603.02863
  [read, summarized]. Shows deciding whether a computable strategy wins is undecidable (halting reduction),
  Pi^1_1-complete, and extends to all strategies via countable well-orders; two legal decks on the F&L list.
  Substrate (per a search snippet, [search]): configurations encoded in spell counters, the program carried by
  the strategy, not an embedded machine. Not forced-play; it is a strategy-decision result.
- Riftbound: arXiv:2609.33839, Dalaklis & Fields, "Riftbound is Turing Complete" (v1 27 Sep 2026, v2 30 Sep 2026,
  cs.CC). Exists. https://arxiv.org/abs/2609.33839 [read abstract, summarized]. Claims universal Turing machines
  from valid game states with tournament-legal decks; machine can be built and run in a single game turn given
  a suitable board state. The abstract does not say what encodes tape/state; I did not read the full paper.
  Substrate is therefore unverified.

## 5. Toolbox for a native combinator embedding

All items: source in brackets; "[infer]" = my suggestion for reuse, not claimed by sources.

**Forced triggers / removing choice**
- Mandatory-only abilities. Avoid every "may"; use "whenever ... create/put" instead. [CBH, read-summarized]
- Single-legal-target engineering: protection-from-type/colour (Masked Gorgon edits), Privileged Position,
  Spectral Guardian, Sterling Grove, Ivory Mask, shroud via Steely Resolve; an ability with no legal target never
  goes on the stack (a free way to turn a trigger off). [CBH; Yin-Churchill, read]
- Forced combat as a scheduler: Grand Melee (attack/block each combat if able) + Stormtide Leviathan (only
  flyers/islandwalkers attack) + Tetsuko Umezawa, Fugitive (small creatures unblockable); a creature that is
  forced to attack and has exactly one forced blocker gives a deterministic combat outcome. [Yin-Churchill, read]
- Wild Evocation / Omen Machine style "cast the top card" for forced casting; Choke/Root Maze to keep
  alternative sources of plays tapped; Recycle to skip draws; Blazing Archon; Worship to make life totals
  irrelevant while damage still triggers things. [CBH; Yin-Churchill]
- Wheel of Sun and Moon: cards that would go to a graveyard go to the library bottom: an order-preserving
  queue discipline (rotation). [both]
- APNAP: if both players have triggers at once, active player's go on the stack first, so non-active player's
  resolve first; use ownership to fix resolution order. [CBH summary; rule 603.3b, recall]

**Text hacking**
- Artificial Evolution (creature-type words), Mind Bend (colour/basic-land words), Glamerdye (colour words),
  Prismatic Lace (colours), Olivia Voldaren (types), Urza, Prince of Kroog + Memnarch (token copies of
  noncreature permanents), Progenitor Mimic (copy then override types), Bludgeon Brawl (artifact ->
  equipment). Dralnu's Crusade edited as a typed "disable/enable" switch. [CBH; Yin-Churchill Appendix B]
- Layer system (rule 613): timestamps, dependency; rule 305.7 (setting a land's basic type removes other types).
  Yin-Churchill rely on these and track timestamps explicitly. [read]

**Conditional enabling (phasing as a switch / pointer)**
- Phased-out permanents don't exist for the rules (rule 702.26, recall); phasing in/out via Cloak of Invisibility,
  Time and Tide, Dream Fighter (phases itself and any creature it blocks/is blocked by), Arwen, Weaver of Hope.
  Used as: (i) state selector (CBH), (ii) instruction decoder (Yin-Churchill), (iii) linked-stack pointer
  (Oubliette tokens, Yin-Churchill B.29-31). [infer] best candidate for a head-pointer in a graph-reduction
  line.
- Blood Sun/Life and Limb/Saproling trick: a type-keyed global ability-removal with a phased-out exception. [read]

**Unbounded data**
- +1/+1 counters on a token as an unbounded integer; Joraga Warcaller-style "+1/+1 per counter" to broadcast
  it; counters as memory address and value (Mouse token). [Yin-Churchill, read]
- Token position = toughness (CBH tape); Zombie/Yeti sides (Churchill v5). [read]
- Unbounded mana: Grim Monolith + Power Artifact (infinite loop of untap; "may"-free only after setup). [CBH, summarized]
- Token copies exist only on the battlefield; copies of spells/abilities only on the stack (rule 707.10 /
  707.2; recall).

**Unbounded copy on the stack / doubling [recall + the sources of 2d]**
- Doubling Season / Rite of Replication / Devilish Valet style doubling: exponential in a *chosen count*; the
  Valet chain gives exponentials in the number of token entries, which tokens-per-token generators make tower-like.
  In the paper-realizable sense they are bounded by what the player can tally, which is why they are not
  infinite. [read, summarized (MTGGoldfish); the 'tower' remark is [infer]]
- Storm/copy chains on the stack (Grapeshot, Stormfront Riders in the SCG puzzle). [read, summarized]
- None of the prior art uses spell/ability copies as *data*; I found no stack-as-term work. That region is open.

**Rules pitfalls**
- Mandatory loops are draws: rule 104.4b (a loop of mandatory actions with no way to stop); 732 "Taking
  Shortcuts" in the 2026 CR numbering (722.4/729.4/716 in older ones; renumbers across editions, so cite by
  version). Search-snippet quotes only; verify against https://media.wizards.com/2026/downloads/MagicCompRules 20260619.pdf
  before citing. [search]
- "May" abilities and "unless" costs: no player can be forced to break a loop (722.6 in the older numbering),
  so any "may" is a potential deviation point. [search]
- Non-mandatory loops: players must announce an iteration count (shortcut), so "infinite" is always a
  finite named number; tournament rules limit shortcuts. [search + CBH summary]
- Tokens that leave the battlefield cease to exist (rule 111.7, recall; state-based action 704.5d); copies of
  spells cease to exist when they leave the stack (rule 707.10a / 704.5e, recall). So terms stored as tokens
  vanish on bounce or death, while cards persist; this forces the tape-in-tokens design of CBH.
- Hand-size / library-size: Recycle (skip draw) avoids decking; empty library draw is a loss (104.3c, recall).
- Arena/online caps (250 creatures, power cap ~2.1e9) are not paper rules; ignore in paper constructions. [read]
- Legal-deck constraints: Legacy/Vintage tournament legality; 4-of limit; Yin-Churchill note Snow-Covered Wastes
  release date issue (June 2024) in their footnote. [read]
- Setup (reaching the initial board) costs a very long, deck-specific bootstrap in both constructions; any
  "native" construction should say whether it is an end-game board state or a from-scratch deck.

## What I did not check

- The actual text of arXiv:1904.09828 (PDF unreadable via fetch); the card list and mechanism come from a
  summarized HTML version and Table III is not verified card-by-card or with counts. Also not verified: the
  exact rule numbers the paper cites.
- The Yin-Churchill instruction implementations other than B.28-B.32 (read selectively), their decklist
  (Appendix C), and the simulator.
- The 2012-2014 papers/posts (Churchill 2012, Churchill et al. 2014) beyond his website's summaries; the
  Draw3Cards thread; the WotC forum thread mentioned on his site.
- The FOM post (404), the MTG Salvation "most damage" and "To Graham's Number and beyond" threads, the Quanta
  Massive Damage Challenge document (truncated), Soniccenter megacombo pages (blocked), the Good Morning Magic video.
  So any claim of "fast-growing hierarchies" in that community is not established here.
- The full Riftbound paper and the full Yu-Gi-Oh! paper (substrate is a snippet-level claim).
- Chatterjee & Ibsen-Jensen paper itself; Esche (2018); Demaine-Hearn background.
- Reddit, MTG Salvation, Discord, StackExchange, GitHub (searches went through a general web search only);
  Forge/XMage/Cockatrice rule-engine projects that might encode combinators; Wolfram/Alex Smith (2,3) details.
- Current Comprehensive Rules text: all rule numbers (104.4b, 603.3b, 613, 702.26, 704.5d/e, 707.10, 732) are from
  search snippets or memory and need checking against the 2026-06-19 CR.
- Any "Magic-like" proof-assistant or Lean formalization of MtG rules (not searched).
