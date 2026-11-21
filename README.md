# Combinators on the Battlefield: BCKW and SKI Reduction in Magic: The Gathering

Draft paper (N. E. Davis / Sigilante). Combinatory-logic terms are laid out as forests of Auras with
"Enchant permanent", where application is attachment, and reduced in normal order by three
game actions: re-attach (Simic Guildmage), copy (Flash Photography or Replicator) and
sacrifice (Auratog), with state-based actions deleting K's discarded argument.

Scope, stated in the paper and kept here: the model is **cooperative**, not forced. One
player chooses every action; the cards permit the reduction moves and do not forbid others.
This is not a Turing-completeness result in the forced sense of Churchill, Biderman and
Herrick. Rules legality is our reading of the Comprehensive Rules of 6 November 2026, with
no judge confirmation. The simulators check the abstract moves and some rule mechanics,
not the rules of Magic.

## Contents

- `paper.tex`, `paper.bib`: the paper. Build with `make` (runs `latexmk -pdf`).
- `sim/`: the checkers the paper reports on, each with its saved output. All are
  standard-library Python 3; `make sim` re-runs them (L9 takes about two minutes).
  - `sim/L6/l6sim.py`, `output.txt`: the Flash Photography / Reiterate engine.
  - `sim/L9/l9sim.py`, `output.txt`: the Replicator engines G and R (the saved file ends
    with an extra `exit 0` line). `l9sim.py` imports `../L6/l6sim.py`, so keep the layout.
  - `sim/L3/l3sim.py`, `l3sim.out`: the first battlefield simulator (bounded copies).
  - `sim/L2/stack_machine.py`, `output.txt`: the term-on-the-stack machine.
  - `sim/L4/lgx_machine.py`, `output.txt`: the library/graveyard two-stack machine. The
    saved file holds four invocations (plain, `--random 3000`, `--budget 1500`,
    `--trace --moves`), each shown after a `$` line.
  - `sim/L7/cursor_machine.py`, `cursor_machine.out`: the one-hop cursor machine.
- `notes/`: the working notes the paper is drawn from, `L1` to `L11`, archived unedited.
  In the notes, `lines/Ln/` means `sim/Ln/` here, and `PLAN.md`, `README.md` and the
  notes `L0` and `P1` refer to files that are not archived.

## The notes are superseded by the paper

Where a note and the paper disagree, the paper is the corrected version. Known
corrections:

- `notes/L6-hybrid.md`: read it with the review addendum at its end (legality is a rules
  reading, not a simulation result; one invariant is only half asserted in `l6sim.py`; the
  second reducer shares code with the first; trace 2's cascade takes three checks).
- `notes/L4-library-paper-native.md`: its summary points to L2 and L3 "for forced
  reduction". Neither achieves forced reduction; see the paper's section on it.
- `notes/L3-battlefield-graph.md`: its label cards (Confiscate as the cell, and so on) were
  replaced in L6 by labels that are inert where they land.
- `notes/L9-replicator.md`: its "8-34%" saving for engine G is 8-35% when recomputed from
  `sim/L9/output.txt`.
- `notes/L1-prior-art.md`: bibliographic details are superseded by `notes/L11-bib-check.md`
  (for example, Churchill, Biderman and Herrick is FUN 2021, LIPIcs 157, published 2020).
- Rule 117.5 is quoted in L6 with rule 704.3's wording, and the 707.10 quotation there is
  reordered; `notes/L10-source-check.md` records both.

## Licence

Paper text, figures, PDF and notes: CC BY 4.0 (`LICENSE`). Simulators: MIT (`LICENSE-CODE`). See `LICENSING.md`.
