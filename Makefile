HERE = $(shell pwd)
BIN = $(HERE)/bin
PYTHON = $(BIN)/python

INSTALL = $(BIN)/pip install
VTENV_OPTS ?= --distribute

.PHONY: all build test

all: build

$(PYTHON):
	virtualenv $(VTENV_OPTS) .

build: $(PYTHON)
	$(PYTHON) setup.py develop
	$(INSTALL) monolith[test]

test: build
	$(BIN)/nosetests -s -d -v --with-coverage --cover-package monolith monolith
