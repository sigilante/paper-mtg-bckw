# L7 — How much combinator reduction can be FORCED?

Line L7 (P2 forcedness probe). Author: L7 subagent, 2026-11-21.
Model code: `lines/L7/cursor_machine.py`, output `lines/L7/cursor_machine.out` (run `python3 -I`, exit 0).

Provenance tags: **[read]** = Oracle text or ruling as returned by the Scryfall API on 2026-11-21 (one
card or one search page per request), or CR text from the single-page CR at yawgatog.com ("effective as
of November 6, 2026"), fetched once and grepped locally. **[inferred]** = my reading of quoted rules/text;
no ruling found. **[guessed]** = from memory or unchecked. "Forced" means what it means in CBH: no player
choices at all; every step is an SBA or a mandatory trigger/replacement with uniquely determined targets
and choices.

## Summary

1. **Minimal honest statement.** With printed Oracle text, no text-changing, and no addressing layer
   (no position-dependent marks such as colours, control, counters or phasing used to single out a node),
   forced play does exactly one part of combinator reduction on the Aura forest: **erasure** (K's discard,
   by the 704.5m cascade). It completes no reduction step anywhere inside a term. At the **root only**, a
   two-sorted micro-encoding gives a forced K/I-shaped *projection* step with real cards
   (Necrotic Plague + a reconfigure Equipment; worked out below), but it does not compose.
2. **The obstruction is sharper than "one hop".** There are two pointer families on the battlefield.
   *Chainable* pointers (an Aura on a non-creature permanent: the only way to get depth ≥ 2) are exactly
   the ones **no surveyed forced effect can rewire without a player choice**. *Rewirable* pointers
   (onto creatures, lands, players) **cannot chain**, because an attached permanent is never a creature
   (704.5p, 303.4d, 702.151b). Unbounded terms need chains; forced rewiring needs creature hosts. Every
   CL rule moves a surviving subterm to a new host (proved below for any compositional encoding for I and K,
   and checked for all six rules in the spine-chain encoding), so none of them is forced.
3. **With an addressing layer it decomposes.** I built and checked a model (lockstep with a reference
   normal-order reducer on 16 fixed terms and 3000 random ones): full SKI+BCKW normal-order reduction
   on the L3 spine-chain forest, where **every operation touches only objects within one hop of a marked
   object**, driven by a finite control and 14 cursors (marks). Four event kinds suffice: MARK (move a
   cursor one hop), MOVE (re-attach), COPY (one node, no attachments, as 707.2 requires), SAC (+ cascade).
   An S step with atomic arguments costs 10 MARK + 5 MOVE + 1 COPY + 1 SAC; copying an n-node argument costs
   n COPY + about 3n MARK. So "forced S/W" reduces to one question: **can a fixed card set perform MARK,
   MOVE and COPY into non-creature hosts by mandatory triggers with unique legal choices?** SAC is easy.
   MOVE has one printed candidate (Glamer Spinners, which needs uniqueness engineering for both its target
   and its receiver). COPY has one (Extravagant Replication, a forced upkeep copy of a target nonland
   permanent), which needs uniqueness for its target and for the token's 303.4f host. That is
   Churchill-style machinery, and the board then carries a fixed reducer program beside the native term.
4. **Duplication of structure is never one event.** No effect copies attachments (707.2; rulings on
   Second Harvest, Mechanized Production, Mirrormade). Mandatory one-object copiers exist (Followed Footsteps,
   Mechanized Production, Helm of the Host); token doubling (Doubling Season family) is forced and keeps
   "attached to X" for every doubled token, but copies one creation event, not a structure.
5. **The stack does not rescue forcedness.** A single 603.3b ordering choice can decide between
   termination and a mandatory infinite loop (a draw under 104.4b) for `K a Ω`. So trigger ordering is
   harmful, not confluent, and CL's Church–Rosser property does not help (it constrains results, not
   termination of a fixed strategy). A forced design must keep at most one pending trigger per player, or
   use APNAP (two players give a two-level order for free).

## Angles

### Angle 1 — self-moving Auras and mandatory re-attachment

Searches (Scryfall): `t:aura o:"attach ~ to"` (19 cards), `o:"attach it to" -o:"you may attach"` (87),
`o:"to the battlefield attached to" t:aura` (16), `o:"attach" o:"whenever" t:aura -o:"you may attach"` (7),
`o:/attach (target|each|all|that|those) auras?/` (8), `o:"auras attached to"` (12),
`o:"becomes attached" or o:"becomes enchanted" or o:"becomes unattached" or ...` (19),
`o:"equipped creature dies" o:attach` (3), `o:attach (t:aura or o:aura) -t:equipment -o:"equip {" -o:"enchant creature"` (95),
plus single-card lookups. **Every mandatory re-attacher I found puts the object on a creature, a land or
a player** [read]:

- **Illusory Gains** — "Enchant creature / You control enchanted creature. / Whenever a creature an opponent controls enters, attach this Aura to that creature." Rulings: "Illusory Gains's last ability is mandatory." "…doesn't target the new creature." The cleanest forced mover; CBH use it.
- **Nettlevine Blight** — "Enchant creature or land / Enchanted permanent has "At the beginning of your end step, sacrifice this permanent and attach Nettlevine Blight to a creature or land you control."" Ruling: "that player chooses the new creature or land". Forced only if exactly one candidate.
- **Necrotic Plague** — "Enchant creature / Enchanted creature has "At the beginning of your upkeep, sacrifice this creature." / When enchanted creature dies, its controller chooses target creature one of their opponents controls. Return this card from its owner's graveyard to the battlefield attached to that creature." Ruling: "the ability is mandatory; a target must be chosen if able"; with no legal target "it just remains in its owner's graveyard."
- **Infectious Rage** — "When enchanted creature dies, choose a creature at random this Aura can enchant. Return this card to the battlefield attached to that creature." (random, so not deterministic)
- **Gift of Immortality** — "When enchanted creature dies, return that card to the battlefield under its owner's control. Return this card to the battlefield attached to that creature at the beginning of the next end step." (forced; creature)
- **Shifting Shadow** — enchanted creature has "At the beginning of your upkeep, destroy this creature. Reveal cards … until you reveal a creature card. Put that card onto the battlefield and attach Shifting Shadow to it …" (forced; creature; library order)
- **Takklemaggot**, **Breath of Fury**, **Kudzu**, **Steam Vines**: controller's choice of creature/land.
- **Forebear's Blade** — "Whenever equipped creature dies, attach this Equipment to target creature you control." Ruling: with no target it "remains on the battlefield unattached".
- Living weapon (702.92a), For Mirrodin! (702.163a): "When this Equipment enters, create a … creature token, then attach this Equipment to it." Forced; onto a new creature.
- **Glamer Spinners** — "Flash / Flying / When this creature enters, attach all Auras enchanting target permanent to another permanent with the same controller." Rulings: the receiver is chosen on resolution, "must have the same controller as the targeted permanent, and it must be able to be enchanted by all the Auras". **The only mandatory effect found that can move Auras onto a non-creature host**, and it moves *all* Auras of the target (a fan), with a target choice and a receiver choice.
- Activated or "may" only (not forced): Simic Guildmage, Aura Graft, Enchantment Alteration (creature/land), Crown of the Ages and Kitsune Sage (creature), Halvar, Ardenn, Brilliant Wings, Prison Term, Shielded by Faith, Spellweaver Volute, Estrid's Mask token ("−1: Create a white Aura enchantment token named Mask attached to another target permanent. The token has enchant permanent …").

Beyond one hop, the only printed references I found [read]: **Artificer's Hex** ("Enchant Equipment / At the beginning of your upkeep, if enchanted Equipment is attached to a creature, destroy that creature." — two hops, through the Equipment–creature link, and only to destroy), **Face of Divinity** (static, sees a sibling: "As long as another Aura is attached to enchanted creature …"), **Kitsune Mystic** (counts children: "if this creature is enchanted by two or more Auras"), **Carry Away** ("When this Aura enters, unattach enchanted Equipment.").

Why the self-movers cannot reach the chain [read + inferred]: CR 704.5p "If a battle or creature is attached to an object or player, it becomes unattached …"; 303.4d "An Aura that's also a creature can't enchant anything"; 702.151b a reconfigured Equipment stops being a creature while attached; licids "become an Aura enchantment with enchant creature". So **an attached permanent is never a creature**, and every node at depth ≥ 2 sits on a non-creature, so it is an Aura with "enchant permanent/enchantment/artifact". All the forced self-movers above are "enchant creature (or land)" and can only sit at depth 1.

**Program-counter Aura walking the spine: fails with printed text.** A PC walking down an Aura chain needs "attach this to the [cell] attached to enchanted permanent", a forced move onto a non-creature host. No card found does it. The nearest is a Glamer Spinners pulse (see Best path), and that needs unique-target engineering.

To test: a broader Oracle sweep for phrasings I did not query (`put onto the battlefield attached to`, `return … attached to` on non-Aura cards, `exchange`); Gatherer rulings on Glamer Spinners with Aura receivers.

### Angle 2 — unique-legal-target engineering

Rules [read]: 603.3d "If a choice is required when the triggered ability goes on the stack but no legal choices can be made for it … the ability is simply removed from the stack." 601.2c governs target choice. With exactly one legal target the choice is forced. 303.4f governs the host of an Aura that enters other than by resolving: "that player chooses what it will enchant … must choose a legal object", so it is forced only with one legal host. 702.16c: "A permanent or player with protection can't be enchanted by Auras that have the stated quality." So protection shrinks the set of legal hosts.

What can mark "current", with what native reach [read for the cards; uses inferred]:

| marker | how set by a forced one-hop event | how it makes a choice unique | cost/limit |
|---|---|---|---|
| control (2 values) | Confiscate-family Auras ("You control enchanted permanent"), Illusory Gains, Frenzied Fugue | **Sterling Grove** "Other enchantments you control have shroud." makes only the opponent's enchantments targetable; Glamer's receiver must share the target's controller | one bit; everything else on the board must also be shrouded or illegal |
| newest timestamp | any creation | world rule 704.5k ("all except the one that has had the world supertype for the shortest amount of time"), Role rule 704.5z, Illusory Gains goes to the newest | forced deletion or move to the *newest* object: a stack-top pointer, not a tree position |
| phasing | 702.26g phases a whole subtree | phased-out objects "can't affect or be affected" (702.26b) | phasing is downward-closed: you can hide subtrees (e.g. the tail of the spine) but never an ancestor without its descendants; that gives a native *window* "everything not under a phased node". Teferi's Curse ("Enchanted permanent has phasing.") is artifact/creature only; I found no forced phasing of Aura nodes |
| tapped | Malfunction, Psychic Overload ("When this Aura enters, tap enchanted permanent."), Volition Reins (untaps) | Dream Leash's "can't choose an untapped permanent" is cast-time only | few targeting restrictions read tapped status |
| colour / type | text-changing (Artificial Evolution, Glamerdye, Sleight of Mind; L5 2a), "Enchanted permanent is …" Auras (Song of the Dryads, One with the Stars) | protection from a colour (702.16c), shroud-by-type (Steely Resolve, per L1) | this is CBH's toolbox; type-changing is not copied (707.2) |
| "enchanted permanent" of a unique cursor Aura | — | a genuine one-hop unique pointer | but the cursor is then an extra child; the marked node's host is two hops from the cursor object |

Conclusion for angle 2: unique-target engineering can make Glamer Spinners and Aura-token placement forced
**in principle**. Doing so needs, at minimum, the marks of the cursor machine (Angle 4). The board then
carries position-dependent marks, so the structure is no longer carried by attachment alone. Forcedness
buys back exactly the addressing that CBH use for their tape.

### Angle 3 — forced duplication

Mandatory copiers [read]:
- **Followed Footsteps** — "Enchant creature / At the beginning of your upkeep, create a token that's a copy of enchanted creature."
- **Mechanized Production** — "Enchant artifact you control / At the beginning of your upkeep, create a token that's a copy of enchanted artifact. Then if you control eight or more artifacts with the same name as one another, you win the game." Ruling: "It doesn't copy … whether it has any counters on it or Auras attached to it".
- **Helm of the Host** — "At the beginning of combat on your turn, create a token that's a copy of equipped creature, except the token isn't legendary. That token gains haste." (Equipment, creature only)
- **Extravagant Replication** — Enchantment: "At the beginning of your upkeep, create a token that's a copy of another target nonland permanent you control." **The one mandatory copier found that can copy an Aura node** (from search `o:"token that's a copy of" (o:"at the beginning" or o:whenever or o:when) (o:enchantment or o:aura or o:permanent) -o:"you may" -o:"may pay"`, 20 cards). It is forced only if the target is unique, and the token Aura's host (303.4f) is chosen.
- **Endless Evil**, **Ghastly Mimicry** (upkeep copies of the enchanted creature); **Ocelot Pride** (end step; conditional on life gain and the city's blessing; "for each token you control that entered this turn, create a token that's a copy of it").
- Token-doubling replacements, mandatory and unbounded in iteration: **Doubling Season**, **Parallel Lives**, **Anointed Procession** ("If an effect would create one or more tokens under your control, it creates twice that many of those tokens instead."), **Mondrak, Glory Dominus**, **Primal Vigor** (all players). Doubling Season ruling: "Everything that is specified by the effect creating the original token or tokens will also be true about the additional token or tokens …" So a token created "attached to X" is doubled, with both copies attached to X [inferred from the ruling's example of "tapped and attacking"]. The switch is control: only tokens "under your control" double, except with Primal Vigor.

Not forced: Minion Reflector ("you may pay {2}"), Mirror March (coin flips, random), Mimic Vat and Splinter Twin (activated), myriad ("you may create", 702.116a), populate ("choose a creature token", 701.36a), Moonlit Meditation and Mirrormind Crown ("you may instead").

Copies with attachment specified [read]: **Stangg, Echo Warrior** ("For each Aura and Equipment attached to Stangg, create a token that's a copy of it attached to Stangg Twin."), **Arna Kennerüd** ("for each nontoken permanent attached to it, create a token that's a copy of that permanent attached to that creature"), **Three Dog** ("may pay"). Each is one level deep, onto a creature, and needs an attack trigger.

**Is any forced event a structure copy? No** [read + inferred]. 707.2 does not copy status, counters or non-copy effects, and attachments are not copiable values. Second Harvest's ruling: "It doesn't copy … any Auras and Equipment attached to it". Aura copies choose hosts under 303.4f, and the Mirrormade/Copy Enchantment rulings (quoted in L5 Q6) say "You can't choose any permanent cards entering the battlefield at the same time as that Aura". So a batch of simultaneous Aura copies (Second Harvest, or a doubled batch) cannot hang on one another [inferred: the ruling is stated for those cards, and I take it as the general principle]. Doubling a batch doubles each token separately with the attachment its creation effect specifies; it never rebuilds edges between new tokens.

One forced and choice-free copy route exists for Equipment [inferred]. A token copy of an Equipment enters unattached, so there is no 303.4f choice. If the copied Equipment has living weapon or For Mirrodin!, the copy's own ETB creates a creature and attaches to it. So Mechanized Production on a living-weapon Equipment gives, each upkeep, a fresh (Germ + Equipment) unit with no choices. It is depth 1 and useless as a term copier.

### Angle 4 — changing the calculus to fit one-hop forced events

(a) **Partial-application agents (interaction-net style).** Rewrite S x y z as S→S1(x)→S2(x,y)→result, with
δ (duplicator) and ε (eraser) agents. Every rule then involves one *active pair*. On the battlefield, an
active pair is exactly "this Aura" + "enchanted permanent", which is the one-hop reach printed text has.
That is the strongest fit between card text and a rewriting discipline that I found. **But δ needs two
parents** (its two outputs feed two places), and attachment has out-degree 1 (303.4d, 301.5c; L3). In a
tree, δ must become a *sequential walker* that copies node by node into a second location. That is what the
cursor machine below does.

(b) **The cursor machine (built and checked).** `lines/L7/cursor_machine.py`: the L3 spine-chain encoding.
Every operation may name a node only as `(cursor, rel)` with rel ∈ {self, host, leaf-child, cell-child}, so
the API itself enforces one-hop locality. The control program is finite and reads only labels and existence
of one-hop neighbours. Each rule is a fixed macro: park the tail, park the old head, move `x` to P, walk a
cursor E to the end of x's own chain, re-hang the freed cells, copy for W/S, re-hang the tail, SAC the old
head (the cascade frees the rest). The copy is a DFS with two cursors (A on the original, Bc on the copy)
and three control states. It needs no visited-marks because children are ordered by label class (leaf
before cell) and parent pointers exist. Results (output file):

```
I: MARK 4  MOVE 2  COPY 0  SAC 1  SBA 1        (atomic args, empty tail, redex search excluded)
K: MARK 6  MOVE 2  COPY 0  SAC 1  SBA 3
B: MARK 9  MOVE 5  COPY 0  SAC 1  SBA 1
C: MARK 8  MOVE 4  COPY 0  SAC 1  SBA 1
W: MARK 7  MOVE 4  COPY 1  SAC 1  SBA 0
S: MARK 10 MOVE 5  COPY 1  SAC 1  SBA 0        S with |z| = n nodes: COPY n, MARK 7+3n
16 fixed terms (incl. L3's 11, Church 2, K a Ω) and 3000 random terms (depth ≤ 5): every step agrees
with the reference reducer; 18 random terms ran out of 60-step fuel, agreeing up to that point.
cursors: A Bc C1 C2 C3 E E2 H P Q R1 R2 R3 T (14, not minimized) + fixed ANCHOR, PARK.
```
Is it still recognisably SKI/BCKW on the table? **The term is**: after every step the board decodes to the
reference term. **The reducer is not native**: it is a fixed finite program, like a G-machine's instruction
set. In a forced realization that program would be on the table as Churchill-style rule cards and markers.
Non-locality that one-hop rules expose and L3 hid: even I and K must append the tail to the *end of x's own
chain*, which is an unbounded walk (cursor E) in this encoding.

(c) **Linear combinators + atom-only copy.** BCKI with a copier restricted to atoms is not combinatorially
complete: W needs `y` arbitrary. Without sharing (out-degree 1) there is no "copy the pointer" option.
Rejected.

(d) **Numeric arguments (counters, P/T).** Numbers *are* natively copiable and comparable: Doubling Season
doubles counters, and "+1/+1 for each Aura attached" counts children. But a combinator whose arguments are
numbers is a register machine with combinator names; this is Yin–Churchill's design (L1 §2b). It is not
CL on the table. Rejected as "native CL", noted as the honest fallback.

(e) **Parallel (Gross–Knuth) firing**, every redex triggering at once (L3's remark). Not forced, because
of 603.3b ordering (Angle 5); residuals created by COPY have no pending triggers, so a "round" is not a
complete development. Gross–Knuth normalization for CL is recalled, not checked [guessed].

### Angle 5 — the stack as a forced call stack

Rules [read]: 603.2 (triggers trigger automatically), 603.3 (a trigger goes on the stack "the next time a
player would receive priority" and "becomes the topmost object"), 603.3b (each player, in APNAP order, puts
their triggers on the stack "in any order they choose"), 704.3 (SBAs repeat to a fixpoint before triggers
go on the stack), 101.4 (APNAP).

A chain in which each resolution causes exactly one new trigger is a forced call chain, depth-first,
because new triggers go on top. One cursor-machine op per resolution fits that shape: **one live trigger at
a time, so no 603.3b choice ever arises.** The cascade is free: 704.5m passes run inside 704.3 before any
trigger is placed.

**Is the 603.3b ordering choice harmful? Yes** [inferred argument]. Take `K a Ω` with Ω = S I I (S I I), in
a design where every redex head fires a trigger. Two triggers wait at the same moment, the K-step and the
first Ω-step, and one player orders them. If K's is placed on top, it resolves first, Ω is erased, and the
Ω-trigger then finds its objects gone and does nothing. If Ω's is placed on top, each Ω-step causes the next
Ω-step trigger, which goes on top of K's pending trigger; K's trigger never resolves, and the game is a
mandatory loop and a draw (104.4b, 733.4). So one ordering choice decides termination. CL's confluence
does not help: confluence says that normal forms agree, not that every strategy reaches one. A forced
design must (i) keep at most one pending trigger per player per checkpoint, or (ii) split triggers between
two players so that APNAP fixes a two-level order (the nonactive player's triggers resolve first; CBH use
this per L1), or (iii) prove that simultaneous triggers commute, which they do only for disjoint,
non-nested redexes.

### Angle 6 — the negative side

See **Obstruction statement** below. Short form: with printed text and no addressing layer, the
transformations forced play can apply to the chainable part of the forest are prunings and suspensions,
and no CL reduction step is a pruning.

## Best forced fragment

**(A) Forced garbage collection, anywhere in the term** (L3, re-verified here). Once a node leaves, its
whole Aura subtree goes by repeated 704.5m inside one 704.3 fixpoint, with no stack and no choices. The
model reproduces L3's `K a (S I I (S I I))`: 1 SAC, then 10 SBA passes. The SAC itself is forced if the
departing node has a mandatory leave trigger, e.g. **Reality Acid** ("Enchant permanent / Vanishing 3 … /
When this Aura leaves the battlefield, enchanted permanent's controller sacrifices it."). That gives a
forced *upward* kill, and **Captain's Hook / Grafted Wargear** ("Whenever this Equipment becomes unattached
from a permanent, destroy/sacrifice that permanent.") give another. Note that forced deletion can travel
up as well as down, but deletion is all it does.

**(B) Forced root projection: one complete K/I-shaped step with real cards, at the root only.** This
uses the only native "who survives" distinction: when a host dies, Auras on it die (704.5m) but Equipment
on it "becomes unattached … remains on the battlefield" (301.5c, 704.5n). Bestowed Auras also survive
(702.103f), and Song of the Dryads makes an Aura node "unattached" per its ruling, so "cut here, keep
the subtree" exists too, though it needs a choice to place.

Board (Alice controls everything; Bob controls no creatures):
- head `K`: any creature, e.g. a token.
- argument 1 `x`: **The Reality Chip** or **Inchblade Companion** (reconfigure: "Attach to target creature you control; or unattach from a creature … While attached, this isn't a creature."), attached to `K` during setup. The structure of `x` hangs from it as "enchant permanent" Auras (L3 labels), which stay legal whether or not x is a creature.
- application slot: **Necrotic Plague** attached to `K` (grants "At the beginning of your upkeep, sacrifice this creature.").
- argument 2 `y`: any L3 Aura tree whose root is "enchant permanent" or "enchant enchantment" on Necrotic Plague (it is an enchantment).

Trace in Alice's upkeep [inferred from the quoted rules; no ruling on this exact combination]:
1. The granted trigger goes on the stack: one trigger, no target. It resolves: Alice sacrifices `K`.
2. Necrotic Plague's "When enchanted creature dies" triggers (a leaves-the-battlefield trigger, which looks back, 603.10a) and waits.
3. SBA pass 1 (704.3): Necrotic Plague is attached to nothing and goes to the graveyard (704.5m). `x` equips a nonexistent permanent, becomes unattached and remains (301.5c, 704.5n). Being unattached, it is a creature again (702.151b).
4. SBA passes 2…: the root of `y`, then its descendants, by 704.5m.
5. Necrotic Plague's trigger: "its controller chooses target creature one of their opponents controls". Bob controls none, so it is removed (603.3d; ruling: "it just remains in its owner's graveyard").
6. Result: `x` alone, a creature root with its structure intact. This is **K x y → x**. With nothing hung on Necrotic Plague it is **I x → x**. `K x` with no Necrotic Plague is stable. Zero player choices.

Honest limits. The head's label plays no role: the "rule" lives in the slot card, so the board must be built
to match the term (the same holds for the cascade). The output does not compose: `x`'s own arguments hang
as Auras, not in the (Equipment, slot) form a next step would need. A third argument `z` could be re-attached
to the surfaced `x` by **Forebear's Blade** as the z-slot ("Whenever equipped creature dies, attach this
Equipment to target creature you control.", with `x` the unique creature), giving K x y z → x z. But then
`x`'s first-argument slot is a non-reconfigure Equipment, so the encoding changes sort after one step. One
step, at the root, depth 1: that is the whole of it.

**(C) Forced, and stated for completeness:** subtree suspension (702.26g indirect phasing, forced at the
untap step for anything with phasing) and forced single-object copies (Angle 3). Neither is a reduction step.

## Best path to forced S/W

Design: **the cursor machine of Angle 4, scheduled as a linear trigger chain, with the cursors realized
as Churchill-style unique marks.** The term stays native (L3 spine-chain Aura forest, labels = card names,
copiable). The reducer is a fixed set of rule cards.

What is settled in the model: 4 event kinds and 14 cursors (not minimized) suffice for normal-order
SKI+BCKW, with one-hop locality enforced by the API and correctness checked step by step. At most two
cursors move per copy step, and every op references at most three objects.

Realization table [read for card text; feasibility inferred]:

| op | printed forced candidate | status |
|---|---|---|
| SAC (+cascade) | Reality Acid (vanishing: a forced timer), Necrotic Plague-granted upkeep sacrifice, Captain's Hook / Grafted Wargear, Artificer's Hex (2-hop destroy), world rule / Role rule (newest survives) | **available** |
| MOVE into a non-creature host | **Glamer Spinners** ETB, made recurrent and forced by **Followed Footsteps** on a Glamer Spinners ("At the beginning of your upkeep, create a token that's a copy of enchanted creature."). Target uniqueness: **Sterling Grove** shrouds Alice's other enchantments, so only Bob-controlled nodes are targetable. Receiver uniqueness: "same controller" + "can be enchanted by all the Auras" | **unresolved**: Glamer moves the target's *whole fan* of Auras, not one node; every other permanent (lands, the Glamer tokens themselves, Followed Footsteps' host) must be shrouded or illegal; one MOVE per upkeep per copier |
| MARK (move a cursor) | control as the mark: a Bob-controlled Confiscate on a node makes it Bob's (layer-2 timestamps decide), Illusory Gains-style "newest" pointers, phasing windows | **unresolved**: control gives one bit; the machine needs about 14 marks live or cyclically reused; marks set by effects are not copied (707.2), which is good: copies start unmarked |
| COPY one node onto a given host | **Extravagant Replication** (forced upkeep copy of "another target nonland permanent you control", so Aura nodes qualify) + 303.4f host choice forced by uniqueness: protection (702.16c) on every node except the destination | **unresolved**: needs a unique legal *target* (the node to copy) and a unique legal *host*. Note the conflict: Sterling Grove (used for MOVE) would shroud the very nodes Extravagant Replication must target |
| scheduling | one live trigger at a time; or APNAP split | settled in principle (Angle 5) |

Unresolved steps, in order of how much they block:
1. **Uniqueness for COPY.** A forced copier of Aura nodes exists (Extravagant Replication, found by the search in Angle 3). It needs (i) exactly one targetable nonland permanent you control other than itself, and (ii) exactly one legal host for the token under 303.4f, for example protection from the node's colour on every other permanent. The shroud used to make Glamer Spinners' target unique works against (i), so the MOVE and COPY uniqueness schemes must be reconciled. Untested.
2. **Single-node MOVE from fan-moves.** Re-derive the macros for an op "move all children of a to b". Each spine-chain node has at most one leaf child and one cell child, so a fan has at most two nodes, and a scratch node could separate them. Untested.
3. **Enough marks.** Either fit the control into the two-valued control mark plus timestamps and phasing windows, or admit text-changing (Artificial Evolution etc.), at which point this is CBH's toolbox.
4. **Throughput.** Upkeep-pulse copiers give one event per turn, so an S step on an n-node argument takes on the order of 4n+20 turns. That is acceptable for "forced", but it should be counted.
5. **Mana and setup.** Not addressed. The construction is an end-game board, like CBH's.

Verdict on the path: plausible as a Churchill-class construction, and not native. The best that can
honestly be claimed is "native term, forced machine".

## Obstruction statement

Assumptions (all stated, all checkable):
- (E) *Compositional attachment encoding:* each subterm occurrence is a subtree whose root is attached to
  the node encoding its context; term structure is carried by attachment and fixed node labels (card
  names) only.
- (P) *Printed text, no text-changing, and the card survey above is complete for forced re-attachment.*
  The searches are listed in Angle 1. This is the empirical premise and the weakest link.
- (H) *No addressing layer:* no node carries a position-dependent mark (control, colour, type, counters,
  tapped status, phasing) that a forced choice could single it out by. So any forced choice among ≥ 2
  same-labelled candidate nodes is a real choice.

Facts used [read]: an attached permanent is never a creature (704.5p; 303.4d; 702.151b). An Aura whose host
leaves goes to the graveyard (704.5m), while Equipment becomes unattached (301.5c, 704.5n). Copies carry no
attachments (707.2 + rulings). Aura tokens choose hosts (303.4f).

**Claim 1 (chains are frozen).** Under (P), no forced event re-attaches an object onto a non-creature,
non-land permanent without a choice. Glamer Spinners and 303.4f Aura entry are the only routes found,
and both involve a choice (target/receiver, host).

**Claim 2 (unbounded terms need chains).** With finitely many labels, a node's children are distinguishable
only by label, so an application spine of unbounded length must be a chain of unbounded depth. Below depth 1
every host is a non-creature (704.5p), so every node there is an Aura on a non-creature.

**Claim 3 (only prunings).** From 1, 2 and (H): on the depth ≥ 2 part of the forest, the forced closure
can only delete subtrees (704.5m cascades, from forced sacrifices) and suspend them (phasing). It changes no
host there, except that a node may become a root via Song of the Dryads-type type changes, which need a
choice to place.

**Claim 4 (no reduction step is a pruning).** Take K x y → x (or I x → x) with x a variable, under (E).
x's node is a proper descendant of the redex's root before the step, and it is the root attached to the
context afterwards, so its host must change. In the spine-chain encoding, all six rules change x's host
(c1 → P), as the simulator's MOVE counts show.

**Conclusion.** Under (E), (P) and (H), no CL reduction step occurring at depth ≥ 2 can be performed by
forced play. What forced play contributes is erasure. At depth 1 (the root, with creature heads) the
Equipment/bestow survival rule lets one K/I-shaped step be forced (Best forced fragment B), but it does
not compose.

**Converse direction (what lifting (H) buys).** If a constant number of marks can be set and read by
forced one-hop events, normal-order SKI+BCKW reduction is a fixed finite program of one-hop events
(Angle 4, simulated). So the obstruction is exactly the **addressing obstruction**, not a depth or
duplication obstruction. Duplication costs one event per node in every design, because no event copies
attachments. Forcedness necessarily brings in an addressing layer (marks plus unique-choice engineering),
i.e. Churchill-style machinery, though not necessarily a tape: the term can stay a tree on the table.

Status of the claims: Claims 2 and 4 are proofs relative to (E). Claim 1 is a survey result, so not a
proof. Claim 3 is a consequence. The whole is model-relative and has not been reviewed (Wizard pending).

## What I did not verify

- Completeness of the Scryfall survey (P). I did not query `put onto the battlefield attached to` on
  non-Aura cards, "exchange" effects, every token-copy card, or Un-set/digital-only legality. Any forced card
  that attaches onto a non-creature permanent without a choice would break Claim 1.
- Gatherer pages themselves: rulings are Scryfall's mirror.
- The general principle that simultaneously entering Auras cannot choose one another as hosts: stated
  only in Mirrormade/Copy Enchantment rulings (via L5), extended by me.
- Doubling Season + "create … attached to X": inferred from the "tapped and attacking" ruling, not from a
  ruling about attachment.
- Forced root projection (Fragment B): each step follows from quoted rules, but no ruling covers the
  combination. Specifically unchecked: the timing of a reconfigure Equipment becoming a creature in the
  same SBA pass, and whether an "enchant permanent" Aura on The Reality Chip has any issue when it surfaces.
- Gross–Knuth normalization for CL; CBH's use of APNAP (both from L1/memory).
- The cursor machine's cursor count is not minimized, and its op set is an abstraction: the mapping
  "one op = one forced event" is the design hypothesis, not a demonstrated card mapping.
- Phasing of Aura nodes by a forced effect: Teferi's Curse is artifact/creature only; I did not search
  further.
- Mana, setup cost, deck legality: not addressed.

## Status

- 2026-11-21: L7 note written; `lines/L7/cursor_machine.py` runs clean (`python3 -I`, exit 0; output in
  `cursor_machine.out`). Result: forced = erasure (anywhere) + one non-composing root projection step with
  real cards; S/W forced only behind an addressing layer (cursor machine verified in model; card
  realization open: uniqueness engineering for Extravagant Replication (COPY) and Glamer Spinners (MOVE,
  which moves fans, not nodes), and enough marks).
