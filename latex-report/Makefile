# Makefile for CSKG LaTeX Report

MAIN = cskg_report
TEX = $(MAIN).tex
PDF = $(MAIN).pdf
DOCKER_IMAGE = texlive/texlive:latest

.PHONY: all clean docker

all: $(PDF)

$(PDF): $(TEX) references.bib sections/*.tex
	pdflatex $(MAIN)
	bibtex $(MAIN)
	pdflatex $(MAIN)
	pdflatex $(MAIN)

clean:
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.synctex.gz *.fls *.fdb_latexmk

docker:
	docker run --rm -v $(PWD):/workdir -w /workdir $(DOCKER_IMAGE) \
		sh -c "pdflatex $(MAIN) && bibtex $(MAIN) && pdflatex $(MAIN) && pdflatex $(MAIN)"
