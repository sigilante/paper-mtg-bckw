# L2: the stack is the term

Line L2 of `PLAN.md`. Author: L2 subagent, 2026-11-21. Executable check:
`lines/L2/stack_machine.py` (stdlib Python; run `python3 -I stack_machine.py`).

## Summary

**What is achieved.** Full normal-order reduction for SKI and BCKW (any mix of
S K I B C W) is carried out on the Magic stack. The term is a sequence of stack
objects in prefix code. The reduction uses three operations, and real cards supply
each one an unbounded number of times:

| abstract op | real-card implementation |
|---|---|
| `copy(o)`: push a copy of any stack object `o` onto the top | cast **Reiterate** (buyback) targeting `o` |
| `counter(o)`: remove any stack object `o` | cast **Reiterate** targeting a parked **Counterspell**, give the copy the new target `o` (CR 707.10c), let the copy resolve |
| `resolve_top()`: the top object resolves | all players pass (CR 117.4, 405.5). Used only for the no-op objects `@` and `I` |

The unbounded mana for Reiterate comes from Isochron Scepter (imprinting Dramatic
Reversal) and Gilded Lotus. Checked against a reference normal-order reducer on 10
fixed terms (including two that duplicate a compound argument and one that drops a
divergent argument) and on 2986 random terms: all agree.

**Model: cooperative, and unrestricted.** The cards make every reduction step legal.
They do **not** make non-reduction steps illegal: the player can copy or counter any
object at any time. Only two kinds of step happen through ordinary resolution and
need no choice beyond passing priority: unwinding an application marker `@`, and an
`I` step. Every other step needs a player's choices. The player parses argument
blocks from the public stack (CR 400.2), picks Reiterate's target, and picks the new
target for each Counterspell copy. The computation is unbounded, given the mana
engine. It is not forced, and I show below why pure stack-as-term cannot be forced
with existing cards.

**Verdict on the line.** Pure stack-as-term works only as a *store with copy and
delete*. The stack is an unbounded, ordered, public tape whose objects can be copied
to the top or deleted anywhere. The combinator semantics lives in the protocol the
player follows, not in the cards. The two native features the question hoped for do
not work out:

- *A spine stack that resolves top-first*: resolving does no work except for no-ops.
- *Sharing through targets*: this fails structurally (see Design B), because the
  stack cannot keep a heap underneath a live spine.

## Representation

**Design A (chosen and simulated): the frame is a list of prefix blocks.**

- Every term object is a *targetless, inert instant spell*. Its card name is its label.
  - The labels are the combinators S K I (or B C K W), the application marker `@`,
    any free variables, and a frame marker `|` (used only when normalizing under
    arguments).
  - Each label is a distinct card from the Fog family. All of them read "Prevent all
    combat damage that would be dealt this turn", so resolving one has no effect on
    the stack.
- A **block** is either an atom, or `@` followed by two blocks. A block is the prefix
  (Polish) code of a subterm.
- A **frame** is the segment of the stack above a `|`, read top-first. It is a
  concatenation of blocks `b0 b1 … bn` and denotes `b0 b1 … bn`, with application
  associating to the left.
  - The prefix code of `((h a1) a2)` is `@ @ h a1 a2`. Stripping the leading `@`s gives
    the spine form `h a1 a2`, and both denote the same term. So **unwinding is just
    letting the top `@` resolve as a no-op**, and the stack then *is* the head-reduction
    spine: head on top, then the arguments as blocks, in order.
- **Templates.** The bottom of the stack holds one original card per label, plus a
  Counterspell that targets one of them. These are the only physical cards. Every
  object in the term is a copy. Templates are never countered or moved.
- **What persists (the engine) versus the term.** The engine is:
  - on the battlefield: Isochron Scepter imprinted with Dramatic Reversal, and Gilded
    Lotus;
  - in hand: Reiterate, which returns to hand through buyback;
  - at the bottom of the stack: the templates.

  The term is everything above the base `|` marker. No triggered abilities are
  involved. Nothing on the battlefield reacts to the term.

**Design B (weighed and rejected; not simulated): application nodes as target
pointers.**

- An application node `App(f,a)` would be a spell with two spell targets, for example
  a Mindbreak Trap copy cast with exactly two targets.
- Copying it keeps its targets (CR 707.10: a copy "copies … all decisions made for
  it, including … targets"). This gives O(1) sharing of a subterm, i.e. graph
  reduction.
- It fails on the stack for three reasons:
  1. **A new node can only go on top** (CR 405.2), above the live spine. To keep the
     spine contiguous under the head, every step has to re-copy the *whole* spine
     above the new node. That costs O(spine length) per step, which is unbounded.
  2. **A referenced object can never be removed.** If a target leaves the stack, the
     pointer dies (CR 608.2b: "A target that's no longer in the zone it was in when it
     was targeted is illegal"). So nothing is ever reclaimed, and K only works by
     "not re-copying".
  3. **Mindbreak Trap has a single "target" word**, and "the same target can't be
     chosen multiple times for any one instance of the word 'target'" (CR 601.2c). So
     `App(y,y)` cannot point twice at one shared object, which is exactly the shape
     that sharing produces.

  Design B is therefore "graph reduction for free" only for the copy step. The heap
  has to live elsewhere: on the battlefield, which is line L3. A hybrid built from the
  Design B pointer idea (spine on the stack, heap of tokens) is the nearest thing that
  could beat Design A on cost. That hybrid belongs to L3/P1, not to this line.

## Card list (Oracle text quoted from Scryfall, fetched 2026-11-21)

Load-bearing cards:

- **Reiterate** {1}{R}{R}, Instant: "Buyback {3} (You may pay an additional {3} as you
  cast this spell. If you do, put this card into your hand as it resolves.) Copy
  target instant or sorcery spell. You may choose new targets for the copy."
- **Counterspell** {U}{U}, Instant: "Counter target spell."
- **Isochron Scepter** {2}, Artifact: "Imprint — When this artifact enters, you may
  exile an instant card with mana value 2 or less from your hand. {2}, {T}: You may
  copy the exiled card. If you do, you may cast the copy without paying its mana
  cost."
- **Dramatic Reversal** {1}{U}, Instant: "Untap all nonland permanents you control."
- **Gilded Lotus** {5}, Artifact: "{T}: Add three mana of any one color."
- The label cards (inert instants):
  - **Fog** {G}: "Prevent all combat damage that would be dealt this turn."
  - **Holy Day** {W}: same text.
  - **Darkness** {B}: same text.
  - **Lull** {1}{G}: same text, plus "Cycling {2}".
  - **Moment's Peace** {1}{G}: same text, plus "Flashback {2}{G}".
  - **Respite** {1}{G}: same text, plus "You gain 1 life for each attacking
    creature."

  That is six distinct labels, enough for `S K I @ |` plus one variable, or for
  `B C K W @ |`. More variables need more targetless inert instants (any card works if
  its resolution does not touch the stack). I have not listed more.

Considered, verified, and not needed (or useful only as variants):

- **Twincast** {U}{U}: "Copy target instant or sorcery spell. You may choose new
  targets for the copy." This is Reiterate without buyback, so it is one-shot.
- **Fork** {R}{R}: "Copy target instant or sorcery spell, except that the copy is red.
  You may choose new targets for the copy." Also one-shot. Its recolouring could serve
  as an extra label bit.
- **Narset's Reversal** {U}{U}: "Copy target instant or sorcery spell, then return it
  to its owner's hand. You may choose new targets for the copy." This is *move-to-top*
  in one effect: a copy returned to hand ceases to exist (CR 704.5e). Copied through
  Reiterate, it would merge a `copy` and a `counter` into one action. That saves
  actions but changes nothing structural.
- **Increasing Vengeance** {R}{R}: "Copy target instant or sorcery spell you control.
  If this spell was cast from a graveyard, copy that spell twice instead. You may
  choose new targets for the copies." Flashback {3}{R}{R}. It doubles one *object*,
  not a block.
- **Lithoform Engine** {4}, Legendary Artifact: "… {3}, {T}: Copy target instant or
  sorcery spell you control. You may choose new targets for the copy. …" It taps, so
  it needs an untapper to repeat.
- **Thousand-Year Storm**: "Whenever you cast an instant or sorcery spell, copy it for
  each other instant and sorcery spell you've cast before it this turn. You may choose
  new targets for the copies." It triggers on *cast*, and copies are not cast
  (CR 707.10), so it cannot chain on the term.
- **Deflecting Swat** {2}{R}: "You may choose new targets for target spell or
  ability." **Misdirection**: "Change the target of target spell with a single
  target." Both rewire pointers, which matters only in Design B.
- **Remand**: "Counter target spell. If that spell is countered this way, put it into
  its owner's hand instead of into that player's graveyard. Draw a card."
- **Mindbreak Trap** {2}{U}{U}: "Exile any number of target spells." This is the App
  node of Design B, and a possible one-shot "drop a whole block".

## Reduction rules

Write `[x]` for the block of argument x and `|x|` for its object count. Each rule
takes the frame top-first from `h [a1] [a2] …` to the result. Where possible, the
suffix stays in place.

| rule | real-card actions | cost: copies / counters / passes |
|---|---|---|
| unwind: `@ F G …` → `F G …` | all pass; the `@` (a Fog copy) resolves as a no-op | 0 / 0 / 1 |
| `I x` → `x` | all pass; the `I` resolves as a no-op | 0 / 0 / 1 |
| `K x y` → `x` | counter each object of `[y]`, then counter `K`. `[x]` is already on top | 0 / \|y\|+1 / 0 |
| `W x y` → `x y y` | copy `[y]` (deepest object first), copy `[x]`, counter the old `[x]` and `W` | \|y\|+\|x\| / \|x\|+1 / 0 |
| `B x y z` → `x (y z)` = `x @ y z` | copy the `@` template, copy `[x]`, counter the old `[x]` and `B`. `[y][z]` stay in place | 1+\|x\| / \|x\|+1 / 0 |
| `C x y z` → `x z y` | copy `[y]`, copy `[z]`, copy `[x]`, counter the old `[x][y][z]` and `C` | \|x\|+\|y\|+\|z\| / \|x\|+\|y\|+\|z\|+1 / 0 |
| `S x y z` → `x z (y z)` = `x z @ y z` | copy `@`, copy `[z]`, copy `[x]`, counter the old `[x]` and `S`. `[y][z]` stay | 1+\|z\|+\|x\| / \|x\|+1 / 0 |

Notes on the table:

- Each `copy` is one Reiterate cast plus one pass.
- Each `counter` is one Reiterate cast, one pass, the new-target choice, and one more
  pass.
- To copy a block, copy its objects deepest first, so the copy reads the same
  top-first. Each copy lands on top (CR 405.2).
- **Normal form under arguments.** When the head is stuck, normalize each argument
  block, deepest first:
  1. Copy a fresh `|` and copy the block above it.
  2. Normalize that frame recursively. Re-wrap its spine `h a1…ak` into one block by
     copying `k` `@`s on top.
  3. Counter the `|`.

  Then copy the head on top and counter the old head and the old argument blocks.
  This is the simulator's `normalize`.

**Does "W = copy, K = counter, C = reorder" survive contact with real cards?**

- **K = counter** survives. It is literally Counterspell when `y` is one object, and
  `|y|` counters otherwise. `x` never moves.
- **W = copy** half survives. Copying `[y]` is native. But the copy lands *above*
  `[x]`, and the stack has no insert-below. So `[x]` must be re-copied to the top and
  its old objects countered.
- **C = reorder** does not survive. No card reorders the stack: the search below
  found no Oracle text that refers to stack position. Reordering *is*
  copy-to-top plus counter, and that makes C the most expensive rule.

The general law: **a rule that puts anything between the head and its old arguments
must re-push the head argument `[x]`.** That covers S, B, C and W. K and I do not.

So the basis choice is a wash. SKI avoids C, the worst rule. BCKW has the cheap B and
the cheap K. Neither fits the stack natively.

## Worked trace

`S K K x` → `x`. This is real output of
`python3 -I stack_machine.py --trace "S K K x"`.

- "Reiterate -> copy L#n" means: cast Reiterate with buyback, targeting object `#n`
  (label `L`), and let it resolve. The copy lands on top.
- "copy CS, new target …; CS copy resolves" means: Reiterate targets the Counterspell
  template; on resolution its controller chooses the new target (CR 707.10c); then all
  pass and the Counterspell copy counters that object. The countered copy ceases to
  exist (CR 704.5e).
- Setup builds `@ @ @ S K K x` from the templates. Template ids: `@`#0, `K`#2, `S`#3,
  `x`#4, `|`#5. The `|`/`CS` templates and everything below the base `|` are not shown.

```
  Reiterate -> copy |#5 [setup: frame]                           | top-first: |
  Reiterate -> copy x#4 [setup]                                  | top-first: x |
  Reiterate -> copy K#2 [setup]                                  | top-first: K x |
  Reiterate -> copy K#2 [setup]                                  | top-first: K K x |
  Reiterate -> copy S#3 [setup]                                  | top-first: S K K x |
  Reiterate -> copy @#0 [setup]                                  | top-first: @ S K K x |
  Reiterate -> copy @#0 [setup]                                  | top-first: @ @ S K K x |
  Reiterate -> copy @#0 [setup]                                  | top-first: @ @ @ S K K x |
  all pass -> @#13 resolves (no-op) [unwind @]                   | top-first: @ @ S K K x |
  all pass -> @#12 resolves (no-op) [unwind @]                   | top-first: @ S K K x |
  all pass -> @#11 resolves (no-op) [unwind @]                   | top-first: S K K x |
  Reiterate -> copy @#0 [S: @]                                   | top-first: @ S K K x |
  Reiterate -> copy x#7 [S: dup z]                               | top-first: x @ S K K x |
  Reiterate -> copy K#9 [S: re-top x]                            | top-first: K x @ S K K x |
  Reiterate -> copy CS, new target K#9; CS copy resolves [S: old x] | top-first: K x @ S K x |
  Reiterate -> copy CS, new target S#10; CS copy resolves [S]    | top-first: K x @ K x |
  Reiterate -> copy CS, new target @#14; CS copy resolves [K: drop y] | top-first: K x K x |
  Reiterate -> copy CS, new target K#8; CS copy resolves [K: drop y] | top-first: K x x |
  Reiterate -> copy CS, new target x#7; CS copy resolves [K: drop y] | top-first: K x |
  Reiterate -> copy CS, new target K#16; CS copy resolves [K]    | top-first: x |
result: x   ops: {'copy': 3, 'counter': 6, 'resolve': 3}
```

How to read it:

1. The three `@`s unwind by resolving: Fog copies, all players pass.
2. The `S` step pushes `@`, then a copy of `[z]`=`x`, then a re-copy of `[x]`=`K`, and
   counters the old `K` and the `S`. The frame is now `K x (K x)`, with the block
   `[K x]` coded as `@ K x`.
3. The `K` step counters the three objects of the block `@ K x` and then the `K`.

BCKW, `W K x` → `x` (real output):

```
  all pass -> @#11 resolves (no-op) [unwind @]                   | top-first: @ W K x |
  all pass -> @#10 resolves (no-op) [unwind @]                   | top-first: W K x |
  Reiterate -> copy x#7 [W: dup y]                               | top-first: x W K x |
  Reiterate -> copy K#8 [W: re-top x]                            | top-first: K x W K x |
  Reiterate -> copy CS, new target K#8; CS copy resolves [W: old x] | top-first: K x W x |
  Reiterate -> copy CS, new target W#9; CS copy resolves [W]     | top-first: K x x |
  Reiterate -> copy CS, new target x#7; CS copy resolves [K: drop y] | top-first: K x |
  Reiterate -> copy CS, new target K#13; CS copy resolves [K]    | top-first: x |
```

B/C example, `C (B f) x y` → `B f y x` → `f (y x)`. This is the head part of the real
trace, after the setup:

```
  all pass -> @#15 resolves (no-op) [unwind @]                   | top-first: C @ B f x y |
  Reiterate -> copy x#10 [C: y]                                  | top-first: x C @ B f x y |
  Reiterate -> copy y#9 [C: z]                                   | top-first: y x C @ B f x y |
  Reiterate -> copy f#11 [C: x]                                  | top-first: f y x C @ B f x y |
  Reiterate -> copy B#12 [C: x]                                  | top-first: B f y x C @ B f x y |
  Reiterate -> copy @#13 [C: x]                                  | top-first: @ B f y x C @ B f x y |
  Reiterate -> copy CS, new target @#13; CS copy resolves [C: old] | top-first: @ B f y x C B f x y |
  ... (counter old B, f, x, y, then C)
  Reiterate -> copy CS, new target C#14; CS copy resolves [C]    | top-first: @ B f y x |
  all pass -> @#22 resolves (no-op) [unwind @]                   | top-first: B f y x |
  Reiterate -> copy @#0 [B: @]                                   | top-first: @ B f y x |
  Reiterate -> copy f#20 [B: re-top x]                           | top-first: f @ B f y x |
  Reiterate -> copy CS, new target f#20; CS copy resolves [B: old x] | top-first: f @ B y x |
  Reiterate -> copy CS, new target B#21; CS copy resolves [B]    | top-first: f @ y x |
```

The `C` step moves the compound block `[B f]` = `@ B f` as a unit: three copies and
three counters. After the `B` step the frame is `f @ y x` = `f (y x)`.

## Simulator and its output

`lines/L2/stack_machine.py` models exactly the abstract mechanism and nothing else of
Magic:

- a list of labelled objects, with templates at the bottom;
- the three primitives `copy`, `counter` and `resolve_top`, where `resolve_top` is
  only allowed for `@` and `I`;
- a controller (the player) that parses blocks from the public stack and applies the
  rule table above.

It checks the result against an independent tree-based normal-order reducer. Its
counts exclude setup.

```
$ python3 -I stack_machine.py
term                         stack machine    reference        copy counter resolve
S K K x                      x                x                   3       6       3  OK
W K x                        x                x                   2       4       2  OK
B f g x                      f (g x)          f (g x)            11      10       4  OK
C f x y                      f y x            f y x               8       9       3  OK
S I I (K a)                  a                a                   5       8       5  OK
W (B f) (K a)                f a              f a                17      19       5  OK
K (I a)                      K a              K a                 5       5       3  OK
S (K (S I)) K a b            b a              b a                17      19       9  OK
K a (W W W)                  a                a                   0       6       2  OK
S (S K K) (S K K) (B a b)    a (b (B a b))    a (b (B a b))      63      61      13  OK
random: 2986/2986 agree with reference normal-order reducer (14 skipped: reference did not normalise within fuel)
cost of the single head step W x y -> x y y, |y| objects (no sharing):
  |y|=  1  copies=   2 counters=   2
  |y|=  3  copies=   4 counters=   2
  |y|=  7  copies=   8 counters=   2
  |y|= 15  copies=  16 counters=   2
ALL OK
exit=0
```

What the tests exercise:

- Compound duplication: `S I I (K a)` and `W (B f) (K a)` duplicate `(K a)`;
  `S (S K K) (S K K) (B a b)` duplicates `(B a b)`.
- Dropping a divergent argument under normal order: `K a (W W W)`.
- Reduction under an argument: `K (I a)`.

The first version of the simulator failed on `B f g x`, because a normalized argument
frame rejoined its parent as several blocks instead of one. The `@` re-wrap step in
`normalize` is the fix.

What the simulator does **not** model:

- casting costs and mana;
- priority passes by the opponent;
- the legality of each target. This is argued by citation, not simulated.
- Design B.

## Where it breaks / open rules questions

1. **Hard part (1): delimiting an argument.** An argument is a block of `|a|`
   objects. Its extent is found by counting: `@` adds 1, an atom subtracts 1, and the
   block ends at 0. No card counts, so the *player* finds it by reading the public
   stack (CR 400.2).
   - Dropping a block costs `|a|` counters. Copying it costs `|a|` copies, deepest
     first.
   - Nothing groups a block into a unit. Mindbreak Trap ("Exile any number of target
     spells") could drop a block in one action, but its number of targets is fixed
     when it is cast (CR 601.2c) and copied with it (CR 707.10). So no single parked
     copy handles blocks of every size.
   - Duplication without sharing costs time linear in the block, and the term can
     grow exponentially across steps (as in any tree-copying reducer).
2. **Hard part (2): behaviour depending on what is beneath.** It doesn't. The term
   objects are inert, and a card reaches another stack object only by *targeting* it.
   A Scryfall search for Oracle text containing "top of the stack", or "beneath"
   together with "stack", returned no cards. The search was wording-limited, not
   exhaustive. The only position-sensitive mechanism is resolution order
   (CR 405.5), and I use it only for the no-op `@` and `I`.
3. **Hard part (3): forcedness. Not achieved; cooperative only, and unrestricted.**
   - Every target is a player's choice (CR 601.2c; "you may choose new targets",
     CR 707.10c, 115.7d). No card picks a target by stack position.
   - Every Reiterate cast and every Scepter activation is optional.
   - Loops with optional actions don't draw (CR 104.4b), so unbounded play is legal,
     but correctness rests on the player following the protocol.
   - A narrower variant could make K *self-executing* when `y` is one object: the `K`
     object is itself a Counterspell copy whose target the player sets to `[y]` when
     the copy is made. It still needs a player choice, and it does not extend to
     compound `y` (point 1). Not modelled.
4. **Hard part (4): the engine** is described under Representation. It is persistent
   and holds no triggered abilities. Everything is instant speed within one step, so
   the mana pool does not empty mid-computation (mana empties between steps) and the
   turn never needs to advance.
5. **Interference.** In a two-player game, every pass gives the opponent priority
   (CR 117.3d), and the opponent may respond. The model assumes they pass. That
   assumption is part of "cooperative".
6. **End of computation.** When the player stops and everyone passes, the whole stack
   resolves, including the Counterspell template, which counters whatever it targets.
   The read-out happens before that. Whether "the answer" should be a game outcome
   rather than a stack state that players read is a P1 question.
7. **Rules points used and believed sound, but not judge-checked:**
   - A copy of Counterspell given a new target counters that target. The copied spell
     is a spell (CR 707.10: "A copy of a spell is itself a spell"). The new target only
     needs to be legal, and "target spell" admits any other spell (CR 115.5,
     CR 707.10c).
   - Reiterate's target is legal when it resolves, because the targeted object is
     still on the stack (CR 608.2b).
   - A countered copy ceases to exist (CR 701.6a, 704.5e).
   - Buyback returns Reiterate to hand (CR 702.27a).
8. **Design B rule obstacles** (if L3 or P1 revisit pointers):
   - one "target" word cannot repeat an object (CR 601.2c), so `App(y,y)` is
     impossible;
   - a removed referent kills the pointer (CR 608.2b);
   - new nodes only go on top (CR 405.2).

## What I did not verify

- **The mana loop's arithmetic is mine.** Lotus makes 3, the Scepter costs 2, and
  Dramatic Reversal untaps both, for +1 mana of one colour per iteration. Each
  buyback-Reiterate costs 6. This is standard community lore that I have not checked
  against a ruling. Any other infinite-mana source would serve.
- No ruling or judge source on chaining Reiterate on Counterspell copies across many
  iterations. I rely on the CR citations above.
- Whether more than six distinct targetless "inert" instants exist. Six were verified;
  a term with many free variables needs more labels. Closed terms need only
  `S K I @ |` or `B C K W @ |`.
- Design B was not simulated, and its cost claims are argument only.
- The Scryfall search for stack-position wording covered two phrasings. I did not do
  an exhaustive sweep for cards that inspect stack order.
- The simulator's controller is trusted code. It shows that the protocol is correct
  given the three primitives. It does not show that Magic's rules permit only those
  primitives.
- Multiplayer, split second, "can't be countered" and similar effects were not
  considered. None appear in the construction.

## Status

- 2026-11-21: L2 note and simulator written; `stack_machine.py` passes (10 fixed and
  2986 random terms). Model: cooperative and unrestricted, unbounded given the
  infinite-mana engine, not forced. Recommend that P1 weigh this design against L3's
  battlefield heap. Design B's pointer idea belongs there.
