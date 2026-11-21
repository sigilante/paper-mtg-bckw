# L6 — Hybrid: L3's Aura forest driven by L2's copy engine

P2 construction for `PLAN.md`, testing the conjecture in `notes/P1-comparison.md` §1.
Author: L6 subagent, 2026-11-21. Executable check: `lines/L6/l6sim.py`, output in
`lines/L6/output.txt` (`python3 -I l6sim.py`, exit 0, ends with `ALL OK`).
Card text: Scryfall Oracle, single-card lookups and four Scryfall searches, all fetched
2026-11-21. Rulings: Scryfall's copies of the Gatherer rulings. Rules: Comprehensive Rules
effective 2026-11-06, fetched once as the single yawgatog page L5 used and grepped locally.

## Summary

**Verdict: the conjecture holds, in the cooperative model.** Join L3's spine-chain encoding
to a repeatable copy engine, and every rewrite of S, K, I, B, C and W becomes a fixed, legal
sequence of real game actions. The engine is Reiterate with buyback copying a parked Flash
Photography, paid for by the Isochron Scepter / Dramatic Reversal / Gilded Lotus loop. The
whole computation runs inside one main phase of one turn, with no bound on the number of
actions. The result is full SKI and full BCKW reduction (any mix of the six combinators) with
these properties:

- **Cooperative.** A player who follows the rewrite table below makes only legal moves, and
  the board then equals the reference normal-order reduct after every step. The cards do not
  forbid other moves; see "What is forced vs chosen".
- **Unbounded.** Each node copy costs 6 mana, each move 2 and each sacrifice nothing. The
  mana loop yields +1 mana of any colour per iteration, without limit. Nothing in the
  construction is one-shot except Flash Photography itself, which is cast once per session
  and never leaves the stack while the session lasts.
- **Structural redex finding.** As in L3, the head of the whole term is the one Aura on the
  anchor, and argument *i* sits at depth *i* of its cell chain.
- **Forced garbage collection.** A K step sacrifices the K leaf. The discarded argument then
  dies in a chain of state-based-action passes that no player can interrupt (704.5m under
  704.3).

**Conditions.**
1. One player (P) controls every permanent involved: the engine, both anchor lands and every
   node. Simic Guildmage needs this (see its ruling below).
2. The opponent passes priority whenever P passes. The opponent could respond at every pass,
   so "cooperative" covers both players.
3. The engine starts on the battlefield, with Reiterate in hand, during P's main phase. I
   assume this and do not construct it. The initial term *is* constructed: physical template
   Auras are cast, and the term is copied from them.
4. Closed terms need no variable labels. Open terms are limited to 6 distinct free variables,
   one per spare label card (see the label table).

**What changed from L3.** L3 stopped at BCKI because it found no repeatable token copy of an
Aura. The join removes that bound. My fixed per-rule sequences sometimes use fewer Guildmage moves
than L3's generic algorithm (`B f g x`: 3 vs 4; Church 2: 20 vs 22; `B (C K) W x y`: 8 vs 10)
and never more on L3's test terms (`S K K x`: 5 for both). My Scryfall search also found **Replicator**, a
permanent that copies token Auras repeatedly, which L3's searches missed. It is an
alternative copy primitive (see Alternatives).

## Card list (Oracle text as returned by Scryfall, 2026-11-21)

Every card below is a paper card, legal in Legacy, Vintage and Commander per Scryfall. The one
exception is Dream Leash, whose print status I did not check: Scryfall rate-limited that
lookup. Its Oracle text was confirmed by search.

### Engine (7 cards plus 2 basic lands)

| card | Oracle text | role |
|---|---|---|
| **Flash Photography** {2}{U}{U} Sorcery | "You may cast this spell as though it had flash if it targets a permanent you control. / Create a token that's a copy of target permanent. / Flashback {4}{U}{U}" | the parked copy spell (FP); cast once per session |
| **Reiterate** {1}{R}{R} Instant | "Buyback {3} (You may pay an additional {3} as you cast this spell. If you do, put this card into your hand as it resolves.) / Copy target instant or sorcery spell. You may choose new targets for the copy." | COPY: one cast per node copied |
| **Isochron Scepter** {2} Artifact | "Imprint — When this artifact enters, you may exile an instant card with mana value 2 or less from your hand. / {2}, {T}: You may copy the exiled card. If you do, you may cast the copy without paying its mana cost." | mana loop |
| **Dramatic Reversal** {1}{U} Instant | "Untap all nonland permanents you control." | imprinted on the Scepter |
| **Gilded Lotus** {5} Artifact | "{T}: Add three mana of any one color." | mana loop |
| **Simic Guildmage** {G/U}{G/U} Creature — Elf Wizard | "({G/U} can be paid with either {G} or {U}.) / {1}{G}: Move a +1/+1 counter from target creature onto another target creature with the same controller. / {1}{U}: Attach target Aura attached to a permanent to another permanent with the same controller." | MOVE |
| **Auratog** {1}{W} Creature — Atog | "Sacrifice an enchantment: This creature gets +2/+2 until end of turn." | SAC (free) |
| **Island** ×2 | "({T}: Add {U}.)" | the anchor A; the template host T |

Relevant rulings:
- Simic Guildmage (2006-05-01): "For the second ability, only the Aura is targeted. When the
  ability resolves, you choose a permanent to move the Aura onto. It can't be the permanent
  the Aura is already attached to, it must be controlled by the player who controls the
  permanent the Aura is attached to, and it must be able to be enchanted by the Aura. (It
  doesn't matter who controls the Aura or who controls Simic Guildmage.) If no such permanent
  exists, the Aura doesn't move." This settles L3's open question 6. The constraint is
  between the *old host* and the *new host*. Every node is a host at some time, so the anchor
  and every node must have one controller. With P controlling everything, the clause always
  holds.
- Reiterate (2021-03-19): "The copy is created on the stack, so it's not 'cast.' … The copy
  will resolve before the original spell does." "You can't choose to pay any alternative or
  additional costs for the copy."
- Flash Photography (2025-10-02): "If the copied permanent is a token, the new token that's
  created copies the original characteristics of that token as stated by the effect that
  created the token." "It doesn't copy … any Auras or Equipment attached to it."
- Mythos of Illuna (2020-04-17), the same effect with a ruling on Auras: "If an Aura is put
  onto the battlefield without being cast, such as by being created as a token, the Aura's
  controller-to-be chooses what it will enchant as it enters the battlefield. An Aura put onto
  the battlefield this way doesn't target anything (so it could be attached to an opponent's
  permanent with hexproof, for example), but the Aura's enchant ability restricts what it can
  be attached to. If an Aura token can't legally be attached to anything, it isn't created."
- Isochron Scepter (2020-08-07): "You cast the copy while the ability is resolving and still
  on the stack."

Mana check, done by me: one loop taps the Lotus for three of one colour, spends {2} on the
Scepter, and casts the Dramatic Reversal copy, which untaps both. The net gain is +1 mana of
a colour chosen freshly each iteration, and the stack returns to what it was. Reiterate with
buyback costs 6 mana including {R}{R}, so it takes 6 loops. The Guildmage costs {1}{U}, so 2
loops. Flash Photography costs {2}{U}{U}. Mana empties only at the end of a step or phase
(106.4), and the whole computation happens inside one main phase. The simulator tracks the
pool by colour.

### Labels: chosen to be inert where they land

L3's labels (Confiscate as the cell; Lay Claim, Take Possession, Dream Leash and Volition
Reins) change *control*. With one player controlling everything they are harmless.
Confiscate's effect, "You control enchanted permanent", gives P control of a permanent P
already controls, so the layer-2 effect (613.1b) changes nothing. Nested control Auras form
chains, never loops, because the forest is acyclic. Their danger lies elsewhere: if an
opponent ever controlled one node, the Guildmage's same-controller clause would split the
forest. So I moved them to the variable slots and chose combinator labels whose effects do
nothing on the permanents they can land on.

**Where label effects land.** The protocol keeps one invariant, and the simulator asserts it
after every step: **a leaf always enchants a cell or the anchor, and a cell always enchants a
leaf or a cell.** So a leaf label's effect falls only on an Indestructibility token or on the
anchor Island. The cell label's effect (indestructible) falls only on Aura tokens.

| role | card | Oracle text | why it is inert here |
|---|---|---|---|
| cell | **Indestructibility** {3}{W} | "Enchant permanent / Enchanted permanent has indestructible. (Effects that say "destroy" don't destroy that permanent. A creature with indestructible can't be destroyed by damage.)" | nothing is ever destroyed; sacrifice and 704.5m are not destruction (701.21a) |
| S | **Bound in Gold** {2}{W} | "Enchant permanent / Enchanted permanent can't attack, block, or crew Vehicles, and its activated abilities can't be activated unless they're mana abilities." | cells have no activated abilities; the Island's is a mana ability |
| K | **Intercessor's Arrest** {2}{W} | "Enchant permanent / Enchanted permanent can't attack, block, or crew Vehicles. Its activated abilities can't be activated unless they're mana abilities." | same |
| I | **Curator's Ward** {2}{U} | "Enchant permanent / Enchanted permanent has hexproof. / When enchanted permanent leaves the battlefield, if it was historic, draw two cards. (Artifacts, legendaries, and Sagas are historic.)" | hexproof stops only opponents (702.11b); cells and basic lands are not historic (700.6), so under the intervening-if rule (603.4) the trigger never fires |
| B | **Essence Leak** {U} | "Enchant permanent / As long as enchanted permanent is red or green, it has "At the beginning of your upkeep, sacrifice this permanent unless you pay its mana cost."" | it lands only on white cells or the colourless Island. Ruling (2004-10-04): "It can enchant a permanent that is not red or green, but it doesn't do anything in that case." |
| C | **Faith's Fetters** {3}{W} | "Enchant permanent / When this Aura enters, you gain 4 life. / Enchanted permanent can't attack or block, and its activated abilities can't be activated unless they're mana abilities." | harmless ETB trigger (life gain) each time a C node is copied; it resolves above FP |
| W | **Elemental Resonance** {2}{G}{G} | "Enchant permanent / At the beginning of your first main phase, add mana equal to enchanted permanent's mana cost. (…)" | triggers only at the start of a precombat main phase; adds mana |
| variables | **Confiscate** {4}{U}{U} "Enchant permanent / You control enchanted permanent."; **Lay Claim** {5}{U}{U} "Enchant permanent / You control enchanted permanent. / Cycling {2} …"; **Volition Reins** {3}{U}{U}{U} "Enchant permanent / When this Aura enters, if enchanted permanent is tapped, untap it. / You control enchanted permanent."; **Take Possession** {5}{U}{U} "Split second … / Enchant permanent / You control enchanted permanent."; **Psychic Overload** {3}{U} "Enchant permanent / When this Aura enters, tap enchanted permanent. / Enchanted permanent doesn't untap during its controller's untap step. / Enchanted permanent has "Discard two artifact cards: Untap this permanent.""; **Dream Leash** {3}{U}{U} "Enchant permanent / You can't choose an untapped permanent as this spell's target as you cast it. / You control enchanted permanent." | control change is idempotent under one controller; tapping or untapping a cell is harmless; split second and Dream Leash's casting restriction matter only when the template is cast (tap the template Island first for Dream Leash) |

An SKI-only deck needs 4 labels (Indestructibility, Bound in Gold, Intercessor's Arrest,
Curator's Ward), and none of them ever triggers. A BCKW-only deck can avoid triggers too, with
C = Bound in Gold and W = Curator's Ward. Only the 7-label mixed deck needs Faith's Fetters
and Elemental Resonance.

**Rejected labels** (from the 32-card search
`t:aura (o:"enchant permanent" or o:"enchant enchantment" or …)`):
- harmful to the structure:
  - **Song of the Dryads** ("Enchanted permanent is a colorless Forest land") would turn a
    node into a land, and a non-Aura that is attached becomes unattached (704.5p).
  - **Minimus Containment** ("is a Treasure artifact … loses all other abilities") fails the
    same way.
  - **Reality Acid** ("When this Aura leaves the battlefield, enchanted permanent's
    controller sacrifices it") would sacrifice the head's host whenever the head is
    sacrificed.
  - **In Bolas's Clutches** is a "Legendary Enchantment — Aura", so its copies die to the
    legend rule (704.5j).
- harmful to the player: the five **Runes** ("When this Aura enters, draw a card") would deck
  P under unbounded copying (704.5b). **Feedback**, **Power Leak**, **Power Taint** and **Soul
  Tithe** cause upkeep damage or a sacrifice tax. **Detention Vortex** has
  "{3}: Destroy this Aura. Only your opponents may activate this ability", which gives the
  opponent a lever.
- unusable on the anchor land: **Suppression Bonds**, **Detention Vortex**, **Gobsmacked**,
  **Soul Tithe** and **Minimus Containment** are "Enchant nonland permanent", and **Steal
  Enchantment**, **Feedback**, **Power Leak** and **Power Taint** are "Enchant enchantment".
  Any label can become the head, which sits on the anchor. (Suppression Bonds would work with
  a nonland anchor such as Darksteel Relic: "Indestructible".)

**Card count.** The engine is 7 cards plus 2 Islands. Labels: 7 for mixed SKI+BCKW, 4 for SKI
only, 5 for BCKW only. Add 0–6 variable labels. The minimum for closed SKI terms is therefore
13 cards, and the full mixed basis takes 16.

## Rules relied on (CR 2026-11-06; quotes copied from the fetched text)

- **303.4f** "If an Aura is entering the battlefield under a player's control by any means other than by resolving as an Aura spell, and the effect putting it onto the battlefield doesn't specify the object or player the Aura will enchant, that player chooses what it will enchant as the Aura enters the battlefield. The player must choose a legal object or player according to the Aura's enchant ability and any other applicable effects." The token copy's host is chosen here. It is not targeted (Mythos of Illuna ruling above), so hexproof on a host does not matter.
- **303.4g** "… If the Aura is a token, it isn't created." This applies only if nothing is legal to enchant, which never happens here.
- **303.4d** "An Aura can't enchant itself. … An Aura can't enchant more than one object or player." Hence a forest, and no sharing (L3).
- **303.4e** "An Aura's controller is separate from the enchanted object's controller … changing control of the object doesn't change control of the Aura, and vice versa."
- **111.2** "The player who creates a token is its owner. The token enters the battlefield under that player's control." Every node is P's.
- **111.3** "The spell or ability that creates a token may define the values of any number of characteristics for the token. … The characteristic values defined this way are functionally equivalent to the characteristic values that are printed on a card; for example, they define the token's copiable values." With **707.2** ("The copiable values are the values derived from the text printed on the object … Other effects …, status, counters, and stickers are not copied."), a token copy of a token copy of Bound in Gold is a Bound in Gold Aura. This answers question 1: a token copy of a token Aura behaves exactly like a copy of the card, and like it carries no attachments (FP and Replicator rulings).
- **707.10** "A copy of a spell … copies … all decisions made for it, including modes, targets … a copy of a spell isn't cast … A copy of a spell or ability is controlled by the player under whose control it was put on the stack. A copy of a spell is itself a spell". **707.10c** "… If the player chooses to change some or all of the targets, the new targets must be legal. Once the player has decided what the copy's targets will be, the copy is put onto the stack with those targets." The FP copy's new target, the node, is legal for "target permanent".
- **405.2** "Each time an object is put on the stack, it's put on top of all objects already there." **405.5** / **117.4**: when all players pass, the top object resolves; "if the stack is empty, the phase or step ends." **500.2** "A phase or step … ends when the stack is empty and all players pass in succession." While FP sits on the stack, the main phase cannot end.
- **608.2b** "A target that's no longer in the zone it was in when it was targeted is illegal. … If all its targets … are now illegal, the spell or ability doesn't resolve." Reiterate's target (FP) must still be on the stack when Reiterate resolves, and each FP copy's node must still be on the battlefield when the copy resolves.
- **702.27a** buyback: "put this spell into its owner's hand instead of into that player's graveyard as it resolves."
- **117.1a** "A player may cast an instant spell any time they have priority. A player may cast a noninstant spell during their main phase any time they have priority and the stack is empty." **307.1** (sorceries, same). **117.1b** "A player may activate an activated ability any time they have priority." Only FP and the template Auras are cast at sorcery speed. Everything else, including every FP *copy* (not cast, 707.10), happens at instant speed above FP.
- **106.4** "Each player's mana pool empties at the end of each step and phase".
- **117.5 / 704.3** "Whenever a player would get priority …, the game checks for any of the listed conditions for state-based actions, then performs all applicable state-based actions simultaneously as a single event. If any state-based actions are performed as a result of a check, the check is repeated". **704.5m** "If an Aura is attached to an illegal object or player, or is not attached to an object or player, that Aura is put into its owner's graveyard." **704.5d** "If a token is in a zone other than the battlefield, it ceases to exist." **111.7** (the same for tokens).
- **701.21a** "To sacrifice a permanent, its controller moves it from the battlefield directly to its owner's graveyard. A player can't sacrifice something that isn't a permanent, or something that's a permanent they don't control. Sacrificing a permanent doesn't destroy it".
- **701.3b** "If an effect tries to attach an Aura … to the object or player it's already attached to, the effect does nothing."
- **104.4b** "… Loops that contain an optional action don't result in a draw." **733.4** "If a loop contains only mandatory actions, the game is a draw."
- **603.4** (intervening "if"), **700.6** (historic), **702.11b** (hexproof: "can't be the target of spells or abilities your opponents control"), **704.5j** (legend rule), **704.5p** (attached non-Aura becomes unattached), **704.5b** (drawing from an empty library loses the game): used in the label analysis only.

Items L5 marked UNVERIFIED that I depend on, re-checked:
- L5 Q6 "I did not locate a specific printed card that makes a token copy of an Aura": now
  located. Flash Photography, Mythos of Illuna and Replication Technique all say "Create a
  token that's a copy of target permanent [you control]", and the Mythos ruling covers Aura
  tokens explicitly.
- L3 open question 6 (Guildmage's controller clause): settled by the ruling quoted above.
- Still open, and not depended on: L3 open question 7 (whether attachment cycles are legal).
  The protocol never creates one.

## Primitive moves

All three run at instant speed while FP sits at the bottom of the stack.

| move | game actions | cost | stack objects resolved |
|---|---|---|---|
| **COPY**(n → h) | 6 mana loops; cast Reiterate with buyback targeting FP; all pass, and Reiterate resolves, putting an FP copy with new target n on the stack (Reiterate returns to hand); all pass, and the FP copy resolves: a token copy of n enters attached to h, chosen under 303.4f | 6 mana ({R}{R} among it) | 2 (+12 for the loops) |
| **MOVE**(n → h) | 2 mana loops; activate Guildmage targeting Aura n; all pass; on resolution choose h ≠ n's current host, with the same controller as that host | {1}{U} | 1 (+4) |
| **SAC**(n) | Auratog: sacrificing n is the cost. Before anyone gets priority, the SBA loop runs 704.5m to a fixpoint | 0 | 1 |

**Copy-engine choreography, session level.**
1. *Open the session.* In P's main phase, with the stack empty, cast Flash Photography
   targeting the template Island T. This is sorcery timing (117.1a). FP's own flash clause
   would also allow casting it later, since T is "a permanent you control". Stack: `[FP(T)]`.
2. *During the session,* every COPY, MOVE and SAC adds objects above FP, and they resolve
   before FP does. Each Reiterate needs *some* instant or sorcery spell on the stack, both
   when it is cast (601.2c) and when it resolves (608.2b). FP is the only one that persists,
   so **the original must stay on the stack for as long as copying goes on.** One could also
   let several FP copies pile up (several Reiterates, then resolve them top-first; hosts are
   chosen on resolution). Nothing needs that.
3. *Close the session.* With only FP left on the stack, P passes and the opponent passes. FP
   resolves and makes a token copy of the Island T, which is harmless. The stack is empty,
   and the next pass ends the phase. If FP's target had left the battlefield, FP would not
   resolve (608.2b) and would go to the graveyard. Flashback {4}{U}{U} then gives one more
   session, and a third would need another copy sorcery (Mythos of Illuna, Replication
   Technique). One session is enough for any computation, because a session has no length
   limit. The danger is ending one by accident: a stray pass with only FP on the stack ends it.

## Rewrite table

Notation: P is the head's host (the anchor, or the cell above an argument when normal order
works inside an argument). h is the head leaf. c1..ck are its redex cells, r_j is the root
leaf of argument j, rest = c(k+1) (with everything below it, or absent), and last(r) is the
last cell of r's spine (or r itself if it has none). Every sequence ends with SAC h. The
sequences come straight from `rewrite()` in `l6sim.py`.

| rule | MOVE sequence (then COPY, then SAC h) | MOVEs | COPYs | dies in the SBA cascade |
|---|---|---|---|---|
| I x → x | r1→P; [rest→last(r1)] | 1 (+1) | 0 | c1 (empty) |
| K x y → x | r1→P; [rest→last(r1)] | 1 (+1) | 0 | c1, c2 and the whole subtree of y: depth(y)+2 passes |
| B x y z → x (y z) | r1→P; c2→last(r1); c3→last(r2); [rest→c2] | 3 (+1) | 0 | c1 (empty) |
| C x y z → x z y | r1→P; c3→last(r1); c2→c3; [rest→c2] | 3 (+1) | 0 | c1 (empty) |
| W x y → x y y | r1→P; c2→last(r1); c1→c2; [rest→c1]; COPY subtree(r2) onto c1 | 3 (+1) | \|y\| | nothing |
| S x y z → x z (y z) | r1→P; c3→last(r1); c2→c3; [rest→c2]; c1→last(r2); COPY subtree(r3) onto c1 | 4 (+1) | \|z\| | nothing |

Here |t| is the number of Auras encoding t: one leaf per atom and one cell per application,
so 2·atoms − 1. **COPY subtree** works top-down and node by node: copy the root leaf onto the
target cell, then for each cell of its chain copy the cell onto the previous new node and
recursively copy that cell's leaf onto the new cell. Every token therefore enters attached to
a permanent that already exists. No move ever attaches a node to one of its own descendants,
because each moved cell is first emptied or carries only what should travel with it. The
simulator checks acyclicity after every primitive.

**Cost per step** (measured in `output.txt`, "per-rule cost" table): MOVEs are constant per
rule (1, 1, 3, 3, 3, 4, plus 1 if the redex has further arguments), with 1 SAC. COPYs are
2n−1 for an n-atom copied argument. Mana is 2·MOVE + 6·COPY. Compare L2, where `W x y` costs
|y|+|x| copies and |x|+1 counters because the stack cannot insert below. On the battlefield,
re-attachment is O(1) whatever the size of x.

**Is it both SKI and BCKW? Which is cheaper?** It is both: all six rules are implemented, and
I is optional for BCKW (`BCKW-noI` replaces I by C K K). Per step, W is one move cheaper than
S and copies the same amount. Over whole programs the gap comes from compiled size and how
much gets copied. Five Church-arithmetic programs, compiled three ways and run to normal form
(mana = total over the run, from `output.txt`):

| program | SKI mana (moves/copies) | BCKW+I mana | SKIBC (Turner) mana |
|---|---|---|---|
| succ 2 p q | 112 (38/6) | 84 (36/2) | 48 (18/2) |
| plus 2 2 p q | 434 (79/46) | 156 (69/3) | 90 (36/3) |
| mult 2 2 p q | 514 (74/61) | 188 (55/13) | 122 (34/9) |
| 2 2 p q | 634 (83/78) | 286 (71/24) | 182 (43/16) |
| mult 3 2 p q | 986 (112/127) | 324 (87/25) | 206 (52/17) |

On these programs BCKW uses 25–67% less mana than SKI, and mixed SKIBC is cheapest. This
compares naive S-only bracket abstraction (with K and eta rules) against B/C-aware
abstraction, on five programs. It is not a theorem about the bases.

**Lazy or shared copying:** none. I accept L3's argument: an Aura has one host (303.4d), and
no copy effect carries attachments (707.2; the FP, Mythos and Replicator rulings). A copy
cannot be deferred either, because there is no pointer to stand in for the deferred copy. The
cost is ordinary tree-copying normal order, so copies made for a duplicated argument may be
thrown away later by a K (`S I I (S I I)` makes 96 copies in 40 steps).

## Worked trace 1: S K K x → x (from `output.txt`)

`#n` is the object id, and the card name is in brackets. Setup, not shown: the template
Auras are cast onto the template Island #6, FP is cast targeting #6, and the 7 nodes are
built by 7 COPYs from the templates (62 mana).

```
initial board (child indented under the permanent it enchants):
  ANCHOR#5[Island]
    S#11[Bound in Gold]
      CELL#12[Indestructibility]
        K#13[Intercessor's Arrest]
        CELL#14[Indestructibility]
          K#15[Intercessor's Arrest]
          CELL#16[Indestructibility]
            x#17[Confiscate]
stack(bottom->top): Flash Photography (original, target THOST#6[Island])
step 1: redex head S#11[Bound in Gold] on ANCHOR#5[Island]
  [one mana loop, in full: tap Gilded Lotus for UUU (mana ability, no stack); pay {2}, tap
   Isochron Scepter: ability on the stack above FP; all pass: it resolves, you cast the copy
   of Dramatic Reversal; all pass: it resolves, untapping Lotus and Scepter. Net: +1 U,
   stack back to FP alone]
  mana: 2 loops
  activate Guildmage targeting K#13; stack: FP(original), Guildmage ability (target K#13)
  MOVE  K#13 : CELL#12 -> ANCHOR#5            (x becomes the head)
  MOVE  CELL#16 : CELL#14 -> K#13             (cell holding z)
  MOVE  CELL#14 : CELL#12 -> CELL#16          (cell holding y)
  MOVE  CELL#12 : S#11 -> K#15                (freed cell: argument of y)
  mana: 6 loops
  cast Reiterate with buyback targeting FP;   stack: FP(original), Reiterate
  Reiterate resolves: copy of FP with new target x#17; Reiterate -> hand;
                                              stack: FP(original), FP copy (target x#17)
  COPY  x#17[Confiscate] => new x#18 on CELL#12   (host chosen under 303.4f)
                                              stack: FP(original)
  SAC   S#11[Bound in Gold]                   (nothing hangs from it: no SBA)
  => K x (K x)
step 2: redex head K#13[Intercessor's Arrest] on ANCHOR#5[Island]
  MOVE  x#17 : CELL#16 -> ANCHOR#5
  SAC   K#13
  SBA pass 1 (704.5m; tokens cease to exist 704.5d): CELL#16
  SBA pass 2: CELL#14
  SBA pass 3: K#15
  SBA pass 4: CELL#12
  SBA pass 5: x#18
  => x
  Flash Photography (original, target THOST#6) resolves: token copy of THOST#6 (harmless)
normal form: x ; steps=2 moves=5 copies=1 sacs=2 sba=5 mana=16 stack_res=42
```

(The trace in `output.txt` prints the full stack line for every Guildmage activation. I
shortened the later ones here.)

## Worked trace 2: one S step that copies a compound argument

`S x y (K a b)`, step 1. Here z = `K a b`: 5 Auras (K, two cells, a, b). Each COPY below is
one full Reiterate/FP cycle, with the stack choreography spelled out in trace 1: 6 loops,
Reiterate onto FP, FP copy with the new target, the token enters, stack back to `[FP]`.

```
initial:  ANCHOR#5 <- S#14 <- CELL#15 (<- x#16) <- CELL#17 (<- y#18) <- CELL#19 (<- K#20 <- CELL#21 (<- a#22) <- CELL#23 (<- b#24))
MOVE  x#16[Volition Reins] : CELL#15 -> ANCHOR#5       (x becomes the head)
MOVE  CELL#19 : CELL#17 -> x#16                         (cell holding z)
MOVE  CELL#17 : CELL#15 -> CELL#19                      (cell holding y)
MOVE  CELL#15 : S#14 -> y#18                            (freed cell: argument of y)
COPY  K#20    => new K#25    on CELL#15                 (root of z's copy)
COPY  CELL#21 => new CELL#26 on K#25                    (its first spine cell)
COPY  a#22    => new a#27    on CELL#26
COPY  CELL#23 => new CELL#28 on CELL#26                 (second spine cell, under the first)
COPY  b#24    => new b#29    on CELL#28
SAC   S#14                                              (empty: no SBA)
=> x (K a b) (y (K a b))
```

Steps 2 and 3 are K steps. Each moves `a` up one level and sacrifices K, and the cascade then
removes the cell holding `b` and `b` itself. The result is `x a (y a)`, with 6 moves, 5
copies, 3 sacrifices and 42 mana in total.

## Simulator output (`lines/L6/output.txt`)

`l6sim.py` models the battlefield (engine permanents, two Islands, template Auras, Aura
tokens with hosts), the stack (FP, Reiterate, FP copies, Guildmage, Auratog and Scepter
abilities, Dramatic Reversal copies, ETB triggers), the mana pool by colour, and SBAs. It
applies two kinds of check:
- *rules* checks: Reiterate needs FP on the stack and Reiterate in hand; an FP copy's
  target must be on the battlefield when it resolves; a 303.4f host must exist; the
  Guildmage's new host must differ from the current one and be a permanent; FP and the
  template Auras need an empty stack when cast; mana must be paid.
- *protocol* checks: acyclicity, the encoding invariants, the leaf-host invariant behind the
  label analysis, and Essence Leak never on a red or green permanent.

It decodes the board after every step and asserts equality with an independent
leftmost-outermost reducer. It also asserts that the board's redex search and the
reference's agree on whether a redex exists, and compares each normal form with a second,
independently written reducer. Results:

- 17 fixed terms, all OK. They include S K K x, W K x, S I I (K a), S I I I, B f g x,
  C f x y, C (B f) x y, B (C K) W x y, S x y (K a b), Church 2 f x, succ 2 f x, 2 2 f x, and
  K a (S I I (S I I)) and K a (W W W), which discard a divergent argument with 1 move,
  1 sacrifice, and a 10- or 6-pass cascade. Also W (B f) (K a), S (K (S I)) K a b and
  K (I a), which reduces under an argument.
- Non-normalising terms under a 40-step bound, in lockstep on every step: S I I (S I I);
  W W W; Y f, which descends into arguments forever.
- The per-rule cost table, and the basis comparison above (20 runs, all OK).
- 500 random terms (1–24 atoms over S K I B C W a b c), all in lockstep: 496 reached normal
  form and 4 hit the 80-step bound. Totals: 1796 steps, 4918 moves, 5693 copies, 1796
  sacrifices.
- Protocol demonstrations: a MOVE that would make an attachment cycle passes every modelled
  rules check and is rejected only by the protocol. Sacrificing a cell mid-term is legal, and
  the cascade silently drops arguments.

Not modelled: the opponent (always passes), turns and phases beyond one main phase, life
totals beyond counting Faith's Fetters, the Island-token side effect beyond logging it, and
the setup of the engine itself.

## What is forced vs chosen

**Forced (no player choice once the preceding action is taken):**
- After a SAC, the cascade: 704.5m applied to a fixpoint before anyone gets priority
  (117.5, 704.3). K's discarded argument, and the empty cells of I, B and C, are collected
  this way, whatever their size.
- What a COPY produces: the label is the copied node's copiable values (707.2, 111.3); no
  attachments, counters or status come along.
- That Reiterate returns to hand (buyback), that FP copies resolve before FP (405.2), and the
  ETB triggers of Faith's Fetters (and of Psychic Overload or Volition Reins if used as
  variables).

**Chosen by the player (P):** every MOVE (which Aura, and the new host on resolution), every
COPY (which node, through Reiterate's new target, and the host under 303.4f), every SAC, every
mana loop, when to open and close the session, and passing priority. Finding the redex is a
deterministic structural walk over a public zone (400.2), but the player performs it.

**The model, stated honestly.** "Cooperative" means P, following the rewrite table, makes
only legal moves, and the opponent passes. The cards do not prevent other moves. A cheating or
erring player could:
- move any Aura onto any permanent P controls, including onto its own descendant, which
  creates a detached cycle that no SBA ever collects (rules allow it on my reading; the
  simulator's demo);
- move a node onto an engine permanent: Bound in Gold or Intercessor's Arrest on Auratog
  switches off its sacrifice ability, which is not a mana ability;
- copy any permanent, not just nodes (more Lotuses, a second Guildmage);
- sacrifice any node: a cell mid-term silently drops arguments (the demo);
- reduce a non-leftmost redex, or stop at any time;
- end the session by passing with FP alone on the stack.

The opponent can also respond at every pass, for example by countering Reiterate or removing
the Guildmage. None of these break the rules. They break the computation.

**Termination and "halting."** Every action in the construction is optional, so a reduction
that never ends is not a draw (104.4b, 733.4). "Halting" means the board reaches a state where
the structural walk finds no redex, P sees this, and P closes the session. The game itself
registers nothing: no trigger fires on normal form and no outcome follows. For a
non-normalising term, P may go on forever; the simulator's Y f run does 40 legal steps with
no end in sight. If P stops, the game simply continues, and a partial reduct sits on the
battlefield. A shortcut (733.2a) could compress the mana loop, and the whole of a normalising
reduction since every outcome is predictable. That is my reading, and the construction does
not depend on it.

## Alternatives weighed

Searches run (Scryfall, 2026-11-21):
1. `o:"token that's a copy of target" -t:instant -t:sorcery -o:"target creature"`: 27 cards.
2. `o:"token that's a copy of target" (t:instant or t:sorcery) -o:"target creature" -o:"target artifact"`: 6 cards.
3. `(o:"copy of target enchantment" or o:"copy of target aura" or o:"copies of target permanent" or o:"copy of each aura")`: 1 card (Venser, Fervent Forger: an opponent's permanent only, once).
4. The label search above (32 Auras).

- **Copy spells that fit FP's slot:** Mythos of Illuna ("Create a token that's a copy of
  target permanent." The RG bonus does not apply to copies, per its ruling) and Replication
  Technique ("target permanent you control") both work. Rejected: Cackling Counterpart,
  Quasiduplicate, Croaking Counterpart and Will of the Temur make creature copies, and an Aura
  that is a creature can't enchant (303.4d). Clone Legion copies only creatures. Applied
  Geometry ("non-Aura"). Ashling's Command (Elementals).
- **Replicator** {2} Artifact: "When this artifact enters, create a Food token. … / {2}, {T}:
  Create a tapped token that's a copy of target token you control." Ruling (2026-10-07): "The
  token copies the original characteristics of the target token as stated by the effect that
  created it … It doesn't copy … any Auras or Equipment attached to it". **This is a
  repeatable token copy of an Aura, the very thing L3 said did not exist.** It requires every
  node to be a token, which holds after setup, since the term is built from FP copies. Dramatic
  Reversal untaps it ("nonland permanents"), so inside the mana loop it gives COPY for {2}
  with one stack object instead of Reiterate's 6 mana and two objects, and it needs no parked
  spell. The physical templates are not tokens, so setup still needs FP and Reiterate, and
  Replicator adds a card. Its costs differ from COPY's, but the abstract primitive is the
  same, so I did not simulate it separately. Without the infinite loop, Replicator gives one
  copy per turn, unbounded in turns. But a multi-turn computation draws a card every turn,
  and 704.5b ("If a player attempted to draw a card from a library with no cards in it …,
  that player loses the game") bounds the turn count by the library. The same caveat applies
  to L3's remark that "only the number of turns is unbounded".
- **Romana II** ("{1}, {T}: Create a tapped token that's a copy of target token that entered
  this turn") would also work inside a single-turn session with an untapper. Not pursued.
- One-shot or narrow, all rejected:
  - one-shot or a few uses: Caretaker's Talent; City of Death, Three Blind Mice and Esper
    Terra (Saga chapters); Specimen Collector (dies); Dutiful Replicator (enters; would need
    flicker);
  - once per turn or per combat: Hazel of the Rootbloom (end step); Esika's Chariot (attack);
  - artifacts or creatures only: Cogwork Assembler, Donatello, Jurati, Schema Thief,
    Worldwalker Helm, Urza, Mishra, Saheeli Rai, Kiki-Jiki, Dance of Many, Shaun, Oltec
    Matterweaver;
  - other restrictions: Ghired (needs nontoken creatures, and the token must have entered
    this turn); Adagia (the copy is legendary); Orvar (one cast spell per copy); Saheeli,
    Radiant Creator (creature copies).
- **Copying an Aura spell** (707.10f: "As that copy resolves, it ceases being a copy of a spell
  and becomes a token permanent."): Lithoform Engine's "{4}, {T}: Copy target permanent spell
  you control. (The copy becomes a token.)" has no "choose new targets" clause. Every copy
  therefore keeps the original Aura spell's target (707.10), so all copies land on one host and
  each would then need a Guildmage move. Worse, a subtree copy needs an Aura spell of *each*
  label on the stack at once, and Aura spells are sorcery-speed (117.1a), so only the first can
  be cast. Rejected as strictly worse. Double Major copies creature spells only.
- **Mirrormade / Copy Enchantment** are nontoken "enter as a copy" effects: one per card unless
  flickered. Not pursued.

## Where it breaks / open rules questions

1. **Not forced.** This is the main limitation, unchanged from L2 and L3. Every MOVE and COPY
   is a chosen target or host; only the K cascade is forced. Forcedness belongs to L7.
2. **The opponent must pass.** Every resolution is a priority round. The model assumes that
   no response comes.
3. **Session fragility.** One stray pass with FP alone on the stack ends the copy engine. The
   flashback gives exactly one restart (a third session needs another copy sorcery), so
   errors are recoverable only a bounded number of times.
4. **Physical scale.** `2 2 f x` in SKI takes 634 mana, which means 634 Scepter/Dramatic
   Reversal loops and 1533 stack resolutions, before counting setup. It works in principle
   and is impractical at a table without shortcuts.
5. **Variables are bounded** by distinct "Enchant permanent" label cards (6 spare). Closed
   terms are unaffected.
6. **Open: attachment cycles** (L3 open question 7). 303.4d forbids only self-attachment, so on
   my reading a Guildmage move can close a cycle. The protocol never does, and no ruling was
   found.
7. **Open: Elemental Resonance and Essence Leak across turns.** They are inert within one main
   phase. In a multi-turn variant, Essence Leak could matter only if a B leaf enchanted a green
   permanent, and the leaf-host invariant prevents that.

## What I did not verify

- Tournament rules: slow play, and shortcut handling beyond CR 733.
- Any judge or official source on chaining Reiterate on a parked sorcery across many copies.
  I rely on 707.10, 707.10c and 608.2b and the Reiterate rulings.
- Gatherer pages themselves (I used Scryfall's mirrors of the rulings); Auratog and Dramatic
  Reversal have no rulings on Scryfall.
- Dream Leash's paper legality (the lookup was rate-limited); its Oracle text was verified.
- Searches 1–3 are wording-limited. A card that copies a permanent's attachments recursively,
  or a repeatable copier phrased differently, could exist.
- The Replicator and Romana II variants are argued, not simulated.
- How the engine reaches the battlefield (deck, draws, earlier turns) is assumed.
- The simulator's controller is trusted code. It shows that the protocol is correct given the
  primitives, and that each primitive passes the rules checks I modelled. It does not show
  that those checks are all the relevant rules.
- No independent review (Wizard or Witchhunter) has been run on this note or on the simulator.

## Status

- 2026-11-21: L6 note and simulator written; `python3 -I lines/L6/l6sim.py` exits 0 with
  `ALL OK` (17 fixed terms, 3 divergent terms under a bound, 20 basis-comparison runs, 500
  random terms, all in lockstep with the reference). Verdict: conjecture holds, cooperative
  and unbounded within one main phase, full SKI and BCKW, structural redexes, forced K
  collection. Engine: 7 cards plus 2 Islands; labels 4 (SKI), 5 (BCKW) or 7 (both). Found
  Replicator as a repeatable Aura-token copier. Not reviewed.

## Review addendum (dara, 2026-11-21, from the Wizard pass)

Verdict on this note: sound with gaps; the rewrite table holds in general (hand-checked by the
reviewer with trailing arguments and nested redexes; mutation tests on the simulator caught
wrong move sequences; 3000 further random terms in lockstep). Corrections to read into the text
above, which is left as written:
- Summary/Status: "a fixed, legal sequence of real game actions" should read "legal on our
  reading of CR 2026-11-06 and the cited rulings, without judge confirmation". The simulator
  shows the abstract moves are right on the terms tested; it does not check the same-controller
  clause, cycle legality, or trigger timing.
- "Labels" invariant: l6sim.py asserts only the leaf half, and only between steps. The cell
  half and the per-move version hold by inspection (leaves move only to P; cells only to
  last(r) or a cell), not by assertion.
- "second, independently written reducer": ref_nf shares contract/unwind/rebuild with ref_step;
  it differs in strategy, not in code.
- Moving a cell carries what is attached to it because the Aura stays the same object on the
  battlefield (no zone change; contrast 400.7); cite 701.3 for attach. Not cited above.
- Trace 2: the K cascade takes 3 passes, not 2 (it also removes the emptied cell that held a).
- "No effect copies a permanent with its attachments" is "none found"; searches were by wording.
Reviewer could not check Oracle text, rulings or CR quotes against their sources (no network).
