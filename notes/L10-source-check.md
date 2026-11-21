# L10 — Source check of the quotes in README.md and notes/L6-hybrid.md

Checked 2026-11-21. Scope: only whether quoted Oracle text, rulings and Comprehensive Rules
(CR) text match their sources. No assessment of the construction.

## Sources and method

- **Cards and rulings:** Scryfall, one request per card to `/cards/named?exact=NAME`, then that
  card's `rulings_uri`. 24 cards, 24 rulings lookups. Generic client name, no other data sent.
- **Rules:** a per-rule source. The mtg.wiki site renders any single CR rule through its `CR`
  template; I called the wiki's `expandtemplates` API once per rule (`{{CR|303.4f}}` and so on),
  about 55 small requests. Each response is headed "From the Comprehensive Rules (November 6,
  2026 — Star Trek)", which is the CR edition L6 cites (effective 2026-11-06). I did not fetch
  the full CR document, and did not retry the yawgatog page. (A WebFetch of one mtg.wiki
  `Rule_303.4` URL returned 403 and that URL does not exist; the API route above worked with an
  honest user agent.)
- Typographic differences (curly vs straight apostrophes, nested quote marks) are ignored.
  Ellipses in a note's quote are accepted when the omitted words are not needed for sense.

## Table 1: cards (24; Oracle text, type line, legalities)

All 24: `games` includes `paper`; Legacy, Vintage and Commander all `legal`; none `reserved`.
All 13 Auras have type line "Enchantment — Aura", Oracle text beginning "Enchant permanent"
(Take Possession after its Split second line), and no Legendary supertype.

| card | quote vs Oracle | type line | Aura / "Enchant permanent" / not legendary | paper; Leg / Vin / Cmdr |
|---|---|---|---|---|
| Flash Photography | match | Sorcery | n/a | paper+mtgo; L/L/L |
| Reiterate | match | Instant | n/a | paper+mtgo; L/L/L |
| Isochron Scepter | match | Artifact | n/a | paper+mtgo; L/L/L |
| Dramatic Reversal | match | Instant | n/a | paper+mtgo+arena; L/L/L |
| Gilded Lotus | match | Artifact | n/a | paper+mtgo; L/L/L |
| Simic Guildmage | match | Creature — Elf Wizard | n/a | paper+mtgo; L/L/L |
| Auratog | match | Creature — Atog | n/a | paper+mtgo; L/L/L |
| Island | match | Basic Land — Island | n/a | paper+mtgo+arena; L/L/L |
| Indestructibility | match | Enchantment — Aura | yes / yes / not legendary | paper+mtgo; L/L/L |
| Bound in Gold | match | Enchantment — Aura | yes / yes / not legendary | paper+arena+mtgo; L/L/L |
| Intercessor's Arrest | match | Enchantment — Aura | yes / yes / not legendary | paper+arena+mtgo; L/L/L |
| Curator's Ward | match | Enchantment — Aura | yes / yes / not legendary | paper+arena+mtgo; L/L/L |
| Essence Leak | match | Enchantment — Aura | yes / yes / not legendary | paper+mtgo; L/L/L |
| Faith's Fetters | match | Enchantment — Aura | yes / yes / not legendary | paper+arena (no MTGO); L/L/L |
| Elemental Resonance | match (reminder text elided by "(…)") | Enchantment — Aura | yes / yes / not legendary | paper+mtgo; L/L/L |
| Confiscate | match | Enchantment — Aura | yes / yes / not legendary | paper+arena+mtgo; L/L/L |
| Lay Claim | match (cycling reminder elided by "…") | Enchantment — Aura | yes / yes / not legendary | paper+mtgo; L/L/L |
| Volition Reins | match | Enchantment — Aura | yes / yes / not legendary | paper+mtgo; L/L/L |
| Take Possession | match (Split second reminder elided by "…") | Enchantment — Aura | yes / yes / not legendary | paper+mtgo; L/L/L |
| Psychic Overload | match | Enchantment — Aura | yes / yes / not legendary | paper+mtgo; L/L/L |
| Dream Leash | match | Enchantment — Aura | yes / yes / not legendary | **paper+mtgo; L/L/L** (the status L6 left unchecked: it is a real paper card and legal in all three) |
| Replicator | match (Food reminder elided by "…") | Artifact | n/a | paper+mtgo+arena; L/L/L |
| Mythos of Illuna | match as far as quoted: the note quotes only the first sentence and omits the {R}{G} fight clause, with no ellipsis | Sorcery | n/a | paper+arena+mtgo; L/L/L |
| Replication Technique | match as far as quoted ("Create a token that's a copy of target permanent you control."; Demonstrate omitted) | Sorcery | n/a | paper+mtgo; L/L/L |

Oracle texts, for the record (not all quoted by L6 verbatim): Flash Photography "You may cast
this spell as though it had flash if it targets a permanent you control. / Create a token that's
a copy of target permanent. / Flashback {4}{U}{U}"; Replicator "When this artifact enters,
create a Food token. (…) / {2}, {T}: Create a tapped token that's a copy of target token you
control." Counts: 24 match, 0 mismatch, 0 not checked.

## Table 2: rulings (Scryfall copies of the Gatherer rulings)

| card, date quoted | result |
|---|---|
| Simic Guildmage 2006-05-01 (second-ability ruling) | **match**: text and date. It is one of 3 rulings dated 2006-05-01. |
| Reiterate 2021-03-19 | **match**: "The copy is created on the stack, so it's not "cast." … The copy will resolve before the original spell does." (the middle sentence is elided) and "You can't choose to pay any alternative or additional costs for the copy." (the source adds "However, effects based on …"; truncated after the period). |
| Flash Photography 2025-10-02 | **match**: "If the copied permanent is a token, the new token that's created copies the original characteristics of that token as stated by the effect that created the token." exact. The "doesn't copy … any Auras or Equipment attached to it" quote is an elision of "It doesn't copy whether that permanent is tapped or untapped, whether it has any counters on it or any Auras or Equipment attached to it, or …". |
| Mythos of Illuna 2020-04-17 (Aura ruling) | **match**, exact, one of 13 rulings dated 2020-04-17. L6's side claim "RG bonus does not apply to copies" matches the ruling "If an effect copies the Mythos spell, no mana was spent to cast the copy, so the copy won't receive the bonus." (that ruling is about copies of the spell, which is the L6 context of copying the spell). |
| Isochron Scepter 2020-08-07 | **match**: "You cast the copy while the ability is resolving and still on the stack." The source continues "You can't wait to cast it later in the turn."; the note truncates there without an ellipsis. |
| Essence Leak 2004-10-04 | **match**: "It can enchant a permanent that is not red or green, but it doesn't do anything in that case." |
| Replicator 2026-10-07 | **match**: the quote ("The token copies the original characteristics of the target token as stated by the effect that created it … It doesn't copy … any Auras or Equipment attached to it") elides the middle correctly; date matches (3 rulings, all 2026-10-07). |
| "Auratog and Dramatic Reversal have no rulings on Scryfall" | **match**: both return 0 rulings. |
| README: "Mythos of Illuna ruling on the same effect" (hosts chosen, not targeted) | **match** (same ruling as above). |

Counts: 9 match, 0 mismatch, 0 not found. Replication Technique has five rulings (2021-04-16,
all about demonstrate); L6 quotes none of them.

## Table 3: Comprehensive Rules (edition November 6, 2026)

"cited" means L6 names the rule but quotes no text; the retrieved text supports the use.

| rule | L6 quotes it? | result |
|---|---|---|
| 303.4d | yes | match (ellipsis between "enchant itself." and "An Aura can't enchant more than one object or player.") |
| 303.4e | yes | match (with elisions) |
| 303.4f | yes | match, word for word |
| 303.4g | yes | match ("… If the Aura is a token, it isn't created.") |
| 111.2 | yes | match |
| 111.3 | yes | match (with elisions) |
| 111.7 | cited | match: "A token that's in a zone other than the battlefield ceases to exist. This is a state-based action" |
| 707.2 | yes | match (with elisions) |
| 707.10 | yes | **mismatch (minor, fragment order)**: see list below |
| 707.10c | yes | match |
| 707.10f | yes | match: "As that copy resolves, it ceases being a copy of a spell and becomes a token permanent." |
| 405.2 | yes | match |
| 405.5 | cited with 117.4 | match in substance. The quoted words "if the stack is empty, the phase or step ends" are 117.4's wording; 405.5 reads "If the stack is empty when all players pass, the current step or phase ends and the next begins." |
| 117.1a | yes | match |
| 117.1b | yes | match |
| 117.4 | yes | match |
| 117.5 | yes, jointly with 704.3 | **mismatch (minor, attribution)**: see list below |
| 500.2 | yes | match (with elision) |
| 608.2b | yes | match (with elisions) |
| 702.27a | yes | match |
| 106.4 | yes | match |
| 704.3 | yes | match, word for word (quoted under "117.5 / 704.3") |
| 704.5b | yes | match |
| 704.5d | yes | match |
| 704.5j | cited | match: legend rule |
| 704.5m | yes | match |
| 704.5p | cited | match: a noncreature, nonbattle permanent that is not an Aura, Equipment or Fortification and is attached "becomes unattached and remains on the battlefield" |
| 701.21a | yes | match |
| 701.3a | no | cited only by the L6 review addendum ("cite 701.3 for attach"); text below |
| 701.3b | yes | match |
| 701.3c | no | text below |
| 104.4b | yes | match |
| 733.4 | yes | match |
| 603.4 | cited | match: intervening "if" rule |
| 700.6 | cited | match: "historic" = legendary supertype, artifact card type, or Saga subtype |
| 702.11b | yes | match: "This permanent can't be the target of spells or abilities your opponents control." |
| 400.7 | addendum only | match: "An object that moves from one zone to another becomes a new object with no memory of, or relation to, its previous existence." |
| 702.26a, b, d, g, h, i | no (phasing; not in L6) | text retrieved; quoted below |
| 307.1, 601.2c, 613.1b, 733.2a, 400.2 | cited | match: 307.1 sorcery timing; 601.2c announcing targets; 613.1b layer 2 control-changing effects; 733.2a shortcuts; 400.2 public zones |

Counts (48 rules checked: the 36 on the list, the 6 phasing rules, and 6 other cited rules):
46 match, 2 mismatch (minor), 0 not checked. The 6 phasing rules and 701.3a/c are not quoted in
L6, so "match" there means only "text retrieved".

### 702.26 (phasing), text as retrieved

- **702.26a** "Phasing is a static ability that modifies the rules of the untap step. During each player's untap step, before the active player untaps permanents, all phased-in permanents with phasing that player controls "phase out." Simultaneously, all phased-out permanents that had phased out under that player's control "phase in.""
- **702.26b** "If a permanent phases out, its status changes to "phased out." Except for rules and effects that specifically mention phased-out permanents, a phased-out permanent is treated as though it does not exist. It can't affect or be affected by anything else in the game. A permanent that phases out is removed from combat."
- **702.26d** "The phasing event doesn't actually cause a permanent to change zones or control, even though it's treated as though it's not on the battlefield and not under its controller's control while it's phased out. Zone-change triggers don't trigger when a permanent phases in or out. Tokens continue to exist on the battlefield while phased out. Counters and stickers remain on a permanent while it's phased out. …"
- **702.26g** "When a permanent phases out, any Auras, Equipment, or Fortifications attached to that permanent phase out at the same time. This alternate way of phasing out is known as phasing out "indirectly." An Aura, Equipment, or Fortification that phased out indirectly won't phase in by itself, but instead phases in along with the permanent it's attached to."
- **702.26h** "If an object would simultaneously phase out directly and indirectly, it just phases out indirectly."
- **702.26i** "An Aura, Equipment, or Fortification that phased out directly will phase in attached to the object or player it was attached to when it phased out, if that object is still in the same zone or that player is still in the game. If not, that Aura, Equipment, or Fortification phases in unattached. State-based actions apply as appropriate. (See rules 704.5m and 704.5n.)"

**Does 702.26g apply recursively (Aura A2 on Aura A1 on permanent X, X phases out)?**
Recursion is **not stated; it is implied, with some residual doubt, so "unclear" in the strict
sense.** What the text gives:
- The trigger clause is "When a permanent phases out, any Auras, Equipment, or Fortifications
  attached to that permanent phase out at the same time." A1 is attached to X, so A1 phases out
  indirectly. The text never says whether A1's indirect phasing counts as "a permanent phases
  out" for the purpose of this same sentence. Read literally, it does (A1 is a permanent and
  702.26g itself calls this "phasing out"), and then A2 follows. Nothing in 702.26 says it does
  not.
- Support for recursion: 702.26g's second sentence says an indirectly phased-out Aura "phases in
  along with the permanent it's attached to". Applied to A2, that permanent is A1, which itself
  phases in only along with X. A chain is implied on the way in. 702.26h ("an object would
  simultaneously phase out directly and indirectly") is also written for objects that can be
  reached by more than one route.
- Against: "at the same time" and "that permanent" could be read as covering only the permanent
  that phases out by its own phasing ability. The text has no example with an Aura on an Aura.
- I did not consult phasing rulings or Gatherer for this; the answer rests on the rule text above.

## Q4: what keeps things attached to a moved Aura?

No single rule says it in positive terms. Retrieved text that bears on it:
- **701.3a** "To attach an Aura, Equipment, or Fortification to an object or player means to take
  it from where it currently is and put it onto that object or player. If something is attached
  to a permanent on the battlefield, it's customary to place it so that it's physically touching
  the permanent. An Aura, Equipment, or Fortification can't be attached to an object or player it
  couldn't enchant, equip, or fortify, respectively."
- **701.3b** "If an effect tries to attach an Aura, Equipment, or Fortification to an object or
  player it can't be attached to, the Aura, Equipment, or Fortification doesn't move. If an effect
  tries to attach an Aura, Equipment, or Fortification to the object or player it's already
  attached to, the effect does nothing. If an effect tries to attach an object that isn't an Aura,
  Equipment, or Fortification to another object or player, the effect does nothing and the first
  object doesn't move."
- **701.3c** "Attaching an Aura, Equipment, or Fortification on the battlefield to a different
  object or player causes the Aura, Equipment, or Fortification to receive a new timestamp."
- **701.3d** (unattach) "…If an Aura, Equipment, or Fortification that was attached to an object
  or player ceases to be attached to it, that counts as "becoming unattached [from that object or
  player]"; this includes if that Aura, Equipment, or Fortification leaves the battlefield, the
  object leaves the zone it was in, or that player leaves the game."
- **400.7** "An object that moves from one zone to another becomes a new object with no memory of,
  or relation to, its previous existence." Attaching (701.3a) changes what the Aura is put onto,
  not its zone, and 701.3c gives only a new timestamp, so 400.7 is not triggered and the moved
  Aura is the same object.
- The ways attachment ends are enumerated elsewhere: 704.5m (an Aura attached to an illegal
  object, or to nothing, goes to the graveyard), 704.5p (a non-Aura attached becomes unattached),
  303.4d (self-enchant or more than one host), 701.3d (the host leaves the zone, or the attachee
  leaves). Attaching A1 elsewhere is none of these for A2, whose host (A1) is still a legal,
  on-battlefield object.

So the claim in L6's review addendum is an argument from absence: 701.3a moves only the named
Aura; nothing in 701.3 detaches what hangs from it; no zone change occurs (400.7); no state-based
action fires. The CR has no sentence of the form "things attached to a moved Aura stay attached".

## Mismatches (every one)

1. **707.10 (L6, "Rules relied on"), fragment order.** L6: "A copy of a spell … copies … all
   decisions made for it, including modes, targets … a copy of a spell isn't cast … A copy of a
   spell or ability is controlled by the player under whose control it was put on the stack. A
   copy of a spell is itself a spell". Source: "To copy a spell, activated ability, or triggered
   ability means to put a copy of it onto the stack; a copy of a spell isn't cast and a copy of an
   activated ability isn't activated. A copy of a spell or ability copies both the characteristics
   of the spell or ability and all decisions made for it, including modes, targets, the value of
   X, and additional or alternative costs. … A copy of a spell or ability is controlled by the
   player under whose control it was put on the stack. A copy of a spell is itself a spell, even
   though it has no spell card associated with it." The note's "isn't cast" fragment comes after
   "copies … decisions" in the note and before it in the source; "A copy of a spell … copies" also
   elides "or ability copies both the characteristics of the spell or ability and". Meaning is
   preserved. Note too that the source says "additional or alternative costs" ARE copied, while
   the Reiterate ruling says the copy's controller cannot pay new ones; L6 uses only the ruling.
2. **117.5 (L6, "117.5 / 704.3"), attribution.** L6 quotes "Whenever a player would get priority
   …, the game checks for any of the listed conditions for state-based actions, then performs all
   applicable state-based actions simultaneously as a single event. If any state-based actions
   are performed as a result of a check, the check is repeated". That is 704.3's wording, verbatim.
   117.5 reads: "Each time a player would get priority, the game first performs all applicable
   state-based actions as a single event (see rule 704, "State-Based Actions"), then repeats this
   process until no state-based actions are performed. Then triggered abilities are put on the
   stack …". Same substance; the quote belongs to 704.3 only.

Not mismatches, but worth knowing: the engine table quotes Mythos of Illuna and Replicator only
in part (flagged above); the Isochron ruling is cut after its first sentence without an ellipsis.

## What I did not check

- The CR text came from mtg.wiki's per-rule rendering, not from Wizards' own document. It
  declares the November 6, 2026 edition. I did not compare with the Wizards text or with
  yawgatog.
- Rulings are Scryfall's copies of the Gatherer rulings; I did not open Gatherer. A ruling newer
  than Scryfall's copy, or a judge's answer, would not appear.
- Cards other than the 24 above: the 32-card label search and its results, the "Rejected
  labels" (Song of the Dryads, Minimus Containment, Reality Acid, In Bolas's Clutches
  "Legendary", the five Runes, Feedback, Power Leak, Power Taint, Soul Tithe, Detention Vortex,
  Suppression Bonds, Gobsmacked), the card list in "Alternatives weighed" (Romana II, Lithoform
  Engine, Cackling Counterpart and the rest), the searches 1-4 and their counts, and any claim
  of the form "no card does X".
- Mana values, costs and mana costs in prose beyond the Oracle text itself (for example "Reiterate
  with buyback costs 6 mana").
- That a printing of each card is currently in print or purchasable: "paper" here means Scryfall
  lists `paper` in `games`, not a check of a specific set.
- Legality was read from Scryfall's `legalities` flags only; no check against the official banned
  lists.
- Whether any of the rules readings (interpretation of the quotes) is right. This note checks
  the words, not the inferences, and not the simulator.
- The phasing rules are not used in L6; they were checked at the request of the reviewer (L8
  covers phasing). I did not read the phasing rulings or other phasing sources.
