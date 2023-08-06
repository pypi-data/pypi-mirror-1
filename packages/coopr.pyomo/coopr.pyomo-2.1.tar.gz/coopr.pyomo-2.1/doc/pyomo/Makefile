#
# Create The Following Documents:
#
#   . Coopr User Manual: Getting Started with the Pyomo Modeling Language
#     pyomo.tex
#
#   . Coopr User Manual: Pyomo Modeling Language and Extension Packages
#     coopr.tex
#

all: coopr pyomo


coopr:
	pdflatex coopr
	bibtex coopr
	pdflatex coopr
	pdflatex coopr
	cp coopr.pdf ../pub

pyomo:
	pdflatex pyomo
	bibtex pyomo
	pdflatex pyomo
	pdflatex pyomo
	cp pyomo.pdf ../pub

