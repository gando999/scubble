
define HELP

This is the scubble Makefile.

Usage:

make interp         - Run interpreter
make requirements   - Install requirements
make clean          - Remove generated files

endef


requirements:
	pip install -r requirements.txt


interp: requirements
	python scubble.py


clean:
	find . -name '*.pyc' -delete
	find . -name '*.out' -delete
	rm -f parsetab.py
