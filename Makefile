# Build the paper with latexmk (pdflatex + bibtex).
PAPER = paper

.PHONY: all clean distclean sim

all: $(PAPER).pdf

$(PAPER).pdf: $(PAPER).tex $(PAPER).bib
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(PAPER).tex

# Re-run the checkers; outputs should match the saved files next to each script
# (L9 takes about two minutes, and its saved output ends with an extra "exit 0" line;
# sim/L4/output.txt holds four invocations, see README).
sim:
	cd sim/L6 && python3 -I -B l6sim.py
	cd sim/L9 && python3 -I -B l9sim.py
	cd sim/L3 && python3 -I -B l3sim.py
	cd sim/L2 && python3 -I -B stack_machine.py
	cd sim/L4 && python3 -I -B lgx_machine.py && python3 -I -B lgx_machine.py --random 3000
	cd sim/L7 && python3 -I -B cursor_machine.py

clean:
	latexmk -c $(PAPER).tex

distclean:
	latexmk -C $(PAPER).tex
