# Build the paper with latexmk (pdflatex + bibtex).
PAPER = paper

.PHONY: all clean distclean sim

all: $(PAPER).pdf

$(PAPER).pdf: $(PAPER).tex $(PAPER).bib
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(PAPER).tex

# Re-run the simulators; outputs should match sim/L6/output.txt and sim/L9/output.txt
# (L9 takes about two minutes, and its saved output ends with an extra "exit 0" line).
sim:
	cd sim/L6 && python3 -I -B l6sim.py
	cd sim/L9 && python3 -I -B l9sim.py

clean:
	latexmk -c $(PAPER).tex

distclean:
	latexmk -C $(PAPER).tex
