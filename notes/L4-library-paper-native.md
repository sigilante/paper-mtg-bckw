# L4: the library as the term, audited; a bounded library/graveyard/exile machine

Line L4 of `PLAN.md`. Written 2026-11-21. Sources checked: the Comprehensive Rules dated
2026-11-06 (`MagicCompRules 20261106.txt` from magic.wizards.com/en/rules), and Scryfall's
single-card endpoint for each card quoted below. Executable check: `lines/L4/lgx_machine.py`
(stdlib Python 3.12); its full output is in `lines/L4/output.txt`.

## Summary

- **The seed sketch does not work as stated.** Six of its nine claims fail on the rules (hidden
  library, no tokens or copies of cards outside the battlefield and the stack, phasing only for
  permanents, no trigger that reads a pattern in the library, arguments that span many cards).
  The idea that survives is the representation: a term can be an ordered pile of real cards in
  prefix order, and mill, exile and "put on top of library" move its cards around.
- **What I built: the LGX machine.** The term sits in prefix (Polish) notation, one card per
  symbol, with an explicit application card `@`. The library L holds the unscanned suffix and
  the graveyard G holds the scanned prefix: L and G form a zipper over the term, and the run of `@`
  cards on top of G is the spine stack. A face-up exile pile X is the fuel reserve and the
  garbage heap. Only four card moves are used, and each one is the printed effect of a real card:
  MILL (L→G), RECLAIM (G→top of L), OOZE (G→X), PULL (X→G). Every BCKWSI rewrite is a fixed
  macro of these moves.
- **Correctness (tested, not proved).** The machine does leftmost-outermost (normal-order)
  reduction. On 14 hand-written terms and 2,987 random normalizing terms, it gives the same
  normal form *and the same sequence of contracted combinators* as a tree-based reference
  reducer.
- **Resources.** The cards are conserved: duplication (W, S) takes spare cards of the same name
  from the exile pool, and deletion (K, and the spent head and `@` cards) returns cards to it.
  The affine fragment (B, C, K, I) needs an empty pool. With N_c physical cards of each name c,
  the machine normalizes t exactly when normal-order reduction of t terminates and no term on the
  path uses more than N_c cards named c. This is argued below and tested on 1,499 random terms at
  the exact threshold. Any fixed deck is therefore a finite-state device and **not Turing complete**.
  The family of decks is universal only non-uniformly.
- **Model achieved: refereed, not forced and not even cooperative in the strong sense.** The data
  is native: the term itself lies on the table, and every move is a legal effect of a quoted card.
  The control is not native. A referee procedure decides which move comes next and counts brackets
  to find where a subterm ends. The cards *permit* the reduction moves; they also permit every
  other move. I also abstract the supply of moves: with one-shot spells and tap abilities, a real
  game affords only finitely many moves unless an untap or mana engine is added, and I have not
  built one.
- **The honest one-line verdict.** This is a two-stack machine whose tape alphabet *is* the term,
  driven by a human scheduler. It is a legible, rules-legal demonstration on the table, not a game
  that computes by itself. For forced reduction, see L2 and L3.

## Audit of the seed sketch

The sketch: "Library = the current term in linearized left-associative or reverse-Polish form,
combinators and parentheses as distinct cards, top few cards = current redex. Stack = evaluation
stack. Phasing suspends a subterm. K: mill/sacrifice y, optionally restore later with Noxious
Revival / Reclaim / Academy Ruins. W: make a token copy of x and put both original and copy on the
library. C: swap positions with Scroll Rack-style library reordering. B x y z: put y, z on the
stack as an application, phase x out, phase it in to consume the result. Loop: look at top of
library; if a redex is present a forced trigger performs the rewrite."

| # | Claim | Verdict | Rules / Oracle |
|---|---|---|---|
| 1 | Library = the term, linearized, cards as symbols | **Survives as a representation, but the term is hidden.** "Each library must be kept in a single face-down pile. Players can't look at or change the order of cards in a library." (401.2). A judge walking up to the table cannot see the term. Graveyard (404.2, "kept in a single face-up pile") and exile (406.3, "kept face up and may be examined by any player") are public. Library order is fixed (400.5). Prefix notation with an `@` card is better than parentheses: it needs no closing bracket, and the spine of a left-nested application is a run of `@` cards. | 401.2, 400.5, 404.2, 406.3 |
| 2 | Top few cards = current redex | **Refuted.** A redex `C a b c` has arguments that are whole subterms of unbounded length, so the redex is not a fixed window. Real static effects reveal only *one* card: Courser of Kruphix, Future Sight, Oracle of Mul Daya and Garruk's Horde say "Play with the top card of your library revealed"; Lantern of Insight says "Players play with the top card of their libraries revealed." Experimental Frenzy, Bolas's Citadel and Vizier of the Menagerie say only "You may look at the top card" (private to their controller). Index (5 cards), Sage Owl (4) and Ponder (3) are one-shot looks at a fixed window. Soothsaying's "{X}: Look at the top X cards" is variable but one-shot and private. If the top card changes mid-cast, the new top card is not revealed until the cast finishes (401.5). | 401.5; Oracle texts below |
| 3 | Stack = evaluation stack | **Refuted for library cards; the idea survives in another zone.** A card reaches the stack only by being cast (601.2a), which needs a permission (Future Sight etc.) and a cost. Land cards can't be cast. Stack objects can't be reordered (400.5), and whenever all players pass in succession the top object resolves (117.4), so the stack can't park arguments while other work proceeds. A resolved instant or sorcery goes to the graveyard (608.2n, 404.1). In the LGX machine the *graveyard* is the spine stack. | 601.2a, 400.5, 117.4, 608.2n |
| 4 | Phasing suspends a subterm | **Refuted.** "A permanent is a card or token on the battlefield." (110.1). Phasing is defined only for permanents (702.26a–b). Phasing in happens in the untap step (702.26a, 502.1) or when an effect's stated event occurs (610.4), not "on demand to consume a result". Library cards can't phase. (Phasing does carry attached Auras and Equipment along with it (702.26g), which may interest L3.) | 110.1, 702.26a,b,g, 502.1, 610.4 |
| 5 | K: mill/sacrifice y; restore with Noxious Revival / Reclaim / Academy Ruins | **Partly survives.** Deletion by moving cards out is sound: mill (701.17a) or exile. "Sacrifice" is impossible: you can only sacrifice a permanent you control (701.21a). y is a subterm, so deleting it needs its extent (a bracket count), not "the next card". Restoring is real but narrow: Reclaim and Noxious Revival return one card each; Academy Ruins returns only artifact cards and taps. K never needs restoring; in LGX, graveyard→library moves are used to *move* arguments. | 701.17a, 701.21a; Oracle below |
| 6 | W: token copy of x; put both on the library | **Refuted.** "A token that's in a zone other than the battlefield ceases to exist" (111.7, SBA 704.5d). "A token that has left the battlefield can't move to another zone" (111.8). "If a copy of a card is in any zone other than the stack or the battlefield, it ceases to exist" (707.10a, 704.5e). Token-copy cards copy permanents: Cackling Counterpart: "Create a token that's a copy of target creature you control." Paper Magic has no effect that creates a card (the CR has no "conjure"; that keyword is digital-only and absent from the CR). And x is a subterm, not one card. **Survives only fuel-bounded:** fetch a spare physical card of the same name from a reserve. The obvious same-name tutors are fatal here, because they all search the *library* and then shuffle it, destroying the term (701.24a): Squadron Hawk, Pack Hunt, Remembrance and Shared Summons all end "then shuffle". | 111.7, 111.8, 704.5d–e, 707.10a, 701.24a |
| 7 | C: Scroll Rack-style reordering | **Survives only as a permission, not a rewrite.** Scroll Rack moves cards through the hand: "Exile any number of cards from your hand face down. Put that many cards from the top of your library into your hand. Then look at the exiled cards and put them on top of your library in any order." It needs a hand as large as the window. Soothsaying's "{X}: Look at the top X cards of your library, then put them back in any order" is the best variable-width permuter I found: it *allows* C on arguments of total length ≤ X, but it allows any other permutation just as well. Nothing in the card makes the move C. | Oracle below |
| 8 | B: y, z on the stack, phase x out and in | **Refuted** (see 3 and 4). It is also unnecessary: in prefix form `B a b c → @ a @ b c` is a rearrangement plus one `@` card. | — |
| 9 | Loop: a forced trigger performs the rewrite when a redex is on top | **Refuted, as far as I can find.** Abilities of a card in the library don't function unless the ability says they do (113.6, 113.6b). A state trigger (603.8) needs a game-state condition, and no card I know conditions on a pattern of several library cards; only the top card is ever revealed (claim 2). The shuffling and random-bottom effects in the sketch's toolkit destroy the term: Mind's Desire begins "Shuffle your library"; cascade puts the cards it exiled "on the bottom of your library in a random order" (702.85a); Ponder says "You may shuffle"; Brainstorm draws three cards off the term first. "No such trigger exists" is a negative claim that I did not search exhaustively. | 113.6, 603.8, 702.85a |

**What survives:** (i) the term as an ordered pile of real cards in prefix order; (ii) deletion as
mill or exile; (iii) graveyard→library-top effects to move cards back; (iv) the library and the
graveyard as two stacks forming a zipper; (v) the graveyard, public and ordered, as the evaluation
stack in place of the play stack. Section B is built from exactly these.

## Representation

- **Cards.** Each symbol is a physical card with a fixed name: `@` (application), `S K I B C W`,
  and variables `x y z …`. Any real cards with distinct names will do; the name is the symbol.
  For a constructed-legal deck with unbounded fuel, use names that the deck rules allow in any
  quantity: basic lands (100.2a: "any number of basic land cards"), or cards that say so, such as
  Relentless Rats and Persistent Petitioners ("A deck can have any number of cards named …"). If
  RECLAIM is to come from Volrath's Stronghold (creature cards only), make every term card a
  creature.
- **Term.** Polish notation: `t u` ↦ `@ t u`. So `((K x) y)` is `@ @ K x y`. A left-nested
  application `h a1 … an` is `@^n h a1 … an`: the head comes right after its spine and the
  arguments follow in order.
- **Zones.** L = library, top card first; this is the unscanned part, and its top card is revealed
  (Courser of Kruphix or Lantern of Insight). G = graveyard, read bottom to top; this is the
  scanned prefix, and the maximal run of `@` cards on its top is the spine of the next head.
  X = exile, face up, unordered (400.5 lets owners arrange cards in other zones freely), holding
  the spare and spent cards. At every moment, G (bottom to top) followed by L (top to bottom),
  with any rewrite in progress completed, spells the current term.
- **Spine fact.** In prefix form, a card immediately preceded by `@` is that `@`'s function child.
  So the `@` cards directly before a head are exactly its spine, and m = (run of `@` on top of G)
  is the number of arguments available to the head on top of L. Earlier, non-`@` cards in G are
  finished context.
- **Subterm extent.** Start a count at 1, add 1 for each `@`, subtract 1 for each other card, and
  stop at 0. **This count is held by the referee, not by the game.** See "Where it breaks" for
  what native counters can and cannot do.

## Card list with quoted Oracle text

Card moves used by the machine (each moves one card):

| Move | Effect | Card(s), Oracle text (Scryfall, 2026-11-21) |
|---|---|---|
| MILL | L top → G top | **Codex Shredder** {1} Artifact: "{T}: Target player mills a card. (They put the top card of their library into their graveyard.)" **Persistent Petitioners** {1}{U}: "{1}, {T}: Target player mills a card. … A deck can have any number of cards named Persistent Petitioners." Rule 701.17a. |
| RECLAIM(d) | any G card (depth d) → L top | **Reclaim** {G} Instant: "Put target card from your graveyard on top of your library." **Noxious Revival** {G/P} Instant: "Put target card from a graveyard on top of its owner's library." Repeatable, creature cards only: **Volrath's Stronghold**: "{1}{B}, {T}: Put target creature card from your graveyard on top of your library." (**Academy Ruins**: "{1}{U}, {T}: Put target artifact card from your graveyard on top of your library.") Targeting gives random access into G, which C and S need. |
| OOZE(d) | any G card → X | **Scavenging Ooze** {1}{G}: "{G}: Exile target card from a graveyard. If it was a creature card, put a +1/+1 counter on this creature and you gain 1 life." (no tap: repeatable for {G} each). Alternative: **Relic of Progenitus**: "{T}: Target player exiles a card from their graveyard." |
| PULL(name) | an X card → G top | **Pull from Eternity** {W} Instant: "Put target face-up exiled card into its owner's graveyard." Cards exiled by Ooze are face up (406.3). |
| reveal | L top public | **Courser of Kruphix**: "Play with the top card of your library revealed." **Lantern of Insight**: "Players play with the top card of their libraries revealed." |
| (optional) | pins graveyard order | **Volrath's Shapeshifter**: "As long as the top card of your graveyard is a creature card, this creature has the full text of that card…". A card in play that cares about graveyard order. See "open rules questions". |

Cards examined for the audit (quoted where they decide a claim): Future Sight ("Play with the top
card of your library revealed. You may play lands and cast spells from the top of your library."),
Experimental Frenzy ("You may look at the top card of your library any time. You may play lands and
cast spells from the top of your library. You can't play lands or cast spells from your hand."),
Bolas's Citadel ("You may look at the top card of your library any time. You may play lands and
cast spells from the top of your library. If you cast a spell this way, pay life equal to its mana
value rather than pay its mana cost."), Vizier of the Menagerie ("You may look at the top card of
your library any time. You may cast creature spells from the top of your library."), Oracle of Mul
Daya ("Play with the top card of your library revealed. You may play lands from the top of your
library."), Garruk's Horde ("Play with the top card of your library revealed. You may cast creature
spells from the top of your library."), Mind's Desire ("Shuffle your library. Then exile the top
card of your library. …"), Ponder ("Look at the top three cards of your library, then put them back
in any order. You may shuffle. Draw a card."), Index ("Look at the top five cards of your library,
then put them back in any order."), Sage Owl ("When this creature enters, look at the top four cards
of your library, then put them back in any order."), Thought Scour ("Target player mills two cards.
Draw a card."), Scroll Rack (quoted in the audit), Soothsaying ("{3}{U}{U}: Shuffle your library.
{X}: Look at the top X cards of your library, then put them back in any order."), Brainstorm ("Draw
three cards, then put two cards from your hand on top of your library in any order."), Squadron
Hawk ("…search your library for up to three cards named Squadron Hawk, reveal them, put them into
your hand, then shuffle."), Pack Hunt ("Search your library for up to three cards with the same name
as target creature, … then shuffle."), Remembrance ("…search your library for a card with the same
name as that creature, … then shuffle."), Shared Summons ("Search your library for up to two
creature cards with different names, … then shuffle."), Mastermind's Acquisition ("• Put a card you
own from outside the game into your hand."; a sideboard reserve reaches only the hand, and the
hand→library-top effects found (Brainstorm, Scroll Rack) draw from the term first), Cackling
Counterpart (quoted in the audit), Teferi's Protection ("All permanents you control phase out."),
Sands of Delirium ("{X}, {T}: Target player mills X cards."), Reito Lantern ("{3}: Put target card
from a graveyard on the bottom of its owner's library."), Sidisi, Brood Tyrant ("Whenever one or
more creature cards are put into your graveyard from your library, create a 2/2 black Zombie
creature token."), Bloodbraid Elf (cascade reminder text: "…Put the exiled cards on the bottom in
a random order.").

## Reduction rules

Arity and right-hand side in prefix form over arguments 1..k:

| h | k | RHS (prefix) | spine `@` kept | body built on L |
|---|---|---|---|---|
| I | 1 | `1` | 0 | `1` |
| K | 2 | `1` | 0 | `1` (arg 2 → X) |
| B | 3 | `@ 1 @ 2 3` | 1 | `1 @ 2 3` |
| C | 3 | `@ @ 1 3 2` | 2 | `1 3 2` |
| W | 2 | `@ @ 1 2 2` | 2 | `1 2 2` |
| S | 3 | `@ @ 1 3 @ 2 3` | 2 | `1 3 @ 2 3` |

Scan loop (referee): look at the revealed top card t of L.
- If t is `@`, or t is a variable, or t is a combinator with arity k > m (the run of `@` on top of
  G): **MILL**. The card joins the finished context or the spine.
- If t is a combinator with k ≤ m, **rewrite**:
  1. MILL t, OOZE t (the head goes to X). OOZE the top (k − kept) spine `@` cards.
  2. For i = 1..k, mill argument i whole into G, using the bracket count; note its length ℓ_i.
  3. OOZE every card of each argument that the body does not use (K's second argument). This is
     garbage collection, and it refuels X.
  4. Build the body on top of L, last item first:
     `@` → PULL `@`, RECLAIM it.
     A *non-leftmost* occurrence of argument i → copy: for each card of segment i, from its last
     card to its first, PULL a card of that name from X and RECLAIM it.
     The *leftmost* occurrence of argument i → RECLAIM the original segment's cards, top first,
     by targeting.
  5. Resume the scan. The kept spine `@` cards are still on top of G, so a redex created at the
     head (as in `C K x y → K y x`) is seen at once.
- When L is empty, G read bottom to top is the normal form.

Every exile (steps 1, 3) happens before any PULL (step 4). If a PULL finds no card of the needed
name in X, the machine stops **OUT OF FUEL**.

**Why this is normal order (argument; the simulator tests it).** In preorder, a redex that contains
another starts before it, and of two disjoint redexes the left one starts first. So the
leftmost-outermost redex is the first redex in prefix order. The scan mills a card only when no
redex starts at the spine ending at that card, and a rewrite changes nothing to the left of its
spine. After a rewrite the only new redex that can start to the left is one whose spine runs into
the contractum's head, and step 5 checks that spine.

**Fuel (argued; tested at the exact threshold).** The cards are conserved (the simulator asserts
L+G+X is constant). During a rewrite, all exiles precede all PULLs, so for each name the cards in
play never exceed max(count in the redex-term, count in the contractum-term). Hence, with N_c
cards named c in the whole deck, the run reaches the normal form **iff** normal-order reduction of
t terminates **and** every term on the path has ≤ N_c cards named c (`@` included). For B, C, K and
I every step removes at least 2 cards (`I`: −2; `K`: −2−|b|; `B`, `C`: the head and one `@`), so
the affine fragment needs an empty pool and takes at most |t|/2 steps. That fragment is easy:
BCK(I) terms are strongly normalizing in linearly many steps. It is faithful but computationally
weak.

**Computational class.** A fixed deck has finitely many configurations (orders of L and G, and the
contents of X), and the referee procedure is deterministic. "Does this run reach a normal form?" is
therefore decidable for a fixed deck, and in PSPACE when the deck size is part of the input. The
family over all deck sizes is universal only *non-uniformly*: every terminating normal-order
computation fits some finite deck, but the deck you need is the largest term on the path, which is
not computable from t in general. So no single game is Turing complete. Whether the bounded
problem is PSPACE-hard is a **guess** (plausible via linear-space simulations), not checked.

## Worked trace

Real output of `python3 lgx_machine.py --trace --moves`. Brackets show L (top first), G (bottom
first) and X. Card used at each move: MILL = Codex Shredder (or Persistent Petitioners);
OOZE = Scavenging Ooze; RECLAIM = Reclaim / Noxious Revival (or Volrath's Stronghold for creature
cards); PULL = Pull from Eternity; the top card of L is visible through Courser of Kruphix.

**C K x y → K y x → y** (affine; empty pool):

```
TRACE C K x y   prefix: @ @ @ C K x y   initial pool: {}
  start                              L=[@ @ @ C K x y]  G=[]  X={}
    MILL @                           L=[@ @ C K x y]  G=[@]  X={}
    MILL @                           L=[@ C K x y]  G=[@ @]  X={}
    MILL @                           L=[C K x y]  G=[@ @ @]  X={}
    MILL C                           L=[K x y]  G=[@ @ @ C]  X={}        # C on top, m=3 >= 3: redex
    OOZE C (depth 0)                 L=[K x y]  G=[@ @ @]  X={Cx1}       # head out
    OOZE @ (depth 0)                 L=[K x y]  G=[@ @]  X={@x1 Cx1}     # 3 spine @ -> keep 2
  C: head + 1 spine @ exiled         L=[K x y]  G=[@ @]  X={@x1 Cx1}
    MILL K                           L=[x y]  G=[@ @ K]  X={@x1 Cx1}     # arg 1 (count 1->0)
    MILL x                           L=[y]  G=[@ @ K x]  X={@x1 Cx1}     # arg 2
    MILL y                           L=[]  G=[@ @ K x y]  X={@x1 Cx1}    # arg 3
  C: args milled, lens=[1, 1, 1]     L=[]  G=[@ @ K x y]  X={@x1 Cx1}
    RECLAIM x (depth 1)              L=[x]  G=[@ @ K y]  X={@x1 Cx1}     # body "1 3 2": place 2 first
    RECLAIM y (depth 0)              L=[y x]  G=[@ @ K]  X={@x1 Cx1}     # then 3
    RECLAIM K (depth 0)              L=[K y x]  G=[@ @]  X={@x1 Cx1}     # then 1
  C: contractum on top of L          L=[K y x]  G=[@ @]  X={@x1 Cx1}     # term = @ @ K y x
    MILL K                           L=[y x]  G=[@ @ K]  X={@x1 Cx1}     # K, m=2 >= 2: redex
    OOZE K (depth 0)                 L=[y x]  G=[@ @]  X={@x1 Cx1 Kx1}
    OOZE @ (depth 0)                 L=[y x]  G=[@]  X={@x2 Cx1 Kx1}
    OOZE @ (depth 0)                 L=[y x]  G=[]  X={@x3 Cx1 Kx1}
  K: head + 2 spine @ exiled         L=[y x]  G=[]  X={@x3 Cx1 Kx1}
    MILL y                           L=[x]  G=[y]  X={@x3 Cx1 Kx1}
    MILL x                           L=[]  G=[y x]  X={@x3 Cx1 Kx1}
  K: args milled, lens=[1, 1]        L=[]  G=[y x]  X={@x3 Cx1 Kx1}
    OOZE x (depth 0)                 L=[]  G=[y]  X={@x3 Cx1 Kx1 xx1}   # K drops arg 2
    RECLAIM y (depth 0)              L=[y]  G=[]  X={@x3 Cx1 Kx1 xx1}
  K: contractum on top of L          L=[y]  G=[]  X={@x3 Cx1 Kx1 xx1}
    MILL y                           L=[]  G=[y]  X={@x3 Cx1 Kx1 xx1}
  halt (G bottom-to-top = normal form) L=[]  G=[y]  X={@x3 Cx1 Kx1 xx1}
  result: PASS y   rewrites=CK ref=CK  moves={'MILL': 11, 'OOZE': 6, 'RECLAIM': 4}
```
(`#` comments added by hand; everything else is program output.)

**S K K x → K x (K x) → x** (one duplication; the pool holds one spare `x`):

```
TRACE S K K x   prefix: @ @ @ S K K x   initial pool: {'x': 1}
  start                              L=[@ @ @ S K K x]  G=[]  X={xx1}
    MILL @                           L=[@ @ S K K x]  G=[@]  X={xx1}
    MILL @                           L=[@ S K K x]  G=[@ @]  X={xx1}
    MILL @                           L=[S K K x]  G=[@ @ @]  X={xx1}
    MILL S                           L=[K K x]  G=[@ @ @ S]  X={xx1}
    OOZE S (depth 0)                 L=[K K x]  G=[@ @ @]  X={Sx1 xx1}
    OOZE @ (depth 0)                 L=[K K x]  G=[@ @]  X={@x1 Sx1 xx1}
  S: head + 1 spine @ exiled         L=[K K x]  G=[@ @]  X={@x1 Sx1 xx1}
    MILL K                           L=[K x]  G=[@ @ K]  X={@x1 Sx1 xx1}
    MILL K                           L=[x]  G=[@ @ K K]  X={@x1 Sx1 xx1}
    MILL x                           L=[]  G=[@ @ K K x]  X={@x1 Sx1 xx1}
  S: args milled, lens=[1, 1, 1]     L=[]  G=[@ @ K K x]  X={@x1 Sx1 xx1}
    PULL x                           L=[]  G=[@ @ K K x x]  X={@x1 Sx1}    # copy of arg 3 (fuel)
    RECLAIM x (depth 0)              L=[x]  G=[@ @ K K x]  X={@x1 Sx1}
    RECLAIM K (depth 1)              L=[K x]  G=[@ @ K x]  X={@x1 Sx1}     # arg 2
    PULL @                           L=[K x]  G=[@ @ K x @]  X={Sx1}
    RECLAIM @ (depth 0)              L=[@ K x]  G=[@ @ K x]  X={Sx1}
    RECLAIM x (depth 0)              L=[x @ K x]  G=[@ @ K]  X={Sx1}       # original arg 3
    RECLAIM K (depth 0)              L=[K x @ K x]  G=[@ @]  X={Sx1}       # arg 1
  S: contractum on top of L          L=[K x @ K x]  G=[@ @]  X={Sx1}       # @ @ K x (@ K x)
    MILL K                           L=[x @ K x]  G=[@ @ K]  X={Sx1}
    OOZE K (depth 0)                 L=[x @ K x]  G=[@ @]  X={Kx1 Sx1}
    OOZE @ (depth 0)                 L=[x @ K x]  G=[@]  X={@x1 Kx1 Sx1}
    OOZE @ (depth 0)                 L=[x @ K x]  G=[]  X={@x2 Kx1 Sx1}
  K: head + 2 spine @ exiled         L=[x @ K x]  G=[]  X={@x2 Kx1 Sx1}
    MILL x                           L=[@ K x]  G=[x]  X={@x2 Kx1 Sx1}
    MILL @                           L=[K x]  G=[x @]  X={@x2 Kx1 Sx1}     # arg 2: count 1,2,1,0
    MILL K                           L=[x]  G=[x @ K]  X={@x2 Kx1 Sx1}
    MILL x                           L=[]  G=[x @ K x]  X={@x2 Kx1 Sx1}
  K: args milled, lens=[1, 3]        L=[]  G=[x @ K x]  X={@x2 Kx1 Sx1}
    OOZE x (depth 0)                 L=[]  G=[x @ K]  X={@x2 Kx1 Sx1 xx1}  # garbage arg (3 cards)
    OOZE K (depth 0)                 L=[]  G=[x @]  X={@x2 Kx2 Sx1 xx1}
    OOZE @ (depth 0)                 L=[]  G=[x]  X={@x3 Kx2 Sx1 xx1}
    RECLAIM x (depth 0)              L=[x]  G=[]  X={@x3 Kx2 Sx1 xx1}
  K: contractum on top of L          L=[x]  G=[]  X={@x3 Kx2 Sx1 xx1}
    MILL x                           L=[]  G=[x]  X={@x3 Kx2 Sx1 xx1}
  halt (G bottom-to-top = normal form) L=[]  G=[x]  X={@x3 Kx2 Sx1 xx1}
  result: PASS x   rewrites=SK ref=SK  moves={'MILL': 13, 'OOZE': 8, 'PULL': 2, 'RECLAIM': 6}
```

With an empty pool the same term stops `OUT OF FUEL (x)` at the first PULL (tested below). The
garbage from the K step returns the spare `x` to X, so fuel can be recycled.

## Simulator and its output

`lines/L4/lgx_machine.py`: zones as Python lists, a `Counter` for exile, the four moves as the only
operations on cards, and the referee procedure as `Machine.run`. The reference is a tree-based
leftmost-outermost reducer (`step`/`normalize`). A test passes when the normal form *and* the
sequence of contracted combinators agree. Run with Python 3.12.7; all output is in
`lines/L4/output.txt`:

```
$ python3 lgx_machine.py
PASS  C K x y                      -> y   rewrites=CK ref=CK  moves={'MILL': 11, 'OOZE': 6, 'RECLAIM': 4}
PASS  B K I x y                    -> x   rewrites=BKI ref=BKI  moves={'MILL': 17, 'OOZE': 9, 'RECLAIM': 8, 'PULL': 1}
PASS  B (C K) I x y                -> y   rewrites=BCK ref=BCK  moves={'MILL': 23, 'OOZE': 11, 'RECLAIM': 12, 'PULL': 1}
PASS  C (B K I) x y z              -> y z   rewrites=CBKI ref=CBKI  moves={'MILL': 28, 'OOZE': 11, 'RECLAIM': 15, 'PULL': 1}
PASS  x (I K) (K y z) (C I w f)    -> x K y (f w)   rewrites=IKCI ref=IKCI  moves={'MILL': 25, 'OOZE': 10, 'RECLAIM': 6}
PASS  K (I x) (B y z w)            -> x   rewrites=KI ref=KI  moves={'MILL': 17, 'OOZE': 12, 'RECLAIM': 4}
PASS  B B C f g x y                -> f y (g x)   rewrites=BBC ref=BBC  moves={'MILL': 28, 'OOZE': 8, 'RECLAIM': 15, 'PULL': 2}
PASS  W K x                        -> x   rewrites=WK ref=WK  moves={'MILL': 9, 'OOZE': 5, 'PULL': 1, 'RECLAIM': 4}
PASS  S K K x                      -> x   rewrites=SK ref=SK  moves={'MILL': 13, 'OOZE': 8, 'PULL': 2, 'RECLAIM': 6}
PASS  S (K x) I y                  -> x y   rewrites=SKI ref=SKI  moves={'MILL': 18, 'OOZE': 8, 'PULL': 2, 'RECLAIM': 9}
PASS  W (B K I) (x y)              -> x y   rewrites=WBKI ref=WBKI  moves={'MILL': 36, 'OOZE': 12, 'PULL': 4, 'RECLAIM': 25}
PASS  S I I (K z)                  -> z   rewrites=SIK ref=SIK  moves={'MILL': 22, 'OOZE': 12, 'PULL': 4, 'RECLAIM': 13}
PASS  S (S K K) (S K K) (K q)      -> q   rewrites=SSKK ref=SSKK  moves={'MILL': 47, 'OOZE': 24, 'PULL': 8, 'RECLAIM': 30}
PASS  C (W (C K)) (S I x) y        -> y (S I x)   rewrites=CWCK ref=CWCK  moves={'MILL': 35, 'OOZE': 9, 'RECLAIM': 20, 'PULL': 1}
PASS  zero-pool S K K x       -> OUT OF FUEL (x)
PASS  zero-pool C K x y            -> y   rewrites=CK ref=CK
PASS  zero-pool B K I x y          -> x   rewrites=BKI ref=BKI
PASS  zero-pool C (B K I) x y z    -> y z   rewrites=CBKI ref=CBKI
PASS  zero-pool B B C f g x y      -> f y (g x)   rewrites=BBC ref=BBC
PASS  W W W (diverges)            -> step-bound after 50 rewrites; cards in play constant = 5
ALL PASS

$ python3 lgx_machine.py --random 3000
random: 2987/2987 normalizing terms agree (term + rewrite sequence); 13 skipped as non-normalizing within 300 steps

$ python3 lgx_machine.py --budget 1500
budget: 1499/1499 terms normalize with exactly the per-name budget and fail with one card less
```

Scope of the tests. The random terms are uniform-ish binary trees of 1–12 leaves over
{S,K,I,B,C,W,x,y,z}, from a fixed seed. The machine's pool there is 400 per name, and terms whose
reference reduction exceeds 300 steps are skipped. The budget check computes, for each name, the
largest count on the normal-order path, gives the machine exactly that (minus the initial term),
and checks that it succeeds, and that it fails for every name when given one card less. These are
tests of the *abstract* machine against the *abstract* reducer. They say nothing about the Magic
rules, which rest on the citations above.

## Where it breaks / open rules questions

1. **Control is external (the main weakness).** Nothing in the game makes the next move. MILL,
   RECLAIM, OOZE and PULL can be applied to any card at any time the costs allow; the referee
   chooses. This is the "referee procedure with real cards as props" model. It is stronger than
   props only in that every move is a legal effect and the data is the literal term.
2. **The bracket count is not a game object.** Native counters exist that track *one-sided*
   counts during milling. Sidisi creates a token each time "one or more creature cards are put
   into your graveyard from your library" (so making `@` a creature and leaves non-creatures counts
   `@` cards milled one at a time), and Scavenging Ooze gains a +1/+1 counter per creature card it
   exiles. The stopping test needs a comparison: #leaves = #`@` + 1. I found no card that compares
   two counts or triggers on reaching a difference. Mana cannot hold the count across steps
   because "each player's mana pool empties at the end of each step and phase" (106.4). Open.
3. **Supply of moves.** Reclaim, Noxious Revival and Pull from Eternity are one-shot; Codex
   Shredder, Persistent Petitioners, Volrath's Stronghold and Relic tap; only Scavenging Ooze
   repeats for mana alone. Unbounded play needs an untap engine, recursion of the one-shot spells,
   and infinite mana. I did not build or verify one, and each extra engine card adds rules risk.
   Without it, a real game affords a bounded number of moves, which is a second bound on top of the
   card bound.
4. **Is a milled card "on top" of the graveyard?** 404.1 puts countered, discarded, destroyed and
   sacrificed objects and resolved instants and sorceries "on top of its owner's graveyard". It
   does not list milling or Pull from Eternity explicitly. 404.2 says order normally can't change;
   404.3 lets the owner order simultaneous arrivals (moot here: every move is one card). I read
   "on top" as the general convention, but that is an interpretation.
5. **Tournament graveyard reordering.** 404.2: "Additional rules applying to sanctioned
   tournaments may allow a player to change the order of cards in their graveyard." I did not read
   the Magic Tournament Rules. My unverified recollection is that order is protected when a card in
   play cares about it, which is why Volrath's Shapeshifter is listed as an optional pin. Outside a
   sanctioned event, 404.2 suffices.
6. **The library part is hidden.** Only the top card of L is public (Courser or Lantern). The rest
   of L is known to anyone who watched the moves, since cards come back face up from a public
   graveyard via RECLAIM, but a late observer cannot verify it without a reveal. 603.10a's
   "object that all players can see is put into … library" covers triggers only, not the
   visibility of order.
7. **Targeting by position.** RECLAIM(d) and OOZE(d) target "a card" in a graveyard. Identical
   names (several `@` cards) make "which `@`" a matter of position the players must agree on. The
   rules identify objects, not positions; for identical cards the outcome is the same up to card
   identity. Harmless, but unstated.
8. **Deck construction.** 100.2a caps non-basic names at four copies. Unbounded fuel, legally,
   needs basic lands or "any number" cards as term cards. Basic lands can't be RECLAIMed by
   Volrath's Stronghold (creature-only) and can be played from the top of the library under
   Courser, a harmless extra option. In a casual or generalized game this point is moot.

## What I did not verify

- No exhaustive search for a card that reads a multi-card pattern in a library, or for a
  two-sided counter comparison. Both negative claims rest on the cards I know.
- No infinite-mana or untap engine (point 3); no check of the Tournament Rules (point 5).
- The normal-order argument and the fuel iff are short informal arguments plus tests, not proofs.
  No Lean. PSPACE membership is stated by the finite-configuration argument; PSPACE-hardness is a
  guess.
- Oracle texts were read from Scryfall on 2026-11-21. Persistent Petitioners and Relentless Rats
  are the only "any number" cards I verified; other such cards (Rat Colony, Shadowborn Apostle,
  etc.) I did not check.
- I did not model priority, timing (sorcery-speed restrictions do not apply: every move above is
  an instant or an activated ability without timing restriction, except that Volrath's
  Stronghold and the Shredder tap), costs, or the opponent's possible interference. The opponent is
  assumed passive.
