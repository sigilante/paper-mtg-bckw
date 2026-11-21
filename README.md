# Combinators on the Battlefield: BCKW and SKI Reduction in Magic: The Gathering

Draft paper (N. E. Davis). Combinatory-logic terms are laid out as forests of Auras with
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
- `sim/L6/l6sim.py`, `sim/L6/output.txt`: simulator for the Flash Photography / Reiterate
  engine and its saved output.
- `sim/L9/l9sim.py`, `sim/L9/output.txt`: simulator for the Replicator engine and its saved
  output (the saved file ends with an extra `exit 0` line). `l9sim.py` imports
  `../L6/l6sim.py`, so keep the directory layout.
- `make sim` re-runs both (standard-library Python 3; L9 takes about two minutes).

The simulators and the notes the paper is drawn from come from the `lean-mtg` working
directory (`lines/L6`, `lines/L9`, `notes/L1`–`L10`).
