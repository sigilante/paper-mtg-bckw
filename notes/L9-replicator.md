# L9 — Replicator as the COPY primitive

Variant of L6 (`notes/L6-hybrid.md`). Author: L9 subagent, 2026-11-21. Executable check:
`lines/L9/l9sim.py` (derived from `lines/L6/l6sim.py`), output in `lines/L9/output.txt`
(`python3 -I l9sim.py`, exit 0, ends with `ALL OK`; about two minutes).
Card text and rulings: Scryfall single-card lookups (`/cards/named?exact=…` and each card's
`rulings_uri`) and one Scryfall search, all fetched 2026-11-21. Rules: the CR quotes already in
L6 and `notes/L5-rules-checks.md` (CR effective 2026-11-06). I fetched no rules text myself;
rules I cite without a quote are marked *(number only, not quoted)*.

Wording, as the L6 review addendum asks: "legal" below means **legal on our reading of the
quoted rules and rulings, without judge confirmation**. The simulator shows that the abstract
moves are right on the terms tested; it does not prove the rules claims.

## Summary

**Verdict: yes, on our reading. A Replicator COPY makes a simpler and smaller unbounded machine
than L6, and a more robust one, under the same cooperative conditions as L6.**

- **No parked spell.** Every primitive is an activated ability that leaves the stack empty when
  it is done. A stray pass no longer ends the session. The computation can stop at any
  primitive boundary, let the step or the whole turn end, and resume later, at instant speed in
  any step of either player's turn. The cost of a pause is at most the unspent mana in the pool.
  The bound on the number of turns is the library, because P draws a card each turn (704.5b);
  each turn still allows unboundedly many actions.
- **Cheaper copy.** COPY costs {2} and one stack object (plus two mana loops, which also untap
  Replicator), against L6's 6 mana and two stack objects. MOVE and SAC are unchanged. On the
  500 random terms L6 used, mana falls from 43,994 to 21,222 (−52%) and stack resolutions from
  107,076 to 55,339. `2 2 p q` in SKI falls from 634 to 322 mana.
- **Fewer cards.** Engine G (Guildmage MOVE, Replicator COPY): 11 cards for closed SKI terms
  with an I label (L6: 13), 14 for the full mixed basis (L6: 16). Engine R (no Guildmage;
  each step rebuilds the reduct by copies and sacrifices the old head): 10 and 13, at about
  2–6 times L6's mana on the test programs (3.3 times on the random terms). The copier swap by itself saves no card (Flash Photography + Reiterate
  becomes Lithoform Engine + Replicator). The saving comes from dropping both Islands
  (Replicator's Food token hosts the label cards, and Lithoform Engine is the anchor). Engine R
  saves one more card by dropping the Guildmage.
- **What it needs.** Every node that is ever copied must be a token. So a one-shot card→token
  step per label remains. The cheapest I found is Lithoform Engine copying each label Aura
  *spell* as it is cast. The copy becomes an Aura token, which is the seed for Replicator.
  One card covers every label.

**Conditions** (as in L6, plus one): P controls every permanent involved; the opponent passes;
the engine starts on the battlefield (assumed, not constructed); open terms are limited to
**5** free variables (L6: 6), because Take Possession's split second forbids the Lithoform
activation that would seed it.

## Oracle text and rulings (Scryfall, fetched 2026-11-21)

**Replicator** {2}, Artifact, rare, *Star Trek* (set `trk`, released 2026-11-13).
`games: paper, mtgo, arena`; `digital: false`; legal in Legacy, Vintage, Modern and Commander
(not Pauper). Oracle text:
> When this artifact enters, create a Food token. (It's an artifact with "{2}, {T}, Sacrifice
> this token: You gain 3 life.")
> {2}, {T}: Create a tapped token that's a copy of target token you control.

Rulings (all three, published 2026-10-07, source wotc):
1. "If the original token is copying something else, then the new token enters as whatever that
   token copied. If it's copying something with {X} in its mana cost, X is 0."
2. "The token copies the original characteristics of the target token as stated by the effect
   that created it (unless that token is copying something else; see below). It doesn't copy
   whether that token is tapped or untapped, whether it has any counters on it, or any Auras or
   Equipment attached to it, or any non-copy effects that have changed its types, color, power
   and toughness, and so on. Notably, the token you create won't be attacking, even if the
   original token is."
3. "If the target token had any "When [this token] enters" abilities, the new token also has
   those abilities, and they'll trigger when it's created. Similarly, any "As [this token]
   enters" or "[This token] enters with" abilities that the token has copied will also work."

**Lithoform Engine** {4}, Legendary Artifact; paper, mtgo, arena; Legacy-legal:
> {2}, {T}: Copy target activated or triggered ability you control. You may choose new targets
> for the copy.
> {3}, {T}: Copy target instant or sorcery spell you control. You may choose new targets for the
> copy.
> {4}, {T}: Copy target permanent spell you control. (The copy becomes a token.)

Rulings used (2020-09-25): "Lithoform Engine can copy any spell or ability on the stack, not
just one with targets. If a permanent spell is copied, new targets can't be chosen for it, if it
has any (perhaps because it's an Aura or a mutating creature spell)." "The copy will resolve
before the original spell or ability does." "If a permanent spell is copied, it's put onto the
battlefield as a token as the spell resolves rather than putting the copy of the spell onto the
battlefield. The rules that apply to a permanent spell becoming a permanent apply to a copy of a
spell becoming a token." "The token that a resolving copy of a spell becomes isn't said to have
been "created.""

Re-fetched in the same session (text identical to L6's quotes): Isochron Scepter, Dramatic
Reversal, Gilded Lotus, Simic Guildmage, Auratog (all paper, Legacy-legal). Also:
- **Elemental Resonance**, full text (L6 cut the reminder): "Enchant permanent / At the beginning
  of your first main phase, add mana equal to enchanted permanent's mana cost. (Mana cost
  includes color. If a mana symbol has multiple colors, choose one.)" Rulings: "You get the mana
  whether you want it or not. If you don't spend it, it will disappear at the end of the current
  step (or phase)." "This ability isn't a mana ability. It uses the stack." "Only the first main
  phase in a turn is the "precombat main phase" …"
- **Take Possession**: "Split second (As long as this spell is on the stack, players can't cast
  spells or activate abilities that aren't mana abilities.) / Enchant permanent / You control
  enchanted permanent."
- **Dream Leash**: paper (`games: paper, mtgo`), Legacy-legal. This closes L6's unchecked item.
  Text as L6 quotes it.

Search for other Aura movers, `o:"attach target aura"` (7 cards): Aura Finesse and Enchantment
Alteration (one-shot instants), Codsworth (creature hosts, sorcery speed), Crown of the Ages,
Kitsune Mystic's flip side and Halvar (creatures only), and Simic Guildmage. **Only the Guildmage
moves an Aura that is attached to a non-creature permanent repeatedly.** The search is limited
by its wording.

## Rules consequences

### 1. Token-only target: what setup needs

Replicator targets "token you control". A target is checked when the ability is activated and
again on resolution (608.2b, quoted in L6). The physical label cards are not tokens, so
Replicator cannot copy them, and the simulator refuses to (demo in `output.txt`). After setup
every node is a token, since every node is a Replicator copy. **So a card→token step is needed
exactly once per label, never during the run.**

Candidates for that step (Oracle text verified here or in L6):
- **Lithoform Engine, {4},{T}: copy target permanent spell** (chosen). Cast the label card at
  sorcery speed (117.1a) targeting the Food token. Run mana loops above it (instant speed), then
  activate Lithoform targeting the Aura spell. The copy resolves first (ruling). It keeps the
  original's target, because new targets "can't be chosen" for a permanent spell (ruling;
  707.10 copies targets). As it resolves it "ceases being a copy of a spell and becomes a token
  permanent" (707.10f, quoted in L5), and by the ruling the permanent-spell rules apply to it.
  So it becomes an Aura token attached to the Food (608.3c, *number only, not quoted*). Then
  the card itself resolves onto the Food. Cost per label: the card's mana cost + {4}. One
  card, repeatable, untapped by Dramatic Reversal. **This is the single non-repeatable step
  per label. Everything after it is Replicator.**
- Flash Photography: two seeds per card (cast and flashback). Mythos of Illuna and Replication
  Technique: one each. With ≥3 labels these take ≥2 cards, so Lithoform is cheaper in cards.
  They are the fallback if the Lithoform reading fails (see Weakest point).

Is a seed a valid Replicator target, and what does a copy of it become? The seed is a token
(707.10f). Its characteristics come from copying the Aura spell (707.10: "copies … the
characteristics of the spell"), so on our reading it "is copying something else", the Aura card.
By Replicator ruling 1, "the new token enters as whatever that token copied", so a copy of the
Bound in Gold seed is a Bound in Gold Aura token. A copy of *that* copy is again Bound in Gold
(ruling 2; 707.2 and 111.3 as quoted in L6). One wrinkle: ruling 2 speaks of "the effect that
created it", and the Lithoform ruling says the seed is not "created". Ruling 1 covers this case,
on our reading. No judge has confirmed it.

**Take Possession cannot be seeded.** Split second (its reminder text, quoted above) forbids
activating Lithoform while it is on the stack. It was L6's fourth variable label, so L9 has 5
variable labels: Confiscate, Lay Claim, Volition Reins, Psychic Overload, Dream Leash. Dream
Leash needs a tapped target as it is cast. Replicator can copy the Food (a token P controls),
and the copy enters tapped, so it is a legal target (simulated).

### 2. "Create a tapped token"

- **Host.** Replicator's effect does not say what the Aura token enchants, so P chooses as it
  enters (303.4f, quoted in L6). This is exactly as with Flash Photography. The choice is not
  targeted (Mythos of Illuna ruling, same effect wording, quoted in L6). 303.4g never applies,
  because a legal host always exists.
- **Tapped status matters nowhere here.** Status is not copied (707.2; Replicator ruling 2), and
  nothing in the protocol reads it. A tapped Aura can be targeted by the Guildmage, sacrificed
  to Auratog (sacrifice is not a {T} cost, 701.21a) and enchanted. The texts that mention tapped
  status are Volition Reins and Psychic Overload, which read their *host's* status, and Dream
  Leash, which reads it only at casting. Each Dramatic Reversal untaps every token anyway ("all
  nonland permanents you control"), so the tapped mark cannot even carry data. In
  `output.txt` the most recent copy shows `(T)` and earlier ones are untapped.
- **Copy carries nothing.** As before, a copy brings no attachments, counters or status
  (ruling 2). "When enters" abilities do copy (ruling 3), so Faith's Fetters, Psychic Overload
  and Volition Reins ETBs fire as in L6.
- **Hexproof** (Curator's Ward on a node's host) stops only opponents (702.11b, in L6). P's
  Replicator can still target the node.

### 3. {T} in the cost: the untap/mana engine

Replicator must be untapped for each activation (602.2, *number only*). Dramatic Reversal
untaps "all nonland permanents you control", so every Scepter loop also untaps Replicator, and
Lithoform during setup. **No extra card is needed for the untap.** COPY costs {2} = 2 loops,
and those loops come before the activation, so Replicator is always untapped when it is paid
for. The one exception: if the pool already holds ≥2 mana (left over, or from Elemental
Resonance after a pause) while Replicator is still tapped, one extra loop is run to untap it.
The simulator counts these (`extra untap loops`; 0 in uninterrupted runs).

| primitive | L6 mana | L6 stack objects | L9 mana | L9 stack objects |
|---|---|---|---|---|
| COPY | 6 incl. {R}{R} (6 loops) | 12 + Reiterate + FP copy = **14** | {2} (2 loops) | 4 + Replicator ability = **5** |
| MOVE | {1}{U} (2 loops) | 5 | same | 5 |
| SAC | 0 | 1 | same | 1 |

Engine G mana is 2·(MOVEs + COPYs). L6's was 2·MOVEs + 6·COPYs.

**Something smaller than Scepter + Reversal + Lotus?** With no {R}{R}, the remaining colour
demand is the Guildmage's {U} (engine G only) and the label casts in setup (W, U, G). Dramatic
Reversal is cast free from the Scepter, so its {U} is never paid. Engine R needs no coloured
mana after setup: Replicator {2}, Scepter {2}, Auratog free. But every engine still needs three
things: unbounded mana, a repeated untap of Replicator, and (G only) blue. Scepter + Reversal +
Lotus gives all three in 3 cards. I found and verified no smaller set, and I did not search
for one beyond the Aura-mover search above. Gilded Lotus is kept in both engines because it
also pays the coloured label casts.

**Could MOVE be replaced?** Yes. Engine R drops the Guildmage. To rewrite the redex at P, it
builds the whole reduct (with any trailing arguments) on P, next to the old head, by
Replicator copies of the old nodes, top-down. Then it sacrifices the old head, and the SBA
cascade (704.5m under 704.3) removes the entire old subterm. The engine is COPY + SAC only, and
colourless during the run. The price is that every step copies the whole reduct at P instead
of only the duplicated argument. The per-rule tables in `output.txt` show this. For example,
B costs 5 copies (10 mana) against 3 moves (6 mana), and S with an n-atom z costs 4n+3 copies
against 4 moves plus 2n−1 copies.

### 4. No parked spell: pausing across steps and turns

Each primitive (loop, Guildmage, Replicator, Auratog) is put on the stack, resolves, and
leaves the stack as it was, which is empty between primitives. No step of the protocol needs
a spell to stay on the stack. So 500.2 ("A phase or step … ends when the stack is empty and all
players pass") no longer threatens the run. A pass with an empty stack just moves to the next
step. All primitives are activated abilities, usable whenever P has priority (117.1b), so the
run can continue in any step of either player's turn. Only the setup casts are sorcery-speed.

What a multi-turn run loses and keeps:
- **Mana** empties at each step and phase end (106.4). At most the leftover pool is lost
  (`mana lost at step ends` in `output.txt`), and loops make more.
- **Tapped permanents** stay tapped until the next Dramatic Reversal or P's untap step (502.3,
  *number only*). The loop leaves Lotus and Scepter untapped whenever the stack is empty. The
  one way to strand them is to decline the "you may" copy or cast of Dramatic Reversal. That
  stalls the engine until P's next untap step, which is recoverable. In L6 a stray pass
  allowed one restart (flashback) and then ended the copy engine.
- **No card in hand is needed** after setup (L6 needed Reiterate in hand). Cleanup discards are
  irrelevant.
- **Summoning sickness**: Guildmage and Auratog abilities have no {T}, and Replicator and
  Lithoform are not creatures (302.6, *number only*).

**Each label's printed text, re-read for multi-turn play** (hosts by the invariant: a leaf
enchants a cell or the anchor, a cell enchants a leaf or a cell; label cards and seeds sit on
the Food):
| label | text that could act outside one main phase | effect here |
|---|---|---|
| Indestructibility (cell) | static only | none |
| Bound in Gold (S), Intercessor's Arrest (K) | static: no activated non-mana abilities | on the anchor, this switches Lithoform off. So **all labels must be seeded before the term is built**, and no new variable can be added mid-run. On cells: nothing |
| Curator's Ward (I) | LTB trigger "if it was historic" | cells are not historic. **The anchor, Lithoform Engine, is historic (artifact and legendary).** The Food is an artifact. Both trigger only if they leave the battlefield, which the protocol never does |
| Essence Leak (B) | upkeep sacrifice, only if the host is red or green | hosts are white cells, the colourless Lithoform, or the colourless Food. Never applies; asserted after every primitive |
| Faith's Fetters (C) | ETB life gain | on each copy, as in L6 |
| Elemental Resonance (W) | **trigger at the beginning of P's first main phase**: add the host's mana cost | now relevant. One trigger per W token each turn: {3}{W} for a cell host, {4} for the Lithoform anchor, nothing for the Food. Mandatory, finite, uses the stack (ruling), and the mana is free. Simulated |
| Psychic Overload (var) | ETB tap host; host "doesn't untap during its controller's untap step" | the host is a cell (or the Food), whose status does not matter. Dramatic Reversal untaps it anyway. Simulated |
| Volition Reins (var) | ETB untap host | harmless |
| Confiscate, Lay Claim, Dream Leash (var) | control, static | idempotent under one controller (L6) |

Nothing else in the label texts triggers at upkeep, draw, untap or end step. The engine cards
have no triggers apart from Replicator's ETB (Food, once). **The computation can therefore be
paused and resumed across turns, on our reading.** The simulator does this between random
primitives, including mid-rewrite, and the lockstep still holds.

## Card lists

All cards below are paper and Legacy-legal per Scryfall (fetched 2026-11-21, here or in L6).

Engine G (11 for closed SKI with I; 14 for the mixed basis):
- Engine (7): **Replicator**, **Lithoform Engine** (seeding; the anchor afterwards), **Isochron
  Scepter**, **Dramatic Reversal** (imprinted), **Gilded Lotus**, **Simic Guildmage**,
  **Auratog**. No lands: the Food token from Replicator's ETB hosts the label cards and seeds.
- (a) closed SKI: + Indestructibility, Bound in Gold, Intercessor's Arrest, Curator's Ward =
  **11** (L6: 13). With I = S K K and no Curator's Ward, **10** (L6: 12).
- (b) mixed S K I B C W: + Essence Leak, Faith's Fetters, Elemental Resonance = **14** (L6: 16).
  BCKW alone (5 labels, as in L6): 12 (L6: 14).
- Variables: + up to 5 (L6: 6).

Engine R (no Guildmage): (a) **10** (9 without Curator's Ward); (b) **13**.

Where the saving comes from: Flash Photography + Reiterate (2) become Lithoform + Replicator
(2), so the copier swap itself saves nothing. Two Islands (anchor and template host) become 0,
since the Food and Lithoform take those roles. This part does not depend on Replicator's
copying, only on its Food, and L6 could have saved one Island by anchoring elsewhere. Engine
R drops the Guildmage. A conservative build that wants a land anchor (see Open questions) adds
one Island: 12 / 15.

## Simulator output (`lines/L9/output.txt`)

`l9sim.py` is L6's simulator with these changes. COPY is now Replicator: the target must be a
token, Replicator must be untapped and becomes tapped, {2} is paid by loops, the new token
enters tapped, and the host is chosen under 303.4f. Seeding is done by Lithoform on cast label
cards, with split second refused. The anchor is Lithoform Engine, and the Food hosts the
seeds. Engine R's rebuild rewrite is added, and so are optional pauses (step end, which empties
the pool; full turn, which adds untap step, upkeep check, draw and Elemental Resonance
triggers). **The leaf/cell invariant is now asserted, both halves, after every primitive**
(MOVE, COPY, SAC, after its SBA cascade, and after each pause): every term leaf enchants a cell
or the anchor, every term cell enchants a term leaf or cell, there is no cycle, and Essence Leak
never sits on a red or green permanent. Between steps, L6's encoding checks still run. The
reference reducer, rule sequences, tests and programs are L6's, unchanged. L6 is imported
read-only for the comparison columns.

Results (all OK, all in lockstep with the reference reducer on every step):
- 17 fixed terms (L6's list), in both engines. Engine G's move, copy and sacrifice counts are
  asserted equal to L6's on every term.
- 3 non-normalising terms (S I I (S I I), W W W, Y f) for 40 steps, in both engines.
- 15 program/basis runs, in both engines.
- **The same 500 random terms as L6** (same seed), in four runs: G, R, G with pauses, R with
  pauses (pause probability 0.15 after each primitive). Each run: 496 normal forms, 4 at the
  80-step bound, 0 failures. Local invariant checks per run: 14,703 (G), 76,290 (R), 16,519
  (G+pauses, with 1,816 pauses of which 898 passed a turn), and 87,393 (R+pauses, with 11,103
  pauses and 5,623 turns).
- Demonstrations: Replicator targeting a label *card* is refused; seeding Take Possession is
  refused (split second); a cycle-making MOVE passes the rules checks and is rejected only by
  the protocol; a MOVE of a leaf onto Auratog passes the rules checks and is caught by the
  per-move invariant; five variables get five distinct labels.

**Costs, same programs as L6** (mana = loops; moves/copies in brackets; from `output.txt`):

| program | basis | L6 | L9-G | L9-R |
|---|---|---|---|---|
| succ 2 p q | SKI | 112 (38/6) | 88 (38/6) | 342 (0/171) |
| succ 2 p q | BCKW | 84 (36/2) | 76 (36/2) | 272 (0/136) |
| succ 2 p q | SKIBC | 48 (18/2) | 40 (18/2) | 86 (0/43) |
| plus 2 2 p q | SKI | 434 (79/46) | 250 (79/46) | 1362 (0/681) |
| plus 2 2 p q | BCKW | 156 (69/3) | 144 (69/3) | 878 (0/439) |
| mult 2 2 p q | SKI | 514 (74/61) | 270 (74/61) | 1152 (0/576) |
| 2 2 p q | SKI | 634 (83/78) | 322 (83/78) | 1414 (0/707) |
| 2 2 p q | BCKW | 286 (71/24) | 190 (71/24) | 942 (0/471) |
| mult 3 2 p q | SKI | 986 (112/127) | 478 (112/127) | 2222 (0/1111) |
| mult 3 2 p q | SKIBC | 206 (52/17) | 138 (52/17) | 490 (0/245) |
| 500 random terms | mixed | 43,994 / 107,076 res | 21,222 / 55,339 res | 144,396 / 368,368 res |

Fixed terms (mana/stack resolutions): S K K x 16/42 (L6), 12/32 (G), 16/42 (R); S x y (K a b)
42/104, 22/58, 34/90; Church 2 f x 58/149, 46/121, 124/316. Setup for S K K x, which seeds 4
labels and builds 7 nodes: 46 loops and 112 resolutions (L6: 62 mana).

The saving in engine G grows with the share of copies. The SKI programs save 21–52% (634 → 322
for `2 2 p q`), and the move-heavy BCKW and SKIBC programs save 8–34%. Engine R costs 1.8–5.6
times L6's mana on these programs (1.0 on S K K x, 3.3 on the random terms). It is the minimal-card engine, not the efficient one.
Mana figures for the pause runs are not comparable: Elemental Resonance adds free mana at each
first main phase, and the leftover pool is lost at step ends (both totals printed).

## What changed versus L6

- COPY: Reiterate(buyback) on a parked Flash Photography is replaced by Replicator. The cost
  drops from 6 mana with {R}{R} and 14 stack objects to {2} generic and 5. Reiterate no longer
  has to be in hand.
- Session: there is no parked spell and no session. The run pauses and resumes freely, and
  only the library bounds the number of turns.
- Setup: template Auras plus 7 Flash Photography copies become seeding by Lithoform Engine
  (one Aura-spell copy per label) followed by Replicator copies.
- Board: no Islands. The anchor is Lithoform Engine, and the label cards and seeds sit on
  Replicator's Food token.
- Variables: 6 → 5 (Take Possession lost to split second).
- Elemental Resonance is no longer inert across turns. It yields free mana each turn, which is
  harmless.
- New optional engine R (COPY + SAC only, no Guildmage, colourless during the run): fewer
  cards, much more mana.
- Simulator: both halves of the leaf/cell invariant are asserted after every primitive (review
  gap closed). Pauses and turns are modelled. Rewrite sequences are unchanged and asserted
  equal in counts.

## Open questions

1. **Seeding by Lithoform.** Does a Replicator copy of a Lithoform-made Aura token become the
   label Aura? Ruling 1 versus "isn't said to have been created" is discussed above. A judge
   or Gatherer confirmation is wanted. The fallback is Flash Photography + Mythos of Illuna
   (or Replication Technique), at +1 card.
2. **Lithoform Engine as anchor.** Nothing in the quoted rules forbids it, but every head label
   then sits on an artifact that is legendary and historic (the Curator's Ward trigger, never
   fired). A land anchor costs one Island.
3. **Replicator is new** (released 2026-11-13; rulings dated 2026-10-07). More rulings may
   follow.
4. Still open from L6: attachment cycles (never created), the Guildmage same-controller clause
   (holds because P controls everything), and forcedness (L7).
5. Engine R's cost per step is the size of the reduct at the redex position, which is the
   whole term for head steps. A cheaper rebuild that keeps the trailing arguments in place
   would need a mover, which engine R does not have.

## What I did not verify

- Any judge or official source for the seeding chain (Lithoform on an Aura spell → token →
  Replicator copy). It rests on 707.10, 707.10f, the Lithoform rulings and Replicator rulings 1–2.
- Rules 608.3c, 602.2, 502.3 and 302.6 are cited by number only. I did not fetch their text, and
  per instructions I did not download the full CR. All other CR quotes are L5's and L6's, which
  I did not re-check against the source.
- Smaller untap/mana engines: none searched for beyond the Aura-mover search. No colourless
  Aura mover was found by that search (wording-limited).
- Opponent responses, combat, tournament shortcut rules, and how the engine reaches the
  battlefield (assumed, as in L6).
- The simulator's controller is trusted code. It shows that the protocol is right on the terms
  tested and that each primitive passes the rules checks I modelled. It does not show that
  those checks are all the relevant rules. The pause model is simplified: the opponent's turn
  does nothing, and only P's untap step, Essence Leak's upkeep condition, the draw and
  Elemental Resonance are modelled.
- No independent review (Wizard or Witchhunter) of this note or of `l9sim.py`.

## Status

- 2026-11-21: L9 note and simulator written. `python3 -I lines/L9/l9sim.py` exits 0 with `ALL
  OK`: 17 fixed terms and 3 divergent terms, in two engines; 15 program runs; 500 random terms ×
  4 runs (including pauses), all in lockstep; per-primitive invariant asserted. Verdict:
  Replicator gives a smaller (11/14 vs 13/16; engine R 10/13), cheaper (≈½ mana) and pausable
  engine, legal on our reading without judge confirmation. Not reviewed.
