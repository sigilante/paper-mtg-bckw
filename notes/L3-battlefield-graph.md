# L3 — The battlefield as a term graph

Line L3 of `PLAN.md`. Author: L3 subagent, 2026-11-21.
Executable check: `lines/L3/l3sim.py` (output saved in `lines/L3/l3sim.out`).
Card texts: Scryfall Oracle, fetched 2026-11-21. Rules: Comprehensive Rules dated 2026-11-06
(`MagicCompRules 20261106.txt`).

## Summary

**What works.** A combinator term can live on the battlefield as a forest of Aura tokens. The
only pointer is "attached to", and the term needs no counters, no text changes and no
side tags. I call this the *spine-chain encoding*. A term `h a1 … an` is a head leaf `h`
(an Aura whose card name gives the combinator or variable) with a chain of "cell" Auras
hanging from it: `c1` is attached to `h`, `c(i+1)` is attached to `c(i)`, and the root leaf
of argument `a(i)` is attached to `c(i)`. A cell is told apart from a leaf by its name alone.
The whole term is attached to one anchor permanent.

- **Finding the redex is free.** The head of the whole term is *the* leaf attached to the anchor,
  and argument `i` sits at a fixed depth `i` down its chain.
- **K's discard is native and forced.** Sacrificing the K leaf leaves the cells below it
  unattached. State-based actions then remove the whole dropped subtree, one level per pass
  (704.5m repeated under 704.3; tokens cease to exist under 704.5d).
- **I, K, B and C need no new objects.** Each step is a few re-attachments (Simic Guildmage)
  and one sacrifice (Auratog). The freed cells are reused.
- **S and W must copy an argument subtree.** The only way I found is node by node: token
  copies of single Auras, each placed by its controller under 303.4f.

**Which model this achieves.**
- **Cooperative, for BCKI.** Every reduction step is a legal sequence of plays with four
  engine cards plus the Aura cards that serve as node labels. But legality does not force
  the step: other moves are legal too, and the player chooses targets. Separately, BCK(I)
  terms are affine. Each step deletes at least the head leaf, so a reduction is never longer
  than the term is large. This fragment is not Turing-complete.
- **Bounded, for S and W.** Each copied node costs one use of a one-shot copy effect (Flash
  Photography, Replication Technique). I found no repeatable, unrestricted way to make token
  copies of an Aura, so the number of S and W firings is bounded by the deck.
- **Forced: not achieved.** No real card can see two or three hops up an attachment chain, or
  re-attach "the Aura attached to the Aura attached to X". The only forced part is K's
  garbage collection.

**Sharing (a DAG) is impossible** with attachment. An Aura enchants at most one object
(303.4d) and an Equipment equips at most one creature (301.5c). Every native pointer I
weighed is either out-degree 1 (so the structure is a forest), one-to-one, or a bounded
label. Graph reduction with sharing therefore does not transfer, and duplication is real
copying, as the PLAN guessed.

Simulator: the abstract mechanism is checked in lockstep, step by step, against a reference
normal-order reducer on 11 terms. Among them are one that duplicates a compound argument
(`S x y (K a b)`), Church 2, and one that discards a divergent argument. All 11 pass.

## Representation

### Pointer survey (why attachment, and why trees)

| candidate | arity / direction | unbounded? | verdict |
|---|---|---|---|
| Aura attached to permanent (303.4) | each Aura → 1 host; a host takes any number | yes (tokens) | **used**: a forest, child → parent |
| Equipment / Fortification (301.5) | 1 host, which must be a creature or land; an Equipment can't equip if it is a creature (301.5c); unattach rather than die (704.5n) | yes | no chains, no cascade |
| bestowed Aura | becomes a creature when unattached (702.103f, an exception to 704.5m) | — | breaks the cascade |
| "exiled with", imprint, haunt, champion | card → permanent, from exile | no: tokens in exile cease to exist (704.5d) | finite |
| soulbond pairing | one-to-one, symmetric | — | not a tree |
| control / ownership / goad | object → player (≤ #players) | bounded label | at most a tag |
| creature types, names, chosen values | shared labels | bounded alphabet | bounded heap only |
| counters | numeric | unbounded | no card reads "permanent with the same number of counters" as an address; this is Churchill-style arithmetic |
| mutate pile | ordered pile inside one permanent | cards only | a copy copies its merged characteristics, not the pile; counters aren't copied (707.2) |
| phasing (702.26g) | a subtree phases with its host | — | suspension marker, not a pointer (see below) |

The "children attach to an application node" design, with an L/R tag, works, but it needs a
side tag on every node. A tag has to be status or a counter, which copies lose (707.2:
"Other effects (including type-changing and text-changing effects), status, counters, and
stickers are not copied."), and every S, B, C or W step moves an argument from the R side to
the L side, so tags would be flipped constantly. The spine-chain encoding removes the tag.
A cell has at most one cell child and exactly one leaf child, and a leaf has at most one
(cell) child. Kind is read from the card name, which *is* copiable.

### Spine-chain encoding

```
term  S K K x              battlefield (arrow = "is attached to")
                           Island (anchor)
                             ^-- S   [Indestructibility]
                                  ^-- c1 [Confiscate]  <-- K [Bound in Gold]
                                       ^-- c2 [Confiscate] <-- K [Bound in Gold]
                                            ^-- c3 [Confiscate] <-- x [Dream Leash]
```

The leaf kind is the card name of the Aura token: S = Indestructibility, K = Bound in Gold,
I = Intercessor's Arrest, B = Faith's Fetters, C = Lay Claim, W = Take Possession. A cell is
Confiscate. The free variables are Dream Leash, Volition Reins, Curator's Ward and Elemental
Resonance (four distinct variables at most). All of these are "Enchant permanent", so an Aura
may enchant an Aura. None of them can be a creature (303.4d), so the chain is legal at any
depth. The anchor is a basic land.

## Card list (Oracle text, quoted)

Engine (four cards):
- **Simic Guildmage** — Creature — Elf Wizard: "{1}{G}: Move a +1/+1 counter from target creature onto another target creature with the same controller. {1}{U}: Attach target Aura attached to a permanent to another permanent with the same controller." — MOVE.
- **Auratog** — Creature — Atog: "Sacrifice an enchantment: This creature gets +2/+2 until end of turn." — SAC (free, repeatable).
- **Flash Photography** — Sorcery: "You may cast this spell as though it had flash if it targets a permanent you control. Create a token that's a copy of target permanent. Flashback {4}{U}{U}" — COPY (two uses per card).
- **Replication Technique** — Sorcery: "Demonstrate (When you cast this spell, you may copy it. If you do, choose an opponent to also copy it. …) Create a token that's a copy of target permanent you control." — COPY, alternative.
- Anchor: any basic land (Island).

Node labels (all "Enchant permanent"; the other lines are harmless when one player controls everything):
- **Confiscate** (cell): "Enchant permanent / You control enchanted permanent."
- **Indestructibility** (S): "Enchant permanent / Enchanted permanent has indestructible." 704.5m puts an Aura into the graveyard; it does not destroy it, so indestructible does not block the cascade. Sacrifice ignores indestructible.
- **Bound in Gold** (K): "Enchant permanent / Enchanted permanent can't attack, block, or crew Vehicles, and its activated abilities can't be activated unless they're mana abilities."
- **Intercessor's Arrest** (I): "Enchant permanent / Enchanted permanent can't attack, block, or crew Vehicles. Its activated abilities can't be activated unless they're mana abilities."
- **Faith's Fetters** (B): "Enchant permanent / When this Aura enters, you gain 4 life. / Enchanted permanent can't attack or block, and its activated abilities can't be activated unless they're mana abilities."
- **Lay Claim** (C): "Enchant permanent / You control enchanted permanent. / Cycling {2}"
- **Take Possession** (W): "Split second … / Enchant permanent / You control enchanted permanent."
- **Dream Leash**, **Volition Reins**, **Curator's Ward**, **Elemental Resonance** (variables): "Enchant permanent / … You control enchanted permanent." (Dream Leash and Volition Reins); "Enchanted permanent has hexproof. / When enchanted permanent leaves the battlefield, if it was historic, draw two cards." (Curator's Ward); "At the beginning of your first main phase, add mana equal to enchanted permanent's mana cost." (Elemental Resonance).
  Caution: the anchor must never be the Guildmage or Auratog. The "activated abilities can't
  be activated" Auras would shut them off.

Cards I checked and **rejected** as the copy engine or the re-attacher:
- **Second Harvest**: "For each token you control, create a token that's a copy of that permanent." It copies every token at once. Whether the new Aura copies may enchant each other as they enter simultaneously is unverified (see below).
- **Yenna, Redtooth Regent**: "{2}, {T}: Choose target enchantment you control that doesn't have the same name as another permanent you control. Create a token that's a copy of it, except it isn't legendary. If the token is an Aura, untap Yenna, then scry 2. Activate only as a sorcery." It is repeatable for Auras, but the name-uniqueness clause allows at most one copy per name. This is the nearest miss.
- **Adagia, Windswept Bastion**: "…Create a token that's a copy of target artifact or enchantment you control, except it's legendary." A second copy of the same name dies to the legend rule.
- **Saheeli, Radiant Creator**: "…create a token that's a copy of target permanent you control, except it's a 5/5 artifact creature…" An Aura that is a creature can't enchant (303.4d).
- **Orvar, the All-Form**: "Whenever you cast an instant or sorcery spell, if it targets one or more other permanents you control, create a token that's a copy of one of those permanents." It needs one cast spell per copy.
- **Stangg, Echo Warrior**: "…For each Aura and Equipment attached to Stangg, create a token that's a copy of it attached to Stangg Twin. Sacrifice all tokens created this way at the beginning of the next end step." This is the closest native "copy the things attached to X", but it goes one level deep, onto a creature, and the copies are temporary.
- **Arna Kennerüd, Skycaptain**: "…for each nontoken permanent attached to it, create a token that's a copy of that permanent attached to that creature." One level, and nontoken only.
- **Aura Graft** ("Gain control of target Aura that's attached to a permanent. Attach it to another permanent it can enchant."), **Enchantment Alteration** ("Attach target Aura attached to a creature or land to another permanent of that type."), and **Crown of the Ages** ("{4}, {T}: Attach target Aura attached to a creature to another creature."): one-shot, or limited to creature and land hosts. Simic Guildmage dominates them.

Scryfall searches I ran for a native subtree copy: `o:"copy of" o:"attached to it"` gave the 3
cards above, `o:"copy of" o:"each aura attached"` gave none, `o:"copy of" o:aura o:token` gave
7 (Stangg and Three Dog are one-level only), and `o:"copy of target permanent"` gave 7, all of
them one-shot or restricted. **No card copies a permanent together with everything attached to
it, recursively.**

## Reduction rules

Notation: `P` is the head's host (the anchor, or a cell when the redex is inside an argument).
`c1..ck` are the redex cells, `r_j` is the root leaf of argument `j`, and `rest` is `c(k+1)`
with everything below it.

Every rule has the same shape:
1. MOVE the result's head argument `r_j0` onto `P`.
2. For each argument position in the result, take a freed redex cell (preferring the cell that
   already holds the right argument, so the argument travels with it) and MOVE it to the end of
   the chain under construction. MOVE `r_j` into it on first use, or COPY the subtree of `r_j`
   on later uses.
3. MOVE `rest` to the end of the result's top chain.
4. SAC the old head leaf. SBA 704.5m then removes the unused cells and dropped arguments,
   level by level.

| rule | result | cells reused | COPY |
|---|---|---|---|
| I x → x | `x`, then rest | 0 | none |
| K x y → x | `x`, then rest; `y` dies in the SBA cascade | 0 | none |
| B x y z → x (y z) | 2 of 3 cells reused; the third dies empty | 2 | none |
| C x y z → x z y | | 2 | none |
| W x y → x y y | | 2 | the subtree of y, once |
| S x y z → x z (y z) | | 3 | the subtree of z, once |

A subtree COPY is a top-down cascade of single-Aura token copies. Each new token enters
attached to an already-copied node, chosen under 303.4f ("…that player chooses what it will
enchant as the Aura enters the battlefield."). Cost: one copy effect per node.

### The five hard parts

1. **Finding the redex.** It is solved structurally. The head of the whole term is the unique
   leaf attached to the anchor. After head normal form, normal order descends into the
   arguments left to right, and the anchor role passes to the cell above each argument. A forced
   version would need a leaf to know that it is attached to the anchor, and it would still fail
   at hard part 2.
2. **Seeing three arguments up the spine.** In this encoding the arguments hang *below* the head
   at depths 1, 2 and 3 down the cell chain, not up the spine, which is the right orientation.
   But printed Aura text reaches exactly one hop ("enchanted permanent", or "Auras attached to
   it", as on Stangg). No card names "the Aura attached to the Aura attached to the Aura attached
   to this". So rules that see 2–3 arguments exist only as player choices of targets
   (cooperative play), not as card text. This is **where forcedness fails**.
3. **Duplication.** Sharing is impossible (out-degree 1). Native subtree copy does not exist
   (see the searches above). The lazy node-by-node cascade works, but each node needs one
   copy-effect use, and the only unrestricted copy effects found are one-shot. The result is a
   bounded copy budget. **This is the weakest point of the line.**
4. **Forcedness.** Only K's garbage collection is forced, and it is fully forced: the SBA loop
   runs with no choices and no stack (704.3). MOVE, COPY and SAC are player-chosen. The model
   is cooperative, and weak cooperative at that: the cards make a correct reduction *legal*, not
   the *only* legal play.
5. **Card count and text-hacking.** There are 4 engine cards (Guildmage, Auratog, one copy
   sorcery, and the land), plus 1 cell Aura and 6 combinator Auras (or 4 for SKI plus the cell)
   plus up to 4 variable Auras. Text-hacking: **none**. Labels are card names.

### Phasing (examined, not used)

Phasing out cell `c1` phases out every argument at once, because the chain and its leaves are
attached to `c1` (702.26g, indirect phasing). That makes phasing a native "suspend this suffix
of the spine" operation. Phased-out permanents "can't affect or be affected by anything"
(702.26b), however, so a suspended argument can be neither moved nor copied. One property does
hold: an Aura that phased out *directly* and whose host has left "phases in unattached. State-
based actions apply" (702.26i). So K's discard still happens lazily, at phase-in. Phasing
therefore gives deferred garbage collection and an evaluation-order marker, not a rewrite
mechanism.

### Parallelism remark (guess, not checked)

Real triggers fire everywhere at once, so the native strategy on a battlefield is closer to
*parallel* (Gross–Knuth-style complete development) than to normal order. Gross–Knuth reduction
is normalizing for orthogonal systems such as CL (I believe; not verified here). A forced design
might therefore aim at "every redex fires each turn" rather than finding the leftmost redex. I
did not develop this.

## Worked trace: S K K x → x

This trace is produced by the simulator, so it matches the model exactly. `#n` is the object
id; card names are in brackets.

Initial: Island ← S#2; S#2 ← CELL#3 ← K#4; CELL#3 ← CELL#5 ← K#6; CELL#5 ← CELL#7 ← x#8.

```
step 1: redex head S#2[Indestructibility] on ANCHOR#1[Island]
  MOVE  K#4[Bound in Gold] -> ANCHOR#1[Island]          Simic Guildmage {1}{U}   (x := K becomes the head)
  MOVE  CELL#7[Confiscate] -> K#4[Bound in Gold]         Simic Guildmage          (cell holding z=x travels with it)
  MOVE  CELL#5[Confiscate] -> CELL#7[Confiscate]         Simic Guildmage          (cell holding y=K: arg 2 of the result)
  MOVE  CELL#3[Confiscate] -> K#6[Bound in Gold]         Simic Guildmage          (freed cell becomes (y _)'s arg cell)
  COPY  x#8[Dream Leash] => new x#9 on CELL#3            Flash Photography; host chosen by 303.4f
  SAC   S#2[Indestructibility]                           Auratog (no SBA: nothing left attached to S)
  => K x (K x)
step 2: redex head K#4[Bound in Gold] on ANCHOR#1[Island]
  MOVE  x#8[Dream Leash] -> ANCHOR#1[Island]             Simic Guildmage
  SAC   K#4[Bound in Gold]                               Auratog
  SBA pass 1 (704.5m; tokens cease 704.5d): CELL#7
  SBA pass 2: CELL#5
  SBA pass 3: K#6
  SBA pass 4: CELL#3
  SBA pass 5: x#9
  => x
```

Totals: 5 Guildmage activations ({10} mana, half of it blue), 1 copy effect, 2 Auratog
sacrifices, and 5 SBA passes. The five passes all happen in one SBA loop before anyone gets
priority.

B example (from the simulator): `B f g x → f (g x)` takes 4 MOVEs and 1 SAC with no COPY. The
third redex cell dies empty with the B leaf. `W K x → x` takes 4 MOVEs, 1 COPY (of `x`) and
2 SACs.

## Simulator and its output

`lines/L3/l3sim.py` (stdlib Python) models exactly the objects above. Nodes have a kind and a
host. The primitives are MOVE (re-attach), COPY (one new Aura on a chosen host), and SAC
followed by the 704.5m fixpoint. Redex search is leftmost-outermost over the encoding. After
every step it checks the structural invariants (the anchor holds exactly one root; a cell holds
exactly one leaf and at most one cell; a leaf holds only its first cell; no unattached Aura
survives SBAs). It decodes the board and asserts equality with the reference reducer's term at
the same step, and it asserts that the two step counts are equal.

Run: `python3 -I lines/L3/l3sim.py` (exit 0). Output (the trace part is above):

```
== lockstep check vs reference normal-order reducer ==
S K K x                  -> x            OK   steps=2 moves=5 copies=1 sacs=2 sba_passes=5 max_depth=5 max_nodes=7
W K x                    -> x            OK   steps=2 moves=4 copies=1 sacs=2 sba_passes=3 max_depth=3 max_nodes=5
B f g x                  -> f (g x)      OK   steps=1 moves=4 copies=0 sacs=1 sba_passes=1 max_depth=1 max_nodes=7
C f x y                  -> f y x        OK   steps=1 moves=3 copies=0 sacs=1 sba_passes=1 max_depth=1 max_nodes=7
S x y (K a b)            -> x a (y a)    OK   steps=3 moves=6 copies=5 sacs=3 sba_passes=6 max_depth=3 max_nodes=15
S I I (K a)              -> a            OK   steps=3 moves=7 copies=3 sacs=3 sba_passes=8 max_depth=7 max_nodes=11
S (S (K S) K) I f x      -> f (f x)      OK   steps=6 moves=22 copies=3 sacs=6 sba_passes=7 max_depth=3 max_nodes=15
K a (S I I (S I I))      -> a            OK   steps=1 moves=1 copies=0 sacs=1 sba_passes=10 max_depth=10 max_nodes=15
S (K (S I)) K a b        -> b a          OK   steps=5 moves=15 copies=2 sacs=5 sba_passes=7 max_depth=3 max_nodes=13
W (S K) (K a b)          -> a            OK   steps=4 moves=9 copies=10 sacs=4 sba_passes=13 max_depth=10 max_nodes=19
B (C K) W x y            -> y            OK   steps=3 moves=10 copies=0 sacs=3 sba_passes=7 max_depth=5 max_nodes=11

== runs that fire no S or W need no COPY (moves + sacrifices only): ==
B f g x                  -> f (g x)  copies=0 moves=4 sacs=1
C f x y                  -> f y x    copies=0 moves=3 sacs=1
K a (S I I (S I I))      -> a        copies=0 moves=1 sacs=1
B (C K) I x y            -> y        copies=0 moves=10 sacs=3
C (B K I) x y            -> y        copies=0 moves=11 sacs=4
ALL OK
```

Reading the numbers:
- `S x y (K a b)` copies the compound `K a b`, 5 nodes (leaf, 2 cells, 2 leaves), in one
  S step.
- `K a (S I I (S I I))` throws away a 13-node divergent argument with 1 sacrifice and a
  10-pass SBA cascade. This is the "K for free" result.
- `W (S K) (K a b)` shows copies compounding: 10 node copies for a 4-step reduction.

What the simulator does **not** model: mana, turns, priority and timing, targeting legality, the
legend rule, triggers of the label Auras, and whether each 303.4f choice is legal in the real game
(it assumes any Aura may be attached to any node, which holds for "Enchant permanent" between
non-creature Auras).

## Where it breaks / open rules questions

1. **No unbounded native copy (fatal for S and W in paper).** Every unrestricted copier found is
   one-shot. Repeatable ones carry a clause that kills Aura-node copies: a name-uniqueness check
   (Yenna), legendary copies (Adagia), or copies that become creatures (Saheeli). So
   SKI-with-S and BCKW-with-W are a bounded fragment. The copy budget is the number of copy-effect
   uses in the deck. *Nearest thing that works:* the copy-free BCKI fragment, cooperative and
   unbounded in principle but terminating by nature.
2. **Not forced.** Each MOVE and COPY needs a chosen target. No printed card reads more than one
   hop of the attachment relation, so no trigger can say "attach the second argument to …".
   Making it forced would mean inventing card text. That is outside "native".
3. **No sharing.** 303.4d and 301.5c give every attachable object out-degree 1, so the battlefield
   holds trees, not DAGs.
4. **Mana and time.** Each MOVE costs {1}{U}. Mana per turn is finite, so the number of steps per
   turn is bounded, and only the number of turns is unbounded. That is acceptable for a
   cooperative model and unacceptable for Churchill-style "the game state computes within one
   turn" (no infinite mana engine was designed here).
5. **Open: simultaneous Aura copies.** Can Aura tokens created by Second Harvest, entering
   simultaneously, choose one another as hosts under 303.4f? If they can, one Second Harvest plus
   a "junk anchor" (copy everything, attach the unneeded copies to one disposable permanent, then
   sacrifice it so the SBA cascade clears them) would copy an arbitrary subtree with one card.
   That is still one-shot. Unverified.
6. **Open: Simic Guildmage's "another permanent with the same controller".** I read this as the
   controller of the Aura's current host. With one player controlling everything it does not
   matter, but the Confiscate-family labels change control of what they enchant, and I did not
   check any Gatherer rulings.
7. **Open: attachment cycles.** MOVE could attach an Aura to one of its own descendants, making a
   detached cycle. No rule I read forbids it (303.4d forbids only self-attachment). The simulator
   never does it. A cycle would be a structure that SBAs never collect, which might be worth a
   look as a curiosity.

## What I did not verify

- Gatherer rulings for any card. I used Oracle text only.
- Whether 303.4f allows choosing as host a permanent that is entering simultaneously (open
  question 5).
- Gross–Knuth normalization for CL (stated from memory, labelled a guess).
- That no card anywhere copies a permanent with its attachments recursively. I ran only the
  Scryfall searches listed above, not an exhaustive survey.
- Licids, reconfigure, Role tokens (Role tokens are "enchant creature" per 111.10j–r, so they
  can't form Aura-on-Aura chains), fortify, meld, crew and saddle. I considered these briefly
  and dismissed them for out-degree or host-type reasons without quoting the rules in full.
- Mana sufficiency, the costs of setting up the initial term (casting or copying the initial
  Auras), and the constructed-deck 4-copy limit. The simulator assumes the initial term is
  given.

## Status

- 2026-11-21: L3 note and simulator written; lockstep check passes on 11 terms (exit 0).
  Result: spine-chain Aura forest; BCKI cooperative with no copying; S/W bounded by the
  one-shot copy budget; not forced.
